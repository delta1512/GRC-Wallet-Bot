class Commands:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Commands(bot))
