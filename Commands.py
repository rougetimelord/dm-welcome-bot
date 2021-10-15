import discord, logging
from Main import Client

log = logging.getLogger(__name__)


async def set_channel(parent: Client, message: discord.Message) -> None:
    """Sets the channel to forward to

    Args:
        parent (Client): The parent bot instance
        message (discord.Message): The message that got us here
    """
    parent._servers[message.guild]["channel"] = message.channel.id
    await parent._dump_to_file()
    log.info(f"Set channel in {message.guild.name}")

    embed = discord.Embed(
        title="Set forwarding channel",
        description="DMs sent to the bot will forward here",
    )
    await message.channel.send(embed=embed)
    return


async def unset_channel(parent: Client, message: discord.Message) -> None:
    """Unsets the channel to forward to

    Args:
        parent (Client): The parent bot instance
        message (discord.Message): The message that got us here
    """
    parent._servers[message.guild].pop("channel", None)
    await parent._dump_to_file()
    log.info(f"Set channel in {message.guild.name}")

    embed = discord.Embed(
        title="Unset forwarding channel", description="DMs will no longer be forwarded"
    )
    await message.channel.send(embed=embed)
    return


async def change_message(parent: Client, message: discord.Message) -> None:
    """Changes the description of DM embeds

    Args:
        parent (Client): The parent bot instance
        message (discord.Message): The message that got here
    """
    new_message = message.content.replace(f"{parent.command_prefix}change message ", "")
    parent._servers[message.guild.id]["message"] = new_message
    await parent._dump_to_file()
    log.info(f"Changed message for {message.guild.name}")
    await message.channel.send("Sending a test message")
    embed = await parent._create_dm_embed(message.author)
    await message.channel.send(embed=embed)

async def change_title(parent: Client, message: discord.Message) -> None:
    """Changes the title of DM embeds

    Args:
        parent (Client): The parent bot instance
        message (discord.Message): The message that got here
    """
    new_title = message.content.replace(f"{parent.command_prefix}change title ", "")
    parent._servers[message.guild.id]["message"] = new_title
    await parent._dump_to_file()
    log.info(f"Changed message for {message.guild.name}")
    await message.channel.send("Sending a test message")
    embed = await parent._create_dm_embed(message.author)
    await message.channel.send(embed=embed)

async def help(parent: Client, message: discord.Message) -> None:
    log.info(f"Sending a help message for {message.guild.name}")
    set_unset_embed = discord.Embed(
        title="Set/Unset Help",
        description=f"To set which channel to forward messages to use {parent.command_prefix}set.\nTo remove the forwarding channel use {parent.command_prefix}unset.",
        color=discord.Color.dark_green()
    )
    change_message_embed = discord.Embed(
        title="Change Message/Title Help",
        description=f"Using {parent.command_prefix}change title or {parent.command_prefix}change message will change the message sent to new members.\nThe title is the string that will show up at the top of the message and message is the text body that will be sent.\nThere are two available format strings {{member_name}} and {{guild_name}}, these will be replaced in the messages sent with the name of the member and the server name. They are available in both the title and message.",
        color=discord.Color.dark_green()
    )
    await message.channel.send(embed=set_unset_embed)
    await message.channel.send(embed=change_message_embed)
