from TicTacToe import TicTacToe
from discord.ext import commands
import random, discord

options = [
    discord.SelectOption(label="Rock", value="rock",
                         description="A blunt material, capable of smashing through scissors"),
    discord.SelectOption(label="Paper", value="paper",
                         description="A single piece of paper, dangerous when used to smother rock"),
    discord.SelectOption(label="Scissors", value="scissors",
                         description="A classic weapon which easily pierces through paper")]


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
        await ctx.send(random.choice(pool).mention + " is " + arg)

    @commands.command(name='how',
                      aliases=['howmuch', 'whatpercent'],
                      description="Uses an advanced algorithm to determine the percentage of something")
    async def how(self, ctx: commands.Context, arg1: str, arg2: str):
        """Determines the percentage"""
        await ctx.send(f"{arg2} is {random.randint(0, 100)}% {arg1}")


def setup(bot):
    bot.add_cog(Fun(bot))
