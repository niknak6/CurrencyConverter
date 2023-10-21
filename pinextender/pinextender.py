# Import the necessary modules
from redbot.core import commands
from discord.ext import tasks
import discord

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

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Updates the extended pins message when a new pin is added to a channel."""
        # Check if the message is pinned
        if after.pinned:
            # Get the channel ID and message ID from the message object
            channel_id = after.channel.id
            message_id = after.id
            
            # Check if the channel has an extended pins message
            if channel_id in self.extended_pins:
                # Get the guild ID from the message object
                guild_id = after.guild.id
                
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
                    
                    # Check if new_pin is not None and is not the extended pins message (to avoid errors when unpinning or editing)
                    if new_pin and new_pin.id != message.id: 

                        # Get or fetch (if not cached) who pinned or edited it from their ID 
                        pinner = before.author or await guild.fetch_member(before.author.id)

                        # Prompt who pinned or edited it for a description 
                        await channel.send(f"{pinner.display_name}, please provide a description for your pin.") 

                        # Wait for a response from who pinned or edited it 
                        try:
                            response = await self.bot.wait_for('message', check=lambda m: m.author == pinner and m.channel == channel, timeout=30) 
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
                        await channel.unpin(new_pin)
                    
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
