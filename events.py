from discord.app_commands import command
from discord.ext import commands
from collections import defaultdict
import discord
import yt_dlp as youtube_dl
from datetime import timedelta
import asyncio

class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_activity = defaultdict(int)  # Tracks activity per channel

    # Helper function to get the most active channel
    def get_most_active_channel(self, guild: discord.Guild):
        if not self.channel_activity:
            return None  # No activity recorded yet
        most_active_channel_id = max(self.channel_activity, key=self.channel_activity.get)
        return guild.get_channel(most_active_channel_id)

    # Event: When the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user}!')
        print(f"Command prefix is: {self.bot.command_prefix}")
        print("Loaded cogs:", list(self.bot.cogs.keys()))  # Debugging: Show loaded cogs

    # Event: When a member joins
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        most_active_channel = self.get_most_active_channel(guild)

        # Fallback to system channel or a channel named "general"
        if most_active_channel is None:
            most_active_channel = guild.system_channel or discord.utils.get(guild.text_channels, name="general")

        if most_active_channel:
            welcome_message = f"Welcome to the server, {member.mention}!"
            if welcome_message.strip():  # Ensure the message is not empty
                await most_active_channel.send(welcome_message)
                print(f"Welcome message sent to {most_active_channel.name}")  # Debugging
        else:
            print("No channel found to send the welcome message.")

    # Event: When the bot joins a new server
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Triggered when the bot joins a new guild (server).
        Sends a welcome message in the system channel or the first available text channel.
        """
        welcome_message = "Hi, I'm NehmanBot! Use `!help` to figure out all my commands. 🦁"

        # Try to send the message in the system channel
        try:
            if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
                await guild.system_channel.send(welcome_message)
                print(f"Welcome message sent in system channel of guild: {guild.name}")
            else:
                # If no system channel, find the first available channel
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(welcome_message)
                        print(f"Welcome message sent in {channel.name} of guild: {guild.name}")
                        break
                else:
                    print(f"No suitable channel found to send welcome message in guild: {guild.name}")
        except Exception as e:
            print(f"Error sending welcome message in guild: {guild.name}. Error: {e}")



class ModerationCog(commands.Cog):
    """Cog for moderation commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kick a user from the server."""
        if member is None:
            await ctx.send("You must mention a user to kick. Example: `!kick @user reason`")
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.send("I cannot kick this user as their role is equal to or higher than mine.")
            return

        try:
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} has been kicked. Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to kick this user.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to kick the user. Error: {e}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Ban a user from the server."""
        if member is None:
            await ctx.send("You must mention a user to ban. Example: `!ban @user reason`")
            return

        if ctx.guild.me.top_role <= member.top_role:
            await ctx.send("I cannot ban this user as their role is equal to or higher than mine.")
            return

        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} has been banned. Reason: {reason}")
        except discord.Forbidden:
            await ctx.send("I do not have permission to ban this user.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to ban the user. Error: {e}")

    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge_messages(self, ctx, amount: int = None, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Purges messages."""
        if amount is None:
            await ctx.send("Specify the number of messages.")
            return

        if amount <= 0:
            await ctx.send("Please specify a value greater than 0.")
            return

        def check_message(msg):
            return not member or msg.author == member

        deleted = await ctx.channel.purge(limit=amount, check=check_message, reason=reason)

        await ctx.send(f"Purged {len(deleted)} messages.", delete_after=3)


class StatsCog(commands.Cog):
    """  A cog that provides server statistics and member information. """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="members")
    async def members(self, ctx):
        """
        Responds with the number of server members.
        """
        guild = ctx.guild  # Get the guild (server) the command was invoked in

        if not guild:
            await ctx.send("This command must be used in a server.")
            return

        # Count the total number of members in the server
        total_members = len(guild.members)

        # Send the count as a message
        await ctx.send(f"There are {total_members} members.")

    @commands.command(name="activemembers")
    async def activemembers(self, ctx):
        """
        Responds with the number of active users.
        """
        guild = ctx.guild

        if not guild:
            await ctx.send("This command must be used in a server.")
            return

        # Filter members who are active (not offline and not a bot)
        active_members = [member for member in guild.members if
                          member.status != discord.Status.offline and not member.bot]

        # Count the active members
        active_count = len(active_members)

        # Send the count as a message
        await ctx.send(f"There are {active_count} active members.")

class PollCog(commands.Cog):
    """A cog to create polls"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll")
    async def poll_message(self, ctx, *, question_and_options: str):
        """
        Creates a poll.
        Usage:
        !poll Question | Option 1, Option 2, Option 3
        """
        # Ensure the input contains a question and options
        if "|" not in question_and_options:
            await ctx.send("Please provide the question and options separated by '|'.")
            return

        # Split the question and options
        question, options = question_and_options.split("|", 1)
        options = [option.strip() for option in options.split(",")]

        # Validate the number of options
        if len(options) < 2:
            await ctx.send("Provide at least two options.")
            return

        if len(options) > 10:
            await ctx.send("You can provide up to 10 options.")
            return

        # Create the embed for the poll
        embed = discord.Embed(title="Poll", description=question.strip(), color=discord.Color.blue())
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        poll_message = ""
        for i, option in enumerate(options):
            poll_message += f"{emojis[i]} {option}\n"

        embed.add_field(name="Options", value=poll_message, inline=False)
        embed.set_footer(text="React with the corresponding emoji to vote!")

        # Send the embed and add reactions
        message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await message.add_reaction(emojis[i])
