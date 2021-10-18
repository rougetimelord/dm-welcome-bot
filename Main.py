from typing import Dict
import discord, json, logging
import Commands

VERSION = "0.0.4"


class Client(discord.Client):
    command_prefix = "👋"

    async def on_ready(self) -> None:
        """On ready event listener that updates activity and loads config"""
        log.info(f"logged in as {self.user.name} with id {self.user.id}")
        await self.change_presence(
            activity=discord.Activity(
                name="Greeting discorders", type=discord.ActivityType.custom
            )
        )

        self._servers: Dict[str, Dict[str, str]] = {}
        self._user_to_server: Dict[str, str] = {}
        try:
            with open("data/servers.json", "r") as f:
                self._servers = json.load(f)
        except FileNotFoundError as e:
            self._dump_to_file()

        await self.change_presence(
            activity=discord.Activity(
                name=f"Admins use {self.command_prefix}help to get help!",
                type=discord.ActivityType.watching,
            )
        )

    async def _dump_to_file(self) -> None:
        """Dumps config to disk, does not care if it's already there"""
        with open("data/servers.json", "w+") as f:
            json.dump(self._servers, f)
        log.info("JSON Dumped")

    async def _create_dm_embed(self, member: discord.Member) -> discord.Embed():
        """Creates a embed to dm to someone.
        Message is checked against the server data and overridden as needed :)

        Args:
            member (discord.Member): The person to send to

        Returns:
            discord.Embed: The embed to send off
        """
        gid = member.guild.id
        title = self._servers["default_title"]
        message = self._servers["default_message"]

        if "title" in self._servers[gid]:
            title = self._servers[gid]["title"]
        if "message" in self._servers[gid]:
            message = self._servers[gid]["message"]

        embed = discord.Embed(
            title=title.format(
                member_name=member.display_name, guild_name=member.guild.name
            ),
            description=message.format(
                member_name=member.display_name, guild_name=member.guild.name
            ),
            color=discord.Color.dark_green(),
        )

        return embed

    async def on_member_join(self, member: discord.Member) -> None:
        """Adds a user to the relationship store and sends a DM

        Args:
            member (discord.Member): The member who joined
        """
        log.info("New member joined, sending DM")
        self._user_to_server[member.id] = member.guild.id
        embed = await self._create_dm_embed(member)
        await member.send(embed=embed)

    async def _dm_handler(self, message: discord.Message) -> None:
        """Handles an incoming DM

        Args:
            message (discord.Message): The message that got sent in
        """
        log.info("Handling a DM")

        # Check for user in the user to server relationship store
        if not message.author.id in self._user_to_server:
            log.info("Rejected, missing guild info")
            await message.channel.send(
                embed=discord.Embed(
                    title="Oops",
                    description="I'm so sorry I lost track of what server you were in, please DM the mods of the server",
                    color=discord.Color.red(),
                )
            )
            return
        # Check for server support
        gid = self._user_to_server[message.author.id]
        if not "channel" in self._servers[gid]:
            log.info("Rejected, missing channel")
            await message.channel.send(
                embed=discord.Embed(
                    title="Oops",
                    description="Ok so, I kinda lied. The server admins haven't set a channel to forward to yet so they can't read this I'm so sorry.\nDM them to get in",
                    color=discord.Color.red(),
                )
            )
            return

        # this forwards the message
        embed = discord.Embed(
            title=f"Message from {message.author.name}#{message.author.discriminator}",
            description=message.content,
        )
        await self.get_channel(self._servers[gid]["channel"]).send(embed=embed)
        # Tell the end user we have done a thing
        await message.channel.send(
            embed=discord.Embed(
                title="Forwarded Message",
                description="Your message has been forwarded along GLHF",
                color=discord.Color.dark_green(),
            )
        )
        # Remove them from the relationship store
        self._user_to_server.pop(message.author.id, None)
        return

    async def _check_admin(self, member: discord.Member) -> bool:
        """Checks if a member is an admin in the guild

        Args:
            member (discord.Member): The member to check

        Returns:
            bool: If the member is an admin
        """
        return member.guild_permissions.administrator

    async def _check_owner(self, member: discord.Member) -> bool:
        """Checks if a member is the bot's owner

        Args:
            member (discord.Member): The member to check

        Returns:
            bool: If the supplied member is bot owner
        """
        info = await self.application_info()
        return info.owner.id == member.id

    async def _command_handler(self, message: discord.Message) -> None:
        """Handles commands by passing them off to other functions

        Args:
            message (discord.Message): The message with a command in it
        """
        log.info("Got a command")
        if await self._check_admin(message.author) or await self._check_owner(
            message.author
        ):
            if message.content.startswith(f"{self.command_prefix}set"):
                await Commands.set_channel(self, message)
            elif message.content.startswith(f"{self.command_prefix}unset"):
                await Commands.unset_channel(self, message)
            elif message.content.startswith(f"{self.command_prefix}change message"):
                await Commands.change_message(self, message)
            elif message.content.startswith(f"{self.command_prefix}change title"):
                await Commands.change_title(self, message)
            elif message.content.startswith(f"{self.command_prefix}help"):
                await Commands.help(self, message)
        return

    async def on_message(self, message: discord.Message) -> None:
        """Handles all messages by delegation

        Args:
            message (discord.Message): The message received
        """
        # ignore bots lol
        if message.author.bot:
            return

        if message.guild is None and isinstance(message.channel, discord.DMChannel):
            await self._dm_handler(message)
        if message.content[0] == self.command_prefix:
            await self._command_handler(message)


def main():
    """Main method, starts everything glhf"""
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    intents.dm_messages = True

    bot = Client(intents=intents)
    try:
        with open("data/key.json", "r") as f:
            keys = json.load(f)
            bot.run(keys["token"])
    except IOError as e:
        log.error("get a key lol")
        exit(1)


if __name__ == "__main__":
    log = logging.getLogger()
    logging.basicConfig(
        format="[%(name)s][%(levelname)s] %(message)s",
        level=logging.INFO,
    )
    log.info(f"DM Bot v{VERSION} started")
    main()
