import asyncio
import logging
from time import time, mktime, strptime, perf_counter
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from os import path # Unused import?

import discord
from discord.ext import commands

import extras
import docs
import emotes as e
import errors
import grcconf as g
import wallet as w
import queries as q
import help_docs
from grc_pricebot import price_bot
from blacklist import Blacklister
from rain_bot import Rainbot
from FAQ import index

# Set up logging functionality
handler = [RotatingFileHandler(g.log_dir+'walletbot.log', maxBytes=10**7, backupCount=3)]
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%d/%m %T',
                    level=logging.INFO,
                    handlers=handler)

client = commands.Bot(command_prefix=g.pre)
client.remove_command('help')
FCT = 'FAUCET'
RN = 'RAIN'
latest_users = {}
price_fetcher = price_bot()
blacklister = None
rbot = None
INITIALISED = False


### DECORATORS
def in_udb():
    async def predicate(ctx):
        if not await q.uid_exists(str(ctx.author.id)):
            raise errors.NotInUDB()
        return True
    return commands.check(predicate)


def limit_to_main_channel():
    def predicate(ctx):
        return str(ctx.channel.id) == g.main_channel
    return commands.check(predicate)


def is_owner():
    def predicate(ctx):
        return str(ctx.author.id) == g.owner_id
    return commands.check(predicate)
###


def checkspam(user): # Possible upgrade: use discord.utils.snowflake_time to get their discord account creation date
    global latest_users
    if user in latest_users:
        if time()-latest_users[user] > 1:
            latest_users[user] = time()
            return False
        else:
            latest_users[user] = time()
            return True
    else:
        latest_users[user] = time()
        return False


def user_time(crtime):
    crtime = str(crtime)
    try:
        crtime = crtime[:crtime.index('.')]
    except ValueError:
        pass
    return mktime(strptime(crtime, '%Y-%m-%d %H:%M:%S'))


async def rain_loop():
    while True:
        await asyncio.sleep(5)
        if rbot.check_rain():
            await rbot.do_rain(client)


#@client.event
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
            return await ctx.send(extras.index_displayer(f'{e.GIVE}Be generous! Below are possible donation options.\nTo donate, type `%donate [selection no.] [amount-GRC]`\n', g.donation_accts))
        if ctx.command.name == 'rdonate':
            return await ctx.send(f'{e.GIVE}To donate to a random contributor type: `%rdonate [amount-GRC]`')
        if ctx.command.name == 'give':
            return await ctx.send(f'{e.INFO}To give funds to a member in the server, type `%give [discord mention of user] [amount to give]`.\nThe person must also have an account with the bot.')
        if ctx.command.name == 'fgive':
            return await ctx.send(f'{e.ERROR}Please specify an amount to give.')
        if ctx.command.name == 'rain':
            return await ctx.send(rbot.status())
        if ctx.command.name == 'faq':
            return await ctx.send(extras.index_displayer(docs.faq_msg, index) + '\n*Thanks to LavRadis and Foxifi for making these resources.*')
        if ctx.command.name == 'block':
            return await ctx.send(extras.show_block(await w.query('getblockcount', [])))
        if ctx.command.name == 'help':
            return await ctx.send(help_docs.help_main())
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.send(docs.pm_restrict)


@client.event
async def on_ready():
    global blacklister, rbot
    if hasattr(client, 'initialised'):
        return  # Prevents multiple on_ready call

    if await w.query('getblockcount', []) > 5:  # 5 is largest error return value
        logging.info('Gridcoin client is online')
    else:
        logging.error('GRC client is not online')
        await client.logout()
        return

    if not await q.uid_exists(FCT):
        logging.error('Could not connect to SQL database')
        await client.logout()
        return
    else:
        logging.info('SQL DB online and accessible')

    try:
        blacklister = Blacklister(await q.get_blacklisted())
        logging.info('Blacklisting service loaded correctly')
    except Exception:
        logging.error('Blacklisting service failed to load')
        await client.logout()
        return

    if await w.unlock() is None:
        logging.info('Wallet successfully unlocked')
    else:
        logging.error('There was a problem trying to unlock the gridcoin wallet')
        await client.logout()
        return

    try:
        rbot = Rainbot(await q.get_user(RN))
        logging.info('Rainbot service loaded correctly')
    except Exception as E:
        logging.error('Rainbot service failed to load: %s', E)
        await client.logout()
        return

    client.initialised = True
    logging.info('Initialisation complete')
    #Protection against errors in the loop
    while True:
        try:
            await rain_loop()
        except KeyboardInterrupt:
            logging.info('Rain loop shutting down')
            return
        except Exception as E:
            logging.error('Rain loop ran into an error: %s', E)


