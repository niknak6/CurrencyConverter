from redbot.core import commands
from discord import Embed
import asyncio

class TreacheryPins(commands.Cog):
    """A cog that allows users to create a pinboard of messages."""

    def __init__(self, bot):
        self.bot = bot
        self.pinboards = {} # A dictionary that maps channel IDs to pinboard message IDs

    @commands.command()
    async def pinboard(self, ctx):
        """Creates a new Treachery Pinboard and pins it to the current channel."""
        try:
            message = await ctx.send(f"__**{ctx.channel.name} Pinboard**__") # Send a new message with the channel name as the content
            await message.pin() # Pin the message to the current channel
            self.pinboards[ctx.channel.id] = message.id # Store the pinboard message ID in the dictionary
            await ctx.send("A new pinboard has been created and pinned.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command()
    async def removepinboard(self, ctx):
        """Removes the current Treachery Pinboard."""
        if ctx.channel.id in self.pinboards: # Check if the channel has a pinboard
            pinboard_id = self.pinboards[ctx.channel.id] # Get the pinboard message ID
            del self.pinboards[ctx.channel.id] # Delete the pinboard message ID from the dictionary
            await ctx.send(f"The pinboard with ID {pinboard_id} has been removed.")
        else:
            await ctx.send("There is no pinboard in this channel.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handles the reaction events."""
        if payload.user_id == self.bot.user.id: # Ignore reactions from the bot
            return
        if payload.emoji.name == "📌": # Check if the reaction is a push pin emoji
            if payload.channel_id in self.pinboards: # Check if the channel has a pinboard
                channel = self.bot.get_channel(payload.channel_id) # Get the channel object
                user = self.bot.get_user(payload.user_id) # Get the user object
                await channel.send(f"{user.mention}, please reply with the subject of the message you want to pin.") # Prompt the user for the message subject
                self.bot.add_listener(self.on_message, "on_message") # Add a listener for the message event
                self.message_to_pin = payload.message_id # Store the message ID that received the push pin reaction

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles the message events."""
        if message.author == self.bot.user: # Ignore messages from the bot
            return
        if message.channel.id in self.pinboards: # Check if the channel has a pinboard
            pinboard_id = self.pinboards[message.channel.id] # Get the pinboard message ID
            pinboard = await message.channel.fetch_message(pinboard_id) # Fetch the pinboard message object
            embeds = pinboard.embeds # Get the list of embeds in the pinboard message
            message_to_pin = await message.channel.fetch_message(self.message_to_pin) # Fetch the message object that received the push pin reaction
            embed = Embed(title=message.content, url=message_to_pin.jump_url) # Create a new embed with the message subject and link to the message to be pinned
            embeds.append(embed) # Append the new embed to the list of embeds
            await pinboard.edit(embeds=embeds) # Edit the pinboard message with the updated list of embeds
            self.bot.remove_listener(self.on_message, "on_message") # Remove the listener for the message event
            prompt = await message.channel.history(limit=1).flatten() # Get the last message in the channel, which is the prompt for the subject
            await prompt[0].edit(content=f"{message.author.mention}'s pin has been successfully added to {ctx.channel.name} Pinboard. ✅") # Edit the prompt to confirm that the message has been added to the pinboard with a checkmark emoji
            await asyncio.sleep(5) # Wait for 5 seconds
            await prompt[0].delete() # Delete the prompt
            await message.delete() # Delete the user's response
