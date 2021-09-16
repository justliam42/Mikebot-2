import asyncio
import random
from asyncio import ALL_COMPLETED, FIRST_COMPLETED
from typing import Optional

import discord
from discord.ext import commands

erps_dict = {
    'water': {
        'kills': ['motorcycle', 'rock', 'british people', 'chainsaw', 'paper', 'ants', 'fire', 'gun'],
        'dies': ['fire extinguisher', 'finger', 'construction paper', 'hand sanitizer', 'paper clip']
    },
    'fire extinguisher': {
        'kills': ['water', 'fire', 'ants', 'paper', 'british people'],
        'dies': ['gun', 'paper clip', 'chainsaw', 'scissors', 'finger', 'rock', 'motorcycle', 'hammer',
                 'construction paper', 'double scissors']
    },
    'hammer': {
        'kills': ['fire extinguisher', 'gun', 'paper clip', 'british people', 'hand sanitizer', 'scissors', 'finger',
                  'rock', 'motorcycle', 'double scissors'],
        'dies': ['fire', 'ants', 'construction paper', 'chainsaw']
    },
    'motorcycle': {
        'kills': ['fire extinguisher', 'british people', 'paper', 'hand sanitizer', 'finger'],
        'dies': ['hammer', 'water', 'fire', 'paper clip', 'ants', 'chainsaw', 'scissors', 'rock', 'construction paper',
                 'double scissors']
    },
    'rock': {
        'kills': ['fire extinguisher', 'motorcycle', 'paper clip', 'british people', 'hand sanitizer', 'chainsaw',
                  'scissors', 'finger', 'double scissors'],
        'dies': ['hammer', 'water', 'gun', 'fire', 'ants', 'paper', 'construction paper']
    },
    'finger': {
        'kills': ['fire extinguisher', 'water', 'gun', 'british people', 'ants'],
        'dies': ['motorcycle', 'rock', 'hammer', 'paper clip', 'fire', 'chainsaw', 'scissors',
                 'construction paper', 'double scissors']
    },
    'scissors': {
        'kills': ['finger', 'motorcycle', 'fire extinguisher', 'british people', 'paper clip', 'paper', 'chainsaw'],
        'dies': ['rock', 'hammer', 'gun', 'fire', 'ants', 'construction paper']
    },
    'chainsaw': {
        'kills': ['finger', 'motorcycle', 'hammer', 'british people', 'fire extinguisher', 'paper clip', 'paper'],
        'dies': ['construction paper', 'scissors', 'rock', 'water', 'gun', 'fire', 'ants', 'double scissors']
    },
    'hand sanitizer': {
        'kills': ['paper', 'ants', 'water', 'british people'],
        'dies': ['construction paper', 'paper clip', 'fire', 'gun', 'hammer', 'motorcycle', 'rock']
    },
    'paper': {
        'kills': ['british people', 'rock'],
        'dies': ['ants', 'paper clip', 'fire', 'gun', 'water', 'fire extinguisher', 'motorcycle', 'chainsaw',
                 'scissors', 'hand sanitizer', 'construction paper', 'double scissors']
    },
    'ants': {
        'kills': ['paper clip', 'fire', 'gun', 'hammer', 'motorcycle', 'rock', 'scissors', 'chainsaw', 'paper',
                  'double scissors'],
        'dies': ['construction paper', 'hand sanitizer', 'finger', 'fire extinguisher', 'water']
    },
    'paper clip': {
        'kills': ['gun', 'water', 'fire extinguisher', 'motorcycle', 'british people', 'finger', 'hand sanitizer',
                  'paper'],
        'dies': ['fire', 'hammer', 'rock', 'scissors', 'chainsaw', 'construction paper', 'ants', 'double scissors']
    },
    'fire': {
        'kills': ['gun', 'hammer', 'british people', 'motorcycle', 'rock', 'finger', 'scissors', 'chainsaw',
                  'hand sanitizer', 'paper', 'double scissors'],
        'dies': ['water', 'fire extinguisher', 'construction paper', 'ants']
    },
    'gun': {
        'kills': ['rock', 'fire extinguisher', 'british people', 'scissors', 'chainsaw', 'hand sanitizer', 'paper',
                  'double scissors'],
        'dies': ['water', 'hammer', 'finger', 'construction paper', 'ants', 'fire', 'paper clip']
    },
    'construction paper': {
        'kills': ['water', 'fire extinguisher', 'british people', 'hammer', 'motorcycle', 'rock', 'finger', 'scissors',
                  'chainsaw', 'hand sanitizer', 'paper', 'paper clip', 'ants', 'fire', 'gun'],
        'dies': ['double scissors']
    },
    'double scissors': {
        'kills': ['construction paper', 'finger', 'motorcycle', 'fire extinguisher', 'british people', 'paper clip',
                  'paper', 'chainsaw'],
        'dies': ['rock', 'hammer', 'gun', 'fire', 'ants', 'construction paper']
    },
    'british people': {
        'kills': [],
        'dies': ['hammer', 'water', 'fire', 'paper clip', 'chainsaw', 'scissors', 'rock', 'construction paper',
                 'double scissors', 'fire extinguisher', 'british people', 'paper', 'hand sanitizer', 'finger',
                 'motorcycle', 'gun']
    },
    'abort': {'kills': [],
              'dies': []},
    'none': {'kills': [],
             'dies': []}
}


