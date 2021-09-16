import asyncio
import random
from typing import Optional

import discord
from discord.ext import commands

from TicTacToe import TicTacToe
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


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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
        message = await ctx.send(choice.mention + " is " + arg,
                                 allowed_mentions=discord.AllowedMentions(replied_user=False, users=[], roles=[],
                                                                          everyone=False))
        # edits the message to make it seem like a ping without notification. Mobile users would otherwise see
        if "<@" in message.content and ">" in message.content:  # @invalid-user.
            await message.edit(content=choice.mention + " is " + arg,
                               allowed_mentions=discord.AllowedMentions(replied_user=True, users=True, roles=True,
                                                                        everyone=False))

    @commands.command(name='how',
                      aliases=['howmuch', 'whatpercent'],
                      description="Uses an advanced algorithm to determine the percentage of something")
    async def how(self, ctx: commands.Context, arg1: str, arg2: str):
        """Determines the percentage"""
        percent = random.randint(0, 100)
        message = await ctx.send(f"{arg2} is {percent}% {arg1}",
                                 allowed_mentions=discord.AllowedMentions(replied_user=False, users=[], roles=[],
                                                                          everyone=False))
        # edits the message to make it seem like a ping without notification. Mobile users would otherwise see
        if "<@" in message.content and ">" in message.content:  # @invalid-user.
            await message.edit(content=f"{arg2} is {percent}% {arg1}",
                               allowed_mentions=discord.AllowedMentions(replied_user=True, users=True, roles=True,
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
            for p in [i.player1,i.player2]:
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.author.bot:
            return
        dad = None
        split_message = message.content.lower().split(" ")
        for i in split_message:
            if i in dad_words:
                dad = message.content.lower().index(i) + len(i) + 1
        if dad is not None:
            await message.channel.send(f"Hi {message.content[dad:]}, im Mikebot")


def setup(bot):
    bot.add_cog(Fun(bot))
