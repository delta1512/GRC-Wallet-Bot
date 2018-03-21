import aiohttp
import json
import requests

class Wallet:
    def __init__(self, auth, port, ip='127.0.0.1'):
        self.url = "http://{}:{}/".format(ip, port)
        self.auth = auth

    def _instruct_wallet(self, instruction, params):
        if not all([isinstance(instruction, str), isinstance(params, list)]):
            raise ValueError('invalid type')
        command = json.dumps({"method": instruction, "params": params})
        response = requests.request("POST", self.url, data=command, headers={'content-type': "application/json", 'cache-control': "no-cache"}, auth=self.auth)
        return json.loads(response.text)

    def create_address(self):
        return self._instruct_wallet('getnewaddress', [])

    def rename_address(self, address, name):
        return self._instruct_wallet('setaccount', [address, name])

    def send(self):
        raise NotImplementedError()

    def get_balance(self):
        raise NotImplementedError()

class AsyncWallet:
    def __init__(self, auth, port, ip='127.0.0.1'):
        self.url = "http://{}:{}/".format(ip, port)
        self.auth = auth

    async def _instruct_wallet(self, instruction, params):
        if not all([isinstance(instruction, str), isinstance(params, list)]):
            raise ValueError('invalid type')
        command = {"method": instruction, "params": params}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=command, headers={'content-type': "application/json", 'cache-control': "no-cache"}, auth=self.auth) as resp:
                return await resp.json()

    async def create_address(self):
        return await self._instruct_wallet('getnewaddress', [])

    async def rename_address(self, address, name):
        return await self._instruct_wallet('setaccount', [address, name])

    async def send(self):
        raise NotImplementedError()

    async def get_balance(self):
        raise NotImplementedError()
