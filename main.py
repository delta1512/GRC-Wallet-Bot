import asyncio
import logging
import time
from logging.handlers import RotatingFileHandler
from os import path

import discord
from discord.ext import commands

import extras
import docs
import emotes as e
import errors
import grcconf as g
import wallet as w
import queries as q
from grc_pricebot import price_bot
from blacklist import Blacklister
from rain_bot import rainbot
from FAQ import index

# Set up logging functionality
handler = [RotatingFileHandler(g.log_dir+'walletbot.log', maxBytes=10**7, backupCount=3)]
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%d/%m %T',
                    level=logging.INFO,
                    handlers=handler)

client = commands.Bot(command_prefix=g.pre)
FCT = 'FAUCET'
RN = 'RAIN'
latest_users = {}
price_fetcher = price_bot()
blacklister = None
rbot = None
INITIALISED = False


def in_udb():
    def predicate(ctx):
        if not await q.uid_exists(ctx.author.id):
            raise errors.NotInUDB()
        return True
    return commands.check(predicate())


def limit_to_main_channel():
    def predicate(ctx):
        return ctx.channel.id == g.main_channel
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


async def rain_loop():
    while True:
        await asyncio.sleep(5)
        if rbot.check_rain():
            await rbot.do_rain(client)


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
            return await ctx.send(extras.donate_list(f'{e.GIVE}Be generous! Below are possible donation options.\nTo donate, type `%donate [selection no.] [amount-GRC]`\n', g.donation_accts))
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
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.send(docs.pm_restrict)


@client.event
async def on_ready():
    global blacklister, rbot
    if hasattr(client, 'initialised'):
        return  # Prevents multiple on_ready call
    await client.remove_command('help')
    if await w.query('getblockcount', []) > 5:  # 5 is largest error return value
        logging.info('Gridcoin client is online')
    else:
        logging.error('GRC client is not online')
        await bot.logout()
        return

    if not await q.uid_exists(FCT):
        logging.error('Could not connect to SQL database')
        await bot.logout()
        return
    else:
        logging.info('SQL DB online and accessible')

    try:
        blacklister = Blacklister(await q.get_blacklisted())
        logging.info('Blacklisting service loaded correctly')
    except Exception:
        logging.error('Blacklisting service failed to load')
        await bot.logout()
        return

    for extension in ['cogs.admin']:
        try:
            client.load_extension(extension)
        except Exception as E:
            logging.error('Failed to load extension %s. Exception: %s', (extension, E))
    client.cogs['cogs.admin'].blacklister = blacklister

    if await w.unlock() is None:
        logging.info('Wallet successfully unlocked')
    else:
        logging.error('There was a problem trying to unlock the gridcoin wallet')
        await bot.logout()
        return

    try:
        rbot = Rainbot(await q.get_user(RN))
        logging.info('Rainbot service loaded correctly')
    except:
        logging.error('Rainbot service failed to load')
        await bot.logout()
        return

    client.initialised = True
    logging.info('Initialisation complete')
    #Protection against errors in the loop
    while True:
        try:
            await rain_loop()
        except KeyboardInterrupt:
            logging.info('Pluggable loop shutting down')
            return
        except Exception as E:
            logging.error('Pluggable loop ran into an error: %s', E)


@client.command()
@limit_to_main_channel()
async def status(ctx):
    await ctx.send(await extras.dump_cfg(price_fetcher))


@client.command()
async def new(ctx):
    if not await uid_exists(ctx.author.id):
        await ctx.send(docs.welcome)
        try:
            addr = await w.query('getnewaddress', [])
            await q.new_user(ctx.author.id, addr)
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
            ctx.author.create_dm()
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
    data = await q.get_bal(ctx.author.id)
    await ctx.send(docs.balance_template.format(data[1], data[0])) # emoji, address, balance, priceUSD


@client.command(aliases=['addr'])
@in_udb()
@limit_to_main_channel()
async def address(ctx):
    await ctx.send((await q.get_bal(ctx.author.id))[1])


@client.command(aliases=['wdr', 'send'])
@in_udb()
@limit_to_main_channel()
async def withdraw(ctx, address: str, amount: float):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(await user_obj.withdraw(extras.amt_filter(amount), address, g.tx_fee))


@client.command()
@in_udb()
@limit_to_main_channel()
async def donate(ctx, selection: int, amount: float):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(extras.donate(user_obj, selection, extras.amt_filter(amount)))


@client.command()
@in_udb()
@limit_to_main_channel()
async def rdonate(ctx, amount: float):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(await extras.rdonate(user_obj, extras.amt_filter(amount)))


@client.command(aliases=['tip'])
@commands.guild_only()
@in_udb()
async def give(ctx, receiver: discord.User, amount: float):
    if receiver.id == ctx.author.id:
        return await ctx.send(docs.cannot_send_self)
    sender_obj = await q.get_user(ctx.author.id)
    receiver_obj = await q.get_user(receiver.id)
    if receiver_obj is None:
        return await ctx.send(f'{e.ERROR}Invalid user specified.')
    await ctx.send(await sender_obj.send_internal_tx(receiver_obj, amount))


@client.command()
@in_udb()
async def fgive(ctx, amount: int):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(await user_obj.send_internal_tx(await q.get_user(FCT), amount, True))
    await ctx.send(docs.faucet_thankyou)


@client.command(aliases=['fct', 'get'])
@commands.guild_only()
@in_udb()
@limit_to_main_channel()
async def faucet(ctx):
    faucet_obj = await q.get_user(FCT) # This is highly inefficient, an alternative is to be found
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(await extras.faucet(faucet_obj, user_obj))


@client.command()
async def rain(ctx, amount: float):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(rbot.contribute(extras.amt_fileter(amount), user_obj))


@client.command()
@commands.guild_only()
@limit_to_main_channel()
async def qr(ctx, text=None):
    if text is None:
        addr = (await q.get_bal(ctx.author.id))[1]
        return await ctx.send(file=discord.File(extras.get_qr(addr), filename=f'{ctx.author.name}.png'))
    await ctx.send(file=discord.File(extras.get_qr(text), filename=f'{ctx.author.name}.png'))


@client.command()
@in_udb()
@limit_to_main_channel()
async def time(ctx):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(extras.check_times(user_obj))


@client.command(aliases=['grcmoon', 'whenmoon', 'lambo', 'whenlambo'])
async def moon(ctx):
    await ctx.send(extras.moon())


@client.command(aliases=['me', 'acc'])
@in_udb()
@limit_to_main_channel()
async def account(ctx):
    user_obj = await q.get_user(ctx.author.id)
    await ctx.send(user_obj.get_stats())


@client.event
async def on_message(msg):
    cmd = msg.content
    chan = msg.channel
    is_private = isinstance(chan, discord.DMChannel)
    a = msg.author
    uname = a.name
    user = a.id
    iscommand = cmd.startswith(g.pre)
    if a.bot or checkspam(user) or blacklister.is_banned(user, is_private):
        return
    if iscommand and time.time() < user_time(a.created_at)+24*60*60*g.NEW_USR_TIME:
        return await msg.channel.send(docs.too_new_msg)
    if iscommand and (len(cmd) > 1):
        cmd = cmd[1:]
        log_msg = 'COMMAND "%s" executed by %s (%s){}'
        if is_private:
            log_msg.format(' in private channel')
        else:
            log_msg.format('')
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