@client.command()
@limit_to_main_channel()
async def status(ctx):
    await ctx.send(await extras.dump_cfg(price_fetcher))


@client.command()
async def new(ctx):
    if not await q.uid_exists(str(ctx.author.id)):
        await ctx.send(docs.welcome)
        try:
            addr = await w.query('getnewaddress', [])
            await q.new_user(str(ctx.author.id), addr)
            await ctx.send(docs.new_user_success.format(e.GOOD, addr))
        except Exception:
            await ctx.send(docs.new_user_fail)
            return

        if ctx.author.dm_channel is None:
            ctx.author.create_dm()
        try:
            await ctx.author.send(embed=docs.rules)
            await ctx.author.send(embed=docs.terms)
        except discord.errors.Forbidden:
            await ctx.send(docs.rule_fail_send)
    else:
        await ctx.send(docs.already_user)


@client.command(name='help')
@limit_to_main_channel()
async def _help(ctx, command):  # Not overwriting the built-in help function
    await ctx.send(embed=extras.help_interface(command))


@client.command()
@limit_to_main_channel()
async def info(ctx):
    await ctx.send(embed=docs.info)


@client.command()
@limit_to_main_channel()
async def faq(ctx, query: int):
    reply = extras.faq(query)
    if isinstance(reply, str):
        await ctx.send(reply)
    else:
        if ctx.author.dm_channel is None:
            await ctx.author.create_dm()
        try:
            await ctx.author.send(embed=reply)
            await ctx.message.add_reaction('\u2705')  # WHITE HEAVY CHECK MARK
        except discord.errors.Forbidden:
            await ctx.send(docs.fail_dm)


@client.command()
async def block(ctx, query: int):
    await ctx.send(await extras.show_block(query))


@client.command()
async def rules(ctx):
    if ctx.author.dm_channel is None:
        ctx.author.create_dm()
    try:
        await ctx.author.send(embed=docs.rules)
        await ctx.message.add_reaction('\u2705')  # WHITE HEAVY CHECK MARK
    except discord.errors.Forbidden:
        await ctx.send(docs.rule_fail_send)


@client.command()
async def terms(ctx):
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
    data = await q.get_bal(str(ctx.author.id))
    await ctx.send(docs.balance_template.format(e.BAL, data[1], data[0], round(await price_fetcher.conv(data[0]), 3))) # emoji, address, balance, priceUSD


@client.command(aliases=['addr'])
@in_udb()
@limit_to_main_channel()
async def address(ctx):
    await ctx.send((await q.get_bal(str(ctx.author.id)))[1])


@client.command(aliases=['wdr', 'send'])
@in_udb()
@limit_to_main_channel()
async def withdraw(ctx, address: str, amount: float):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(await user_obj.withdraw(extras.amt_filter(amount), address, g.tx_fee))


@client.command()
@in_udb()
@limit_to_main_channel()
async def donate(ctx, selection: int, amount: float):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(await extras.donate(user_obj, selection, extras.amt_filter(amount)))


@client.command()
@in_udb()
@limit_to_main_channel()
async def rdonate(ctx, amount: float):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(await extras.rdonate(user_obj, extras.amt_filter(amount)))


@client.command(aliases=['tip'])
@commands.guild_only()
@in_udb()
async def give(ctx, receiver: discord.User, amount: float):
    if str(receiver.id) == str(ctx.author.id):
        return await ctx.send(docs.cannot_send_self)
    sender_obj = await q.get_user(str(ctx.author.id))
    receiver_obj = await q.get_user(str(receiver.id))
    if receiver_obj is None:
        return await ctx.send(f'{e.ERROR}Invalid user specified.')
    await ctx.send(await sender_obj.send_internal_tx(receiver_obj, extras.amt_filter(amount)))


