from time import time
import grcconf as g
import emotes as e
import wallet as w

class usr:
    def __init__(self, uid, **k):
        self.usrID = uid
        self.balance = k.get('balance', 0.0)
        self.active_tx = k.get('lastTX', [None, 0, None]) # [amount, timestamp, txid]
        self.donations = k.get('donations', 0.0)
        self.last_active = k.get('last_active', 0)
        addr = w.query('getnewaddress', [])
        if not isinstance(addr, str):
            raise Exception('Client down')
        self.address = k.get('address', addr)

    def withdraw(self, amount, addr):
        self.last_active = round(time())
        if round(time()) > self.active_tx[1]+1.5*60*g.tx_timeout:
            txid = w.tx(addr, amount-g.tx_fee)
            if isinstance(txid, str):
                with open(g.FEE_POOL, 'r') as fees:
                    owed = float(fees.read())
                with open(g.FEE_POOL, 'w') as fees:
                    fees.write(str(owed+g.tx_fee))
                self.active_tx = [amount, round(time()), txid]
                self.balance -= amount
                return '{}Transaction of `{} GRC` (inc. {} GRC fee) was successful, ID: `{}`'.format(e.GOOD, round(amount, 8), g.tx_fee, txid)
            else:
                return '{}Error: The withdraw operation failed. Try again soon.'.format(e.ERROR)
        else:
            return '{}Please wait for your previous transaction to be confirmed.'.format(e.CANNOT)

    def donate(self, addr, amount):
        self.last_active = round(time())
        if round(time()) > self.active_tx[1]+1.5*60:
            txid = w.tx(addr, amount-0.0001)
            if isinstance(txid, str):
                self.active_tx = [amount, round(time()), txid]
                self.donations += amount
                self.balance -= amount
                return '{}Donation of `{} GRC` was successful, ID: `{}`'.format(e.GOOD, round(amount, 8), txid)
            else:
                return '{}Error: Transaction was unsuccessful.'.format(e.ERROR)
        else:
            return '{}Please wait for your previous transaction to be confirmed.'.format(e.CANNOT)
