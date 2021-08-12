import discord
from discord.ext import commands
import youtube_dl


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, name='connect', aliases=['join'])
    async def connect(self, ctx):
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        return voice_client

    @commands.command(hidden=True,name='disconnect', aliases=['leave'])
    async def disconnect(self, ctx):
        voice_client = ctx.guild.voice_client
        await voice_client.disconnect()

    @commands.command(hidden=True,name='play')
    async def play(self, ctx: commands.Context):
        if ctx.guild.voice_client is None:
            voice_client = await self.connect(ctx)
        else:
            voice_client = ctx.guild.voice_client
        voice_client.play(discord.FFmpegPCMAudio(source='Monsters Inc theme.mp3'))


def setup(bot):
    bot.add_cog(Music(bot))