@client.command()
@in_udb()
async def fgive(ctx, amount: int):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(await user_obj.send_internal_tx(await q.get_user(FCT), amount, True))
    await ctx.send(docs.faucet_thankyou)


@client.command(aliases=['fct', 'get'])
@commands.guild_only()
@in_udb()
@limit_to_main_channel()
async def faucet(ctx):
    faucet_obj = await q.get_user(FCT) # This is highly inefficient, an alternative is to be found
    user_obj = await q.get_user(str(ctx.author.id))
    result = await extras.faucet(faucet_obj, user_obj)
    if result.startswith(e.GOOD):
        await ctx.send(docs.faucet_msg.format(faucet_obj.balance, faucet_obj.address))
    await ctx.send(result)


@client.command()
async def rain(ctx, amount: float):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(await rbot.contribute(extras.amt_filter(amount), user_obj))


@client.command()
@commands.guild_only()
@limit_to_main_channel()
async def qr(ctx, text=None):
    if text is None:
        addr = (await q.get_bal(str(ctx.author.id)))[1]
        return await ctx.send(file=discord.File(extras.get_qr(addr), filename=f'{ctx.author.name}.png'))
    await ctx.send(file=discord.File(extras.get_qr(text), filename=f'{ctx.author.name}.png'))


@client.command(name='time')
@in_udb()
@limit_to_main_channel()
async def _time(ctx):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(extras.check_times(user_obj))


@client.command(aliases=['grcmoon', 'whenmoon', 'lambo', 'whenlambo'])
async def moon(ctx):
    await ctx.send(extras.moon())


@client.command(aliases=['me', 'acc'])
@in_udb()
@limit_to_main_channel()
async def account(ctx):
    user_obj = await q.get_user(str(ctx.author.id))
    await ctx.send(user_obj.get_stats())


@client.command()
async def ping(ctx):
    t1 = perf_counter()
    await ctx.trigger_typing()
    t2 = perf_counter()
    time_delta = round((t2 - t1) * 1000)
    await ctx.send(f"`{time_delta}ms`")


### ADMINISTRATION COMMANDS
@client.command()
@is_owner()
async def blist(ctx, *args):  # TODO: Add private message check -jorkermc
    if len(args) > 0:
        await ctx.send(await extras.blist_iface(args, blacklister))
    else:
        await ctx.send(blacklister.get_blisted())


@client.command(name='bin')
@is_owner()
async def _bin(ctx, *args):  # Not overriding built-in function bin
    if len(args) == 2:
        await ctx.send(await extras.burn_coins(args))


@client.command()
@is_owner()
async def stat(ctx, *args):
    if len(args) == 0:
        user_obj = await q.get_user(str(ctx.author.id))
    else:
        user_obj = await q.get_user(args[0])
        if user_obj is None: return;
    await ctx.send(extras.user_stats(user_obj, client, user_time))
###


@client.event
async def on_message(msg):
    cmd = msg.content
    chan = msg.channel
    is_private = isinstance(chan, discord.DMChannel)
    a = msg.author
    uname = a.name
    user = str(a.id)
    iscommand = cmd.startswith(g.pre)

    # Check for if the user is a bot, spamming or is blacklisted
    if a.bot or checkspam(user) or blacklister.is_banned(user, is_private):
        return

    # Check for new user
    if iscommand and time() < user_time(a.created_at)+24*60*60*g.NEW_USR_TIME:
        return await msg.channel.send(docs.too_new_msg)

    # Execute command if it is more than a single prefix character
    if iscommand and (len(cmd) > 1):
        cmd = cmd[1:]
        log_msg = 'COMMAND "%s" executed by %s (%s)'
        if is_private:
            log_msg = log_msg + ' in private channel'
            log_msg.format(log_msg, cmd.split()[0], user, uname)
        else:
            log_msg.format(log_msg)
        logging.info(log_msg, cmd.split()[0], user, uname)
    await client.process_commands(msg)


try:
    with open('API.key', 'r') as key_file:
        API_KEY = str(key_file.read().replace('\n', ''))
    logging.info('API Key loaded')
except Exception:
    logging.error('Failed to load API key')
    exit(1)


client.run(API_KEY)
