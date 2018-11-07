from time import time
import async_timeout
import logging
import aiohttp
import asyncio
import json

class price_bot:
    last_updated = 0
    last_price = 0
    timeout_sec = 380
    price_url = 'https://api.coingecko.com/api/v3/coins/gridcoin-research'

    async def price(self):
        if round(time()) > self.last_updated+self.timeout_sec:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.price_url) as response:
                        self.last_price = json.loads(await response.text())['market_data']['current_price']['usd']
            except Exception as E:
                logging.warning('[WARN] Error when trying to fetch USD price: %s', E)
            self.last_updated = round(time())
        return self.last_price

    async def conv(self, amt):
        return '{:.2f}'.format(amt*(await self.price()))
