import logging

import wallet as w
import queries as q

# Set up logging functionality
handler = [RotatingFileHandler(g.log_dir+'deposits.log', maxBytes=10**7, backupCount=3)]
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    datefmt='%d/%m %T',
                    level=logging.INFO,
                    handlers=handler)

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
            logging.error('Bad signal in GRC client: %s', tx)
    except RuntimeError as E:
        logging.error('check_tx ran into an unhandled error: %s', E)
    except KeyError:
        pass
    return recv_addrs, send_addrs, recv_vals

async def blk_searcher():
    newblock = await w.query('getblockcount', [])
    if newblock > LAST_BLK:
        try:
            for blockheight in range(LAST_BLK+1, newblock+1):
                blockhash = await w.query('getblockhash', [blockheight])
                await asyncio.sleep(0.05) # Protections to guard against reusing the bind address
                blockdata = await w.query('getblock', [blockhash])
                if isinstance(blockdata, dict):
                    LAST_BLK = blockheight
                    for txid in blockdata['tx']:
                        if await q.deposit_exists(txid): continue;
                        recv_addrs, send_addrs, vals = await check_tx(txid)
                        if len(recv_addrs) > 0:
                            users = await q.get_addr_uid_dict()
                            for uaddr in users:
                                found = False
                                for i, addr in enumerate(recv_addrs):
                                    if uaddr == addr:
                                        # Check whether change address
                                        found = not addr in send_addrs
                                        index = i
                                        if found:
                                            break
                                if found:
                                    uid = users[uaddr]
                                    await db.register_deposit(txid, vals[index], uid)
                                    logging.info('Processed deposit with TXID: %s for %s', txid, uid)
                                    try: # In event of change address
                                        send_addrs.pop(send_addrs.index(recv_addrs.pop(index)))
                                    except ValueError:
                                        pass
                                    vals.pop(index)
                elif blockdata == 3:
                    pass # Don't render the reuse address error as an exception
                else:
                    logging.error('Bad signal in GRC client: %s', blockdata)
        except Exception as E:
            logging.exception('Block searcher ran into an error: %s', E)
