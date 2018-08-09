from discord.ext import commands
import commands as bot_com


class AdminCog:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def blist(self, ctx, *args):  # TODO: Add private message check -jorkermc
        if len(args) > 0:
            await ctx.send(bot_com.blist_iface(args, self.blacklister))
        else:
            await ctx.send(self.blacklister.get_blisted())

    @commands.command(name='bin')
    async def _bin(self, ctx, *args):  # Not overriding built-in function bin
        await ctx.send(bot_com.burn_coins(args, UDB))

    @commands.command()
    async def stat(self, ctx, *args):
        if len(args) > 0:
            await ctx.send(bot_com.user_stats(args[0], UDB.get(args[0], None), user_time, self.bot))


def setup(bot):
    bot.add_cog(AdminCog(bot))