def erps_check_basic(element1: str, element2: str) -> Optional[int]:
    if element1 in erps_dict:
        if element2 in erps_dict[element1]['kills']:
            return 1
        elif element2 in erps_dict[element1]['dies']:
            return -1
        else:
            return 0
    else:
        print(f'{element1} not in dictionary')
        return


static_elements = ['fire extinguisher', 'hammer', 'rock', 'finger', 'chainsaw', 'hand sanitizer', 'ants',
                   'paper clip', 'fire', 'gun', 'water', 'british people', '**abort**']


def format_options(options: list):
    message = "**Your Options:**\n"
    for i in options:
        message += i + "\n"
    return message


def not_bot(m):
    return not m.author.bot


class erps_player:
    def __init__(self, player: discord.User):
        self.user = player
        self.points = 0
        self.pointsWon = None  # the previous points won from the trick(reset to None if none are earned)
        self.roundsWon = 0
        self.cut = False
        self.paperCount = 0
        self.paperClip = False  # get reset everytime construction paper is played
        self.doubleScissors = False  # every other time scissors becomes double scissors
        self.options = []
        self.viewOptions = []
        self.crashed = False
        self.dmChannel = self.user.dm_channel

        self.refresh_options()
        self.selectedOption = None

    async def make_dm_channel(self):
        self.dmChannel = self.user.dm_channel
        if self.dmChannel is None:
            self.dmChannel = await self.user.create_dm()

    def refresh_options(self):
        self.options = static_elements.copy()
        if not self.crashed:
            self.options.insert(2, 'motorcycle')
        if not self.doubleScissors:
            self.options.insert(5, 'scissors')
        elif self.doubleScissors:
            self.options.insert(5, 'double scissors')
        if self.paperCount < 3:
            self.options.insert(8, 'paper')
        elif self.paperCount >= 3:
            self.options.insert(8, 'construction paper')
        # self.options.append('abort')
        self.viewOptions = []
        for i in self.options:
            self.viewOptions.append(discord.SelectOption(label=i, value=i))


