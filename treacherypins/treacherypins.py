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
            
            pinboard = await ctx.channel.fetch_message(pinboard_id) # Fetch the pinboard message object
            await pinboard.unpin() # Unpin the pinboard message from the channel
            
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
                message_to_pin = payload.message_id # Store the message ID that received the push pin reaction in a local variable

                def check_message(message):
                    """A function that checks if the message is a valid response to the prompt."""
                    return message.author != self.bot.user and message.channel.id in self.pinboards and message_to_pin == self.message_to_pin # Return True if the message is not from the bot, is in a channel with a pinboard, and matches the message ID that received the push pin reaction

                await self.bot.wait_for("message", check=check_message) # Wait for a message that passes the check function

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles the message events."""
        if not hasattr(self, "message_to_pin"): # Check if there is a message ID stored in self.message_to_pin 
            return # If not, return early 
        if message.author == self.bot.user: # Ignore messages from the bot
            return
        if message.channel.id in self.pinboards: # Check if

            await self.bot.wait_for("message", check=self.check_message) # Wait for a message that passes the check function
            
            pinboard_id = self.pinboards[message.channel.id] # Get the pinboard message ID
            pinboard = await message.channel.fetch_message(pinboard_id) # Fetch the pinboard message object
            embeds = pinboard.embeds # Get the list of embeds in the pinboard message
            message_to_pin = await message.channel.fetch_message(message_to_pin) # Fetch the message object that received the push pin reaction using the local variable # MODIFIED
            embed = Embed(title=message.content, url=message_to_pin.jump_url) # Create a new embed with the message subject and link to the message to be pinned
            embeds.append(embed) # Append the new embed to the list of embeds
            await pinboard.edit(embeds=embeds) # Edit the pinboard message with the updated list of embeds
            
            confirmation = await message.channel.send(f"{message.author.mention}'s pin has been successfully added to {message.channel.name} Pinboard.") # Send a new message to confirm that the message has been added to the pinboard
            await confirmation.add_reaction("✅") # Add a green checkmark reaction to the confirmation message
            
            await asyncio.sleep(5) # Wait for 5 seconds
            
            prompt = await message.channel.history(limit=2).flatten() # Get the last two messages in the channel, which are the prompt and confirmation messages
            await prompt[0].delete() # Delete the confirmation message
            await prompt[1].delete() # Delete the prompt message
            
            await message.delete() # Delete the user's response
