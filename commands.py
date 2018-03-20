from user import usr
import grcconf as g
import emotes as e
import wallet as w

def dump_cfg():
    block_height = w.query('getblockcount', [])
    block_hash = w.query('getblockhash', [block_height])
    if block_height < 5 or not isinstance(block_hash, str): # 5 is largest error return value
        return '{}Could not access the Gridcoin client.'.format(e.ERROR)

    return '''{}Bot is up. Configuration:```
Withdraw fee: {}
Required confirmations per withdrawl: {}
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
    if amount == None:
        return '{}Amount provided is invalid.'.format(e.ERROR)
    if amount <= 0:
        return '{}Amount provided is invalid.'.format(e.ERROR)
    if amount-g.tx_fee <= 0:
        return '{}Invalid amount, withdrawl an amount higher than the fee. (Fee: `{} GRC`)'.format(e.ERROR, g.tx_fee)
    if userobj.balance < amount:
        return '{}Insufficient funds to withdraw. You have {} GRC'.format(e.ERROR, userobj.balance)
    return userobj.withdraw(amount, addr)
