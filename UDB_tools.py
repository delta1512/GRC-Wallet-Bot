from user import usr
import grcconf as g
import aiomysql
import asyncio

async def check_uid(uid):
    conn = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await conn.cursor()
    await c.execute('SELECT uid FROM {}.udb WHERE uid=%s'.format(g.udb_name), (uid))
    response = c.fetchall()
    conn.close()
    return response

async def check_db():
    try:
        asyncio.ensure_future(await check_uid('FAUCET')).result()
    except:
        return 1
    return 0

async def read_db():
    tmpdb = {}
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT * FROM {}.udb'.format(g.udb_name))
    for record in await c.fetchall():
        tmpdb[record[0]] = usr(record[0],
        address=record[1],
        last_faucet=record[2],
        balance=record[3],
        donations=record[4],
        lastTX=[record[5], record[6], record[7]])
    db.close()
    return tmpdb

async def check_deposit(txidq):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT count(txid) FROM {}.deposits WHERE txid=%s'.format(g.udb_name), txidq)
    result = await c.fetchone()
    db.close()
    return result[0]

async def register_deposit(txid, amount, uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('INSERT INTO {}.deposits VALUES (%s, %s, %s)'.format(g.udb_name),
                    (txid, amount, uid))
    await db.commit()
    db.close()

async def save_db(udb):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    for u in udb:
        if len(asyncio.ensure_future(await check_uid(u)).result()) > 0:
            await c.execute('''UPDATE {}.udb SET
                last_faucet=%s,
                balance=%s,
                donations=%s,
                lastTX_amt=%s,
                lastTX_time=%s,
                lastTX_txid=%s
                WHERE uid=%s;'''.format(g.udb_name), (udb[u].last_faucet,
                udb[u].balance, udb[u].donations, udb[u].active_tx[0],
                udb[u].active_tx[1], udb[u].active_tx[2], u))
        else:
            await c.execute('INSERT INTO {}.udb VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'.format(g.udb_name), (
            u, udb[u].address, udb[u].last_faucet, udb[u].balance, udb[u].donations,
            udb[u].active_tx[0], udb[u].active_tx[1], udb[u].active_tx[2]))
    await db.commit()
    db.close()
