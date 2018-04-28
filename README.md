# GRC-Wallet-Bot

Discord bot by [Delta](https://github.com/delta1512) for the [Gridcoin Discord chat](https://discord.me/page/gridcoin).

This bot aims to be a third part wallet service for the Gridcoin cryptocurrency and allows people to deposit, store, withdraw, donate and get Gridcoins. The bot contains its own faucet to encourage new users and provides an easy and interactive interface for generosity and donating.

## Requirements

* Python 3.6

* A remote MYSQL database (such as [MariaDB](https://mariadb.com/))

* An active Gridcoin Client

* Filled out configuration file

* Two files in the same directory as main.py called **blist** and **priv_blist** (these are your total and private message blacklists)

* A record in the DB with the userID `'FAUCET'` and a preset GRC address

## Database Setup

The following is an example SQL script for creating a table that is compatible with the bot:
```
CREATE TABLE `YOURDB`.`YOURTABLE` (
  `uid` CHAR(18) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NOT NULL,
  `address` CHAR(34) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NOT NULL,
  `last_faucet` BIGINT(20) NULL DEFAULT NULL,
  `balance` DOUBLE NULL DEFAULT NULL,
  `donations` DOUBLE NULL DEFAULT NULL,
  `lastTX_amt` DOUBLE NULL DEFAULT NULL,
  `lastTX_time` BIGINT(20) NULL DEFAULT NULL,
  `lastTX_txid` CHAR(70) CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci' NULL DEFAULT NULL,
  PRIMARY KEY (`uid`, `address`));
```

### Feature ideas:

These are just ideas, not all of them may be implemented in the future. Any suggestions are welcome.

- [ ] Interactive donation presentation

- [ ] Site or command to view donation ranks

- [x] Faucet

- [x] Random donations

- [ ] Dice and other assorted features

- [ ] Rain/soak

- [ ] Help topics such as getting started with GRC

- [ ] Block exploring features

- [ ] BOINC stats

- [X] Private messaging support

- [X] FAQ interface

- [ ] Static withdraw address option

- [ ] %time function to show eligibility of %faucet, %withdraw and %donate

- [ ] Random facts/FAQ article

### FAQ Ideas:

- [ ] Linux compilation guide

- [ ] Third-party walets

- [ ] Exchanges

- [ ] Faucets

- [ ] History of Gridcoin
