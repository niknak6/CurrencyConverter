# Import the discord.py library and the commands module
import discord
from redbot.core import commands

# Import the datetime module for formatting timestamps
import datetime

# Create a cog class that inherits from commands.Cog
class TreacheryPins(commands.Cog):
    """A cog that allows users to pin messages with a push pin emoji."""

    # Define the name and description of the cog
    def __init__(self, bot):
        self.bot = bot
        self.name = "TreacheryPins"
        self.description = "A cog that allows users to pin messages with a push pin emoji."

    # Create a listener function that listens for the on_raw_reaction_add event
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """This event is triggered when a user reacts to a message with an emoji."""

        # Get the guild, channel, and message objects from the payload
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Get the reaction emoji and the user who reacted from the payload
        emoji = payload.emoji
        user = guild.get_member(payload.user_id)

        # Check if the reaction emoji is a push pin and if the message is not pinned already
        if emoji.name == "📌" and not message.pinned:
            # Get the message link, which is a URL that points to the message in the channel
            message_link = message.jump_url

            # Create a short summary of the message, which could include the author name, the content, and the timestamp
            summary = f"{message.author.display_name}: {message.content}\n{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

            # Find or create a "Pinnable Message" in the channel, which is a message that contains all the links and summaries of the pinned messages
            pinnable_message = None
            async for msg in channel.history(limit=50):
                if msg.author == self.bot and msg.content.startswith("Pinnable Message:"):
                    pinnable_message = msg
                    break

            if pinnable_message is None:
                pinnable_message = await channel.send("Pinnable Message:\n")

            # Append the message link and summary to the "Pinnable Message" in a well formatted way
            await pinnable_message.edit(content=pinnable_message.content + f"\n📌 {summary}")
