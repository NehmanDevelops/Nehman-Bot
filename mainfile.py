from typing import Final
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')

# Event: When a message is received
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Allow commands to be processed
    await bot.process_commands(message)

    # Import and use get_response function from responses.py
    from responses import get_response
    user_message = message.content

    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    is_private = user_message.startswith('?')
    if is_private:
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)

bot.remove_command("help")


# Load the cogs
async def main():
    # Import the EventsCog and ModerationCog from events.py
    from events import EventsCog, ModerationCog, StatsCog, PollCog, TicTacToe, MusicCog
    from help import HelpCog

    await bot.add_cog(HelpCog(bot))
    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(TicTacToe(bot))
    await bot.add_cog(PollCog(bot))
    await bot.add_cog(StatsCog(bot))
    await bot.add_cog(EventsCog(bot))
    await bot.add_cog(ModerationCog(bot))  # ModerationCog is in the same file as EventsCog
    await bot.start(TOKEN)
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
