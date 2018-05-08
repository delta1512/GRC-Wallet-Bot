from random import uniform
import discord

from commands import give
import grcconf as g
import emotes as e
import docs

class rainbot:
    RBOT = None
    thresh = 0

    def __init__(self, rainuser):
        self.RBOT = rainuser
        self.get_next_thresh()

    async def do_rain(self, UDB, client):
        ulist = [uid for uid in UDB]
        online = []
        bias = uniform(0.001, 0.01)
        rain_amt = round(self.RBOT.balance - bias, 8)
        for member in client.get_all_members():
            if member.status == discord.Status.online and member.id in ulist:
                online.append(member.id)
        for i, val in enumerate(self.get_rain_vals(len(online), bias)):
            give(val, self.RBOT, UDB[online[i]])
        big_string = '{}Rained `{} GRC`\n'.format(e.RAIN, rain_amt)
        for user in online:
            big_string += '<@{}>\n'.format(user)
        if len(big_string) >= 2000:
            big_string = '{}Rainbot has rained `{} GRC` on {} users. See if you are lucky!'.format(e.RAIN, rain_amt, len(online))
        await client.send_message(client.get_channel(g.RAIN_CHAN), big_string)
        self.get_next_thresh()

    def get_next_thresh(self):
        self.thresh = round(uniform(10, g.MAX_RAIN), 8)

    def check_rain(self):
        return self.RBOT.balance > self.thresh

    def process_message(self, args, user):
        if len(args) == 0:
            return docs.rain_msg.format(round(self.RBOT.balance, 8),
                                        round(self.thresh, 8),
                                        self.RBOT.address)
        if 0 < len(args) < 2:
            return give(args[0], user, self.RBOT,
                        add_success_msg='\n\nThank you for raining on the users!', donation=True)
        return '{}Too many arguments provided'.format(e.CANNOT)

    def get_rain_vals(self, n, bias):
        rand_set = [uniform(0.1, 0.8) for i in range(n)]
        set_sum = sum(rand_set)
        return list(map(lambda x: (x/set_sum)*self.RBOT.balance-bias, rand_set))
