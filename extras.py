from math import ceil, isfinite
import random as r
import time
import io

import qrcode

import grcconf as g
import emotes as e
import wallet as w
import help_docs
import docs
import FAQ


def amt_filter(inp):
    try:
        inp = float(inp)
        if (inp < 0) or (inp <= g.MIN_TX) or not isfinite(inp):
            return None
        else:
            return round(inp, 8)
    except:
        return None


async def dump_cfg(price_fetcher):
    block_height = await w.query('getblockcount', [])
    block_hash = await w.query('getblockhash', [block_height])
    if block_height < 5 or not isinstance(block_hash, str): # 5 is largest error return value
        return '{}Could not access the Gridcoin client.'.format(e.ERROR)

    return '''{}Bot is up. Configuration:```
Withdraw fee: {} GRC
Min. transfer limit: {} GRC
Required confirmations per withdraw: {}
Faucet timeout: {} Hours
Users: {}
Block height: {}
Latest hash: {}
Price (USD): ${}```'''.format(e.ONLINE, g.tx_fee, g.MIN_TX, g.tx_timeout,
                            g.FCT_REQ_LIM, len(await q.get_addr_uid_dict()), block_height, block_hash,
                            round(await price_fetcher.price(), 4))


async def donate(selection, amount, userobj):
    amount = amt_filter(amount, userobj)
    try:
        selection = int(selection)-1
    except ValueError:
        return '{}Invalid selection.'.format(e.ERROR)
    if amount is None:
        return '{}Amount provided is invalid.'.format(e.ERROR)
    if round(userobj.balance, 8) < amount:
        return '{}Insufficient funds to donate. You have `{} GRC`'.format(e.ERROR, round(userobj.balance, 2))
    if 0 <= selection < len(g.donation_accts):
        acct_dict = g.donation_accts[selection]
        address = acct_dict[list(acct_dict.keys())[0]]
        return await userobj.donate(address, amount)
    return '{}Invalid selection.'.format(e.ERROR)


async def rdonate(amount, userobj):
    selection = r.randint(1, len(g.donation_accts))
    reply = await donate(selection, amount, userobj)
    if reply.startswith(e.GOOD):
        acct_dict = g.donation_accts[selection-1]
        return reply + '\n\nYou donated to: {}'.format(list(acct_dict.keys())[0])
    return reply


def index_displayer(header, index):
    acc = ''
    for count, acct in enumerate(index):
        name = list(acct.keys())[0]
        acc += '\n{}. {}'.format(str(count+1), name)
    return '{}```{}```'.format(header, acc[1:])


def faucet(faucet_usr, current_usr):
    nxtfct = current_usr.last_faucet+3600*g.FCT_REQ_LIM
    ctime = round(time.time())
    if faucet_usr.balance <= g.FCT_MAX:
        return '{}Unfortunately the faucet balance is too low. Try again soon.'.format(e.DOWN)
    elif ctime < nxtfct:
        return '{}Request too recent. Faucet timeout is {} hours. Try again in: {}'.format(e.CANNOT, g.FCT_REQ_LIM,
                time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(nxtfct-ctime))))
    current_usr.last_faucet = ctime
    return give(round(r.uniform(g.FCT_MIN, g.FCT_MAX), 8), faucet_usr, current_usr) + ' Your new balance is `{} GRC`'.format(round(current_usr.balance, 8))


def get_qr(string):
    qr = qrcode.QRCode(
         version=1,
         error_correction=qrcode.constants.ERROR_CORRECT_L,
         box_size=10,
         border=2)
    qr.add_data(string)
    qr.make(fit=True)
    savedir = io.BytesIO()
    img = qr.make_image(fill_color='#5c00b3', back_color='white')
    img.save(savedir, format="PNG")
    savedir.seek(0)
    return savedir


def help_interface(query):
    try:
        return help_docs.help_dict[query]
    except KeyError:
        return help_docs.help_main()