from discord.ext import commands
import discord

from discord.ext import commands
import discord

class TicTacToe(commands.Cog):
    """A cog to play Tic-Tac-Toe"""

    def __init__(self, bot):
        self.bot = bot
        self.game_board = None
        self.current_player = None
        self.players = {}

    @commands.command(name="tictactoe")
    async def start_game(self, ctx, opponent: discord.Member):
        if ctx.author == opponent:
            await ctx.send("You cannot play against yourself!")
            return
        if self.game_board:
            await ctx.send("A game is already in progress! Please wait for it to finish.")
            return
        self.game_board = [" " for _ in range(9)]
        self.players = {ctx.author: "X", opponent: "O"}
        self.current_player = ctx.author
        await ctx.send(f"{ctx.author.mention} (X) vs {opponent.mention} (O)\nType `!move [position]` to play!")
        await self.display_board(ctx)

    async def display_board(self, ctx):
        board = "\n".join([
            f"{self.game_board[0]} | {self.game_board[1]} | {self.game_board[2]}",
            "---+---+---",
            f"{self.game_board[3]} | {self.game_board[4]} | {self.game_board[5]}",
            "---+---+---",
            f"{self.game_board[6]} | {self.game_board[7]} | {self.game_board[8]}",
        ])
        await ctx.send(f"```\n{board}\n```")

    @commands.command(name="move")
    async def make_move(self, ctx, position: int):
        if not self.game_board:
            await ctx.send("No game in progress. Start one with `!tictactoe @opponent`.")
            return
        if ctx.author != self.current_player:
            await ctx.send(f"It's not your turn, {ctx.author.mention}!")
            return
        if position < 1 or position > 9 or self.game_board[position - 1] != " ":
            await ctx.send("Invalid move! Choose a position between 1-9 that isn't already taken.")
            return
        self.game_board[position - 1] = self.players[ctx.author]
        if self.check_winner():
            await ctx.send(f"{ctx.author.mention} wins!")
            self.reset_game()
            return
        if " " not in self.game_board:
            await ctx.send("It's a tie!")
            self.reset_game()
            return
        self.current_player = next(player for player in self.players if player != ctx.author)
        await self.display_board(ctx)
        await ctx.send(f"It's {self.current_player.mention}'s turn!")

    @commands.command(name="endgame")
    async def end_game(self, ctx):
        if not self.game_board:
            await ctx.send("No game is currently in progress.")
            return
        if ctx.author not in self.players:
            await ctx.send("You are not part of the current game!")
            return
        await ctx.send(f"The game has been ended by {ctx.author.mention}.")
        self.reset_game()

    def check_winner(self):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6],
        ]
        for combo in winning_combinations:
            if self.game_board[combo[0]] == self.game_board[combo[1]] == self.game_board[combo[2]] != " ":
                return True
        return False

    def reset_game(self):
        self.game_board = None
        self.players = {}
        self.current_player = None



class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    @commands.command(name="play")
    async def play(self, ctx, url: str):
        """
        Play music from a YouTube URL.
        """
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command!")
            return

        voice_channel = ctx.author.voice.channel

        if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_connected():
            self.voice_clients[ctx.guild.id] = await voice_channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_flat': False,
            'noplaylist': True,
            'source_address': '0.0.0.0',
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                title = info.get('title', 'Unknown Title')

            voice_client = self.voice_clients[ctx.guild.id]

            if voice_client.is_playing():
                voice_client.stop()

            ffmpeg_options = {
                'options': '-vn',
            }
            voice_client.play(
                discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: print(f"Finished playing: {e}" if e else "Playback complete.")
            )
            await ctx.send(f"Now playing: {title}")

        except youtube_dl.DownloadError as e:
            print(f"yt_dlp Error: {e}")
            await ctx.send("An error occurred while processing the YouTube URL. Please try again.")
        except Exception as e:
            print(f"Unexpected Error: {e}")
            await ctx.send("An unexpected error occurred while trying to play the audio.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """
        Stop the music and disconnect.
        """
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send("Stopped and disconnected from the voice channel.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """
        Pause the currently playing music.
        """
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.is_playing():
                voice_client.pause()
                await ctx.send("Paused the music.")
            else:
                await ctx.send("No music is currently playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """
        Resume paused music.
        """
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.is_paused():
                voice_client.resume()
                await ctx.send("Resumed the music.")
            else:
                await ctx.send("The music is not paused.")

