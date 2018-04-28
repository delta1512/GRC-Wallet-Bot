import grcconf as g

class blist:
    blacklist = {}

    def __init__(self):
        self.read_blists()

    def is_banned(self, user, ispriv):
        try:
            priv_ban = self.blacklist[user]
            return (not priv_ban) or (priv_ban and ispriv)
        except KeyError:
            return False

    def get_blisted(self):
        return '```UID | Private ban\n{}```'.format(''.join(['{} | {}\n'.format(u, self.blacklist[u]) for u in self.blacklist]))

    def new_blist(self, user, priv_ban):
        self.blacklist[user] = priv_ban
        if priv_ban:
            f = 'priv_blist'
        else:
            f = 'blist'
        with open(f, 'a') as b:
            b.write(user + '\n')

    def remove_blist(self, user):
        if user in self.blacklist:
            if self.blacklist.pop(user):
                with open('priv_blist', 'w') as b:
                    for u in self.blacklist:
                        if self.blacklist[u] is True:
                            b.write(u + '\n')
            else:
                with open('blist', 'w') as b:
                    for u in self.blacklist:
                        if self.blacklist[u] is False:
                            b.write(u + '\n')

    def read_blists(self):
        with open('blist', 'r') as b:
            for ln in b.read().split():
                self.blacklist[ln.replace('\n', '')] = False
        with open('priv_blist', 'r') as b:
            for ln in b.read().split():
                self.blacklist[ln.replace('\n', '')] = True
