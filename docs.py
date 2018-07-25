import grcconf as g
import emotes as e
import discord

hlp = '''```
Type %help [topic] for more detailed information about the following:
- new
- balance
- withdraw
- donate
- rdonate
- give
- rain
- faucet
- qr
- faq
- block
- status
- time
- rules
- terms
- info
```'''

new = '''```
Create an new account: %new
    An account is required to use the bot. (No personal details required)
```'''

bal = '''```
Balance: %bal, %balance
    Checks your current balance and shows your deposit address.
    To get a clipboard friendly address, use %addr.
    Deposits should arrive within 5 minutes of a transaction taking place.
    If the bot is offline, you are still safe to make deposits.
```'''

wdr = '''```
Withdraw your funds: %wdr, %withdraw, %send
    Format: %wdr [address to send to] [amount-GRC]

    Takes your GRC out of the bot's wallet.
    Fee for withdraw is {} GRC and is automatically deducted.
    If you wish to transfer to another user, use %give instead.
```'''.format(g.tx_fee)

donate = '''```
Donate to someone: %donate
    Format: %donate [selection no.] [amount-GRC]

    A list of possible donation addresses to encourage generosity.
    Choose a number from the list of selections and then the amount to donate.
```'''

rdonate = '''```
Donate to a random contributor: %rdonate
    Format: %rdonate [amount-GRC]

    Same as %donate but a random person on the bot's donation list is chosen for you.
```'''

give = '''```
Give funds to another user: %give %tip
    Format: %give [discord mention of user] [amount-GRC]

    Give some GRC to another person within the server. (no fees apply)
    Requires the mentioned user to also have an account with the bot through %new.
```'''

rain = '''```
Rain on active users: %rain
    Typing %rain on its own will display the current rain balance and threshold.
    Once the balance of the rainbot exceeds the threshold, it will rain on all online users.

    To contribute GRC to the rain pool, type: %rain [amount-GRC]
```'''

faucet = '''```
Get some free GRC: %faucet %get
    Type this command to get some free Gridcoins.
    Amounts are random and you can only request once per {} hours.
    To help fund the faucet, you can type `%fgive [amount-GRC]`.
```'''.format(g.FCT_REQ_LIM)

qr = '''```
Generate a QR code: %qr
    Format: %qr [optional data]

    Generates a qr code. If no data is given, it will send a QR code of your
    wallet address. Any data given must contain no spaces.
```'''

faq = '''```
Read answers to frequently asked questions: %faq
    Format: %faq [selection no.]

    All answers are formulated by Delta, Foxifi and LavRadis, and checked by
    community members and developers.
```'''

block = '''```
Explore blocks on the Gridcoin chain: %block
    Format: %block [height]

    Fetches information about a particular block on the Gridcoin blockchain.
```'''

status = '''```
Bot and network status: %status
```'''

time = '''```
Shows what functionality is available given recent activity: %time
    Specifically shows faucet, withdrawal and donation availability.
    Requested by LavRadis.
```'''

rules_help = '''```
Rules about using the bot and what may result in a ban: %rules
```'''

terms_help = '''```
Terms and conditions for making an account with the bot: %terms
```'''

info_help = '''```
Info about author and this bot: %info
```'''

info = discord.Embed(title='This bot is the original work of Delta and various contributors.', colour=discord.Colour.purple(),
description='''
The source code for the bot can be found [here](https://github.com/delta1512/GRC-Wallet-Bot).

If there are any problems, glitches or crashes, please notify me or the contributors below as soon as possible. Any queries can be sent to `boincosdelta@gmail.com`.

Notable mentions:
- [Jorkermc](https://github.com/jorkermc)
- Foxifi
- [LavRadis](https://steemit.com/@lavradis)
''')

help_dict = {
    'default'   :   hlp,
    'new'       :   new,
    'balance'   :   bal,
    'withdraw'  :   wdr,
    'donate'    :   donate,
    'rdonate'   :   rdonate,
    'give'      :   give,
    'rain'      :   rain,
    'faucet'    :   faucet,
    'qr'        :   qr,
    'faq'       :   faq,
    'block'     :   block,
    'status'    :   status,
    'time'      :   time,
    'rules'     :   rules_help,
    'terms'     :   terms_help,
    'info'      :   info_help
}

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
