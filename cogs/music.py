import asyncio
from functools import partial

from discord.ext import commands
from utils import YTDLSource
from typing import NoReturn


class Music(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.queue: list[tuple[str, int]] = []
        self.playing: dict[int, str] = {guild.id: "" for guild in bot.guilds}

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
                await self.add_to_queue(url, ctx.message.guild.id)
                await ctx.send(f"**Added to Queue -** {url}")
                return

        async with ctx.typing():
            player: YTDLSource = await ytdl.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=partial(self.play_next, ctx))
            await self.set_playing(ctx.guild.id, player.title)
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
    async def skip(self, ctx: commands.Context) -> NoReturn:
        if await self.is_queue_empty(ctx.guild.id):
            await ctx.send("**ERROR:** The queue is empty!")
            raise commands.CommandError("Queue is empty!")

        next_song = await self.get_next_in_queue(ctx.guild.id)
        ctx.voice_client.stop()
        await ctx.send(f"**Skipping - ** {await self.get_playing(ctx.guild.id)}")
        await self.play(ctx, url=next_song[0])

    @commands.command(name="playing")
    async def playing(self, ctx: commands.Context) -> None:
        await ctx.send(f"**Playing:** {await self.get_playing(ctx.guild.id)}")

    @commands.group(name="queue")
    async def queue(self, ctx: commands.Context) -> None:
        pass

    @queue.command(name="list")
    async def list_queue(self, ctx: commands.Context) -> None:
        queue: list = await self.get_queue(ctx.guild.id)
        async with ctx.typing():
            i: int = 0
            for song in queue:
                print(f"Listing Song - URL: {song[0]} Guild Id: {song[1]}")
                await ctx.send(f"**Position:** {i+1} | **Song:** {song[0]}")
                i += 1

    @queue.command(name="remove")
    async def remove_from_queue_command(self, ctx: commands.Context, url: str) -> NoReturn:
        if not await self.is_in_queue(url, ctx.guild.id):
            await ctx.send("**ERROR:** The song URL you specified is not in the queue!")
            raise commands.CommandError("The specified song is not in the queue!")

        await ctx.send(f"**Removed from queue:** {await self.remove_from_queue(url, ctx.guild.id)}")

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

    @list_queue.before_invoke
    @remove_from_queue_command.before_invoke
    async def assure_queue(self, ctx: commands.Context) -> NoReturn:
        if ctx.guild.voice_client is None:
            await ctx.send("**ERROR:** I'm not connected to a voice channel!")
            raise commands.CommandError("Author is not connected to a voice channel!")
        elif await self.is_queue_empty(ctx.guild.id):
            await ctx.send("**ERROR:** The queue is empty!")
            raise commands.CommandError("Queue is empty!")

    def play_next(self, ctx: commands.Context, error=None) -> None:
        if error:
            print(f"Error occurred during playback: {error}")

        if self.queue:
            next_song: tuple[str, int] = asyncio.run_coroutine_threadsafe(self.get_next_in_queue(ctx.guild.id),
                                                                          self.bot.loop).result()
            print(f"Next Song - URL: {next_song[0]} Guild Id: {next_song[1]}")
            coro = self.play(ctx, url=next_song[0])
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        else:
            asyncio.run(self.set_playing(ctx.guild.id))

    async def add_to_queue(self, url: str, guild: int) -> None:
        self.queue.append((url, guild))

    async def remove_from_queue(self, url: str, guild: int) -> str:
        for song in self.queue:
            if song[1] == guild and song[0] == url:
                self.queue.remove(song)
                return song[0]

    async def is_in_queue(self, url: str, guild: int) -> bool:
        for song in self.queue:
            if guild == song[1] and url == song[0]:
                return True
        return False

    async def get_next_in_queue(self, guild: int) -> tuple[str, int]:
        for song in self.queue:
            if guild in song:
                self.queue.remove(song)
                return song

    async def get_queue(self, guild: int) -> list:
        return [song for song in self.queue if song[1] == guild]

    async def is_queue_empty(self, guild: int) -> bool:
        return not any(song[1] == guild for song in self.queue)

    async def set_playing(self, guild: int, title: str = "") -> None:
        self.playing[guild] = title

    async def get_playing(self, guild: int) -> str:
        return self.playing.get(guild, "")


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
