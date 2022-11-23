from random import randrange

# TODO if using Github diff deployment on HeroKu uncomment the next line
import os
import discord

import disnake
from disnake.ext import commands

import re

from discord.utils import get

class Message(commands.Converter):
    def __init__(self, insert=False, local_only=False) -> None:
        self.insert = insert
        self.local_only = local_only

    async def convert(self, ctx, argument):
        async with ctx.typing():
            message_id, channel_id = self.extract_ids(ctx, argument)
            logged, message, = await self.fetch_messages(ctx, message_id, channel_id)
            if message is None:
                raise commands.BadArgument('unknown_message')
            if logged is not None and logged.content != message.content:
                logged.content = message.content
                await logged.save()
        if message.channel != ctx.channel and self.local_only:
            raise commands.BadArgument('message_wrong_channel')
        return message

    @staticmethod
    def extract_ids(ctx, argument):
        message_id = None
        channel_id = None
        if "-" in argument:
            parts = argument.split("-")
            if len(parts) == 2:
                try:
                    channel_id = int(parts[0].strip(" "))
                    message_id = int(parts[1].strip(" "))
                except ValueError:
                    pass
            else:
                parts = argument.split(" ")
                if len(parts) == 2:
                    try:
                        channel_id = int(parts[0].strip(" "))
                        message_id = int(parts[1].strip(" "))
                    except ValueError:
                        pass
        else:
            result = JUMP_LINK_MATCHER.match(argument)
            if result is not None:
                channel_id = int(result.group(1))
                message_id = int(result.group(2))
            else:
                try:
                    message_id = int(argument)
                except ValueError:
                    pass
        if message_id is None:
            raise commands.BadArgument('message_invalid_format')
        return message_id, channel_id

    @staticmethod
    async def fetch_messages(ctx, message_id, channel_id):
        message = None
        logged_message = None
        async with ctx.typing():
            if logged_message is None:
                if channel_id is None:
                    for channel in ctx.guild.text_channels:
                        try:
                            permissions = channel.permissions_for(channel.guild.me)
                            if permissions.read_messages and permissions.read_message_history:
                                message = await channel.fetch_message(message_id)
                                channel_id = channel.id
                                break
                        except (disnake.NotFound, disnake.Forbidden):
                            pass
                    if message is None:
                        raise commands.BadArgument('message_missing_channel')
            elif channel_id is None:
                channel_id = logged_message.channel
            channel = ctx.bot.get_channel(channel_id)
            if channel is None:
                raise commands.BadArgument('unknown_channel')
            elif message is None:
                try:
                    permissions = channel.permissions_for(channel.guild.me)
                    if permissions.read_messages and permissions.read_message_history:
                        message = await channel.fetch_message(message_id)
                except (disnake.NotFound, disnake.Forbidden):
                    raise commands.BadArgument('unknown_message')

        return logged_message, message

# Author: hyppytyynytyydytys#1010
# Created: 26 MAY 2020
# Last updated: 17 JULY 2022
# About: This is a version of Passel Bot that should ONLY be used as a private server bot.
#        Follow the instructions here on how to set up with heroku:
#
#        Passel Bot is a solution to the number of limited number of pins in a discord server.
#        It manages pins in 2 modes, Mode 1 and Mode 2. 
#
#        More information can be found on https://passelbot.wixsite.com/home
#        Passel Support Server: https://discord.gg/wmSsKCX
#
#        Mode 1: In mode 1, the most recent pinned message gets sent to a pins archive
#        channel of your choice. This means that the most recent pin wont be viewable in
#        the pins tab, but will be visible in the pins archive channel that you chose during setup
#
#        Mode 2: In mode 2, the oldest pinned message gets sent to a pins archive channel of
#        your choice. This means that the most recent pin will be viewable in the pins tab, and
#        the oldest pin will be unpinned and put into the pins archive channel
#
#        Furthermore: the p.sendall feature described later in the code allows the user to set
#        Passel so that all pinned messages get sent to the pins archive channel.

# TODO change command here if you want to use another command, replace p. with anything you want inside the single ('') quotes
intents = disnake.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='p.',
                      status='Online',
                      case_insensitive=True,
                      intents=intents)
client.remove_command("help")

# TODO change mode to 1 or 2 here
mode = 2

# TODO 
# sendall is set to 0 by default, change to 1 if you want
# the bot to send all pinned messages to the pins channel
sendall = 0

# TODO 
# replace the 0 with the pins channel ID for your sever
pins_channel = 1037185916441214987

