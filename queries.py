from user import User
import grcconf as g
import aiomysql


async def uid_exists(uid):
    conn = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await conn.cursor()
    await c.execute('SELECT uid FROM {}.udb WHERE uid=%s'.format(g.udb_name), (uid))
    response = await c.fetchall()
    conn.close()
    return response > 0


async def get_user(uid):
    conn = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await conn.cursor()
    await c.execute('SELECT * FROM {}.udb WHERE uid=%s'.format(g.udb_name), (uid))
    result = await c.fetchone()
    db.close()
    if len(result) == 0: return None;
    return User(uid, address=result[1], last_faucet=result[2], balance=result[3],
                donations=result[4], lastTX=[result[5], result[6], result[7]])


async def deposit_exists(txidq):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT count(txid) FROM {}.deposits WHERE txid=%s'.format(g.udb_name), txidq)
    result = await c.fetchone()
    db.close()
    return result[0] > 0


async def get_bal(uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT balance, address FROM {}.udb WHERE uid=%s'.format(g.udb_name), (uid))
    result = await c.fetchone()
    db.close()
    return result[0]


async def register_deposit(txid, amount, uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('INSERT INTO {}.deposits VALUES (%s, %s, %s);'.format(g.udb_name),
                    (txid, amount, uid))
    await c.execute('UPDATE {}.udb SET balance=%s WHERE uid=%s;'.format(g.udb_name),
                    (await get_bal(uid) + amount, uid))
    await db.commit()
    db.close()


async def save_user(user_objs):
    if not issinstance(user_objs, list): user_objs = [user_objs];
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    for user in user_objs:
        await c.execute('''UPDATE {}.udb SET
            last_faucet=%s,
            balance=%s,
            donations=%s,
            lastTX_amt=%s,
            lastTX_time=%s,
            lastTX_txid=%s
            WHERE uid=%s;'''.format(g.udb_name),
            (user.last_faucet, user.balance, user.donations,
            user.active_tx[0], user.active_tx[1], user.active_tx[2],
            user.userID))
    await db.commit()
    db.close()


async def new_user(uid, address):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('INSERT INTO {}.udb VALUES (%s, %s, %s, %s, %s, %s, %s)'.format(g.udb_name),
                    (uid, address, 0, 0, 0, 0, 0))
    await db.commit()
    db.close()


async def get_addr_uid_dict():
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT address, uid FROM {}.udb'.format(g.udb_name))
    user_data = {}
    for tup in await c.fetchall():
        user_data[tup[0]] = tup[1]
    db.close()
    return user_data


async def apply_balance_changes(user_vals):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    for uid in user_vals:
        await c.execute('UPDATE {}.udb SET balance = balance + %s WHERE uid=%s'.format(g.udb_name),
                        (user_vals[uid], uid))
    await db.commit()
    db.close()