class erps_game:
    def __init__(self, player1: discord.User, player2: discord.User, pointsToWin: int, channel, bot: commands.Bot):
        self.player1 = erps_player(player1)
        self.player2 = erps_player(player2)
        self.bot = bot
        self.statusMessage = None
        self.pointsToWin = pointsToWin
        self.channel = channel
        self.aborted = False

    async def dm_options(self, player):
        player.refresh_options()
        await player.dmChannel.send(format_options(player.options))
        valid = False
        while not valid:
            msg = await self.bot.wait_for('message', check=not_bot)
            if msg.channel.id == player.dmChannel.id and msg.author == player.user:
                if msg.content.lower() in player.options or msg.content.lower() == 'abort':
                    player.selectedOption = msg.content.lower()
                    valid = True
                else:
                    await player.dmChannel.send('invalid option')

    def get_embed(self) -> discord.Embed:
        embed = embed = discord.Embed(title="Extreme Rock Paper Scissors")
        for i in [self.player1, self.player2]:
            value = f"Rounds won: {i.roundsWon}\nPoints this round: {i.points}"
            if i.pointsWon is not None:
                value += f"(+{i.pointsWon})"
            if i.selectedOption is not None:
                value += f"\nLast action: {i.selectedOption}"
            embed.add_field(name=i.user.display_name, value=value)
        return embed

    async def abort(self, player: erps_player, opponent: erps_player):
        await self.statusMessage.edit(f"**The game was aborted by {player.user.display_name}**")
        await player.dmChannel.send(f"**You aborted the game**")
        await opponent.dmChannel.send(f"**{player.user.display_name} aborted the game**")
        self.aborted = True

    async def trick(self):
        tasks = [asyncio.create_task(self.dm_options(self.player1)), asyncio.create_task(self.dm_options(self.player2))]

        def abort_check(msg):
            if msg.content.lower() == 'abort':
                if msg.author.id == self.player1.user.id and msg.author.dm_channel.id == self.player1.dmChannel.id:
                    self.player1.selectedOption = 'abort'
                    self.player2.selectedOption = 'none'
                    return True
                if msg.author.id == self.player2.user.id and msg.author.dm_channel.id == self.player2.dmChannel.id:
                    self.player2.selectedOption = 'abort'
                    self.player1.selectedOption = 'none'
                    return True
            else:
                return False

        tasks2 = [asyncio.create_task(asyncio.wait(tasks, return_when=ALL_COMPLETED)),
                  asyncio.create_task(self.bot.wait_for('message', check=abort_check))]
        # try:
        done, _ = await asyncio.wait(tasks2, return_when=FIRST_COMPLETED, timeout=180)
        if done == set():
            for p in [self.player1, self.player2]:
                await p.dmChannel.send("The game has timed out and has been aborted")
            await self.statusMessage.edit("The Game Timed Out")
            self.aborted = True
            return
        for p in [self.player1, self.player2]:
            if p.selectedOption == 'paper clip' and not p.paperClip:
                p.paperClip = True
                await p.dmChannel.send("You have used a paper clip. You may now start stacking paper")
            if p.paperClip and p.selectedOption == 'paper':
                p.paperCount += 1
            if p.selectedOption == 'construction paper':
                p.paperClip = False
                p.paperCount = 0
            if p.selectedOption == 'scissors':
                p.doubleScissors = True
            if p.selectedOption == 'double scissors':
                p.doubleScissors = False
        if erps_check_basic(self.player1.selectedOption, self.player2.selectedOption) == 1:
            self.player1.points += 1
            self.player1.pointsWon = 1
            self.player2.pointsWon = None
            await self.player1.dmChannel.send(
                f"{self.player2.user.display_name} has played {self.player2.selectedOption}. You **won** the point")
            await self.player2.dmChannel.send(
                f"{self.player1.user.display_name} has played {self.player1.selectedOption}. You **lost** the point")

        elif erps_check_basic(self.player1.selectedOption, self.player2.selectedOption) == -1:
            self.player2.points += 1
            self.player2.pointsWon = 1
            self.player1.pointsWon = None
            await self.player2.dmChannel.send(
                f"{self.player1.user.display_name} has played {self.player1.selectedOption}. You **won** the point")
            await self.player1.dmChannel.send(
                f"{self.player2.user.display_name} has played {self.player2.selectedOption}. You **lost** the point")

        elif self.player1.selectedOption == 'motorcycle' and self.player2.selectedOption == 'motorcycle':
            for p in [self.player1, self.player2]:
                p.pointsWon = None
                await p.dmChannel.send(
                    "You both played motorcycle and got into a crash. You can no longer play motorcycle")
                p.crashed = True

        elif (self.player1.selectedOption == 'paper' and self.player2.selectedOption == 'finger') or (
                self.player1.selectedOption == 'finger' and self.player2.selectedOption == 'paper'):
            if self.player1.selectedOption == 'paper':
                winner = self.player1
                loser = self.player2
            else:
                winner = self.player2
                loser = self.player1
            if not loser.cut:
                await winner.dmChannel.send(
                    f"You cut {loser.user.display_name}'s finger with your paper and **won** a point")
                await loser.dmChannel.send(
                    f"Ouch! {winner.user.display_name} cut your finger, and you **lost** a point")
                loser.cut = True
            else:
                await winner.dmChannel.send(
                    f"{loser.user.display_name} has played {loser.selectedOption}. You **won** the point")
                await loser.dmChannel.send(
                    f"{winner.user.display_name} has played {winner.selectedOption}. You **lost** the point")
            winner.points += 1
            winner.pointsWon = 1
            loser.pointsWon = None

        elif (self.player1.selectedOption == 'hand sanitizer' and self.player2.selectedOption == 'finger') or (
                self.player1.selectedOption == 'finger' and self.player2.selectedOption == 'hand sanitizer'):
            if self.player1.selectedOption == 'finger':
                finger = self.player1
                sanitizer = self.player2
            else:
                finger = self.player2
                sanitizer = self.player1
            if finger.cut:
                await finger.dmChannel.send(
                    f'{sanitizer.user.display_name} played hand sanitizer which stings your cut. You **lost** the point.')
                await sanitizer.dmChannel.send(
                    f"Your hand sanitizer triumphs over {finger.user.display_name}'s cut finger. You **won** the point.")
                sanitizer.points += 1
                sanitizer.pointsWon = 1
                finger.pointsWon = None
            else:
                await finger.dmChannel.send(
                    f"{sanitizer.user.display_name} has played {sanitizer.selectedOption}. You **won** the point")
                await sanitizer.dmChannel.send(
                    f"{finger.user.display_name} has played {finger.selectedOption}. You **lost** the point")

        elif (self.player1.selectedOption == 'british people' and self.player2.selectedOption == 'ants') or (
                self.player1.selectedOption == 'ants' and self.player2.selectedOption == 'british people'):
            if self.player1.selectedOption == 'ants':
                ants = self.player1
                brits = self.player2
            else:
                brits = self.player1
                ants = self.player2
            await ants.dmChannel.send(f"{brits.user.display_name} played british people. They **won 2 points**")
            await brits.dmChannel.send(f"{ants.user.display_name} played ants. You **won 2 points**")
            brits.points += 2
            brits.pointsWon = 2
            ants.pointsWon = None

        elif self.player1.selectedOption == 'ants' and self.player2.selectedOption == 'ants':
            rps = ['rock', 'paper', 'scissors']

            async def dm_rps_options(player: erps_player) -> (str, erps_player):
                await player.dmChannel.send("**Options:**\nrock\npaper\nscissors")
                valid = False
                while not valid:
                    msg = await self.bot.wait_for('message', check=not_bot)
                    if msg.channel.id == player.dmChannel.id and msg.author == player.user:
                        if msg.content.lower() in rps:
                            return msg.content.lower(), player.user.id

            for p in [self.player1, self.player2]:
                await p.dmChannel.send(
                    "You both played ants. Play Rock Paper Scissors(best 2 of 3) to determine which ant army is victorious")
            points1 = 0
            points2 = 0
            while True:
                tasks = [dm_rps_options(self.player1), dm_rps_options(self.player2)]
                option1, _ = await asyncio.wait(tasks, return_when=ALL_COMPLETED, timeout=180)
                if len(list(option1)) < 2:
                    for p in [self.player1, self.player2]:
                        await p.dmChannel.send("The game has timed out and has been aborted")
                    await self.statusMessage.edit("The Game Timed Out")
                    self.aborted = True
                    return
                options = list(option1)
                print(type(options[0].result()[1]), options[1].result()[1])
                print(self.player1.user.id == options[0].result()[1])
                if int(options[0].result()[1]) == self.player1.user.id:
                    selected1 = options[0].result()[0]
                    selected2 = options[1].result()[0]
                else:
                    selected2 = options[0].result()[0]
                    selected1 = options[1].result()[0]

                player1 = self.player1
                player2 = self.player2

                if rps.index(selected1) - 1 == rps.index(selected2) or rps.index(selected1) + 2 == rps.index(selected2):
                    points1 += 1
                    await player1.dmChannel.send(
                        f"{player2.user.display_name} played {selected2}. Your ant army won a point")
                    await player2.dmChannel.send(
                        f"{player1.user.display_name} played {selected1}. Your ant army lost a point")
                elif rps.index(selected2) - 1 == rps.index(selected1) or rps.index(selected2) + 2 == rps.index(
                        selected1):
                    points2 += 1
                    await player2.dmChannel.send(
                        f"{player1.user.display_name} played {selected1}. Your ant army won a point")
                    await player1.dmChannel.send(
                        f"{player2.user.display_name} played {selected2}. Your ant army lost a point")
                else:
                    await player1.dmChannel.send("you tied...")
                    await player2.dmChannel.send("you tied...")
                if points1 >= 2 or points2 >= 2:
                    break
            if points1 >= 2:
                await self.player1.dmChannel.send(f"Your ant army won the war. You have gained a point")
                await self.player2.dmChannel.send(f"Your ant army lost the war. Your opponent has gained a point")
                self.player1.points += 1
                self.player1.pointsWon = 1
                self.player2.pointsWon = None
            else:
                await self.player2.dmChannel.send(f"Your ant army won the war. You have gained a point")
                await self.player1.dmChannel.send(f"Your ant army lost the war. Your opponent has gained a point")
                self.player2.points += 1
                self.player2.pointsWon = 1
                self.player1.pointsWon = None

        elif (self.player1.selectedOption == 'gun' and self.player2.selectedOption == 'motorcycle') or (
                self.player1.selectedOption == 'motorcycle' and self.player2.selectedOption == 'gun') or (
                self.player1.selectedOption == 'hand sanitizer' and self.player2.selectedOption == 'chainsaw') or (
                self.player1.selectedOption == 'chainsaw' and self.player2.selectedOption == 'hand sanitizer') or (
                self.player1.selectedOption == 'chainsaw' and self.player2.selectedOption == 'chainsaw'):
            # speed
            async def button_pressed(interaction: discord.Interaction):
                victor = None
                theloser = None
                if self.player1.user == interaction.user:
                    victor = self.player1
                    theloser = self.player2
                elif self.player2.user == interaction.user:
                    victor = self.player2
                    theloser = self.player1
                else:
                    pass
                await victor.dmChannel.send("Congrats you were faster. You gained the point")
                await theloser.dmChannel.send(f"You're slow. Your opponent gained the point")
                victor.points += 1
                victor.pointsWon = 1
                theloser.pointsWon = None

            def check(interaction: discord.Interaction):
                if self.player1.user == interaction.user or self.player2.user == interaction.user:
                    return True
                else:
                    return False

            class button(discord.ui.Button):
                def __init__(self):
                    super().__init__()
                    self.label = "click here"
                    self.custom_id = 'speed'

                async def callback(self, interaction: discord.Interaction):
                    await button_pressed(interaction)

            view = discord.ui.View()
            view.add_item(button())
            await self.player1.dmChannel.send(
                f'**think fast** click the button in the original channel where the challenge was initiated. {self.player2.user.display_name} played {self.player2.selectedOption}')
            await self.player2.dmChannel.send(
                f'**think fast** click the button in the original channel where the challenge was initiated. {self.player1.user.display_name} played {self.player1.selectedOption}')
            await asyncio.sleep(.5)
            message = await self.channel.send('speed button', view=view)
            await self.bot.wait_for('interaction', check=check)
            await message.delete()

        elif self.player1.selectedOption == 'gun' and self.player2.selectedOption == 'gun':
            duel_embed = discord.Embed(color=discord.Color.blurple(),
                                       title=f'Duel({self.player1.user.display_name} vs {self.player2.user.display_name})',
                                       description='---🚶<:personwalkingbackwards:886781603362267147>---')
            shot = False

            async def button_pressed(interaction: discord.Interaction):

                if self.player1.user == interaction.user:
                    shot = True
                    await duel.delete()
                    if fire:
                        await self.player1.dmChannel.send("You won the duel and another point!")
                        await self.player2.dmChannel.send(
                            f"{self.player1.user.display_name} shot you first and gained a point")
                        self.player1.points += 1
                        self.player1.pointsWon = 1
                        self.player2.pointsWon = None
                        return
                    else:
                        await self.player1.dmChannel.send(
                            f"You were too early and shot yourself. {self.player2.user.display_name} gained a point.")
                        await self.player2.dmChannel.send(
                            f"Congrats!, {self.player1.user.display_name} was too early and shot themself. You gained a free point")

                        self.player2.points += 1
                        self.player2.pointsWon = 1
                        self.player1.pointsWon = None
                        return
                elif self.player2.user == interaction.user:
                    shot = True
                    await duel.delete()
                    if fire:
                        await self.player2.dmChannel.send("You won the duel and another point!")
                        await self.player1.dmChannel.send(
                            f"{self.player2.user.display_name} shot you first and gained a point")
                        self.player2.points += 1
                        self.player2.pointsWon = 1
                        self.player1.pointsWon = None
                        return
                    else:
                        await self.player2.dmChannel.send(
                            f"You were too early and shot yourself. {self.player1.user.display_name} gained a point.")
                        await self.player1.dmChannel.send(
                            f"Congrats!, {self.player2.user.display_name} was too early and shot themself. You gained a free point")

                        self.player1.points += 1
                        self.player1.pointsWon = 1
                        self.player2.pointsWon = None
                        return

            class button(discord.ui.Button):
                def __init__(self):
                    super().__init__()
                    self.label = "Fire!"
                    self.custom_id = 'fire'

                async def callback(self, interaction: discord.Interaction):
                    await button_pressed(interaction)

            view = discord.ui.View()
            view.add_item(button())
            duel = await self.channel.send(embed=duel_embed, view=view)
            fire = False
            embed = discord.Embed(color=discord.Color.blurple(),
                                  title='A duel has begun, **CLICK HERE**(you both chose gun)',
                                  url=duel.jump_url)
            for p in [self.player1, self.player2]:
                await p.dmChannel.send(embed=embed)

            await asyncio.sleep(2.5)
            for i in [3, 2, 1, 0]:
                try:
                    duel_embed.description = ('-' * i) + '🚶' + (
                            (3 - i) * 2 * '-') + '<:personwalkingbackwards:886781603362267147>' + (i * '-')
                    await duel.edit(embed=duel_embed)
                    await asyncio.sleep(2.5)
                except discord.ext.commands.errors.CommandInvokeError:
                    return
                except discord.errors.NotFound:
                    return
            duel_embed.description = '<:personwalkingbackwards:886781603362267147><:gunbackwards:886786531988209685>----🔫🚶'
            try:
                await duel.edit(embed=duel_embed)
            except discord.ext.commands.errors.CommandInvokeError:
                return
            except discord.errors.NotFound:
                return
            fire = True

            def check(interaction: discord.Interaction):
                if self.player1.user == interaction.user or self.player2.user == interaction.user:
                    return True
                else:
                    return False

            await self.bot.wait_for('interaction', check=check)
            await asyncio.sleep(.2)


        elif self.player1.selectedOption == 'finger' and self.player2.selectedOption == 'finger':
            emotes = ['🖐', '👌', '👐', '🤏', '🤚', '✋', '🙌', '🤝', '🤙', '🤞', '🖕', '🖖', '✊']

            message = await self.channel.send("\"finger war\"(react with the emoji dmed to you)")
            embed = discord.Embed(color=discord.Color.blurple(),
                                  title='Prepare for a finger war(click here)',
                                  url=message.jump_url)
            await self.player1.dmChannel.send(embed=embed)
            await self.player2.dmChannel.send(embed=embed)
            for emote in emotes:
                await message.add_reaction(emote)
            p1emote = random.choice(emotes)
            p2emote = random.choice(emotes)
            await self.player1.dmChannel.send(f'Your attack spot is {p1emote}')
            await self.player2.dmChannel.send(f'Your attack spot is {p2emote}')
            reaction = (None, None)

            def check(reaction, user) -> bool:
                if self.player1.user == user or self.player2.user == user:
                    return True
                else:
                    return False

            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            await message.delete()
            if user == self.player1.user:
                if reaction.emoji == p1emote:
                    await self.player1.dmChannel.send(
                        f"You attacked {self.player2.user.display_name}'s hand/finger and gained a point")
                    await self.player2.dmChannel.send(
                        f"{self.player1.user.display_name} attacked your hand/finger first and gained a point")
                    self.player1.points += 1
                    self.player1.pointsWon = 1
                    self.player2.pointsWon = None
                    return
                else:
                    await self.player1.dmChannel.send(
                        f"Oops! You attacked your own hand/finger. {self.player2.user.display_name} gained a point.")
                    await self.player2.dmChannel.send(
                        f"Congrats!, {self.player1.user.display_name} attacked their own hand/finger. You gained a free point")
                    self.player2.points += 1
                    self.player2.pointsWon = 1
                    self.player1.pointsWon = None
                    return
            elif user == self.player2.user:
                if reaction.emoji == p2emote:
                    await self.player2.dmChannel.send(
                        f"You attacked {self.player1.user.display_name}'s hand/finger and gained a point")
                    await self.player1.dmChannel.send(
                        f"{self.player2.user.display_name} attacked your hand/finger first and gained a point")
                    self.player2.points += 1
                    self.player2.pointsWon = 1
                    self.player1.pointsWon = None
                    return
                else:
                    await self.player2.dmChannel.send(
                        f"Oops! You attacked your own hand/finger. {self.player1.user.display_name} gained a point.")
                    await self.player1.dmChannel.send(
                        f"Congrats!, {self.player2.user.display_name} attacked their own hand/finger. You gained a free point")
                    self.player1.points += 1
                    self.player1.pointsWon = 1
                    self.player2.pointsWon = None
                    return
        elif self.player1.selectedOption == 'rock' and self.player2.selectedOption == 'rock':
            async def punch(player: erps_player, opponent: erps_player):
                punch_view = discord.ui.View()
                punch_button = discord.ui.Button(label='punch', custom_id='punch')
                punch_view.add_item(punch_button)

                def punch_check(interaction):
                    if interaction.user == player.user and interaction.channel.id == player.dmChannel.id:
                        return True
                    else:
                        return False

                punch_message = await player.dmChannel.send("Punch the other player within 2 seconds", view=punch_view)
                try:
                    await self.bot.wait_for("interaction", check=punch_check, timeout=2)
                    await player.dmChannel.send(f"You punched {opponent.user.display_name}")
                    player.pointsWon = None
                except asyncio.TimeoutError:
                    await punch_message.delete()
                    await player.dmChannel.send(
                        f"You didn't punch {opponent.user.display_name} in time(you got deducted 1 point)")
                    player.points -= 1
                    player.pointsWon = -1

            tasks = [asyncio.create_task(punch(self.player1, self.player2)),
                     asyncio.create_task(punch(self.player2, self.player1))]
            await asyncio.wait(tasks, return_when=ALL_COMPLETED)

        elif self.player1.selectedOption == 'paper' and self.player2.selectedOption == 'paper':
            async def slap(player: erps_player, opponent: erps_player):
                slap_view = discord.ui.View()
                slap_button = discord.ui.Button(label='slap', custom_id='slap')
                slap_view.add_item(slap_button)

                def slap_check(interaction):
                    if interaction.user == player.user and interaction.channel.id == player.dmChannel.id:
                        return True
                    else:
                        return False

                slap_message = await player.dmChannel.send("Slap the other player within 2 seconds", view=slap_view)
                try:
                    await self.bot.wait_for("interaction", check=slap_check, timeout=2)
                    await player.dmChannel.send(f"You slapped {opponent.user.display_name}")
                    player.pointsWon = None
                except asyncio.TimeoutError:
                    await slap_message.delete()
                    await player.dmChannel.send(
                        f"You didn't slap {opponent.user.display_name} in time(you got deducted 1 point)")
                    player.points -= 1
                    player.pointsWon = -1

            tasks = [asyncio.create_task(slap(self.player1, self.player2)),
                     asyncio.create_task(slap(self.player2, self.player1))]
            await asyncio.wait(tasks, return_when=ALL_COMPLETED)

        elif self.player1.selectedOption == 'abort':
            await self.abort(self.player1, self.player2)
        elif self.player2.selectedOption == 'abort':
            await self.abort(self.player2, self.player1)

        else:
            self.player1.pointsWon = None
            self.player2.pointsWon = None
            await self.player2.dmChannel.send(
                f"{self.player1.user.display_name} has played {self.player1.selectedOption}. You **tied**")
            await self.player1.dmChannel.send(
                f"{self.player2.user.display_name} has played {self.player2.selectedOption}. You **tied**")

        await self.statusMessage.edit(embed=self.get_embed())
        self.player1.selectedOption = None
        self.player2.selectedOption = None

    async def start(self):
        await self.player1.make_dm_channel()
        await self.player2.make_dm_channel()
        self.statusMessage = await self.channel.send(embed=self.get_embed())

        while self.player1.roundsWon < 2 and self.player2.roundsWon < 2:

            while self.player1.points < self.pointsToWin and self.player2.points < self.pointsToWin:
                await self.trick()
                if self.aborted:
                    return
            if self.player1.points >= self.pointsToWin:
                winner = self.player1
                loser = self.player2
            else:
                winner = self.player2
                loser = self.player1

            await winner.dmChannel.send(f"**You achieved {winner.points} points, and won the round**")
            await loser.dmChannel.send(
                f"**{winner.user.display_name} achieved {winner.points} points, and won the round(you lost loser)**")
            winner.roundsWon += 1
            self.player1.points, self.player2.points = 0, 0

        if self.player1.roundsWon >= 2:
            await self.player1.dmChannel.send("**You won the game. congrats!**")
            await self.player2.dmChannel.send("**You lost the game...**")
            await self.statusMessage.edit(embed=self.get_embed())
            await self.channel.send(
                f"{self.player1.user.mention} has won Extreme Rock Paper Scissors against {self.player2.user.mention}")
        else:
            await self.player2.dmChannel.send("**You won the game. congrats!**")
            await self.player1.dmChannel.send("**You lost the game...**")
            await self.statusMessage.edit(embed=self.get_embed())
            await self.channel.send(
                f"{self.player2.user.mention} has won Extreme Rock Paper Scissors against {self.player1.user.mention}")
