from time import time
import logging

import grcconf as g
import emotes as e
import wallet as w

class usr:
    def __init__(self, uid, **k):
        self.usrID = uid
        self.balance = k.get('balance', 0.0)
        self.active_tx = k.get('lastTX', [None, 0, None]) # [amount, timestamp, txid]
        self.donations = k.get('donations', 0.0)
        self.last_faucet = k.get('last_faucet', 0)
        self.address = k.get('address', None)
        if self.address is None:
            raise ValueError('[ERROR] Null value passed to user instantiation')

    async def withdraw(self, amount, addr):
        if round(time()) > self.active_tx[1]+1.5*60*g.tx_timeout:
            txid = await w.tx(addr, amount-g.tx_fee)
            if isinstance(txid, str):
                with open(g.FEE_POOL, 'r') as fees:
                    owed = float(fees.read())
                with open(g.FEE_POOL, 'w') as fees:
                    fees.write(str(owed+g.tx_fee))
                self.active_tx = [amount, round(time()), txid.replace('\n', '')]
                self.balance -= amount
                logging.info('Transaction successfully made with txid: %s', txid)
                return '{}Transaction of `{} GRC` (inc. {} GRC fee) was successful, ID: `{}`{}'.format(e.GOOD, round(amount, 8), g.tx_fee, txid, '\n\nYour new balance is {} GRC.'.format(round(self.balance, 2)))
            logging.error('Failed transaction. Addr: %s, Amt: %s, exit_code: %s', addr, amount, txid)
            return '{}Error: The withdraw operation failed.'.format(e.ERROR)
        return '{}Please wait for your previous transaction to be confirmed.'.format(e.CANNOT)

    async def donate(self, addr, amount):
        if round(time()) > self.active_tx[1]+1.5*60:
            txid = await w.tx(addr, amount-0.0001)
            if isinstance(txid, str):
                self.active_tx = [amount, round(time()), txid.replace('\n', '')]
                self.donations += amount
                self.balance -= amount
                logging.info('Donation successfully made with txid: %s', txid)
                return '{}Donation of `{} GRC` was successful, ID: `{}`{}'.format(e.GOOD, round(amount, 8), txid, '\n\nThankyou for donating! Your new balance is {} GRC.'.format(round(self.balance, 2)))
            logging.error('Failed transaction. Addr: %s, Amt: %s, exit_code: %s', addr, amount, txid)
            return '{}Error: Transaction was unsuccessful.'.format(e.ERROR)
        return '{}Please wait for your previous transaction to be confirmed.'.format(e.CANNOT)
