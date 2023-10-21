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
        self.pin_limit = 49 # The pin limit of a channel, excluding the extended pins message
        self.extended_pins = {} # A dictionary that maps channel IDs to extended pins messages IDs
        self.pin_check.start() # Start the background task that checks for new pins

    def cog_unload(self):
        self.pin_check.cancel() # Stop the background task when the cog is unloaded

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

    @tasks.loop(seconds=10) # Run this task every 10 seconds
    async def pin_check(self):
        """Checks for new pins in channels that have an extended pins message and updates them accordingly."""
        # Loop through all the channels that have an extended pins message
        for channel_id, message_id in self.extended_pins.items():
            # Get the channel and the message objects
            channel = self.bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)
            
            # Get the list of pinned messages in the channel
            pinned_messages = await channel.pins()
            
            # Check if there are 49 pinned messages in the channel, excluding the extended pins message
            if len(pinned_messages) - 1 == self.pin_limit:
                # Get the last pinned message (the newest one)
                last_pin = pinned_messages[0]
                
                # Check if the last pin is the extended pins message
                if last_pin.id == message.id: # Added this line to skip the extended pins message
                    continue # Skip this iteration of the loop
                
                # Prompt the user who pinned it for a description
                await channel.send(f"{last_pin.pinner.mention}, please provide a description for your pin.") # Changed this line to use last_pin.pinner instead of last_pin.author
                
                # Wait for a response from the user
                try:
                    response = await self.bot.wait_for('message', check=lambda m: m.author == last_pin.pinner and m.channel == channel, timeout=30) # Changed this line to use last_pin.pinner instead of last_pin.author
                except asyncio.TimeoutError: # Changed this line to use asyncio.TimeoutError exception
                    # If no response is received within 30 seconds, use a default description
                    description = "No description provided."
                else:
                    # If a response is received, use it as the description
                    description = response.content
                
                # Get the link of the last pinned message
                link = last_pin.jump_url
                
                # Update the extended pins message by adding the description and the link at the top
                content = message.content + f"\n- {description}: {link}"
                await message.edit(content=content)
                
                # Remove the last pinned message from the channel
                await last_pin.unpin()
                
                # Send a confirmation message
                await channel.send("Updated the extended pins message and removed the last pin from the channel.")

    @commands.command() # Added this line to define a new command called pinnumber
    async def pinnumber(self, ctx):
        """Shows the current total number of pins in the channel."""
        # Get the list of pinned messages in the channel
        pinned_messages = await ctx.channel.pins()
        
        # Get the number of pinned messages in the channel
        pin_count = len(pinned_messages)
        
        # Send a message with the pin count
        await ctx.send(f"There are currently {pin_count} pins in this channel.")
