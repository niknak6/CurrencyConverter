# Import the discord.py library and the commands module
import discord
from redbot.core import commands

# Import the datetime module for formatting timestamps
import datetime

# Import the checks module for checking permissions
from redbot.core import checks

# Create a cog class that inherits from commands.Cog
class TreacheryPins(commands.Cog):
    """A cog that allows users to pin messages with a push pin emoji."""

    # Define the name and description of the cog
    def __init__(self, bot):
        self.bot = bot
        self.name = "TreacheryPins"
        self.description = "A cog that allows users to pin messages with a push pin emoji."

        # Define a variable to store the ID of the "Pinnable Message" in each channel
        # You can also use a database instead of a variable
        self.pinnable_message_id = {}

        # Define a variable to store the user who reacted with a push pin in each channel
        # You can also use a database instead of a variable
        self.push_pin_user = {}

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
            # Send a message to the user who reacted, asking them to provide a summary of the message they are pinning
            await user.send(f"You have reacted with a push pin emoji to this message:\n{message.content}\nPlease reply with a summary of this message that you want to pin.")

            # Store the user who reacted with a push pin in the variable or database
            self.push_pin_user[channel.id] = user

    # Create another listener function that listens for the on_message event
    @commands.Cog.listener()
    async def on_message(self, message):
        """This event is triggered when a user sends a message in any channel."""

        # Get the guild, channel, and author objects from the message
        guild = message.guild
        channel = message.channel
        author = message.author

        # Check if the message author is the same user who reacted with a push pin in this channel, and if the message content is not empty
        if author == self.push_pin_user.get(channel.id) and message.content:
            # Get the message link and summary from the message object
            message_link = message.jump_url
            summary = f"{author.display_name}: {message.content}"

            # Get the "Pinnable Message" by its ID, which is stored in the variable or database
            pinnable_message_id = self.pinnable_message_id.get(channel.id)
            if pinnable_message_id is not None:
                pinnable_message = await channel.fetch_message(pinnable_message_id)

                # Append the message link and summary to the "Pinnable Message" in a well formatted way
                await pinnable_message.edit(content=pinnable_message.content + f"\n📌 {summary}")

            # Delete the message that contains the summary, so that it does not clutter the channel
            await message.delete()

    # Create a command function that allows an admin to set the "Pinnable Message" in the current channel
    @commands.command()
    @checks.admin_or_permissions(manage_messages=True)
    async def setpinnable(self, ctx):
        """This command allows an admin to set the "Pinnable Message" in the current channel."""

        # Get the bot, channel, and guild objects from the context
        bot = ctx.bot
        channel = ctx.channel
        guild = ctx.guild

        # Check if there is already a "Pinnable Message" in the channel
        pinnable_message_id = self.pinnable_message_id.get(channel.id)
        if pinnable_message_id is not None:
            # Delete the old "Pinnable Message"
            pinnable_message = await channel.fetch_message(pinnable_message_id)
            await pinnable_message.delete()

        # Create a new "Pinnable Message" in the channel
        pinnable_message = await channel.send("Pinnable Message:\n")

        # Store the ID of the new "Pinnable Message" in the variable or database
        self.pinnable_message_id[channel.id] = pinnable_message.id

        # Send a confirmation message to the user
        await ctx.send(f"{ctx.author.mention}, you have successfully set the Pinnable Message in this channel.")

