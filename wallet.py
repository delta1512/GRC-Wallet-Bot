import grcconf as g
import aiohttp
import asyncio
import json

'''
1 - protocol/client error
2 - invalid args
3 - net exception
4 - invalid type
'''

async def query(cmd, params):
    if not all([isinstance(cmd, str), isinstance(params, list)]):
        print('[WARN] Invalid data sent to wallet query')
        return 2
    command = json.dumps({'method' : cmd, 'params' : params})
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(g.rpc_url, data=command, headers={'content-type': "application/json", 'cache-control': "no-cache"}, auth=aiohttp.BasicAuth(g.rpc_usr, password=g.rpc_pass)) as resp:
                response = await resp.json()
    except Exception as E:
        print('[WARN] Exception triggered in communication with GRC client\n', E)
        return 3
    if response['error'] != None:
        if response['error']['code'] == -17:
            return None
        print('[WARN] Error response collected by GRC client: ', response['error'])
        return 1
    else:
        return response['result']

async def tx(addr, amount):
    if isinstance(addr, str) and len(addr) > 1:
        return await query('sendtoaddress', [addr, amount])
    else:
        return 4

async def unlock():
    return await query('walletpassphrase', [g.grc_pass, 999999999, False])
