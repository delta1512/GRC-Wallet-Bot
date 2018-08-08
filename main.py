import asyncio
import logging
import time
from logging.handlers import RotatingFileHandler
from os import path

import discord
from discord.ext import commands

import commands as bot
import docs
import emotes as e
import errors
import grcconf as g
import wallet as w
import UDB_tools as db
from grc_pricebot import price_bot
from blacklist import blist
from rain_bot import rainbot
from scavenger import blk_searcher

# Set up logging functionality
handler = [RotatingFileHandler(g.log_dir+'walletbot.log', maxBytes=10**7, backupCount=3)]
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%d/%m %T',
                    level=logging.INFO,
                    handlers=handler)

client = commands.Bot(command_prefix=g.pre)
LAST_BLK = 0
FCT = 'FAUCET'
RN = 'RAIN'
UDB = {}
latest_users = {}
price_fetcher = price_bot()
blacklister = None
rbot = None
INITIALISED = False
UDB_LOCK = False


def in_udb():
    def predicate(ctx):
        global UDB
        if ctx.author.id not in UDB:
            raise errors.NotInUDB()
        return True
    return commands.check(predicate)


def checkspam(user): # Possible upgrade: use discord.utils.snowflake_time to get their discord account creation date
    global latest_users
    if user in latest_users:
        if time.time()-latest_users[user] > 1:
            latest_users[user] = time.time()
            return False
        else:
            latest_users[user] = time.time()
            return True
    else:
        latest_users[user] = time.time()
        return False


def user_time(crtime):
    crtime = str(crtime)
    try:
        crtime = crtime[:crtime.index('.')]
    except ValueError:
        pass
    return time.mktime(time.strptime(crtime, '%Y-%m-%d %H:%M:%S'))


async def pluggable_loop():
    sleepcount = 0
    while True:
        await asyncio.sleep(5)
        await blk_searcher()
        if rbot.check_rain():
            await rbot.do_rain(UDB, client)
        if sleepcount % g.SLP == 0:
            if not UDB_LOCK:
                await db.save_db(UDB)
            with open(g.LST_BLK, 'w') as last_block:
                last_block.write(str(LAST_BLK))
            with open(g.FEE_POOL, 'r') as fees:
                owed = float(fees.read())
            if owed >= g.FEE_WDR_THRESH:
                txid = await w.tx(g.admin_wallet, owed)
                if not isinstance(txid, str):
                    logging.error('Admin fees could not be sent, exit_code: %s', txid)
                else:
                    logging.info('Admin fees sent')
                    with open(g.FEE_POOL, 'w') as fees:
                        fees.write('0')
        sleepcount += 5


@client.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return

    if isinstance(error, commands.CommandNotFound):
        return await ctx.send(f'{e.INFO}Invalid command. Type `%help` for help.')
    if isinstance(error, errors.NotInUDB):
        return await ctx.send(f'{e.ERROR}You are not in user database. (try `%new` or type `%help` for help)')
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'withdraw':
            return await ctx.send(f'{e.INFO}To withdraw from your account type: `%wdr [address to send to] [amount-GRC]`\nA service fee of {g.tx_fee} GRC is subtracted from what you send. If you wish to send GRC to someone in the server, use `%give`')
        if ctx.command.name == 'donate':
            return await ctx.send(bot.index_displayer(f'{e.GIVE}Be generous! Below are possible donation options.\nTo donate, type `%donate [selection no.] [amount-GRC]`\n', g.donation_accts))
        if ctx.command.name == 'rdonate':
            return await ctx.send(f'{e.GIVE}To donate to a random contributor type: `%rdonate [amount-GRC]`')
        if ctx.command.name == 'give':
            return await ctx.send(f'{e.INFO}To give funds to a member in the server, type `%give [discord mention of user] [amount to give]`.\nThe person must also have an account with the bot.')
        if ctx.command.name == 'fgive':
            return await ctx.send(f'{e.ERROR}Please specify an amount to give.')
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.send(docs.pm_restrict)


