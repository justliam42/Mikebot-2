from discord.ext import commands
import json
import discord


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='clear',
                      aliases=['purge'],
                      description='Clears the specified number of messages from the text channel')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, num):
        """Clears messages"""
        try:
            num = int(num)
            if num > 0:
                await ctx.channel.purge(limit=num + 1)
            else:
                await ctx.send('Please use positive numbers')
        except ValueError:
            await ctx.send('Please use valid numbers')

    @commands.command(name='autorole',
                      aliases=['AutoRole', 'arole'],
                      description='Set or Remove roles the get automatically assigned on joining the server')
    @commands.has_permissions(manage_messages=True)
    async def auto_role(self, ctx: commands.Context, arg1: str, *arg2: str):
        """Assign roles on joining"""
        role_id = None
        if len(arg2) > 0:
            arg2 = arg2[0]  # so there can be no second arg if necessary
            try:
                role_id = int("".join(filter(str.isdigit, arg2)))
            except ValueError:
                await ctx.send("invalid role")
                return
        role = ctx.guild.get_role(role_id)
        if arg1 == "add":
            if role is not None:
                autoRole = None
                with open("autorole.json", 'r') as f:
                    autoRole = json.load(f)  # autorole is the json object containing an [{guild_id:[role_ids]},etc]
                if str(ctx.guild.id) not in autoRole:
                    autoRole[str(ctx.guild.id)] = []
                elif role_id in autoRole[str(ctx.guild.id)]:
                    await ctx.send(f"role is already in the list({ctx.prefix}autorole view)")
                    return
                autoRole[str(ctx.guild.id)].append(role_id)
                with open("autorole.json", 'w') as f:
                    json.dump(autoRole, f, indent=4)
                await ctx.send("**`done`**")
            else:
                await ctx.send("invalid role")
                return
        elif arg1 in ['remove', 'subtract', 'minus', 'clear', 'purge']:
            if role is not None:
                autoRole = None
                with open("autorole.json", 'r') as f:
                    autoRole = json.load(f)  # autorole is the json object containing an [{guild_id:[role_ids]},etc]
                if str(ctx.guild.id) in autoRole and role_id in autoRole[str(ctx.guild.id)]:
                    autoRole[str(ctx.guild.id)].remove(role_id)
                else:
                    await ctx.send(f"this role isnt in the autorole list({ctx.prefix}autorole view)")
                with open("autorole.json", 'w') as f:
                    json.dump(autoRole, f, indent=4)
                await ctx.send("**`done`**")

            else:
                await ctx.send("invalid role")
                return
        elif arg1 in ["view", "see", "observe", "list"]:
            with open("autorole.json", 'r') as f:
                autoRole = json.load(f)  # autorole is the json object containing an [{guild_id:[role_ids]},etc]
            if str(ctx.guild.id) in autoRole and len(autoRole[str(ctx.guild.id)]) >= 1:
                message = ""
                for i in autoRole[str(ctx.guild.id)]:
                    message += ctx.guild.get_role(i).mention + "\n"
                await ctx.send(
                    embed=discord.Embed(title=f"autoroles for {ctx.guild.name}", description=message, color=1304659))
            else:
                await ctx.send("no autoroles have been set up yet")
            pass
        else:
            await ctx.send(f"Invalid argument:{arg1}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        with open("autorole.json", 'r') as f:
            autoRole = json.load(f)  # autorole is the json object containing an [{guild_id:[role_ids]},etc]
        if str(member.guild.id) in autoRole:
            for i in autoRole[str(member.guild.id)]:
                await member.add_roles(member.guild.get_role(i), reason="autorole")


def setup(bot):
    bot.add_cog(Moderation(bot))
