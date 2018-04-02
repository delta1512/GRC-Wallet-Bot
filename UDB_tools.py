import subprocess as sp
from user import usr
import sqlite3

def create_db(dbdir):
    db = sqlite3.connect(dbdir)
    c = db.cursor()
    c.execute('''CREATE TABLE udb (
    userID text,
    address text,
    last_active int,
    balance float,
    donations float,
    lastTX_amt float,
    lastTX_time int,
    lastTX_txid text
    )''')
    db.commit()
    db.close()

def read_db(dbdir):
    global UDB
    db = sqlite3.connect(dbdir)
    c = db.cursor()
    c.execute('SELECT * FROM udb')
    for record in c.fetchall():
        UDB[record[0]] = usr(record[0],
        address=record[1],
        last_faucet=record[2],
        balance=record[3],
        donations=record[4],
        lastTX=[record[5], record[6], record[7]])
    db.close()

def save_db(dbdir):
    create_db(g.TMP_DIR)
    db = sqlite3.connect(g.TMP_DIR)
    c = db.cursor()
    for u in UDB:
        c.execute('INSERT INTO udb VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
        UDB[u].usrID, UDB[u].address, UDB[u].last_faucet, UDB[u].balance, UDB[u].donations,
        UDB[u].active_tx[0], UDB[u].active_tx[1], UDB[u].active_tx[2]))
    db.commit()
    db.close()
    sp.call('mv {} {}'.format(g.TMP_DIR, dbdir), shell=True)