@client.event
async def on_ready():
    global UDB, LAST_BLK, blacklister, rbot
    if hasattr(client, 'initialised'):
        return  # Prevents multiple on_ready call
    await client.remove_command('help')
    if await w.query('getblockcount', []) > 5:  # 5 is largest error return value
        logging.info('Gridcoin client is online')
    else:
        logging.error('GRC client is not online')
        await bot.logout()

    if not await db.check_db() == 0:
        logging.error('Could not connect to SQL database')
        await bot.logout()
    else:
        logging.info('SQL DB online and accessible')

    try:
        blacklister = blist()
        logging.info('Blacklisting service loaded correctly')
    except Exception:
        logging.error('Blacklisting service failed to load')
        await bot.logout()

    if path.exists(g.LST_BLK):
        with open(g.LST_BLK, 'r') as last_block:
            LAST_BLK = int(last_block.read())
    else:
        with open(g.LST_BLK, 'w') as last_block:
            LAST_BLK = await w.query('getblockcount', [])
            last_block.write(str(LAST_BLK))
        logging.info('No start block specified. Setting block to client latest')

    if not path.exists(g.FEE_POOL):
        logging.info('Fees owed file not found. Setting fees owed to 0')
        with open(g.FEE_POOL, 'w') as fees:
            fees.write('0')

    if await w.unlock() is None:
        logging.info('Wallet successfully unlocked')
    else:
        logging.error('There was a problem trying to unlock the gridcoin wallet')
        await bot.logout()

    UDB = await db.read_db()

    try:
        rbot = rainbot(UDB[RN])
        logging.info('Rainbot service loaded correctly')
    except Exception:
        logging.error('Rainbot service failed to load')
        await bot.logout()

    client.initialised = True
    logging.info('Initialisation complete')
    # Temporary Protection against errors in the loop
    while True:
        try:
            await pluggable_loop()
        except KeyboardInterrupt:
            logging.info('Pluggable loop shutting down')
            return
        except Exception as E:
            logging.error('Pluggable loop ran into an error: %s', E)


@client.command()
async def status(ctx):
    await ctx.send(await bot.dump_cfg(price_fetcher, len(UDB)))


@client.command()
async def new(ctx):
    global UDB_LOCK
    if ctx.author.id not in UDB:
        UDB_LOCK = True
        await ctx.send(docs.welcome)
        status, reply, user_object = await bot.new_user(ctx.author.id)
        if not status:
            UDB[ctx.author.id] = user_object
        await ctx.send(reply)
        if ctx.author.dm_channel is None:
            ctx.author.create_dm()
        try:
            await ctx.author.send(embed=docs.rules)
            await ctx.author.send(embed=docs.terms)
        except discord.errors.Forbidden:
            await ctx.send(docs.rule_fail_send)
        UDB_LOCK = False
    else:
        await ctx.send(f'{e.CANNOT}Cannot create new account, you already have one.')


@client.command(name='help')
async def _help(ctx, command):  # Not overwriting the built-in help function
    await ctx.send(bot.help_interface(command))


@client.command()
async def info(ctx):
    await ctx.send(embed=docs.info)


@client.command()
async def faq(ctx, *query):
    reply = bot.faq(query)
    if isinstance(reply, str):
        await ctx.send(reply)
    else:
        if ctx.author.dm_channel is None:
            ctx.author.create_dm()
        try:
            await ctx.author.send(embed=reply)
            await ctx.message.add_reaction('\u2705')  # WHITE HEAVY CHECK MARK
        except discord.errors.Forbidden:
            await ctx.send(docs.rule_fail_send)


@client.command()
async def block(ctx, *query):
    await ctx.send(await bot.get_block(query))


@client.command()
async def rule(ctx):
    if ctx.author.dm_channel is None:
        ctx.author.create_dm()
    try:
        await ctx.author.send(embed=docs.rules)
        await ctx.message.add_reaction('\u2705')  # WHITE HEAVY CHECK MARK
    except discord.errors.Forbidden:
        await ctx.send(docs.rule_fail_send)


@client.command()
async def term(ctx):
    if ctx.author.dm_channel is None:
        ctx.author.create_dm()
    try:
        await ctx.author.send(embed=docs.terms)
        await ctx.message.add_reaction('\u2705')  # WHITE HEAVY CHECK MARK
    except discord.errors.Forbidden:
        await ctx.send(docs.rule_fail_send)


@client.command(aliases=['bal'])
@in_udb()
async def balance(ctx):
    user_object = UDB[ctx.author.id]
    await ctx.send(await bot.fetch_balance(user_object, price_fetcher))


@client.command(aliases=['addr'])
@in_udb()
async def address(ctx):
    user_object = UDB[ctx.author.id]
    await ctx.send(user_object.address)


@client.command(aliases=['wdr', 'send'])
@in_udb()
async def withdraw(ctx, address: str, amount: int):
    user_object = UDB[ctx.author.id]
    await ctx.send(await bot.withdraw(amount, address, user_object))


