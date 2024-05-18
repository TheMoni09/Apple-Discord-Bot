from discord.ext import commands
from utils import YTDLSource
from typing import NoReturn


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.queue: list[list] = list()
        self.playing: str = str()

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
    async def play(self, ctx: commands.Context, url: str) -> None:
        ytdl = YTDLSource.YTDLSource
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            async with ctx.typing():
                title: str = await ytdl.get_title(url)
                await self.add_to_queue(url, title)
                await ctx.send(f"**Added to Queue -** {title}")
                return

        async with ctx.typing():
            player: YTDLSource = await ytdl.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            self.playing = player.title
            await ctx.send(f'**Now playing:** {player.title}')

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context) -> None:
        ctx.voice_client.pause()
        await ctx.send("**Pausing Playback**")

    @commands.command(name="resume")
    async def resume(self, ctx: commands.Context) -> None:
        if not ctx.voice_client.is_paused():
            await ctx.send("**ERROR:** I'm not paused!")
            raise commands.CommandError("Bot is not paused!")

        ctx.voice_client.resume()
        await ctx.send("**Resuming Playback**")

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context) -> None:
        ctx.voice_client.stop()
        await ctx.send("**Stopping Playback**")

    @commands.command(name="skip")
    async def skip(self, ctx: commands.Context) -> None:
        if await self.is_queue_empty():
            await ctx.send("**ERROR:** The queue is empty!")
            return

        next_song = await self.get_next_in_queue()
        ctx.voice_client.stop()
        await ctx.send(f"**Skipping - ** {self.playing}")
        await self.play(ctx, url=next_song[0])

    @play.before_invoke
    async def ensure_voice(self, ctx: commands.Context) -> NoReturn:
        if ctx.guild.voice_client is None and not ctx.author.voice:
            await ctx.send(f'**ERROR:** You aren\'t connected to a voice channel!')
            raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.guild.voice_client is not None and ctx.guild.voice_client.channel != ctx.author.voice.channel:
            await ctx.send(f'**ERROR:** You aren\'t connected to the same voice channel as me!')
            raise commands.CommandError("Author not connected to the same voice channel as bot.")
        elif ctx.guild.voice_client is None:
            await ctx.author.voice.channel.connect()

    @stop.before_invoke
    @pause.before_invoke
    @skip.before_invoke
    async def assure_music(self, ctx: commands.Context) -> NoReturn:
        if ctx.guild.voice_client is None:
            await ctx.send("**ERROR:** I'm not connected to a voice channel!")
            raise commands.CommandError("Author is not connected to a voice channel!")
        elif not ctx.voice_client.is_playing():
            await ctx.send("**ERROR:** I'm not playing anything!")
            raise commands.CommandError("Bot is not playing anything!")

    async def add_to_queue(self, url: str, title: str) -> None:
        self.queue.append(list({url, title}))

    async def remove_from_queue(self, index: int) -> None:
        self.queue.pop(index)

    async def get_next_in_queue(self) -> list:
        return self.queue.pop(0)

    async def get_queue(self) -> list:
        return self.queue

    async def is_queue_empty(self) -> bool:
        return not self.queue


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
