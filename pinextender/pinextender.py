# Import the necessary modules
from redbot.core import commands
from discord.ext import tasks
import discord
import logging
import datetime # Import the datetime module

# Define constants
PIN_LIMIT = 50 # The pin limit of a channel, as per Discord's documentation
EXTENDED_PINS_CONTENT = "**Extended Pins**\n" # The content of the extended pins message

# Define a logger
log = logging.getLogger("red.pinextender")

# Define a check for bot permissions
def bot_has_manage_messages():
    """A check that ensures that the bot has manage messages permission."""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        return ctx.channel.permissions_for(ctx.guild.me).manage_messages
    return commands.check(predicate)

# Define a check for guild only
def guild_only():
    """A check that ensures that the command is invoked in a guild."""
    async def predicate(ctx):
        return ctx.guild is not None
    return commands.check(predicate)

# Define a check for owner only
def owner_only():
    """A check that ensures that the command is invoked by the owner."""
    return commands.check(commands.is_owner())

# Define a cog class
class PinExtender(commands.Cog):
    """A cog that extends the pin limit of a channel by using a pinned message as a container for more pins."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.extended_pins: Dict[int, int] = {} # A dictionary that maps channel IDs to extended pins messages IDs

    def cog_unload(self):
        pass # No need to cancel the task loop since we are not using it anymore

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def pinextender(self, ctx: commands.Context):
        """Creates an extended pins message in the current channel and pins it."""
        # Check if the channel already has an extended pins message
        if ctx.channel.id in self.extended_pins:
            await ctx.send("This channel already has an extended pins message.")
            return
        
        # Create the extended pins message and pin it
        message = await ctx.reply(EXTENDED_PINS_CONTENT)
        await message.pin()
        
        # Store the message ID in the dictionary
        self.extended_pins[ctx.channel.id] = message.id
        
        # Send a confirmation message
        await ctx.send("Created and pinned an extended pins message in this channel.")

    @commands.Cog.listener()
    @bot_has_manage_messages()
    async def on_guild_channel_pins_update(self, channel: discord.TextChannel, last_pin: datetime.datetime):
        """Updates the extended pins message when a new pin is added to a channel."""
        # Get the channel ID from the channel object
        channel_id = channel.id
        
        # Check if the channel has an extended pins message
        if channel_id in self.extended_pins:
            # Get the guild ID from the channel object
            guild_id = channel.guild.id
            
            # Get the guild object from its ID
            guild = self.bot.get_guild(guild_id)
            
            # Try to fetch the extended pins message from the channel
            try:
                message = await channel.fetch_message(self.extended_pins[channel_id])
            except discord.NotFound: # Handle the case when the message is not found
                del self.extended_pins[channel_id] # Delete the entry from the dictionary if the message is deleted
                return # Return from the method if the message is deleted
            except discord.Forbidden: # Handle the case when the bot lacks permissions
                log.error(f"I do not have permission to access pinned messages in {channel}.") # Log an error message to inform the owner
                return # Return from the method if the bot lacks permissions
            
            # Get the list of pinned messages in the channel
            pinned_messages = await channel.pins()
            
            # Check if there are 50 or more pinned messages in the channel, including the extended pins message
            if len(pinned_messages) >= PIN_LIMIT: 
                # Get the new pin message from the list of pinned messages using its index
                new_pin = pinned_messages[0]
                
                # Check if new_pin is not None and is not the extended pins message (to avoid errors when unpinning or editing)
                if new_pin and new_pin.id != message.id: 

                    # Get or fetch (if not cached) who pinned it from their ID using the audit log entry for the pin action
                    audit_log_entries = guild.audit_logs(action=discord.AuditLogAction.message_pin) # Get the audit log entries for the pin action
                    async for entry in audit_log_entries: # Use an async for loop to iterate over the async generator
                        break # Exit the loop after getting the first entry
                    pinner = entry.user or await self.bot.fetch_user(entry.user.id) # Get the user object from the audit log entry

                    # Prompt who pinned it for a description 
                    await new_pin.channel.send(f"{pinner.display_name}, please provide a description for your pin.") 

                    # Wait for a response from who pinned it 
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
                    content = EXTENDED_PINS_CONTENT + f"\n- {description}: {link}"
                    await message.edit(content=content)
                    
                    # Try to unpin the new pin message from the channel
                    try:
                        await new_pin.unpin()
                    except discord.NotFound:
                        # Handle the case when the message is not found
                        log.error(f"The new pin {new_pin} was not found in {channel}.") # Log an error message to inform the owner
                    except discord.Forbidden:
                        # Handle the case when the bot lacks permissions
                        log.error(f"I do not have permission to unpin messages in {channel}.") # Log an error message to inform the owner
                    else:
                        # Send a confirmation message
                        await new_pin.channel.send("Updated the extended pins message and removed the new pin from the channel.")

    @commands.command() 
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def pinnumber(self, ctx: commands.Context):
        """Shows the current total number of pins in the channel."""
        # Get the list of pinned messages in the channel
        pinned_messages = await ctx.channel.pins()
        
        # Get the number of pinned messages in the channel
        pin_count = len(pinned_messages)
        
        # Send a message with the pin count
        await ctx.send(f"There are currently {pin_count} pins in this channel.")
