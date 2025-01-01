from discord.app_commands import command
from discord.ext import commands
from collections import defaultdict
import discord
import yt_dlp as youtube_dl
from datetime import timedelta
import asyncio

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        """
        Sends a message listing all the features of the bot.
        """
        embed = discord.Embed(
            title="NehmanBot Help hehe",
            description="Here are all the features and commands NehmanBot supports! 🦁🦁🦁",
            color=discord.Color.blue()
        )

        # Adding feature descriptions
        embed.add_field(
            name="🎉 Events",
            value=(
                "`on_guild_join`: Sends a welcome message when the bot joins a server.\n"
                "`on_member_join`: Welcomes new members to the server."
            ),
            inline=False
        )

        embed.add_field(
            name="🛠 Moderation Commands",
            value=(
                "`!kick <@user> [reason]`: Kicks a user from the server.\n"
                "`!ban <@user> [reason]`: Bans a user from the server.\n"
                "`!purge <amount>`: Deletes the specified number of messages."
                "`!timeout <amount>`: Times out a user."
                "'!mute <amount>: Mutes a user."
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Statistics Commands",
            value=(
                "`!members`: Shows the total number of members in the server.\n"
                "`!activemembers`: Shows the number of active (non-offline) members."
            ),
            inline=False
        )

        embed.add_field(
            name="📋 Poll Commands",
            value=(
                "`!poll <question> | <option1>, <option2>, ...`: Creates a poll for users to vote on."
            ),
            inline=False
        )

        embed.add_field(
            name="🎵 Music Commands",
            value=(
                "`!play <YouTube URL>`: Plays music from the provided YouTube URL.\n"
                "`!pause`: Pauses the currently playing music.\n"
                "`!resume`: Resumes paused music.\n"
                "`!stop`: Stops the music and disconnects the bot."
            ),
            inline=False
        )

        embed.add_field(
            name="🎮 Games",
            value=(
                "`!tictactoe <@opponent>`: Start a game of Tic-Tac-Toe with an opponent.\n"
                "`!move <position>`: Make a move in an ongoing Tic-Tac-Toe game."
                "'!rolldice': Rolls a dice between 1-6"
            ),
            inline=False
        )

        # Add an image of a lion
        embed.set_image(url="https://media.istockphoto.com/id/458017717/vector/king-lion-aslan.jpg?s=612x612&w=0&k=20&c=yKt4ae9kvAdf3JsMsZqb4vZ43sch49ky5rEQ_n8X7-Q=")

        embed.set_footer(text="Use !help <command> for more details on a specific command.")

        # Send the help message
        await ctx.send(embed=embed)

