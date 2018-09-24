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


def scan_projects(data):
    final = {}
    start_projects = list(finditer('<AVERAGES>', data))[0].end()
    end_projects = list(finditer('</AVERAGES>', data))[0].start()-1
    for project_info in data[start_projects:end_projects].split(';'):
        project, team_rac, __ = project_info.split(',')
        if project != 'NeuralNetwork':
            final[project] = team_rac + ' RAC'
    return final


async def query(cmd, params):
    if not all([isinstance(cmd, str), isinstance(params, list)]):
        logging.warning('Invalid data sent to wallet query')
        return 2
    command = json.dumps({'method' : cmd, 'params' : params})
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(g.rpc_url, data=command, headers={'content-type': "application/json", 'cache-control': "no-cache"}, auth=aiohttp.BasicAuth(g.rpc_usr, password=g.rpc_pass)) as resp:
                # split up steps as a workaround for resp.json() not working
                # with output from `gettransaction` for superblock transactions
                # (aiohttp trying to decode <BINARY> part in hashboinc string?) 
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
        return await query('sendtoaddress', [addr, amount])
    return 4


async def get_block(height):
    current_block = await query('getblockcount', [])
    if height < 0 or height > current_block:
        return None
    else:
        data = {}
        block_hash = await query('getblockhash', [height])
        block_data = await query('getblock', [block_hash])
        if type(block_data) is int:
            return None
        data['Height'] = height
        data['Hash'] = block_hash
        data['Timestamp (UTC)'] = datetime.utcfromtimestamp(block_data['time']).isoformat(' ')
        data['Difficulty'] = round(block_data['difficulty'], 4)
        data['Net Weight'] = round(g.NET_W_MULT * block_data['difficulty'])
        data['No. of TXs'] = len(block_data['tx'])
        data['Amount Minted'] = block_data['mint']
        data['Superblock'] = 'No' if (block_data['IsSuperBlock'] == 0) else 'Yes'
        return data


async def get_last_superblock():
    superblocks = await query('superblocks', [])
    height_key_string = [k for k in list(superblocks[1].keys()) if 'Block #' in k][0]
    height = height_key_string[height_key_string.index('#')+1:]
    last_time = superblocks[1]['Date'] + ' UTC'
    superblock = await query('getblock', [superblocks[1][height_key_string]])
    super_tx = await query('gettransaction', [superblock['tx'][0]])
    final = {'Height' : height, 'Time' : last_time}
    final.update(scan_projects(super_tx['hashboinc']))
    return final


async def unlock():
    return await query('walletpassphrase', [g.grc_pass, 999999999, False])