@client.command()
@in_udb()
async def donate(ctx, selection: int, amount: int):
    user_object = UDB[ctx.author.id]
    await ctx.send(await bot.donate(selection, amount, user_object))


@client.command()
@in_udb()
async def rdonate(ctx, amount: int):
    user_object = UDB[ctx.author.id]
    await ctx.send(await bot.rdonate(amount, user_object))


@client.command(aliases=['tip'])
@commands.guild_only()
@in_udb()
async def give(ctx, receiver: discord.User, amount: int):
    receiver_object = UDB.get(receiver.id, None)
    if receiver_object is None:
        return await ctx.send(f'{e.ERROR}Invalid user specified.')
    sender_object = UDB[ctx.author.id]
    await ctx.send(bot.give(amount, sender_object, receiver_object))


@client.command()
@in_udb()
async def fgive(ctx, amount: int):
    user_object = UDB[ctx.author.id]
    await ctx.send(bot.give(amount, user_object, UDB[FCT], add_success_msg='\n\nThank you for donating to the faucet!', donation=True))


@client.command(aliases=['fct', 'get'])
@commands.guild_only()
@in_udb()
async def faucet(ctx):
    faucet_object = UDB[FCT]
    user_object = UDB[ctx.author.id]
    await ctx.send(docs.faucetmsg.format(round(faucet_object.balance, 8), g.FCT_REQ_LIM, faucet_object.address))
    await ctx.send(bot.faucet(faucet_object, user_object))


@client.command()
async def rain(ctx, amount: float):
    user_object = UDB[ctx.author.id]
    await ctx.send(rbot.process_message([amount], user_object))


@client.command()
@commands.guild_only()
async def qr(ctx, text=None):
    if text is None:
        user_object = UDB[ctx.ctx.author.id]
        return await ctx.send(file=discord.File(bot.get_qr(user_object.address), filename=f'{ctx.author.name}.png'))
    await ctx.send(file=discord.File(bot.get_qr(text), filename=f'{ctx.author.name}.png'))


@client.command()
@in_udb()
async def time(ctx):
    user_object = UDB[ctx.author.id]
    await ctx.send(bot.check_times(user_object))


@client.command(aliases=['grcmoon', 'whenmoon'])
async def moon(ctx):
    await ctx.send(bot.moon())


@client.command(aliases=['me', 'acc'])
@in_udb()
async def account(ctx):
    user_object = UDB[ctx.author.id]
    await ctx.send(bot.get_usr_info(user_object))


@client.command()
@commands.is_owner()
async def blist(ctx, *args): # TODO: Add private message check -jorkermc
    if len(args) > 0:
        await ctx.send(bot.blist_iface(args, blacklister))
    else:
        await ctx.send(blacklister.get_blisted())


@client.command(name='bin')
@commands.is_owner()
async def _bin(ctx, *args): # Not overriding built-in function bin
    await ctx.send(bot.burn_coins(args, UDB))


@client.command()
@commands.is_owner()
async def stat(ctx, *args):
    if len(args) > 0:
        await ctx.send(bot.user_stats(args[0], UDB.get(args[0], None), user_time, client))


@client.event
async def on_message(msg):
    global UDB, UDB_LOCK
    cmd = msg.content
    chan = msg.channel
    is_private = isinstance(chan, discord.DMChannel)
    a = msg.author
    uname = a.name
    user = a.id
    iscommand = cmd.startswith(g.pre)
    if a.bot or checkspam(user) or blacklister.is_banned(user, is_private):
        return
    elif iscommand and time.time() < user_time(a.created_at)+24*60*60*g.NEW_USR_TIME:
        return await msg.channel.send(docs.too_new_msg)
    elif iscommand and (len(cmd) > 1):
        cmd = cmd[1:]
        if is_private:
            logging.info('COMMAND "%s" executed by %s (%s) in private channel',
            cmd.split()[0], user, uname)
        else:
            logging.info('COMMAND "%s" executed by %s (%s)',
            cmd.split()[0], user, uname)
    await client.process_commands(msg)


try:
    with open('API.key', 'r') as key_file:
        API_KEY = str(key_file.read().replace('\n', ''))
    logging.info('API Key loaded')
except Exception: # Do not use bare except because it also catches BaseException
    logging.error('Failed to load API key')
    exit(1)

client.run(API_KEY)
