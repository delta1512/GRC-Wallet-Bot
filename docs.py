import grcconf as g
import emotes as e

hlp = '''```
- new
- balance
- withdraw
- donate
- give
- faucet
- status
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

give = '''```
Give funds to another user: %give
    Format: %give [discord mention of user] [amount-GRC]

    Give some GRC to another person within the server. (no fees apply)
    Requires the mentioned user to also have an account with the bot through %new.
```'''

faucet = '''```
Get some free GRC: %faucet
    Type this command to get some free Gridcoins.
    Amounts are random and you can only request once per {} hours.
    To help fund the faucet, you can type `%fgive [amount-GRC]`.
```'''.format(g.FCT_REQ_LIM)

status = '''```
Bot and network status: %status
```'''

info_help = '''```
Info about author and this bot: %info
```'''

info = '''
**This bot is the original work of Delta and various contributors.**

The source code for the bot can be found here: https://github.com/delta1512/GRC-Wallet-Bot

Notable mentions:
- Jorkermc https://github.com/jorkermc
- Foxifi
'''

help_dict = {
    'default'   :   hlp,
    'new'       :   new,
    'balance'   :   bal,
    'withdraw'  :   wdr,
    'donate'    :   donate,
    'give'      :   give,
    'faucet'    :   faucet,
    'status'    :   status,
    'info'      :   info_help
}

faucetmsg = '''
The faucet currently contains `{} GRC` and has a timeout of {} hours.

Donate GRC to this address `{}`
or type `%fgive [amount-GRC]` to help refill the faucet
'''

server_lock_msg = '{} This server is currently not taking commands. The bot is under maintenance.'.format(e.SETTING)

PM_msg = '{} The bot does not take commands through private messages.'.format(e.CANNOT)
