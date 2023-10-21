# Import the discord and commands modules from discord.py
import discord
from discord.ext import commands

# Import the necessary modules
from redbot.core import commands
from discord.ext import tasks
import discord

# Define the cog class
class PinExtender(commands.Cog):
    """A cog that extends the pin limit of a channel by using a pinned message as a container for more pins."""

    def __init__(self, bot):
        self.bot = bot
        self.pin_limit = 50 # The pin limit of a channel
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
            
            # Check if there are 50 pinned messages in the channel
            if len(pinned_messages) == self.pin_limit:
                # Get the last pinned message (the newest one)
                last_pin = pinned_messages[0]
                
                # Prompt the user who pinned it for a description
                await channel.send(f"{last_pin.author.mention}, please provide a description for your pin.")
                
                # Wait for a response from the user
                try:
                    response = await self.bot.wait_for('message', check=lambda m: m.author == last_pin.author and m.channel == channel, timeout=30)
                except asyncio.TimeoutError:
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
