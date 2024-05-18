from discord.ext import commands
from helpers import config_helper


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='about')
    async def info(self, ctx: commands.Context):
        await ctx.send(f"{str(config_helper.read_info()['about'])}\n{str(config_helper.read_info()['about2'])}")

    @commands.command(name='version')
    async def version(self, ctx: commands.Context):
        await ctx.send(f"**Version:** {str(config_helper.read_info()['ver'])}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