def faq(query):
    if 0 <= query < len(FAQ.index):
        article = FAQ.index[query]
        return article[list(article.keys())[0]]
    return '{}Invalid selection.'.format(e.ERROR)


async def show_block(height):
    data = await w.get_block(height)
    if data is None:
        return '{}Could not fetch block data.'.format(e.ERROR)
    acc = ''
    for key in data:
        acc += key + str(data[key]) + '\n'
    return '```{}```'.format(acc)


def moon():
    clock = ':clock{}:'.format(r.randint(1, 12))
    day = '{}{}'.format(r.choice(e.NUMS[:3]), r.choice(e.NUMS))
    month0 = r.choice(e.NUMS[:2])
    month1 = r.choice(e.NUMS[:3]) if e.NUMS.index(month0) == 1 else r.choice(e.NUMS)
    month = month0 + month1
    year = ':two::zero:{}{}'.format(r.choice(e.NUMS[2:]), r.choice(e.NUMS))
    return '{}So when will we moon? Exactly on this date {} {}  {} / {} / {}'.format(
            e.CHART_UP, clock, e.ARR_RIGHT, day, month, year)


#check [usr] [chan]
#ban [user] [chan]
#unban [user]
def blist_iface(args, blist_obj):
    if args[0] == 'check':
        if len(args) == 3:
            return str(blist_obj.is_banned(args[1], True if args[2] == 'priv' else False))
        return '{}Invalid args'.format(e.ERROR)
    elif args[0] == 'ban':
        if len(args) == 3:
            blist_obj.new_blist(args[1], True if args[2] == 'priv' else False)
            return e.GOOD[:-3]
        return '{}Invalid args'.format(e.ERROR)
    elif args[0] == 'unban':
        if len(args) == 2:
            blist_obj.remove_blist(args[1])
            return e.GOOD[:-3]
        return '{}Invalid args'.format(e.ERROR)
    else:
        return '{}Invalid command'.format(e.ERROR)


def burn_coins(args, udb):
    if len(args) > 1:
        amt = 0 if (amt_filter(args[1], None) == None) else amt_filter(args[1], None)
        udb[args[0]].balance -= amt
        if args[0] != g.owner_id:
            udb[g.owner_id].balance += amt
        return 'Burned `{} GRC` from `{}`'.format(amt, args[0])


def user_stats(uid, userobj, crtime_f, client):
    final = 'User ID: {}\n'.format(uid)
    user = None
    members = client.get_all_members() if g.main_server == '' else [server.members for server in client.servers if server.id == g.main_server][0]
    for member in members:
        if member.id == uid:
            user = member
            crtime = round(crtime_f(member.created_at))
            break
    if user is None:
        return '```{}```'.format(final)
    if not userobj is None:
        final += '''Address: {}
Balance: {}
Last TX time: {}
Last TXID: {}
'''.format(userobj.address, userobj.balance, userobj.active_tx[1], userobj.active_tx[2])
    final += 'Created at: {} {}\n'.format(crtime, time.strftime("(%m Months %d Days %H Hours %M Minutes ago)", time.gmtime(time.time()-crtime)))
    jtime = round(time.mktime(member.joined_at.timetuple()))
    final += 'Joined at: {} {}'.format(jtime, time.strftime("(%m Months %d Days %H Hours %M Minutes ago)", time.gmtime(time.time()-jtime)))
    return '```{}```'.format(final)


def check_times(userobj):
    ctime = time.time()
    return '''
Faucet: {}
Withdrawals: {}
Donations: {}
'''.format(e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(userobj.next_fct()-ctime)))) if not userobj.can_faucet() else e.GOOD[:-3],
            e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(userobj.next_wdr()-ctime)))) if not userobj.can_withdraw() else e.GOOD[:-3],
            e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(userobj.next_dnt()-ctime)))) if not userobj.can_donate() else e.GOOD[:-3])
