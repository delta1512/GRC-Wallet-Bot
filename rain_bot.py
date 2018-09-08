from random import uniform
import discord

from extras import do_announce, dm_user
import queries as q
import grcconf as g
import emotes as e
import docs

class Rainbot:
    RBOT = None
    thresh = 0


    def __init__(self, rainuser):
        if rainuser is None:
            raise TypeError
        self.RBOT = rainuser
        self.get_next_thresh()


    async def do_rain(self, client):
        ulist_dict = await q.get_addr_uid_dict()
        ulist = [ulist_dict[addr] for addr in ulist_dict]
        online_ids = set()
        online_members = set()
        remainder = uniform(0.001, 0.01)
        rain_amt = round(self.RBOT.balance - remainder, 8)

        for member in client.get_all_members():
            if member.status == discord.Status.online and str(member.id) in ulist:
                online_ids.add(str(member.id))
                online_members.add(member)
        num_rain = len(online_ids)

        final_rains = {}
        for val in self.get_rain_vals(num_rain, self.RBOT.balance-remainder):
            final_rains[online_ids.pop()] = val
        await q.apply_balance_changes(final_rains)
        self.RBOT.balance -= rain_amt
        await q.save_user(self.RBOT)

        for member in online_members:
            await dm_user(member, docs.dm_rain_msg)
        await do_announce('Rainbot has rained `{} GRC` on {} users!'.format(rain_amt, num_rain), docs.rain_title, client)

        self.get_next_thresh()


    def get_next_thresh(self):
        self.thresh = round(uniform(g.MIN_RAIN, g.MAX_RAIN), 8)


    def can_rain(self):
        return self.RBOT.balance > self.thresh


    def status(self):
        return docs.rain_msg.format(round(self.RBOT.balance, 8), round(self.thresh, 8), self.RBOT.address)


    async def contribute(self, amount, user_obj):
        result = await user_obj.send_internal_tx(self.RBOT, amount, True)
        if result.startswith(e.GOOD):
            result += docs.rain_thankyou.format(round(self.RBOT.balance, 3))
        return result


    def get_rain_vals(self, n, amount):
        rand_set = [uniform(0.1, 0.25) for i in range(n)]
        set_sum = sum(rand_set)
        return list(map(lambda x: (x/set_sum)*amount, rand_set))
