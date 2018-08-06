import grcconf as g
import emotes as e
import discord

welcome = '{}Welcome to the GRC Wallet Bot! Type `%help` for more commands and be sure to read the `%terms` and `%rules`'.format(e.CELEBRATE)

faucetmsg = '''
The faucet currently contains `{} GRC` and has a timeout of {} hours.

Donate GRC to this address `{}`
or type `%fgive [amount-GRC]` to help refill the faucet.
'''

rain_msg = '''
The rainbot currently contains `{} GRC` and will rain at `{} GRC`.

Donate GRC to this address `{}`
or type `%rain [amount-GRC]` to build up rain.
'''

rule_fail_send = '''{}It appears the bot cannot PM you.
Please enable direct messages via discord and type `%rules` and `%terms` or check the pinned messages.
'''.format(e.INFO)

rules = discord.Embed(title='GRC Wallet Bot Rules', colour=discord.Colour.purple(),
description='''
1. Do not spam the bot in any way.

2. Do not create duplicate or alternate accounts to maximise faucet or rain collections.

3. Do not mislead other users or attempt to steal the funds of other users through technical or social means.

4. Contact the owner of the bot immediately once a bug has been discovered.
''')

terms = discord.Embed(title='GRC Wallet Bot Terms and Conditions', colour=discord.Colour.purple(),
description='''
By holding an account with the bot (ie, after typing %new) you, the user, agree to the following terms of use:

i. You are fully liable for the movement of your funds. Any transaction that occurs to the wrong person or address is not the responsibility of the owner of the bot.

ii. You are fully liable for all funds stored in the bot. **If in the event your funds were lost due to failure, it is not the responsibility of the owner of the bot to reimburse you.**

iii. You agree to act fairly, considering other users, when using the bot and agree to not abuse the 'generous' functionality such as faucet and rain.

iv. You agree to maintain secrecy where possible in the event that you discover a bug with the bot until the owner is contacted and a resolution found.

v. If you fail to follow any rules outlined by the "rules" command, the owner has every right to take administrative action in banning or removing your account.

vi. If any of the above terms are violated, the owner has every right to take administrative action in banning or removing your account.

***

As the owner of the bot, I agree to the following:

i. To act fairly and in accordance with user opinions in a democratic manner.

ii. In the event of catastrophic failure, explore everything in my capability to recover or reimburse those who have lost their balance.

iii. To have sufficient reason in banning or removing a user account from the bot.
''')

PM_msg = '{}The bot cannot process this command through private messages.'.format(e.CANNOT)

new_usr_msg = '{}Your account is too new to be using the bot, please ensure your account is at least {} days old.'.format(e.CANNOT, g.NEW_USR_TIME)
