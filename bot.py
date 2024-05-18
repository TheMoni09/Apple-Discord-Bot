import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from helpers import config_helper
import asyncio

load_dotenv()
TOKEN: str = os.getenv('USER_TOKEN')
config: dict = config_helper.read_config()


class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=discord.Color.blurple(), description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)


client: commands.Bot = commands.Bot(
                                    command_prefix=config['command_prefix'],
                                    intents=discord.Intents.all(),
                                    help_command=MyHelpCommand()
                                   )


@client.event
async def on_ready():
    print(f'Logged in as {client.user} inside {len(client.guilds)} guilds!')


async def empty_music():
    print("Emptying music!")
    for music in os.listdir('./music'):
        os.remove(f'./music/{music}')


async def load() -> None:
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main() -> None:
    await load()
    await empty_music()
    await client.start(TOKEN)


def run_bot() -> None:
    asyncio.run(main())
