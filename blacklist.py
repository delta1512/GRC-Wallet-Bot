import logging

import queries as q

class Blacklister:
    blacklist = {} # {user ID : private channel ban}

    def __init__(self, blacklisted):
        self.blacklist = blacklisted

    def is_banned(self, user, ispriv):
        try:
            priv_ban = self.blacklist[user]
            return (not priv_ban) or (priv_ban and ispriv)
        except KeyError:
            return False

    def get_blisted(self):
        return '```UID | Private ban\n{}```'.format(''.join(['{} | {}\n'.format(u, self.blacklist[u]) for u in self.blacklist]))

    async def new_blist(self, user, priv_ban):
        logging.info('New ban made for UID: %s', user)
        self.blacklist[user] = priv_ban
        await q.commit_ban(user, priv_ban)

    async def remove_blist(self, user):
        logging.info('Removed ban for UID: %s', user)
        if user in self.blacklist:
            await q.commit_unban(user)
            self.blacklist.pop(user)
