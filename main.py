from os import path
import asyncio
import discord
import logging
from logging.handlers import RotatingFileHandler

from GRC_pricebot import price_bot
import UDB_tools as db
import commands as bot
import grcconf as g
import emotes as e
import wallet as w
import docs

# Set up logging functionality
handler = [RotatingFileHandler(g.log_dir, maxBytes=10**7, backupCount=3)]
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%d/%m %T',
                    level=logging.INFO,
                    handlers=handler)

client = discord.Client()
LAST_BLK = 0
FCT = 'FAUCET'
price_fetcher = price_bot()
UDB = {}

async def check_tx(txid):
    tx = await w.query('gettransaction', [txid])
    recv_addrs = []
    send_addrs = []
    recv_vals = []
    try:
        if not isinstance(tx, int):
            for details in tx['details']:
                if details['category'] == 'receive':
                    recv_addrs.append(details['address'])
                    recv_vals.append(details['amount'])
                elif details['category'] == 'send':
                    send_addrs.append(details['address'])
        elif tx == 1:
            pass
        else:
            raise RuntimeError('Bad signal in GRC client: {}'.format(tx))
    except RuntimeError as E:
        logging.error(E)
    except KeyError:
        pass
    return recv_addrs, send_addrs, recv_vals

async def blk_searcher():
    global UDB, LAST_BLK
    newblock = await w.query('getblockcount', [])
    if newblock > LAST_BLK:
        try:
            for blockheight in range(LAST_BLK+1, newblock+1):
                blockhash = await w.query('getblockhash', [blockheight])
                await asyncio.sleep(0.05) # Protections to guard against reusing the bind address
                blockdata = await w.query('getblock', [blockhash])
                if isinstance(blockdata, dict): # Protections to guard against reusing the bind address
                    LAST_BLK = blockheight
                    for txid in blockdata['tx']:
                        recv_addrs, send_addrs, vals = await check_tx(txid)
                        if len(recv_addrs) > 0:
                            for uid in UDB:
                                found = False
                                usr_obj = UDB[uid]
                                for i, addr in enumerate(recv_addrs):
                                    if usr_obj.address == addr:
                                        # Check whether change address
                                        found = not addr in send_addrs
                                        index = i
                                        if found:
                                            break
                                if found:
                                    logging.info('Processed deposit for {}'.format(usr_obj.usrID))
                                    usr_obj.balance += vals[index]
                                    tmp = recv_addrs.pop(index)
                                    try: # In event of change address
                                        send_addrs.pop(send_addrs.index(tmp))
                                    except ValueError:
                                        pass
                                    vals.pop(index)
                elif blockdata == 3:
                    pass # Don't render the reuse address error as an exception, otherwise it may flood the terminal
                else:
                    raise RuntimeError('Received erroneous signal in GRC client interface.')
        except Exception as E:
            logging.exception('Block searcher ran into an error: {}'.format(E))

async def pluggable_loop():
    sleepcount = 0
    while True:
        await asyncio.sleep(5)
        await blk_searcher()
        if sleepcount % g.SLP == 0:
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
async def on_ready():
    global UDB, LAST_BLK
    if await w.query('getblockcount', []) > 5: # 5 is largest error return value
        logging.info('Gridcoin client is online')
    else:
        logging.error('GRC client is not online')
        exit(1)

    if await db.check_db() != 0:
        logging.error('Could not connect to SQL database')
        exit(1)
    else:
        logging.info('SQL DB online and accessible')

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
        exit(1)

    UDB = await db.read_db()
    logging.info('Initialisation complete')
    await pluggable_loop()