# TODO
# add any black listed channel IDs as a list separated by a comma (,)
# a good idea is to add admin channels to this
blacklisted_channels = [
    1037184519066894408,
    1037184567381082203,
    1037502880615243837,
    1037524439044198520,
    1037185265359388725,
    1037185636869885963
]

# discord embed colors
EMBED_COLORS = [
    discord.Colour.magenta(),
    discord.Colour.blurple(),
    discord.Colour.dark_teal(),
    discord.Colour.blue(),
    discord.Colour.dark_blue(),
    discord.Colour.dark_gold(),
    discord.Colour.dark_green(),
    discord.Colour.dark_grey(),
    discord.Colour.dark_magenta(),
    discord.Colour.dark_orange(),
    discord.Colour.dark_purple(),
    discord.Colour.dark_red(),
    discord.Colour.darker_grey(),
    discord.Colour.gold(),
    discord.Colour.green(),
    discord.Colour.greyple(),
    discord.Colour.orange(),
    discord.Colour.purple(),
    discord.Colour.magenta(),
]

# When the bot is ready following sets the status of the bot
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# Command to check what the settings of the bot
@client.command(name='settings', pass_context=True)
async def settings(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        return

    await ctx.send("The mode you have setup is: " + str(mode))
    await ctx.send("Sendall is toggled to: " + str(sendall))
    await ctx.send("The pins channel for this server is: " + ctx.channel.guild.get_channel(pins_channel).mention)
    await ctx.send("Black listed channels are: ")
    for c in blacklisted_channels:
        try:
            await ctx.send(ctx.channel.guild.get_channel(c).mention)
        except:
            await ctx.send("Error: Check black listed channels")
            return
    await ctx.send("done")


@client.command(name='pins', pass_context=True)
async def pins(ctx):
    numPins = await ctx.message.channel.pins()
    await ctx.send(ctx.message.channel.mention + " has " + str(len(numPins)) + " pins.")

# The method that takes care of pin updates in a server
@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    global data
    try:
        randomColor = randrange(len(EMBED_COLORS))
        numPins = await channel.pins()

        # checks to see if message is in the blacklist
        # message is only sent if there is a blacklisted server with 50 messages pinned, informs them
        # that passel is in the server and they can un-blacklist the channel to have passel work
        if str(channel.id) in blacklisted_channels:
            return

        isChannelThere = False
        # checks to see if pins channel exists in the server
        channnelList = channel.guild.channels
        for channel in channnelList:
            if int(pins_channel) == int(channel.id):
                isChannelThere = True

        # checks to see if pins channel exists or has been deleted
        if not isChannelThere:
            await channel.send("Check to see if the pins archive channel during setup has been deleted")
            return

        # only happens if send all is toggled on
        if len(numPins) < 49 and sendall == 1:
            last_pinned = numPins[0]
            pinEmbed = discord.Embed(
                description="\"" + last_pinned.content + "\"",
                colour=EMBED_COLORS[randomColor]
            )
            # checks to see if pinned message has attachments
            attachments = last_pinned.attachments
            if len(attachments) >= 1:
                pinEmbed.set_image(url=attachments[0].url)
            pinEmbed.add_field(
                name="Jump", value=last_pinned.jump_url, inline=False)
            pinEmbed.set_footer(
                text="sent in: " + last_pinned.channel.name + " - at: " + str(last_pinned.created_at))
            pinEmbed.set_author(name='Sent by ' + last_pinned.author.name)
            await channel.guild.get_channel(int(pins_channel)).send(embed=pinEmbed)
            
            # remove this message if you do not want the bot to send a message when you pin a message
            await last_pinned.channel.send(
                "See pinned message in " + channel.guild.get_channel(int(pins_channel)).mention)
            return

        # if guild mode is one does the process following mode 1
        if mode == 1:
            last_pinned = numPins[len(numPins) - 1]
            # sends extra messages
            if len(numPins) == 50:
                last_pinned = numPins[0]
                pinEmbed = discord.Embed(
                    # title="Sent by " + last_pinned.author.name,
                    description="\"" + last_pinned.content + "\"",
                    colour=EMBED_COLORS[randomColor]
                )
                # checks to see if pinned message has attachments
                attachments = last_pinned.attachments
                if len(attachments) >= 1:
                    pinEmbed.set_image(url=attachments[0].url)
                pinEmbed.add_field(
                    name="Jump", value=last_pinned.jump_url, inline=False)
                pinEmbed.set_footer(
                    text="sent in: " + last_pinned.channel.name + " - at: " + str(last_pinned.created_at))
                pinEmbed.set_author(name='Sent by ' + last_pinned.author.name)
                await channel.guild.get_channel(int(pins_channel)).send(embed=pinEmbed)

                # remove this message if you do not want the bot to send a message when you pin a message
                await last_pinned.channel.send(
                    "See pinned message in " + channel.guild.get_channel(int(pins_channel)).mention)
                await last_pinned.unpin()

        # if guild mode is two follows the process for mode 2
        if mode == 2:
            last_pinned = numPins[0]
            if len(numPins) == 50:
                last_pinned = numPins[len(numPins) - 1]
                pinEmbed = discord.Embed(
                    # title="Sent by " + last_pinned.author.name,
                    description="\"" + last_pinned.content + "\"",
                    colour=last_pinned.author.color
                )
                # checks to see if pinned message has attachments
                attachments = last_pinned.attachments
                if len(attachments) >= 1:
                    pinEmbed.set_image(url=attachments[0].url)
                pinEmbed.add_field(
                    name="Jump", value=last_pinned.jump_url, inline=False)
                pinEmbed.set_footer(
                    text="sent in: " + last_pinned.channel.name + " - at: " + str(last_pinned.created_at))
                pinEmbed.set_author(name='Sent by ' + last_pinned.author.name,
                    url=last_pinned.author.avatar_url,
                    icon_url=last_pinned.author.avatar_url)
                await last_pinned.guild.get_channel(int(pins_channel)).send(embed=pinEmbed)

                # remove this message if you do not want the bot to send a message when you pin a message
                await last_pinned.channel.send(
                    "See oldest pinned message in " + channel.guild.get_channel(int(pins_channel)).mention)
                await last_pinned.unpin()
    except:
        print("unpinned a message, not useful for bot so does nothing")

@client.command(name='quote')
@commands.guild_only()
@commands.bot_has_permissions(embed_links=True)
async def quote(ctx: commands.Context, *, message: Message):
    """quote_help"""
    await ctx.trigger_typing()
    if ctx.message.author is None:
        await send_to(ctx, '🚫', 'quote_not_visible_to_user')
    else:
        permissions = message.channel.permissions_for(ctx.message.author)
        if permissions.read_message_history and permissions.read_message_history:
            attachment = None
            attachments = message.attachments
            if len(attachments) == 1:
                attachment = attachments[0]
            embed = disnake.Embed(colour=disnake.Color(0xd5fff),
                                    timestamp=message.created_at)
            if message.content is None or message.content == "":
                if attachment is not None:
                    url = attachment.url
                    if attachment.content_type != None and "image" in attachment.content_type:
                        embed.set_image(url=url)
                    else:
                        embed.add_field(name="attachment_link", value=url)
            else:
                description = message.content
                embed = disnake.Embed(colour=disnake.Color(0xd5fff), description=description,
                                        timestamp=message.created_at)
                embed.add_field(name="​",
                                value=f"[Jump to message]({message.jump_url})")
                if attachment is not None:
                    url = attachment.url
                    if attachment.content_type != None and "image" in attachment.content_type:
                        embed.set_image(url=url)
                    else:
                        embed.add_field(name="attachment_link", value=url)
            user = message.author
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.set_footer(
                text=f"Sent in {message.channel.name} | Quote requested by {clean_user(ctx.author)} | {message.id}"
            )
            await ctx.send(embed=embed)
            if ctx.channel.permissions_for(ctx.me).manage_messages:
                await ctx.message.delete()

        else:
            await send_to(ctx, '🚫', 'quote_not_visible_to_user')

def replace_lookalikes(text):
    replacements = {
        "`": "ˋ"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def escape_markdown(text):
    text = str(text)
    for c in ["\\", "*", "_", "~", "|", "{", ">"]:
        text = text.replace(c, f"\\{c}")
    return text.replace("@", "@\u200b")

def clean_user(user):
    if user is None:
        return "UNKNOWN USER"
    return f"{escape_markdown(replace_lookalikes(user.name))}#{user.discriminator}"

async def send_to(destination, emoji, message, embed=None, attachment=None, **kwargs):
    return await destination.send(f"{emoji} {message}", embed=embed, allowed_mentions=disnake.AllowedMentions(everyone=False, users=True, roles=False), file=attachment)

JUMP_LINK_MATCHER = re.compile(r"https://(?:canary|ptb)?\.?discord(?:app)?.com/channels/\d{15,20}/(\d{15,20})/(\d{15,20})")

@client.event
async def on_message(message):
    if 'shrimp check' in message.content:
        await message.add_reaction("🦐")
    if message.channel.id == 1037184519066894408 and re.search(r"\btictactic\b", message.content):
        await message.add_reaction(get(client.emojis(), name='threethumbsup'))
        await message.add_reaction("📊")
        await message.add_reaction("🎈")

client.run(os.environ.get('TOKEN'))
