from random import uniform
import discord

from extras import do_announce, dm_user
import queries as q
import grcconf as g
import emotes as e
import docs


class Rainbot:
    thresh = 0
    balance = 0
    lock = False


    def __init__(self):
        self.get_next_thresh()


    async def do_rain(self, client):
        if self.lock:
            return
        else:
            self.lock = True
        ulist_dict, enables_data = await q.get_addr_uid_dict(dm_enables=True)
        ulist = [ulist_dict[addr] for addr in ulist_dict]
        online_ids = set()
        online_members = set()
        remainder = uniform(0.001, 0.01)
        rain_amt = round(self.balance - remainder, 8)

        for member in client.get_all_members():
            if member.status == discord.Status.online and str(member.id) in ulist:
                online_ids.add(str(member.id))
                online_members.add(member)
        num_rain = len(online_ids)

        final_rains = {}
        for val in self.get_rain_vals(num_rain, self.balance-remainder):
            final_rains[online_ids.pop()] = val
        final_rains['RAIN'] = -rain_amt
        await q.apply_balance_changes(final_rains)

        for member in online_members:
            if enables_data[str(member.id)]:
                await dm_user(member, docs.dm_rain_msg)
        await do_announce(f'Rainbot has rained `{rain_amt} GRC` on {num_rain} users!', docs.rain_title, client)

        self.get_next_thresh()
        self.lock = False


    async def get_balance(self):
        self.balance = (await q.get_bal('RAIN'))[0]
        return self.balance


    def get_next_thresh(self):
        self.thresh = round(uniform(g.MIN_RAIN, g.MAX_RAIN), 8)


    async def can_rain(self):
        return await self.get_balance() > self.thresh and not self.lock


    async def status(self):
        return docs.rain_msg.format(round(await self.get_balance(), 8), round(self.thresh, 8), (await q.get_bal('RAIN'))[1])


    async def contribute(self, amount, user_obj):
        result = await user_obj.send_internal_tx(await q.get_user('RAIN'), amount, True)
        if result.startswith(e.GOOD):
            result += docs.rain_thankyou.format(round(await self.get_balance(), 3))
        return result


    def get_rain_vals(self, n, amount):
        rand_set = [uniform(0.1, 0.25) for i in range(n)]
        set_sum = sum(rand_set)
        return list(map(lambda x: (x/set_sum)*amount, rand_set))
