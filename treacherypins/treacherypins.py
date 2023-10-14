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
        message = await ctx.send(f"__**{ctx.channel.name} Pinboard**__") # Send a new message with the channel name as the content
        await message.pin() # Pin the message to the current channel
        self.pinboards[ctx.channel.id] = message.id # Store the pinboard message ID in the dictionary
        await ctx.send("A new pinboard has been created and pinned.")

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
                
                def check_message(message):
                    """A function that checks if

the message is a valid response to the prompt."""
                    return message.author != self.bot.user and message.channel.id in self.pinboards and payload.message_id == message.id # Return True if the message is not from the bot, is in a channel with a pinboard, and matches the message ID that received the push pin reaction

                await self.on_message(await self.bot.wait_for("message", check=check_message), payload.message_id) # Wait for a message that passes the check function and pass it along with the local variable to the on_message listener

    @commands.Cog.listener()
    async def on_message(self, message, message_to_pin): 
        """Handles

the message events."""
        if not hasattr(self, "message_to_pin"): 
            return 
        if message.author == self.bot.user: 
            return
        if message.channel.id in self.pinboards: 

            
            pinboard_id = self.pinboards[message.channel.id] 
            pinboard = await message.channel.fetch_message(pinboard_id) 
            embeds = pinboard.embeds 
            embed = Embed(title=message.content, url=message.jump_url) 
            embeds.append(embed) 
            await pinboard.edit(embeds=embeds) 
            
            confirmation = await message.channel.send(f"{message.author.mention}'s pin has been successfully added to {message.channel.name} Pinboard.") 
            await confirmation.add_reaction("✅") 
            
            await asyncio.sleep(5) 
            
            prompt = await message.channel.history(limit=2).flatten() 
            for msg in prompt:
                await msg.delete() 
            
            await message.delete() 
