import grcconf as g
import emotes as e

hlp = '''
```Commands:
    Create an new account: %new
        An account is required to use the bot. (No personal details required)

    Balance: %bal, %balance
        Checks your current balance and shows your deposit address.
        Deposits should arrive within 5 minutes of a transaction taking place.

    Withdraw: %wdr, %withdraw, %send
        Format: %wdr [address to send to] [amount-GRC]
        Takes your GRC out of the bot's wallet.
        Fee for withdraw is {} GRC and is automatically deducted.

    Donate: %donate
        Format: %donate [selection no.] [amount-GRC]
        A list of possible donation addresses.
        Choose a number from the list of selections and then the amount to donate.

    Give: %give
        Format: %give [discord mention of user] [amount-GRC]
        Give some GRC to another person within the server. (no fees apply)
        Requires the mentioned user to also have an account with the bot through %new.

    Bot and network status: %status

    Info about author and this bot: %info

Authors and Contributors:
    - Delta https://delta1512.github.io/BOINCOS/
    - Foxifi```'''.format(g.tx_fee)

info = '''
**This bot is the original work of Delta and various contributors.**

The source code for the bot can be found here: https://github.com/delta1512/GRC-Wallet-Bot

Notable mentions:
- Foxifi
- Jorkermc https://github.com/jorkermc
'''

faucetmsg = '''
The faucet currently contains `{} GRC` and has a timeout of {} hours.

Donate GRC to this address `{}`
or type `%fgive [amount-GRC]` to help refill the faucet
'''

server_lock_msg = '{} This server is currently not taking commands. The bot is under maintenance.'.format(e.SETTING)
