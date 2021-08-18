from discord.ext import commands
import json
import discord
from typing import Union
import random


def get_role(role: str, guild: discord.Guild) -> Union[discord.Role, None]:
    if len(role) > 0:
        try:
            role_id = int("".join(filter(str.isdigit, role)))
        except ValueError:
            return None
    else:
        return None
    return guild.get_role(role_id)


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
                      description='Set or Remove roles the get automatically assigned on joining the server\nnote: when using the "view" argument, a role does not need to be specified',
                      usage=f"[add|remove|view] [role]")
    @commands.has_permissions(manage_messages=True)
    async def auto_role(self, ctx: commands.Context, arg1: str, *arg2: str):
        """Assign roles on joining"""
        try:
            with open("autorole.json") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("autorole.json", "w") as file:
                json.dump({}, file)

        role = None
        if len(arg2) > 0:  # so there can be no second arg if necessary
            arg2 = arg2[0]
            role = get_role(arg2, ctx.guild)
        if arg1 == "add":
            if role is not None:
                autoRole = None
                with open("autorole.json", 'r') as f:
                    autoRole = json.load(f)  # autorole is the json object containing an [{guild_id:[role_ids]},etc]
                if str(ctx.guild.id) not in autoRole:
                    autoRole[str(ctx.guild.id)] = []
                elif role.id in autoRole[str(ctx.guild.id)]:
                    await ctx.send(f"role is already in the list({ctx.prefix}autorole view)")
                    return
                autoRole[str(ctx.guild.id)].append(role.id)
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
                if str(ctx.guild.id) in autoRole and role.id in autoRole[str(ctx.guild.id)]:
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

    @commands.Cog.listener()  # autorole logic
    async def on_member_join(self, member: discord.Member):
        if member == self.bot.user or member.bot:
            return
        with open("autorole.json", 'r') as f:
            autoRole = json.load(f)  # autorole is the json object containing an [{guild_id:[role_ids]},etc]
        if str(member.guild.id) in autoRole:
            for i in autoRole[str(member.guild.id)]:
                await member.add_roles(get_role(i, member.guild), reason="autorole")

    @commands.command(name='selfrole',
                      aliases = ['rolereactions','srole'],
                      description = 'Creates a message that assigns users certain roles on their reaction to the appropriate emote')  # the rest of this cog is for self role
    @commands.has_permissions(manage_messages=True, manage_roles=True)
    async def selfrole(self, ctx: commands.Context, title: str, *roles):
        """creates a selfrole message"""
        try:
            with open("selfrole.json") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("selfrole.json", "w") as file:
                json.dump({}, file)

        self_roles = []
        for i in roles:
            role = get_role(i, ctx.guild)
            if role is not None:
                self_roles.append(role)
        role_emojis = []  # the generated emotes to use as reactions
        role_emoji_nums = []
        emojis = list(range(128512, 128591))
        for i in range(len(self_roles)):
            random_emote = random.choice(emojis)
            role_emoji_nums.append(random_emote)
            role_emojis.append(chr(random_emote))
            emojis.remove(random_emote)

        text = f"{title}"
        for i in range(len(self_roles)):
            text += f"\n{role_emojis[i]} - {self_roles[i].name}"
        message = await ctx.send(text)
        for i in role_emojis:
            await message.add_reaction(i)
        with open("selfrole.json", 'r') as f:
            self_role = json.load(f)
        if str(ctx.guild.id) not in self_role:
            self_role[str(ctx.guild.id)] = {}
        if str(ctx.channel.id) not in self_role[str(ctx.guild.id)]:
            self_role[str(ctx.guild.id)][str(ctx.channel.id)] = {}
        role_ids = []
        for i in self_roles:
            role_ids.append(i.id)
        self_role[str(ctx.guild.id)][str(ctx.channel.id)][str(message.id)] = {'emotes': role_emoji_nums,
                                                                              'roles': role_ids}
        with open("selfrole.json", 'w') as f:
            json.dump(self_role, f, indent=4)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        user = self.bot.get_user(payload.user_id)
        if user == self.bot.user or user.bot:
            return
        del user
        try:
            with open("selfrole.json") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("selfrole.json", "w") as file:
                json.dump({}, file)

        with open("selfrole.json", 'r') as f:
            self_role = json.load(f)

        if str(payload.guild_id) in self_role and str(payload.channel_id) in self_role[str(payload.guild_id)] and str(
                payload.message_id) in self_role[str(payload.guild_id)][str(payload.channel_id)]:
            data = self_role[str(payload.guild_id)][str(payload.channel_id)][str(payload.message_id)]
            for i in range(len(data['emotes'])):
                if payload.emoji.name == chr(data['emotes'][i]):
                    guild = self.bot.get_guild(payload.guild_id)
                    role = guild.get_role(data['roles'][i])
                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        user = self.bot.get_user(payload.user_id)
        if user == self.bot.user or user.bot:
            return
        del user
        try:
            with open("selfrole.json") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("selfrole.json", "w") as file:
                json.dump({}, file)

        with open("selfrole.json", 'r') as f:
            self_role = json.load(f)

        if str(payload.guild_id) in self_role and str(payload.channel_id) in self_role[str(payload.guild_id)] and str(
                payload.message_id) in self_role[str(payload.guild_id)][str(payload.channel_id)]:
            data = self_role[str(payload.guild_id)][str(payload.channel_id)][str(payload.message_id)]
            for i in range(len(data['emotes'])):
                if payload.emoji.name == chr(data['emotes'][i]):
                    guild = self.bot.get_guild(payload.guild_id)
                    role = guild.get_role(data['roles'][i])
                    user = guild.get_member(payload.user_id)
                    if role in user.roles:
                        await user.remove_roles(role)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            with open("selfrole.json") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("selfrole.json", "w") as file:
                json.dump({}, file)

        with open("selfrole.json", 'r') as f:
            self_role = json.load(f)

        for guild_id in self_role:
            guild = self.bot.get_guild(int(guild_id))
            for channel_id in self_role[guild_id]:
                channel = self.bot.get_channel(int(channel_id))
                for message_id in self_role[guild_id][channel_id]:
                    data = self_role[guild_id][channel_id][message_id]
                    try:
                        message = await channel.fetch_message(int(message_id))
                    except discord.errors.NotFound:
                        del self_role[guild_id][channel_id][message_id]
                        with open("selfrole.json", 'w') as f:
                            json.dump(self_role, f, indent=4)
                        return
                    role_ids = list(map(int, data['roles']))
                    roles = list(map(guild.get_role, role_ids))
                    for member in guild.members:
                        for reaction in message.reactions:
                            emotes = list(map(chr, data['emotes']))
                            role = roles[emotes.index(reaction.emoji)]
                            if reaction.emoji in emotes:
                                users = []
                                async for user in reaction.users():
                                    if user == self.bot.user or user.bot:
                                        continue
                                    if member == user and role not in member.roles:
                                        await member.add_roles(role)
                                    users.append(user)
                                if member not in users and role in member.roles:
                                    await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        try:
            with open("selfrole.json") as file:
                json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            with open("selfrole.json", "w") as file:
                json.dump({}, file)

        with open("selfrole.json", 'r') as f:
            self_role = json.load(f)
        if str(payload.guild_id) in self_role and str(payload.channel_id) in self_role[str(payload.guild_id)] and str(
                payload.message_id) in self_role[str(payload.guild_id)][str(payload.channel_id)]:
            del self_role[str(payload.guild_id)][str(payload.channel_id)][str(payload.message_id)]
        with open("selfrole.json", 'w') as f:
            json.dump(self_role, f, indent=4)


def setup(bot):
    bot.add_cog(Moderation(bot))
