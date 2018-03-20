from random import uniform
from time import time
from user import usr
import grcconf as g
import emotes as e
import wallet as w

def amt_filter(inp, userobj):
    if inp == 'all':
        return round(userobj.balance, 8)
    try:
        inp = float(inp)
        if (inp < 0) or (inp <= g.MIN_TX) or (inp == float('inf')):
            return None
        else:
            return round(inp, 8)
    except:
        return None

def dump_cfg():
    block_height = w.query('getblockcount', [])
    block_hash = w.query('getblockhash', [block_height])
    if block_height < 5 or not isinstance(block_hash, str): # 5 is largest error return value
        return '{}Could not access the Gridcoin client.'.format(e.ERROR)

    return '''{}Bot is up. Configuration:```
Withdraw fee: {}
Required confirmations per withdraw: {}
Block height: {}
Latest hash: {}```'''.format(e.ONLINE, g.tx_fee, g.tx_timeout, block_height, block_hash)

def new_user(uid):
    try:
        userobj = usr(uid)
        return 0, '{}User account created successfully. Your address is `{}`'.format(e.GOOD, userobj.address), userobj
    except:
        return 1, '{}Error: Something went wrong when attempting to make your user account.'.format(e.ERROR), None

def fetch_balance(userobj):
    return '''{}Your balance for: `{}`
```Wallet: {} GRC```'''.format(e.BAL, userobj.address, round(userobj.balance, 8))

def donate(selection, amount, userobj):
    try:
        selection = int(selection)-1
    except:
        return '{}Invalid selection.'.format(e.ERROR)
    if amount == None:
        return '{}Amount provided is invalid.'.format(e.ERROR)
    if userobj.balance < amount:
        return '{}Insufficient funds to donate. You have `{} GRC`'.format(e.ERROR, round(userobj.balance, 8))
    if 0 <= selection < len(g.donation_accts):
        acct_dict = g.donation_accts[selection]
        address = acct_dict[list(acct_dict.keys())[0]]
        return userobj.donate(address, amount)
    else:
        return '{}Invalid selection.'.format(e.ERROR)

def fetch_donation_addrs():
    big_string = '{}Be generous! Below are possible donation options.```{}```\nTo donate, type `%donate [selection no.] [amount-GRC]`'
    acc = ''
    for count, acct in enumerate(g.donation_accts):
        name = list(acct.keys())[0]
        acc += '\n{}. {}\t\t{}'.format(str(count+1), name, acct[name])
    return big_string.format(e.GIVE, acc[1:])

def withdraw(amount, addr, userobj):
    if amount is None or amount <= 0:
        return '{}Amount provided is invalid.'.format(e.ERROR)
    if amount-g.tx_fee <= 0:
        return '{}Invalid amount, withdrawl an amount higher than the fee. (Fee: `{} GRC`)'.format(e.ERROR, g.tx_fee)
    if userobj.balance < amount:
        return '{}Insufficient funds to withdraw. You have `{} GRC`'.format(e.ERROR, round(userobj.balance, 8))
    return userobj.withdraw(amount, addr)

def give(amount, current_usrobj, rec_usrobj):
    amount = amt_filter(amount, current_usrobj)
    if amount != None:
        if amount <= current_usrobj.balance:
            current_usrobj.balance -= amount
            rec_usrobj.balance += amount
            return '{}In-server transaction of `{} GRC` successful.'.format(e.GOOD, round(amount, 8))
        else:
            return '{}Insufficient funds to give. You have `{} GRC`'.format(e.ERROR, round(current_usrobj.balance, 8))
    else:
        return '{}Amount provided was not a number.'.format(e.ERROR)

def faucet(faucet_usr, current_usr):
    if faucet_usr.balance == 0:
        return '{}Unfortunately the faucet is out of GRC. Try again soon.'.format(e.DOWN)
    elif round(time()) < current_usr.last_active+3600*g.FCT_REQ_LIM:
        return '{}Request too recent. Faucet timeout is {} hours.'.format(e.CANNOT, g.FCT_REQ_LIM)
    else:
        current_usr.last_active = round(time())
        return give(round(uniform(g.FCT_MIN, min(g.FCT_MAX, faucet_usr.balance)), 8), faucet_usr, current_usr)
