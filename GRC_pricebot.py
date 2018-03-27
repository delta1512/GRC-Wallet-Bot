from urllib.request import urlopen
from time import time
import json

class price_bot:
    last_updated = 0
    last_price = 0
    timeout_sec = 380
    price_url = 'https://api.coinmarketcap.com/v1/ticker/gridcoin/'

    def price(self):
        if round(time()) > self.last_updated+self.timeout_sec:
            try:
                self.last_price = float(json.loads(urlopen(self.price_url).read().decode())[0]['price_usd'])
            except Exception as E:
                print('[WARN] Error when trying to fetch USD price: ', E)
            self.last_updated = round(time())
        return self.last_price

    def conv(self, amt):
        return round(amt*self.price(), 2)
