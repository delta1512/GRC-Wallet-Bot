from discord.ext import commands


class NotInUDB(commands.CommandError):
    pass

class TooNew(commands.CommandError):
    pass

class LimChannel(commands.CommandError):
    pass
