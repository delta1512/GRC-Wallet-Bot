from math import ceil, isfinite
import discord
import random as r
import time
import io
from datetime import timezone

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
        if (inp < 0) or (inp < g.MIN_TX) or not isfinite(inp):
            return None
        else:
            return round(inp, 8)
    except:
        return None


async def dump_cfg(price_fetcher):
    block_height = await w.query('getblockcount', [])
    block_hash = await w.query('getblockhash', [block_height])
    fct_info = await q.get_bal('FAUCET')
    rain_info = await q.get_bal('RAIN')
    if block_height < 5 or not isinstance(block_hash, str): # 5 is largest error return value
        return f'{e.ERROR}Could not access the Gridcoin client.'

    return f'''{e.ONLINE}Bot is up. Configuration:

```
Withdraw fee: {g.tx_fee} GRC
Min. transfer limit: {g.MIN_TX} GRC
Required confirmations per withdraw: {g.tx_timeout}
Faucet timeout: {g.FCT_REQ_LIM} Hours
Users: {len(await q.get_addr_uid_dict())}
Block height: {block_height}
Latest hash: {block_hash}
Price (USD): ${round(await price_fetcher.price(), 4)}

Faucet funds: {round(fct_info[0], 8)} GRC ({fct_info[1]})
Rain Funds: {round(rain_info[0], 8)} GRC ({rain_info[1]})```'''


async def donate(user_obj, selection, amount):
    selection -= 1
    donation_accts = await q.get_donors()
    if 0 <= selection < len(donation_accts):
        acct_dict = donation_accts[selection]
        selection_name = list(acct_dict.keys())[0]
        addr = acct_dict[selection_name]
        result = await user_obj.withdraw(amount, addr, g.net_fee, True)
        if result.startswith(e.GOOD):
            return result + docs.donation_recipient.format(selection_name)
        return result
    return docs.invalid_selection


async def rdonate(user_obj, amount):
    return await donate(user_obj, r.randint(1, len(await q.get_donors())), amount)


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
        return f'{e.DOWN}Unfortunately the faucet balance is too low. Try again soon.'
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
    query -= 1
    if 0 <= query < len(FAQ.index):
        article = FAQ.index[query]
        return article[list(article.keys())[0]]
    return docs.invalid_selection


async def show_block(height):
    data = await w.get_block(height)
    if data is None:
        return f'{e.ERROR}Could not fetch block data.'
    acc = ''
    for key in data:
        acc += key + str(data[key]) + '\n'
    return f'```{acc}```'


def moon():
    clock = ':clock{}:'.format(r.randint(1, 12))
    day = '{}{}'.format(r.choice(e.NUMS[:3]), r.choice(e.NUMS))
    month0 = r.choice(e.NUMS[:2])
    month1 = r.choice(e.NUMS[:3]) if e.NUMS.index(month0) == 1 else r.choice(e.NUMS)
    month = month0 + month1
    year = ':two::zero:{}{}'.format(r.choice(e.NUMS[2:]), r.choice(e.NUMS))
    return '{}So when will we moon? Exactly on this date {} {}  {} / {} / {}'.format(
            e.CHART_UP, clock, e.ARR_RIGHT, day, month, year)


async def do_announce(msg, title, client):
    announcement = discord.Embed(title=title, colour=discord.Colour.red(), description=msg)
    chans = await q.get_main_chans()
    for chanID in chans:
        try:
            chan = client.get_channel(int(chanID))
            await chan.send(embed=announcement)
        except Exception:
            pass


async def dm_user(authr, msg_embed, msg_on_fail=False):
    if not isinstance(authr, discord.Member):
        ctx = authr
        authr = authr.author
    if authr.dm_channel is None:
        await authr.create_dm()
    try:
        await authr.send(embed=msg_embed)
        return True
    except discord.errors.Forbidden:
        if msg_on_fail:
            await ctx.send(docs.rule_fail_send)
        return False


#ban [user] [chan]
#unban [user]
async def blist_iface(args, blist_obj):
    if args[0] == 'ban':
        if len(args) == 3:
            await blist_obj.new_blist(args[1], True if args[2] == 'priv' else False)
            return e.GOOD[:-3]
        return f'{e.ERROR}Invalid args'
    elif args[0] == 'unban':
        if len(args) == 2:
            await blist_obj.remove_blist(args[1])
            return e.GOOD[:-3]
        return f'{e.ERROR}Invalid args'
    else:
        return f'{e.ERROR}Invalid command'


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
    return f'Burned `{amt} GRC` from `{args[0]}`'


def user_stats(user_obj, client, user_time):
    final = f'User ID: {user_obj.usrID}\n'
    user = None
    for member in client.get_all_members():
        if str(member.id) == user_obj.usrID:
            user = member
            crtime = round(member.created_at.replace(tzinfo=timezone.utc).timestamp())
            break
    if user is None:
        return f'```{final}```'
    final += user_obj.get_stats().replace('`', '') + '\n'
    final += 'Created at: {} {}\n'.format(crtime, time.strftime("(%m Months %d Days %H Hours %M Minutes ago)", time.gmtime(time.time()-crtime)))
    jtime = round(member.joined_at.replace(tzinfo=timezone.utc).timestamp())
    final += 'Joined at: {} {}'.format(jtime, time.strftime("(%m Months %d Days %H Hours %M Minutes ago)", time.gmtime(time.time()-jtime)))
    return f'```{final}```'


def check_times(user_obj):
    ctime = round(time.time())
    return '''
Faucet: {}
Withdrawals: {}
Donations: {}
'''.format(e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_fct()-ctime)))) if not user_obj.can_faucet() else e.GOOD[:-3],
            e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_net_tx()-ctime)))) if not user_obj.can_net_tx() else e.GOOD[:-3],
            e.CANNOT[:-3] + ' ({})'.format(time.strftime("%H Hours %M Minutes %S Seconds", time.gmtime(ceil(user_obj.next_net_tx()-ctime)))) if not user_obj.can_net_tx() else e.GOOD[:-3])
