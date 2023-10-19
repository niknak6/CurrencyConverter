# Import discord and the commands extension
import discord
from redbot.core import commands

# Create a class for the cog
class TreacheryPins(commands.Cog):
    """A cog that allows users to pin messages to a channel-specific pinboard."""

    # Initialize the cog with the bot instance
    def __init__(self, bot):
        self.bot = bot
        # Create a dictionary to store the pinboard messages by channel id
        self.pinboards = {}
        # Create a dictionary to store the pinboard emojis by guild id
        self.pinboard_emojis = {}

    # Create a command to create a pinboard message in the current channel
    @commands.command()
    @commands.has_permissions(administrator=True) # Check for Administrator permission
    async def createpinboard(self, ctx):
        """Create a pinboard message in the current channel."""
        # Check if there is already a pinboard message in the current channel
        if ctx.channel.id in self.pinboards:
            # If yes, send an error message
            await ctx.send("There is already a pinboard message in this channel.")
        else:
            # If no, create a new message with the title "Treachery Pin Board"
            pinboard = await ctx.send("Treachery Pin Board")
            # Pin the message
            await pinboard.pin()
            # Save the message id in the dictionary by channel id
            self.pinboards[ctx.channel.id] = pinboard.id
            # Send a confirmation message
            await ctx.send("Pinboard message created and pinned.")

    # Create a command to remove the pinboard message from the current channel
    @commands.command()
    @commands.has_permissions(administrator=True) # Check for Administrator permission
    async def removepinboard(self, ctx):
        """Remove the pinboard message from the current channel."""
        # Check if there is a pinboard message in the current channel
        if ctx.channel.id in self.pinboards:
            # If yes, get the message object by id
            pinboard = await ctx.channel.fetch_message(self.pinboards[ctx.channel.id])
            # Unpin the message
            await pinboard.unpin()
            # Delete the message
            await pinboard.delete()
            # Remove the channel id from the dictionary
            del self.pinboards[ctx.channel.id]
            # Send a confirmation message
            await ctx.send("Pinboard message removed and unpinned.")
        else:
            # If no, send an error message
            await ctx.send("There is no pinboard message in this channel.")

    # Create a command to set the pinboard emoji for the current guild
    @commands.command()
    @commands.has_permissions(administrator=True) # Check for Administrator permission
    async def pinboardemoji(self, ctx, emoji: discord.PartialEmoji):
        """Set the pinboard emoji for the current guild."""
        # Save the emoji in the dictionary by guild id
        self.pinboard_emojis[ctx.guild.id] = emoji
        # Send a confirmation message
        await ctx.send(f"Pinboard emoji set to {emoji}.")

    # Create a listener for reaction add events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions to messages."""
        # Get the channel object by id
        channel = self.bot.get_channel(payload.channel_id)
        # Check if the channel has a pinboard message
        if channel.id in self.pinboards:
            # Get the guild object by id
            guild = self.bot.get_guild(payload.guild_id)
            # Check if the guild has a pinboard emoji
            if guild.id in self.pinboard_emojis:
                # Get the emoji object by id
                emoji = self.pinboard_emojis[guild.id]
                # Check if the reaction emoji matches the pinboard emoji
                if payload.emoji == emoji:
                    # Get the user object by id
                    user = self.bot.get_user(payload.user_id)
                    # Check if the user is not a bot and not an admin
                    if not user.bot and not user.guild_permissions.administrator:
                        # Get the message object by id
                        message = await channel.fetch_message(payload.message_id)
                        # Get the pinboard message object by id
                        pinboard = await channel.fetch_message(self.pinboards[channel.id])
                        # Send a prompt message to the user for a description of the message to pin
                        prompt = await user.send(f"You reacted to a message with {emoji}. Please provide a description of the message to pin.")
                        # Wait for the user's response
                        try:
                            response = await self.bot.wait_for("message", check=lambda m: m.author == user and m.channel == prompt.channel, timeout=60)
                        except asyncio.TimeoutError:
                            # If the user does not respond in time, send an error message
                            await user.send("You did not provide a description in time. Pin aborted.")
                        else:
                            # If the user responds, get the description from the message content
                            description = response.content
                            # Edit the pinboard message to add a new line with the description and the message link
                            await pinboard.edit(content=pinboard.content + f"\n{description}: {message.jump_url}")
                            # Send a confirmation message to the user
                            await user.send("Pin successfully added!")
