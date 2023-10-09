# Import the discord.py library and the commands module
import discord
from redbot.core import commands

# Import the datetime module for formatting timestamps
import datetime

# Import the checks module for checking permissions
from redbot.core import checks

# Import asyncio for creating tasks and timers
import asyncio

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
        self.push_pin_user = {}

        # Define a variable to store the channel where the reaction happened for each user
        self.push_pin_channel = {}

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
            # Send a message to the channel where the reaction happened, tagging the user who reacted and asking them to provide a summary of the message they are pinning
            request_message = await channel.send(f"{user.mention}, you have reacted with a push pin emoji to this message:\n{message.content}\nPlease reply with a summary of this message that you want to pin.")

            # Store the user who reacted with a push pin in the variable or database
            self.push_pin_user[channel.id] = user

            # Store the channel where the reaction happened in the variable or database
            self.push_pin_channel[user.id] = channel.id

            # Create a task that waits for 3 minutes and then checks if there is a response
            task = asyncio.create_task(self.wait_for_response(user, request_message))

    # Create another listener function that listens for the on_message event
    @commands.Cog.listener()
    async def on_message(self, message):
        """This event is triggered when a user sends a message in any channel."""

        # Get the guild, channel, and author objects from the message
        guild = message.guild
        channel = message.channel
        author = message.author

        # Check if the message author is tagged by the bot in the previous message in this channel, and if the message content is not empty, and if the message is in the same channel as the reaction, and if the message is a reply to the bot's request
        
        previous_message = await channel.history(limit=1, before=message).__anext__() # use __anext__() to get the next value from an async generator
        
        # Check if the message.reference is not None before comparing the message IDs
        if author in previous_message.mentions and previous_message.author == self.bot and message.content and channel.id == self.push_pin_channel.get(author.id) and message.reference is not None and message.reference.message_id == previous_message.id:
            # Get the message link and summary from the message object
            message_link = message.jump_url
            summary = f"{author.display_name}: {message.content}"

            # Get the "Pinnable Message" by its ID, which is stored in the variable or database
            pinnable_message_id = self.pinnable_message_id.get(channel.id)
            if pinnable_message_id is not None:
                pinnable_message = await channel.fetch_message(pinnable_message_id)

                # Append the message link and summary to the "Pinnable Message" in a well formatted way
                await pinnable_message.edit(content=pinnable_message.content + "\n" + f"📌 {summary}")

            # Delete both messages that contain the summary and the bot's request, so that they do not clutter the channel
            await message.delete()
            await previous_message.delete()

    # Create an async function that waits for 3 minutes and then checks if there is a response
    async def wait_for_response(self, user, request_message):
        """This function waits for 3 minutes and then checks if there is a response."""

        # Wait for 3 minutes using asyncio.sleep
        await asyncio.sleep(180)

        # Get the guild, channel, and author objects from the request message
        guild = request_message.guild
        channel = request_message.channel
        author = request_message.author

        # Check if the user is still tagged by the bot in the previous message in this channel, and if the message content is still empty
        
        previous_message = await channel.history(limit=1, before=request_message).__anext__() # use __anext__() to get the next value from an async generator
        
        if user in previous_message.mentions and previous_message.author == self.bot and not request_message.content:
            # Cancel the task and send a message to inform the user that the time is up
            task.cancel()
            await channel.send(f"{user.mention}, you have not provided a summary of the message that you want to pin within 3 minutes. The request has been cancelled.")

            # Delete both messages that contain the summary and the bot's request, so that they do not clutter the channel
            await request_message.delete()
            await previous_message.delete()

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

        # Pin the "Pinnable Message" to the channel
        await pinnable_message.pin()

        # Send a confirmation message to the user
        await ctx.send(f"{ctx.author.mention}, you have successfully set the Pinnable Message in this channel.")
