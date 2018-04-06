from user import usr
import grcconf as g
import aiomysql
import asyncio

async def check_db():
    try:
        conn = await aiomysql.connect(host=g.sql_db_host, port=3306, user=g.sql_db_usr,
                                    password=g.sql_db_pass, db='mysql')
        c = await conn.cursor()
        await c.execute('SELECT * FROM {}'.format(g.udb_name))
    except:
        return 1
    conn.close()
    return 0

async def read_db():
    tmpdb = {}
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr,
                                password=g.sql_db_pass, db='mysql')
    c = await db.cursor()
    await c.execute('SELECT * FROM {}'.format(g.udb_name))
    for record in await c.fetchall():
        tmpdb[record[0]] = usr(record[0],
        address=record[1],
        last_faucet=record[2],
        balance=record[3],
        donations=record[4],
        lastTX=[record[5], record[6], record[7]])
    db.close()
    return tmpdb

async def save_db(udb):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr,
                                password=g.sql_db_pass, db='mysql')
    c = await db.cursor()
    for u in udb:
        await c.execute('SELECT * FROM {} WHERE uid=%s'.format(g.udb_name), (u,))
        if len(await c.fetchall()) > 0:
            await c.execute('''UPDATE {} SET
                            last_faucet=%s,
                            balance=%s,
                            donations=%s,
                            lastTX_amt=%s,
                            lastTX_time=%s,
                            lastTX_txid=%s;
                            WHERE uid=%s'''.format(g.udb_name),
                (udb[u].last_faucet, udb[u].balance, udb[u].donations,
                udb[u].active_tx[0], udb[u].active_tx[1], udb[u].active_tx[2], udb[u].usrID))
        else:
            await c.execute('INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'.format(g.udb_name), (
            udb[u].usrID, udb[u].address, udb[u].last_faucet, udb[u].balance, udb[u].donations,
            udb[u].active_tx[0], udb[u].active_tx[1], udb[u].active_tx[2]))
    await db.commit()
    db.close()
