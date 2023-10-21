# Import the necessary modules
from redbot.core import commands
from discord.ext import tasks
import discord
import asyncio # Added this line to import the asyncio module

# Define the cog class
class PinExtender(commands.Cog):
    """A cog that extends the pin limit of a channel by using a pinned message as a container for more pins."""

    def __init__(self, bot):
        self.bot = bot
        self.pin_limit = 50 # The pin limit of a channel, as per Discord's documentation
        self.extended_pins = {} # A dictionary that maps channel IDs to extended pins messages IDs

    def cog_unload(self):
        pass # No need to cancel the task loop since we are not using it anymore

    @commands.command()
    async def pinextender(self, ctx):
        """Creates an extended pins message in the current channel and pins it."""
        # Check if the channel already has an extended pins message
        if ctx.channel.id in self.extended_pins:
            await ctx.send("This channel already has an extended pins message.")
            return
        
        # Create the extended pins message and pin it
        message = await ctx.send("**Extended Pins**\n")
        await message.pin()
        
        # Store the message ID in the dictionary
        self.extended_pins[ctx.channel.id] = message.id
        
        # Send a confirmation message
        await ctx.send("Created and pinned an extended pins message in this channel.")

    @commands.Cog.listener() # Added this line to register a listener for the on_raw_message_edit event
    async def on_raw_message_edit(self, payload): # Added this method to handle the event when a message is edited
        """Updates the extended pins message when a new pin is added to a channel."""
        # Check if there is any data in payload.data (the raw data of an edited message)
        if payload.data:
            # Check if there is any data in payload.data['flags'] (the flags of an edited message)
            if payload.data['flags']:
                # Check if payload.data['flags'] has 4 as one of its values (the value for a pinned message)
                if 4 in payload.data['flags']:
                    # Get the channel ID and message ID from payload.data
                    channel_id = int(payload.data['channel_id'])
                    message_id = int(payload.data['id'])
                    
                    # Check if the channel has an extended pins message
                    if channel_id in self.extended_pins:
                        # Get the guild ID from payload.data
                        guild_id = int(payload.data['guild_id'])
                        
                        # Get the guild and channel objects from their IDs
                        guild = self.bot.get_guild(guild_id)
                        channel = guild.get_channel(channel_id)
                        
                        # Try to fetch the extended pins message from the channel
                        try:
                            message = await channel.fetch_message(self.extended_pins[channel_id])
                        except discord.NotFound: # Handle the case when the message is not found
                            del self.extended_pins[channel_id] # Delete the entry from the dictionary if the message is deleted
                            return # Return from the method if the message is deleted
                        except discord.Forbidden: # Handle the case when the bot lacks permissions
                            await channel.send("I do not have permission to access pinned messages in this channel.") # Send an error message to inform the user
                            return # Return from the method if the bot lacks permissions
                        
                        # Get the list of pinned messages in the channel
                        pinned_messages = await channel.pins()
                        
                        # Check if there are 50 or more pinned messages in the channel, including the extended pins message
                        if len(pinned_messages) >= self.pin_limit: 
                            # Fetch the new pin message from the channel using its ID
                            new_pin = await channel.fetch_message(message_id)
                            
                            # Check if the new pin is the extended pins message
                            if new_pin.id == message.id: 
                                return # Return from the method if it is

                            # Get the user ID of who pinned the message from payload.data['pinner_id'] (the ID of who pinned it) 
                            pinner_id = int(payload.data['pinner_id']) 

                            # Get the user object of who pinned it from their ID 
                            pinner = guild.get_member(pinner_id) 

                            # Prompt who pinned it for a description 
                            await channel.send(f"{pinner.mention}, please provide a description for your pin.")  # Changed this line to use pinner instead of new_pin.author

                            # Wait for a response from who pinned it 
                            try:
                                response = await self.bot.wait_for('message', check=lambda m: m.author == pinner and m.channel == channel, timeout=30)  # Changed this line to use pinner instead of new_pin.author
                            except asyncio.TimeoutError: 
                                # If no response is received within 30 seconds, use a default description
                                description = "No description provided."
                            else:
                                # If a response is received, use it as the description
                                description = response.content
                            
                            # Get the link of the new pin message
                            link = new_pin.jump_url
                            
                            # Update the extended pins message by adding the description and the link at the top
                            content = message.content + f"\n- {description}: {link}"
                            await message.edit(content=content)
                            
                            # Remove the new pin message from the channel
                            await new_pin.unpin()
                            
                            # Send a confirmation message
                            await channel.send("Updated the extended pins message and removed the new pin from the channel.")

    @commands.command() 
    async def pinnumber(self, ctx):
        """Shows the current total number of pins in the channel."""
        # Get the list of pinned messages in the channel
        pinned_messages = await ctx.channel.pins()
        
        # Get the number of pinned messages in the channel
        pin_count = len(pinned_messages)
        
        # Send a message with the pin count
        await ctx.send(f"There are currently {pin_count} pins in this channel.")
