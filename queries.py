import aiomysql

from user import User
import grcconf as g
import wallet as w

async def uid_exists(uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT uid FROM {}.udb WHERE uid=%s'.format(g.db_name), (uid))
    response = await c.fetchall()
    db.close()
    return len(response) > 0


async def get_user(uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT * FROM {}.udb WHERE uid=%s'.format(g.db_name), (uid))
    result = await c.fetchall()
    db.close()
    if len(result) == 0: return None;
    result = result[0]
    return User(uid, address=result[1], last_faucet=result[2], balance=result[3],
                donations=result[4], lastTX=[result[5], result[6], result[7]])


async def get_bal(uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT balance, address FROM {}.udb WHERE uid=%s'.format(g.db_name), (uid))
    result = await c.fetchone()
    db.close()
    return result


async def register_deposit(txid, amount, uid):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT count(txid) FROM {}.deposits WHERE txid=%s AND uid=%s'.format(g.db_name), (txid, uid))
    unique = (await c.fetchone())[0] == 0
    if unique:
        await c.execute('INSERT INTO {}.deposits VALUES (%s, %s, %s);'.format(g.db_name),
                        (txid, amount, uid))
        await c.execute('UPDATE {}.udb SET balance=%s WHERE uid=%s;'.format(g.db_name),
                        ((await get_bal(uid))[0] + amount, uid))
        await db.commit()
    db.close()
    return unique


async def save_user(user_objs):
    if not isinstance(user_objs, list): user_objs = [user_objs];
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
            WHERE uid=%s;'''.format(g.db_name),
            (user.last_faucet, user.balance, user.donations,
            user.active_tx[0], user.active_tx[1], user.active_tx[2],
            user.usrID))
    await db.commit()
    db.close()


async def new_user(uid, address):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('INSERT INTO {}.udb VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'.format(g.db_name),
                    (uid, address, 0, 0, 0, 0, 0, ''))
    await db.commit()
    db.close()


async def get_addr_uid_dict():
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT address, uid FROM {}.udb'.format(g.db_name))
    user_data = {}
    for tup in await c.fetchall():
        user_data[tup[0]] = tup[1]
    db.close()
    return user_data


async def apply_balance_changes(user_vals):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    for uid in user_vals:
        await c.execute('UPDATE {}.udb SET balance = balance + %s WHERE uid=%s;'.format(g.db_name),
                        (user_vals[uid], uid))
    await db.commit()
    db.close()


async def get_blacklisted():
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT uid, channel FROM {}.blacklist'.format(g.db_name))
    blacklisted = {}
    for tup in await c.fetchall():
        channel = int.from_bytes(tup[1], 'big')
        blacklisted[tup[0]] = True if channel == 1 else False
    db.close()
    return blacklisted

async def commit_ban(user, channel):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('INSERT INTO {}.blacklist VALUES (%s, %s);'.format(g.db_name), (user, channel))
    await db.commit()
    db.close()


async def commit_unban(user):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('DELETE FROM {}.blacklist WHERE uid=%s;'.format(g.db_name), (user))
    await db.commit()
    db.close()


async def add_to_fee_pool(fee):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT amount FROM {}.admin_claims WHERE txid="PENDING"'.format(g.db_name))
    current_owed = (await c.fetchone())[0] + fee
    await c.execute('UPDATE {}.admin_claims SET amount = %s WHERE txid="PENDING";'.format(g.db_name), (current_owed))
    if current_owed > g.FEE_WDR_THRESH:
        txid = await w.tx(g.admin_wallet, current_owed)
        if isinstance(txid, str):
            await c.execute('UPDATE {}.admin_claims SET txid = %s WHERE txid="PENDING";'.format(g.db_name), (txid))
            await c.execute('INSERT INTO {}.admin_claims VALUES (%s, %s);'.format(g.db_name), ('PENDING', 0))
    await db.commit()
    db.close()


# Highly redundant but efficient faucet operation
async def faucet_operations(uid, amount, ctime):
    db = await aiomysql.connect(host=g.sql_db_host, user=g.sql_db_usr, password=g.sql_db_pass)
    c = await db.cursor()
    await c.execute('SELECT * FROM {}.udb WHERE uid=%s'.format(g.db_name), (uid))
    result = (await c.fetchall())[0]
    user_obj = User(uid, address=result[1], last_faucet=result[2], balance=result[3],
                donations=result[4], lastTX=[result[5], result[6], result[7]])
    if not user_obj.can_faucet():
        db.close()
        return user_obj, 1

    await c.execute('SELECT balance FROM {}.udb WHERE uid=%s'.format(g.db_name), ('FAUCET'))
    fct_bal = (await c.fetchone())[0]
    if fct_bal < g.FCT_MAX:
        db.close()
        return None, 2

    user_vals = {'FAUCET' : -amount, uid : amount}
    for uid in user_vals:
        await c.execute('UPDATE {}.udb SET balance = balance + %s WHERE uid=%s;'.format(g.db_name),
                        (user_vals[uid], uid))
    await c.execute('UPDATE {}.udb SET last_faucet = %s WHERE uid=%s'.format(g.db_name), (ctime, uid))
    await db.commit()
    db.close()
    user_obj.balance += amount
    return user_obj, 0
