from math import ceil, isfinite
import random as r
import time
import io

import qrcode

import queries as q
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
Price (USD): ${}

Faucet funds: {} GRC```'''.format(e.ONLINE, g.tx_fee, g.MIN_TX, g.tx_timeout,
g.FCT_REQ_LIM, len(await q.get_addr_uid_dict()), block_height, block_hash,
round(await price_fetcher.price(), 4), (await q.get_bal('FAUCET'))[0])


async def donate(user_obj, selection, amount):
    selection -= 1
    if 0 <= selection < len(g.donation_accts):
        acct_dict = g.donation_accts[selection]
        selection_name = list(acct_dict.keys())[0]
        addr = acct_dict[selection_name]
        result = await user_obj.withdraw(amount, addr, g.net_fee, True)
        if result.startswith(e.GOOD):
            return result + docs.donation_recipient.format(selection_name)
        return result
    return docs.invalid_selection


async def rdonate(user_obj, amount):
    return await donate(user_obj, r.randint(1, len(g.donation_accts)), amount)


def index_displayer(header, index):
    acc = ''
    for count, acct in enumerate(index):
        name = list(acct.keys())[0]
        acc += '\n{}. {}'.format(str(count+1), name)
    return '{}```{}```'.format(header, acc[1:])


async def faucet(uid):
    ctime = round(time.time())
    amount = round(r.uniform(g.FCT_MIN, g.FCT_MAX), 8)
    user_obj, exit_code = await q.faucet_operations(uid, amount, ctime)
    if exit_code == 1:
        return '{}Request too recent. Faucet timeout is {} hours. Try again in: {}'.format(e.CANNOT, g.FCT_REQ_LIM,
        time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_fct()-ctime))))
    if exit_code == 2:
        return '{}Unfortunately the faucet balance is too low. Try again soon.'.format(e.DOWN)
    return docs.claim.format(e.GOOD, amount) + ' Your new balance is `{} GRC`'.format(round(user_obj.balance, 8))


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
    return docs.invalid_selection


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


#ban [user] [chan]
#unban [user]
async def blist_iface(args, blist_obj):
    if args[0] == 'ban':
        if len(args) == 3:
            await blist_obj.new_blist(args[1], True if args[2] == 'priv' else False)
            return e.GOOD[:-3]
        return '{}Invalid args'.format(e.ERROR)
    elif args[0] == 'unban':
        if len(args) == 2:
            await blist_obj.remove_blist(args[1])
            return e.GOOD[:-3]
        return '{}Invalid args'.format(e.ERROR)
    else:
        return '{}Invalid command'.format(e.ERROR)


async def burn_coins(args):
    if (amt_filter(args[1]) is None):
        amt = 0
    else:
        amt = amt_filter(args[1])
    from_user = await q.get_user(args[0])
    if args[0] != g.owner_id and (not from_user is None):
        to_user = await q.get_user(g.owner_id)
        await from_user.send_internal_tx(to_user, amt)
    else:
        from_user.balance -= amt
        await q.save_user(from_user)
    return 'Burned `{} GRC` from `{}`'.format(amt, args[0])


def user_stats(user_obj, client, user_time):
    final = 'User ID: {}\n'.format(user_obj.usrID)
    user = None
    for member in client.get_all_members():
        if str(member.id) == user_obj.usrID:
            user = member
            crtime = round(user_time(member.created_at))
            break
    if user is None:
        return '```{}```'.format(final)
    final += user_obj.get_stats().replace('`', '') + '\n'
    final += 'Created at: {} {}\n'.format(crtime, time.strftime("(%m Months %d Days %H Hours %M Minutes ago)", time.gmtime(time.time()-crtime)))
    jtime = round(time.mktime(member.joined_at.timetuple()))
    final += 'Joined at: {} {}'.format(jtime, time.strftime("(%m Months %d Days %H Hours %M Minutes ago)", time.gmtime(time.time()-jtime)))
    return '```{}```'.format(final)


def check_times(user_obj):
    ctime = round(time.time())
    return '''
Faucet: {}
Withdrawals: {}
Donations: {}
'''.format(e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_fct()-ctime)))) if not user_obj.can_faucet() else e.GOOD[:-3],
            e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_net_tx()-ctime)))) if not user_obj.can_net_tx() else e.GOOD[:-3],
            e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_net_tx()-ctime)))) if not user_obj.can_net_tx() else e.GOOD[:-3])
