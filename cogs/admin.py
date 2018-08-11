from discord.ext import commands
import extras


class AdminCog:
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def blist(self, ctx, *args):  # TODO: Add private message check -jorkermc
        if len(args) > 0:
            await ctx.send(await extras.blist_iface(args, self.blacklister))
        else:
            await ctx.send(blacklister.get_blisted())

    @commands.command(name='bin')
    async def _bin(self, ctx, *args):  # Not overriding built-in function bin
        await ctx.send(await extras.burn_coins(args))

    @commands.command()
    async def stat(self, ctx, *args):
        if len(args) == 0:
            user_obj = await q.get_user(ctx.author.id)
        else:
            user_obj = await q.get_user(args[0])
            if user_obj is None: return;
        await ctx.send(extras.user_stats(user_obj, client))


def setup(bot):
    bot.add_cog(AdminCog(bot))
