import grcconf as g
import emotes as e
import discord

### GENERAL MESSAGES
welcome = '{}Welcome to the GRC Wallet Bot! Type `%help` for more commands and be sure to read the `%terms` and `%rules`'.format(e.CELEBRATE)

faucet_msg = '''The faucet currently contains `{} GRC`.

Donate GRC to this address: `{}` or use `%fgive` to refill the faucet.'''

rain_msg = '''The rainbot currently contains `{} GRC` and will rain at `{} GRC`.

Donate GRC to this address `{}`
or type `%rain [amount-GRC]` to build up rain.'''

user_data_template = '''```
Address: {}
Balance: {}
Donated: {}

Last faucet request (unix): {}
Last transaction (unix): {}
Last TXID out: {}
Last transaction amount: {}```'''

balance_template = '''{}Your balance for: `{}`
```{} GRC (${} USD)```'''

faucet_thankyou = '{}Thank you for donating to the faucet!'.format(e.HEART)

rain_thankyou = '\n\nThank you for raining on the users! The rain pot is now at `{} GRC`'

faq_msg = '{}The following are currently documented FAQ articles. To read, type `%faq [selection no.]` '.format(e.BOOK)

donation_recipient = '\nYou donated to {}!'

info = discord.Embed(title='This bot is the original work of Delta and various contributors.', colour=discord.Colour.orange(),
description='''
The source code for the bot can be found [here](https://github.com/delta1512/GRC-Wallet-Bot).

If there are any problems, glitches or crashes, please notify me or the contributors below as soon as possible. Any queries can be sent to `boincosdelta@gmail.com`.

Notable mentions:
- [Jorkermc](https://github.com/jorkermc)
- Nathanielcwm
- Foxifi
- [LavRadis](https://steemit.com/@lavradis)
''')

claim = '{}You claimed `{} GRC` from the faucet!'

server_invite = '{}Come join us over at the Gridcoin Discord! {} https://discord.me/gridcoin'.format(e.HEART, e.ARR_RIGHT)


### SUCCESS MESSAGES
new_user_success = '{}User account created successfully. Your address is `{}`'

net_tx_success = '{}Transaction of `{} GRC` (inc. {} GRC fee) was successful, ID: `{}`{}'

internal_tx_success = '{}In-server transaction of `{} GRC` was successful.'


### ERROR MESSAGES
new_user_fail = '{}Something went wrong when trying to make your account, please contact the owner.'.format(e.ERROR)

already_user = '{}Cannot create new account, you already have one.'.format(e.CANNOT)

fail_dm = '{}It appears the bot cannot PM you.'.format(e.INFO)

cannot_send_self = '{}You cannot send funds to yourself.'.format(e.ERROR)

rule_fail_send = fail_dm + '\nPlease enable direct messages via discord and type `%rules` and `%terms` or check the pinned messages.'.format(e.INFO)

wait_confirm = '{}Please wait for your previous transaction to be confirmed.'.format(e.CANNOT)

invalid_val = '{}The value provided was invalid.'.format(e.ERROR)

invalid_selection = '{}Invalid selection.'.format(e.ERROR)

insufficient_funds = '{}You have insufficient funds to make that transfer.'.format(e.ERROR)

more_than_fee_and_min = '{}You must provide an amount that is greater than the fee and minimum (`{} GRC`).'.format(e.ERROR, g.tx_fee + g.MIN_TX)

tx_error = '{}Error: A transaction could not be made.'.format(e.ERROR)

pm_restrict = '{}The bot cannot process this command through private messages.'.format(e.CANNOT)

too_new_msg = '{}Your account is too new to be using the bot, please ensure your account is at least {} days old.'.format(e.CANNOT, g.NEW_USR_TIME)


### RULES AND TERMS
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
