from time import time
import logging

import grcconf as g
import emotes as e
import wallet as w
import queries as q
import docs

class User:
    def __init__(self, uid, **k):
        self.usrID = uid
        self.balance = k.get('balance', 0.0)
        self.active_tx = k.get('lastTX', [None, 0, None]) # [amount, timestamp, txid]
        self.donations = k.get('donations', 0.0)
        self.last_faucet = k.get('last_faucet', 0)
        self.address = k.get('address', None)


    async def withdraw(self, amount, addr, fee, donation=False):
        validation_result = self.can_transact(amount, fee, True)
        if isinstance(validation_result, bool):
            txid = await w.tx(addr, amount-fee)
            if isinstance(txid, str):
                tx_time = round(time())
                self.active_tx = [amount, tx_time, txid.replace('\n', '')]
                self.balance -= amount
                if donation:
                    self.donations += amount - fee
                await q.save_user(self)
                if fee == g.tx_fee:
                    await q.add_to_fee_pool(fee)
                logging.info('Transaction successfully made with txid: %s', txid)
                return docs.net_tx_success.format(e.GOOD, round(amount, 8), fee, txid, '\n\nYour new balance is {} GRC.'.format(round(abs(self.balance), 2)))
            logging.error('Failed transaction. Addr: %s, Amt: %s, exit_code: %s', addr, amount, txid)
            return docs.tx_error
        return validation_result


    async def send_internal_tx(self, other_user, amount, donation=False):
        validation_result = self.can_transact(amount, 0)
        if isinstance(validation_result, bool):
            self.balance -= amount
            other_user.balance += amount
            if donation:
                self.donations += amount
            await q.save_user([self, other_user])
            return docs.internal_tx_success.format(e.GOOD, amount)
        return validation_result


    def get_stats(self):
        return docs.user_data_template.format(self.address, self.balance,
                    self.donations, self.last_faucet, self.active_tx[1],
                    self.active_tx[2], self.active_tx[0])


    def next_net_tx(self):
        return self.active_tx[1]+1.5*g.BLK_TIME*g.tx_timeout


    def next_fct(self):
        return self.last_faucet+3600*g.FCT_REQ_LIM


    def can_net_tx(self):
        return time() > self.next_net_tx()


    def can_faucet(self):
        return time() > self.next_fct()


    def can_transact(self, amount, fee, net_tx=False):
        if net_tx:
            if not self.can_net_tx(): return docs.wait_confirm;
        if amount is None: return docs.invalid_val;
        if amount > round(self.balance, 8): return docs.insufficient_funds;
        if fee != 0 and amount <= (fee + g.MIN_TX): return docs.more_than_fee_and_min;
        return True # If values passed all checks
