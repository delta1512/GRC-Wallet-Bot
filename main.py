from GRC_pricebot import price_bot
import UDB_tools as db
import commands as bot
from user import usr
from sys import exit
import grcconf as g
from os import path
import emotes as e
import wallet as w
import discord
import asyncio
import docs

client = discord.Client()
LAST_BLK = 0
FCT = 'FAUCET'
price_fetcher = price_bot()
UDB = {}

async def check_tx(txid):
    tx = await w.query('gettransaction', [txid])
    final_addrs = []
    final_vals = []
    try:
        for details in tx['details']:
            if details['category'] == 'receive':
                final_addrs.append(details['address'])
                final_vals.append(details['amount'])
    except:
        pass
    return final_addrs, final_vals

async def blk_searcher():
    global UDB, LAST_BLK
    newblock = await w.query('getblockcount', [])
    if newblock > LAST_BLK:
        for blockheight in range(LAST_BLK+1, newblock+1):
            try:
                blockhash = await w.query('getblockhash', [blockheight])
                await asyncio.sleep(0.05) # Protections to guard against reusing the bind address
                blockdata = await w.query('getblock', [blockhash])
                if isinstance(blockdata, dict): # Protections to guard against reusing the bind address
                    LAST_BLK = blockheight
                    for txid in blockdata['tx']:
                        addrs, vals = await check_tx(txid)
                        if len(addrs) > 0:
                            for uid in UDB:
                                found = False
                                usr_obj = UDB[uid]
                                for i, addr in enumerate(addrs):
                                    if usr_obj.address == addr:
                                        found = True
                                        index = i
                                        break
                                if found:
                                    print('[DEBUG] Processed deposit.')
                                    usr_obj.balance += vals[index]
                                    addrs.pop(index)
                                    vals.pop(index)
                elif blockdata == 3:
                    pass # Don't render the reuse address error as an exception, otherwise it may flood the terminal
                else:
                    raise Exception('Received erronous signal in GRC client interface.')
            except Exception as E:
                print('[ERROR] Block searcher ran into an error: {}'.format(E))
                exit(0)

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
                    print('[ERROR] Admin fees could not be sent')
                else:
                    print('[DEBUG] Admin fees sent')
                    with open(g.FEE_POOL, 'w') as fees:
                        fees.write('0')
        sleepcount += 5

@client.event
async def on_ready():
    global UDB, LAST_BLK
    if await w.query('getblockcount', []) > 5: # 5 is largest error return value
        print('[DEBUG] Gridcoin client is online')
    else:
        print('[ERROR] GRC client is not online')
        exit(1)

    if await db.check_db() != 0:
        print('[ERROR] Could not connect to SQL database')
        exit(1)
    else:
        print('[DEBUG] SQL DB online and accessible')

    if path.exists(g.LST_BLK):
        with open(g.LST_BLK, 'r') as last_block:
            LAST_BLK = int(last_block.read())
    else:
        with open(g.LST_BLK, 'w') as last_block:
            last_block.write(str(await w.query('getblockcount', [])))
        print('[DEBUG] No start block specified. Setting block to client latest')

    if not path.exists(g.FEE_POOL):
        print('[DEBUG] Fees owed file not found. Setting fees owed to 0')
        with open(g.FEE_POOL, 'w') as fees:
            fees.write('0')

    if await w.unlock() == None:
        print('[DEBUG] Wallet successfully unlocked')
    else:
        print('[ERROR] There was a problem trying to unlock the gridcoin wallet')
        exit(1)

    UDB = await db.read_db()
    print('[DEBUG] Initialisation complete')
    await pluggable_loop()

@client.event
async def on_message(msg):
    global UDB
    cmd = msg.content
    chan = msg.channel
    user = msg.author.id
    INDB = user in UDB
    iscommand = cmd.startswith(g.pre)
    if iscommand and chan.is_private:
        await client.send_message(chan, docs.PM_msg)
    elif iscommand and (len(cmd) > 1):
        cmd = cmd[1:]
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
                if (len(args) != 2) or (len(msg.mentions) != 1):
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
                    await client.send_message(chan, bot.give(args[0], USROBJ, UDB[FCT], add_success_msg='\n\nThankyou for donating to the faucet!', donation=True))
            elif cmd in ['faucet', 'fct', 'get']:
                fctobj = UDB[FCT]
                await client.send_message(chan, docs.faucetmsg.format(round(fctobj.balance, 8), g.FCT_REQ_LIM, fctobj.address))
                await client.send_message(chan, bot.faucet(fctobj, USROBJ))
            elif cmd.startswith('qr'):
                args = cmd.split()[1:]
                if len(args) == 1:
                    await client.send_file(chan, bot.get_qr(args[0], user))
                elif len(args) > 1:
                    await client.send_message(chan, '{}Too many arguments provided'.format(e.CANNOT))
                else:
                    await client.send_file(chan, bot.get_qr(USROBJ.address, user))
            else:
                await client.send_message(chan, '{}Invalid command. Type `%help` for help.'.format(e.INFO))
        else:
            await client.send_message(chan, '{}Either incorrect command or not in user database (try `%new` or type `%help` for help)'.format(e.ERROR))

try:
    with open('API.key', 'r') as APIkeyfile:
        APIkey = str(APIkeyfile.read().replace('\n', ''))
    print('[DEBUG] API Key loaded')
except:
    print('[ERROR] Failed to load API key')
    exit(1)

client.run(APIkey)
