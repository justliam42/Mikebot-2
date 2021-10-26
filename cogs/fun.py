import asyncio
import json
import random
import socket
from pprint import pprint
from typing import Optional
from mcstatus import MinecraftServer
import discord
import requests
from discord.ext import commands, tasks

from cogs.extra.TicTacToe import TicTacToe
from cogs.extra.erpsLib import erps_game

dad_words = ["im", "i'm", u"i’m", "i am"]
options = [
    discord.SelectOption(label="Rock", value="rock",
                         description="A blunt material, capable of smashing through scissors"),
    discord.SelectOption(label="Paper", value="paper",
                         description="A single piece of paper, dangerous when used to smother rock"),
    discord.SelectOption(label="Scissors", value="scissors",
                         description="A classic weapon which easily pierces through paper")]
erps_games = []
counting_json = "data/counting.json"
mcsrvstat_json = "data/mcsrvstat.json"

def get_user_from_mention(user: str, bot: discord.ext.commands.Bot) -> Optional[discord.User]:
    user = str(user)
    if len(user) > 0:
        try:
            user_id = int("".join(filter(str.isdigit, user)))
        except ValueError:
            return None
    else:
        return None
    return bot.get_user(user_id)

def get_mcsrvstat_embed(ip:str):
    server = MinecraftServer.lookup(ip)
    try:
        status = server.status(tries=1)
    except socket.gaierror:
        server = MinecraftServer.lookup(ip + '.just42.me')
        ip = ip + '.just42.me'
        try:
            status = server.status(tries=1)
        except socket.gaierror:
            return None, ip
    content = f"**motd:** {status.description}\n**version**: {status.version.name}\n**players online({status.players.online}/{status.players.max}):**"
    if status.players.sample is not None:
        for i in status.players.sample:
            content += ('\n' + i.name)
    embed = discord.Embed(title=ip + " status:", description=content)
    return embed, ip