@client.event
async def on_message(msg):
    global UDB
    cmd = msg.content
    chan = msg.channel
    uname = msg.author.name
    user = msg.author.id
    INDB = user in UDB
    iscommand = cmd.startswith(g.pre)
    if iscommand and (len(cmd) > 1):
        cmd = cmd[1:]
        if chan.is_private:
            logging.info('COMMAND "%s" executed by %s (%s) in private channel',
            cmd.split()[0], user, uname)
        else:
            logging.info('COMMAND "%s" executed by %s (%s)',
            cmd.split()[0], user, uname)
        if cmd.startswith('status'):
            await client.send_message(chan, await bot.dump_cfg(price_fetcher))
        elif cmd.startswith('new'):
            if not INDB:
                await client.send_message(chan, '{}Creating your account now...'.format(e.SETTING))
                status, reply, userobj = await bot.new_user(user)
                if status == 0:
                    UDB[user] = userobj
                await client.send_message(chan, reply)
            else:
                await client.send_message(chan, '{}Cannot create new account, you already have one.'.format(e.CANNOT))
        elif cmd.startswith('help'):
            await client.send_message(chan, bot.help_interface(cmd.split().pop()))
        elif cmd.startswith('info'):
            await client.send_message(chan, docs.info)
        elif INDB:
            USROBJ = UDB[user]
            if cmd in ['bal', 'balance']:
                await client.send_message(chan, await bot.fetch_balance(USROBJ, price_fetcher))
            elif cmd.startswith('addr'):
                await client.send_message(chan, USROBJ.address)
            elif cmd.split()[0] in ['wdr', 'withdraw', 'send']:
                args = cmd.split()[1:]
                if len(args) == 2:
                    reply = await bot.withdraw(args[1], args[0], USROBJ)
                else:
                    reply = '{}To withdraw from your account type: `%wdr [address to send to] [amount-GRC]`\nA service fee of {} GRC is subtracted from what you send. If you wish to send GRC to someone in the server, use `%give`'.format(e.INFO, str(g.tx_fee))
                await client.send_message(chan, reply)
            elif cmd.startswith('donate'):
                args = cmd.split()[1:]
                if len(args) == 2:
                    reply = await bot.donate(args[0], args[1], USROBJ)
                else:
                    reply = bot.fetch_donation_addrs()
                await client.send_message(chan, reply)
            elif cmd.startswith('rdonate'):
                args = cmd.split()[1:]
                if len(args) == 1:
                    reply = await bot.rdonate(args[0], USROBJ)
                else:
                    reply = '{}To donate to a random contributor type: `%rdonate [amount-GRC]`'.format(e.GIVE)
                await client.send_message(chan, reply)
            elif cmd.startswith('give'):
                args = cmd.split()[1:]
                if chan.is_private:
                    await client.send_message(chan, docs.PM_msg)
                elif (len(args) != 2) or (len(msg.mentions) != 1):
                    await client.send_message(chan, '{}To give funds to a member in the server, type `%give [discord mention of user] [amount to give]`.\nThe person must also have an account with the bot.'.format(e.INFO))
                elif not msg.mentions[0].id in UDB:
                    await client.send_message(chan, '{}Invalid user specified.'.format(e.ERROR))
                else:
                    await client.send_message(chan, bot.give(args[1], USROBJ, UDB[msg.mentions[0].id]))
            elif cmd.startswith('fgive'):
                args = cmd.split()[1:]
                if len(args) < 1:
                    await client.send_message(chan, '{}Please specify an amount to give.'.format(e.ERROR))
                else:
                    await client.send_message(chan, bot.give(args[0], USROBJ, UDB[FCT], add_success_msg='\n\nThank you for donating to the faucet!', donation=True))
            elif cmd in ['faucet', 'fct', 'get']:
                fctobj = UDB[FCT]
                await client.send_message(chan, docs.faucetmsg.format(round(fctobj.balance, 8), g.FCT_REQ_LIM, fctobj.address))
                if chan.is_private:
                    await client.send_message(chan, docs.PM_msg)
                else:
                    await client.send_message(chan, bot.faucet(fctobj, USROBJ))
            elif cmd.startswith('qr'):
                args = cmd.split()[1:]
                if chan.is_private:
                    await client.send_message(chan, docs.PM_msg)
                elif len(args) == 1:
                    await client.send_file(chan, bot.get_qr(args[0], filename=user + '.png'))
                elif len(args) > 1:
                    await client.send_message(chan, '{}Too many arguments provided'.format(e.CANNOT))
                else:
                    await client.send_file(chan, bot.get_qr(USROBJ.address), filename=user + '.png')
            elif cmd.startswith('bin {}'.format(user)):
                args = cmd.split()[2:]
                if len(args) > 0 and chan.is_private:
                    amt = 0 if (bot.amt_filter(args[0], USROBJ) == None) else bot.amt_filter(args[0], USROBJ)
                    USROBJ.balance -= amt
                    await client.send_message(chan, 'Burned `{} GRC`'.format(amt))
            else:
                await client.send_message(chan, '{}Invalid command. Type `%help` for help.'.format(e.INFO))
        else:
            await client.send_message(chan, '{}Either incorrect command or not in user database (try `%new` or type `%help` for help)'.format(e.ERROR))

try:
    with open('API.key', 'r') as key_file:
        API_KEY = str(key_file.read().replace('\n', ''))
    logging.info('API Key loaded')
except:
    logging.error('Failed to load API key')
    exit(1)

client.run(API_KEY)
