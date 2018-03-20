import grcconf as g
import requests
import json

'''
1 - protocol/client error
2 - invalid args
3 - net exception
4 - invalid type
'''

def query(cmd, params):
    if not all([isinstance(cmd, str), isinstance(params, list)]):
        print('[WARN] Invalid data sent to wallet query')
        return 2
    command = json.dumps({'method' : cmd, 'params' : params})
    try:
        response = json.loads(requests.request("POST", g.rpc_url, data=command, headers={'content-type': "application/json", 'cache-control': "no-cache"}, auth=(g.rpc_usr, g.rpc_pass)).text)
    except Exception as E:
        print('[WARN] Exception triggered in communication with GRC client\n', E)
        return 3
    if response['error'] != None:
        return 1
    else:
        return response['result']

def tx(addr, amount):
    try:
        amount = float(amount)
    except:
        return 4
    if isinstance(addr, str) and len(addr) > 1:
        return query('sendtoaddress', [addr, float(amount)])
    else:
        return 4
