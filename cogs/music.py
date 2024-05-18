from discord.ext import commands
from utils import YTDLSource


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name='join')
    async def join(self, ctx: commands.Context) -> None:
        if ctx.guild.voice_client is not None:
            await ctx.send(f'**ERROR:** I\'m already connected to a voice channel!')
        elif not ctx.author.voice:
            await ctx.send(f'**ERROR:** You aren\'t connected to a voice channel!')
        elif ctx.author.voice:
            await ctx.send(f'**Joining channel:** {ctx.author.voice.channel.mention}')
            await ctx.author.voice.channel.connect()

    @commands.command(name='play')
    async def yt(self, ctx, *, url):
        async with ctx.typing():
            ytdl = YTDLSource.YTDLSource
            player = await ytdl.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'**Now playing:** {player.title}')


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
