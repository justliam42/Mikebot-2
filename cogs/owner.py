import discord
from discord.ext import commands


class CogOptions(discord.ui.Button):
    def __init__(self, Cog, bot, ctx, mode: int):
        super().__init__()
        self.cog = Cog
        self.bot = bot
        self.label = Cog
        self.custom_id = 'cogs.' + self.cog.lower()
        self.ctx = ctx
        self.mode = mode

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.bot.owner_id:
            try:
                if self.mode >= 2:
                    self.bot.unload_extension(self.custom_id)
                    await self.ctx.send(f'**`Unloaded {self.custom_id}`**')
                    print(f"Unloaded {self.custom_id}")
                    self.mode -= 2
                if self.mode >= 1:
                    self.bot.load_extension(self.custom_id)
                    await self.ctx.send(f'**`Loaded {self.custom_id}`**')
                    print(f"Loaded {self.custom_id}")
                    self.mode -= 1
            except Exception as e:
                await self.ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await self.ctx.send("You are not allowed to do that!")


class Owner(commands.Cog):
    """Owner-only commands for managing the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reload',
                      description='Reloads the extension/module specified(use dot path: cogs.owner)',
                      hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *cogs):
        """Reloads a cog"""
        if len(cogs) > 0:
            try:
                for cog in cogs:
                    self.bot.unload_extension(cog)
                    self.bot.load_extension(cog)
            except Exception as e:
                await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            else:
                await ctx.send('**`SUCCESS`**')
        else:
            choices = discord.ui.View()
            for cog in list(self.bot.cogs):
                choices.add_item(CogOptions(cog, self.bot, ctx, 3))
            await ctx.channel.send('**Select Which Module to Reload:**', view=choices)

    @commands.command(name='load', description='Loads the extension/module specified(use dot path: cogs.owner)',
                      hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *cogs):
        """Loads a cog"""
        if len(cogs) > 0:
            try:
                for cog in cogs:
                    self.bot.load_extension(cog)
            except Exception as e:
                await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            else:
                await ctx.send('**`SUCCESS`**')
        else:
            choices = discord.ui.View()
            for cog in list(self.bot.cogs):
                choices.add_item(CogOptions(cog, self.bot, ctx, 1))
            await ctx.channel.send('**Select Which Module to Load:**', view=choices)

    @commands.command(name='unload',
                      description='Unloads the extension/module specified(use dot path: cogs.owner)',
                      hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *cogs):
        """Unloads a cog"""
        if len(cogs) > 0:
            try:
                self.bot.unload_extension(cogs)
            except Exception as e:
                await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            else:
                await ctx.send('**`SUCCESS`**')
        else:
            choices = discord.ui.View()
            for cog in list(self.bot.cogs):
                if cog != 'Owner':
                    choices.add_item(CogOptions(cog, self.bot, ctx, 2))
            await ctx.channel.send('**Select Which Module to Unload:**', view=choices)

    @commands.command(name='stop',
                      hidden=True)
    @commands.is_owner()
    async def stop(self, ctx):
        """Stops the bot"""
        await self.bot.close()


def setup(bot):
    bot.add_cog(Owner(bot))
