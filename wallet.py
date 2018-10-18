import aiohttp
import logging
import json
from re import finditer
from datetime import datetime

import grcconf as g

'''
1 - protocol/client error
2 - invalid args
3 - net exception
4 - invalid type
'''


def scan_projects(averages: str) -> dict:
    final = {}
    for project_info in averages.split(';')[:-1]:
        project, team_rac, __ = project_info.split(',')
        if project != 'NeuralNetwork':
            final[project] = team_rac + ' RAC'
    return final


async def query(cmd: str, *params):
    try:
        assert isinstance(cmd, str)
        command = json.dumps({'method' : cmd, 'params' : params})
    except (AssertionError, TypeError):
        # Either cmd isn't str, or params isn't serializable
        logging.warning('Invalid data sent to wallet query')
        return 2
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(g.rpc_url, data=command, headers={'content-type': "application/json", 'cache-control': "no-cache"}, auth=aiohttp.BasicAuth(g.rpc_usr, password=g.rpc_pass)) as resp:
                # split up steps as a workaround for resp.json() not working
                # with output from `gettransaction` for superblock transactions
                # (aiohttp trying to decode <BINARY> part in hashboinc string)
                raw = await resp.read()
                text = raw.decode('utf-8', 'ignore')
                response = json.loads(text)
    except Exception as E:
        logging.warning('Exception triggered in communication with GRC client: %s', E)
        logging.warning('CMD: %s ARGS: %s', cmd, params)
        return 3
    if response['error'] != None:
        if response['error']['code'] == -17:
            return None
        logging.warning('Error response sent by GRC client: %s', response['error'])
        logging.warning('CMD: %s ARGS: %s', cmd, params)
        return 1
    else:
        return response['result']


async def tx(addr, amount):
    if isinstance(addr, str) and len(addr) > 1:
        return await query('sendtoaddress', addr, amount)
    return 4


async def get_block(height):
    current_block = await query('getblockcount')
    if height < 0 or height > current_block:
        return None
    else:
        block_data = await query('getblockbynumber', height)
        if type(block_data) is int:
            return None
        data = {
            'Height': height,
            'Hash': block_data['hash'],
            'Time (UTC)':
                datetime.utcfromtimestamp(block_data['time']).isoformat(' '),
            'Difficulty': round(block_data['difficulty'], 4),
            'Net Weight': round(g.NET_W_MULT * block_data['difficulty']),
            'No. of TXs': len(block_data['tx']),
            'Amount Minted': block_data['mint'],
            'Superblock': 'No' if (block_data['IsSuperBlock'] == 0) else 'Yes',
        }
        return data


async def get_last_superblock():
    listdata_sb = await query('listdata', 'superblock')
    height = listdata_sb['block_number']
    sb_details = await query('showblock', int(height))
    sb_time = datetime.utcfromtimestamp(sb_details['time']).isoformat(' ')
    final = {'Height' : height, 'Time (UTC)' : sb_time}
    final.update(scan_projects(listdata_sb['averages']))
    return final


async def unlock():
    return await query('walletpassphrase', g.grc_pass, 999999999, False)
