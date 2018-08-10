from random import uniform
import discord

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
        ulist = await q.get_addr_uid_dict()
        online = set()
        remainder = uniform(0.001, 0.01)
        rain_amt = round(self.RBOT.balance - remainder, 8)

        for member in client.get_all_members():
            if member.status == discord.Status.online and member.id in ulist:
                online.add(member.id)
        num_rain = len(online)

        final_rains = {}
        for val in self.get_rain_vals(num_rain, self.RBOT.balance-remainder):
            final_rains[online.pop()] = val
        await q.apply_balance_changes(final_rains)
        self.RBOT.balance -= rain_amt
        await q.save_user(self.RBOT)

        big_string = '{}Rained `{} GRC`\n'.format(e.RAIN, rain_amt)
        for user in final_rains:
            big_string += '<@{}>\n'.format(user)
        if len(big_string) >= 2000:
            big_string = '{}Rainbot has rained `{} GRC` on {} users. See if you are lucky!'.format(e.RAIN, rain_amt, num_rain)
        await client.send_message(client.get_channel(g.RAIN_CHAN), big_string)
        self.get_next_thresh()


    def get_next_thresh(self):
        self.thresh = round(uniform(g.MIN_RAIN, g.MAX_RAIN), 8)


    def check_rain(self):
        return self.RBOT.balance > self.thresh


    def status(self):
        return docs.rain_msg.format(round(self.RBOT.balance, 8), round(self.thresh, 8), self.RBOT.address)


    def contribute(amount, user_obj):
        return user_obj.send_internal_tx(self.RBOT, amount, True) + docs.rain_thanks.format(round(self.RBOT.balance, 3))


    def get_rain_vals(self, n, amount):
        rand_set = [uniform(0.1, 0.8) for i in range(n)]
        set_sum = sum(rand_set)
        return list(map(lambda x: (x/set_sum)*amount, rand_set))