class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dynamic_mcstat_update.start()

    def cog_unload(self):
        self.dynamic_mcstat_update.cancel()
    @commands.command(name='mcsrvstat',
                      aliases=['mcsrv', 'mcserver', 'mcsvr', 'mcstat'],
                      description='get the info of a minecraft server',
                      usage='[server ip]')
    async def mcsrvstat(self, ctx: commands.Context, ip):
        embed, _ = get_mcsrvstat_embed(ip)
        if embed is None:
            await ctx.send("failed to ping server ip")
            return
        await ctx.send(embed=embed)

    @tasks.loop(seconds=15)
    async def dynamic_mcstat_update(self):
        try:
            with open(mcsrvstat_json) as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        with open(mcsrvstat_json, 'r') as f:
            srvstat = json.load(f)

        for guild_id in srvstat:
            for channel_id in srvstat[guild_id]:
                for message_id in srvstat[guild_id][channel_id]:
                    channel = self.bot.get_channel(int(channel_id))
                    message = await channel.fetch_message(int(message_id))
                    ip = srvstat[guild_id][channel_id][message_id]
                    embed, _ = get_mcsrvstat_embed(ip)
                    await message.edit(embed=embed)

    @commands.command(name='dynamicmcsrvstat',
                      aliases=['permstat', 'dynmcsrv', 'dynstat', 'permsrvstat', 'dynsrvstat'],
                      description='Create a message that updates the status of the server every minute')
    @commands.has_permissions(manage_channels=True)
    async def dynamicmcsrvstat(self, ctx: commands.Context, ip):
        """create a dynamic minecraft status message"""
        embed, ip = get_mcsrvstat_embed(ip)
        if embed is None:
            await ctx.send("failed to ping server ip")
            return
        try:
            with open(mcsrvstat_json) as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(mcsrvstat_json, "w") as file:
                json.dump({}, file)

        with open(mcsrvstat_json, 'r') as f:
            srvstat = json.load(f)
        guild_id = str(ctx.guild.id)

        channel_id = str(ctx.channel.id)
        if guild_id not in srvstat:
            srvstat[guild_id] = {}
        if channel_id not in srvstat[guild_id]:
            srvstat[guild_id][channel_id] = {}

        message = await ctx.send(embed=embed)
        srvstat[guild_id][channel_id][str(message.id)] = ip


        with open(mcsrvstat_json, 'w') as f:
            json.dump(srvstat, f, indent=4)
    @commands.command(name='startcounting',
                      aliases=['begincounting', 'startcount', 'countstart', 'begincount', 'countbegin'],
                      description='Begin counting in the current channel')
    @commands.has_permissions(manage_channels=True)
    async def start_counting(self, ctx: commands.Context):
        """initiate counting"""
        try:
            with open(counting_json) as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(counting_json, "w") as file:
                json.dump({}, file)

        counting = None
        with open(counting_json, 'r') as f:
            counting = json.load(f)

        guild_id = str(ctx.guild.id)
        channel_id = str(ctx.channel.id)
        if guild_id not in counting:
            counting[guild_id] = {}
        if channel_id not in counting[guild_id]:
            counting[guild_id][channel_id] = {"number": 0, "last_user": None}
            await ctx.send("Counting has begun! Begin at 1.")

        else:
            await ctx.send("this channel is already being counted...")
            return

        with open(counting_json, 'w') as f:
            json.dump(counting, f, indent=4)

    async def end_counting(self, channel: discord.TextChannel):
        with open(counting_json, 'r') as f:
            counting = json.load(f)
        guild_id = str(channel.guild.id)
        channel_id = str(channel.id)
        if guild_id in counting and channel_id in counting[guild_id]:
            counting[guild_id].pop(channel_id)
        else:
            await channel.send("The channel isn't being used for counting right now.")
        with open(counting_json, 'w') as f:
            json.dump(counting, f, indent=4)

    @commands.command(name='stopcounting',
                      aliases=['quitcounting', 'stopcount', 'quitcount', 'countstop'],
                      description='Stop counting in the current channel')
    @commands.has_permissions(manage_channels=True)
    async def stop_counting(self, ctx: commands.Context):
        """stop counting"""
        try:
            with open(counting_json) as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.channel.send("The channel isn't being used for counting right now.")
            return

        await self.end_counting(ctx.channel)
        await ctx.channel.send("This channel no longer tracks counting.")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.TextChannel):
        try:
            with open(counting_json) as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        with open(counting_json, 'r') as f:
            counting = json.load(f)
        guild_id = str(channel.guild.id)
        channel_id = str(channel.id)
        if guild_id in counting and channel_id in counting[guild_id]:
            await self.end_counting(channel)

    async def count(self, message):
        try:
            with open(counting_json) as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return
        with open(counting_json, 'r') as f:
            counting = json.load(f)
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        if guild_id in counting and channel_id in counting[guild_id]:
            try:
                attempt = int(message.content)
            except ValueError:
                return
            if message.author.id == counting[guild_id][channel_id]['last_user']:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention} sent a number twice in a row! Restart at 1.")
                counting[guild_id][channel_id]['number'] = 0
                counting[guild_id][channel_id]['last_user'] = None
            elif attempt == counting[guild_id][channel_id]['number'] + 1:
                counting[guild_id][channel_id]['number'] += 1
                counting[guild_id][channel_id]['last_user'] = message.author.id
                await message.add_reaction("✅")
            elif attempt != counting[guild_id][channel_id]['number'] + 1:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention} doesn't know how to count! Restart at 1.")
                counting[guild_id][channel_id]['number'] = 0
                counting[guild_id][channel_id]['last_user'] = None
            else:
                await message.channel.send('something went wrong')
            with open(counting_json, 'w') as f:
                json.dump(counting, f, indent=4)

    @commands.command(name='tictactoe',
                      aliases=['Tic', 'Tac', 'tic', 'tac', 'TicTacToe'],
                      description='Play a game of tictactoe with a friend')
    async def tic_tac_toe(self, ctx: commands.Context):
        """play some tic tac toe"""
        await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())

    @commands.command(name='rockpaperscissors',
                      aliases=['rps', 'RockPaperScissors'],
                      description='Play some rock paper scissors(the first 2 to respond are the challengers)')
    async def rockpaperscissors(self, ctx: commands.Context):
        """initiate rock paper scissors"""

        class rpsSelector(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.player1 = None
                self.player2 = None
                self.select1 = None
                self.select2 = None

            @discord.ui.select(placeholder="Select your champion", options=options, max_values=1, min_values=1)
            async def rock(self, select: discord.ui.Select, interaction: discord.Interaction):
                if self.player1 is None or interaction.user == self.player1:
                    self.player1 = interaction.user
                    self.select1 = select.values[0]
                elif self.player2 is None:
                    self.player2 = interaction.user
                    self.select2 = select.values[0]

                    temp = ['rock', 'paper', 'scissors']
                    if temp.index(self.select1) - temp.index(self.select2) in [1, -2]:
                        await interaction.message.edit(view=None, content=
                        f"{self.player1.mention}({self.select1}) Won Against {self.player2.mention}({self.select2})")
                    elif temp.index(self.select2) - temp.index(self.select1) in [1, -2]:
                        await interaction.message.edit(view=None, content=
                        f"{self.player2.mention}({self.select2}) Won Against {self.player1.mention}({self.select1})")
                    elif temp.index(self.select2) == temp.index(self.select1):
                        await interaction.message.edit(view=None, content=
                        f"{self.player1.mention}({self.select1}) Tied Against {self.player2.mention}({self.select2})")

        view = rpsSelector()
        await ctx.send("Rock Paper Scissors", view=view)

    @commands.command(name='whois',
                      aliases=['who', 'whomis'],
                      description="Scientifically pick a person who matches the question you have asked")
    async def who_is(self, ctx: commands.Context, *, arg):
        """Answers life's questions"""
        pool = []
        for i in ctx.guild.members:
            if not i.bot and i.status is not discord.Status.offline:
                pool.append(i)
        choice = random.choice(pool)

        content = choice.mention + " is " + arg
        if len(ctx.message.mentions) > 0:
            for i in ctx.message.mentions:
                content = content.replace(i.mention, i.display_name)

        message = await ctx.send(content, allowed_mentions=discord.AllowedMentions(roles=False,
                                                                                   everyone=False))

    @commands.command(name='how',
                      aliases=['howmuch', 'whatpercent'],
                      description="Uses an advanced algorithm to determine the percentage of something")
    async def how(self, ctx: commands.Context, arg1: str, arg2: str):
        """Determines the percentage"""
        percent = random.randint(0, 100)
        content = f"{arg2} is {percent}% {arg1}"
        if len(ctx.message.mentions) > 0:
            for i in ctx.message.mentions:
                content = content.replace(i.mention, i.display_name)
        message = await ctx.send(content, allowed_mentions=discord.AllowedMentions(roles=False,
                                                                                   everyone=False))

    @commands.command(name='extremerockpaperscissors',
                      aliases=['erps', 'ExtremeRockPaperScissors'],
                      description='Play a game of extreme rock paper scissors',
                      usage='[points to win a round]')
    async def extremerockpaperscissors(self, ctx: commands.Context, opponent: str, *, rounds=None):
        """initiate **extreme** rock paper scissors"""
        opponent = get_user_from_mention(opponent, self.bot)
        if opponent is None:
            await ctx.channel.send("please challenge a valid user")
            return
        if opponent.id == ctx.author.id:
            await ctx.channel.send("You can't challenge yourself")
            return
        for i in erps_games:
            for p in [i.player1, i.player2]:
                if p.user.id == ctx.author.id:
                    await ctx.channel.send("You are already playing a game")
                    return
                if p.user.id == opponent.id:
                    await ctx.channel.send(f"{opponent.display_name} is already playing a game")
                    return

        def check(msg):
            if msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id:
                return True
            else:
                return False

        if rounds is not None:
            try:
                rounds = int(rounds)
            except ValueError:
                await ctx.channel.send("please send a valid number of rounds or dont send one at all")
                return
            game = erps_game(ctx.author, opponent, rounds, ctx.channel, self.bot)
        else:
            stuff = await ctx.send("Type the number of points to win a round(traditional is 26)")
            try:
                rounds_message = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                await stuff.edit(content="The command has timed out")
                await stuff.delete(delay=10)
                return
            try:
                rounds = int(rounds_message.content)
                game = erps_game(ctx.author, opponent, rounds, ctx.channel, self.bot)
            except ValueError:
                await ctx.channel.send("invalid number")
                return

        erps_games.append(game)
        await game.start()
        erps_games.remove(game)

    async def dad_bot(self, message):
        if message.author == self.bot.user or message.author.bot:
            return
        dad = None
        split_message = message.content.lower().split(" ")
        for i in split_message:
            if i in dad_words:
                dad = message.content.lower().index(i) + len(i) + 1
        if dad is not None:
            await message.channel.send(f"Hi {message.content[dad:]}, im Mikebot")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.dad_bot(message)
        await self.count(message)


def setup(bot):
    bot.add_cog(Fun(bot))
