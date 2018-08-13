import asyncio
import logging
from logging.handlers import RotatingFileHandler

import wallet as w
import queries as q
import grcconf as g

last_block = 0

# Set up logging functionality
handler = [RotatingFileHandler(g.log_dir+'deposits.log', maxBytes=10**7, backupCount=3)]
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%d/%m %T',
                    level=logging.INFO,
                    handlers=handler)


async def check_tx(txid):
    tx = await w.query('gettransaction', [txid])
    receivers = []
    send_addrs = []
    try:
        if not isinstance(tx, int):
            for details in tx['details']:
                if details['category'] == 'receive':
                    receivers.append({details['address'] : details['amount']})
                elif details['category'] == 'send':
                    send_addrs.append(details['address'])
        elif tx == 1:
            pass
        else:
            logging.error('Bad signal in GRC client: %s', tx)
    except RuntimeError as E:
        logging.error('check_tx ran into an unhandled error: %s', E)
    except KeyError:
        pass

    final_receivers = []
    for received in receivers:
        if (not list(received.keys())[0] in send_addrs):
            final_receivers.append(received)

    return final_receivers


async def blk_searcher():
    global last_block
    newblock = await w.query('getblockcount', [])
    if newblock > last_block:
        try:
            users = await q.get_addr_uid_dict()
            for blockheight in range(last_block+1, newblock+1):
                last_block = blockheight
                blockhash = await w.query('getblockhash', [blockheight])
                await asyncio.sleep(0.05) # Protections to guard against reusing the bind address
                blockdata = await w.query('getblock', [blockhash])
                if isinstance(blockdata, dict):
                    for txid in blockdata['tx']:
                        for received in await check_tx(txid):
                            addr = list(received.keys())[0]
                            uid = users[addr]
                            if await q.register_deposit(txid, received[addr], uid):
                                logging.info('Processed deposit with TXID: %s for %s', txid, uid)
                elif blockdata == 3:
                    pass # Don't render the reuse address error as an exception
                else:
                    logging.error('Bad signal in GRC client: %s', blockdata)
        except Exception as E:
            logging.exception('Block searcher ran into an error: %s', E)


async def scavenge():
    global last_block
    with open(g.LST_BLK, 'r') as last_block_file:
        last_block = int(last_block_file.read().replace('\n', ''))
        logging.info('Starting blockchain scavenger at height: {}.'.format(last_block))
    while True:
        try:
            await blk_searcher()
            with open(g.LST_BLK, 'w') as last_block_file:
                last_block_file.write(str(last_block))
            await asyncio.sleep(g.SCAV_SLP)
        except KeyboardInterrupt:
            return


loop = asyncio.get_event_loop()
task = asyncio.ensure_future(scavenge())
loop.run_until_complete(task)
loop.close()
