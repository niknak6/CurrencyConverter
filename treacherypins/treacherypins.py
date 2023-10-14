# Import the required modules
from redbot.core import commands, checks, Config
import discord

# Define the cog class
class TreacheryPins(commands.Cog):
    """A cog that creates pinboards for messages"""

    # Initialize the cog
    def __init__(self, bot):
        self.bot = bot
        # Create a config object to store the pinboard data
        self.config = Config.get_conf(self, identifier=1234567890)
        # Register the pinboard data as a dict with channel IDs as keys and message IDs as values
        self.config.register_global(pinboards={})

    # Define a command to create a pinboard in the current channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def pinboard(self, ctx):
        """Create a new pinboard in this channel and pin it"""
        # Check if there is already a pinboard in this channel
        pinboards = await self.config.pinboards()
        if ctx.channel.id in pinboards:
            await ctx.send("There is already a pinboard in this channel.")
            return
        # Create a new message with the title "Pinboard" and an empty description
        embed = discord.Embed(title="Pinboard", description="")
        message = await ctx.send(embed=embed)
        # Pin the message to the channel
        await message.pin()
        # Save the message ID as the pinboard for this channel
        pinboards[ctx.channel.id] = message.id
        await self.config.pinboards.set(pinboards)
        await ctx.send("Pinboard created and pinned.")

    # Define a command to remove the pinboard in the current channel
    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def removepinboard(self, ctx):
        """Remove the current pinboard in this channel"""
        # Check if there is a pinboard in this channel
        pinboards = await self.config.pinboards()
        if ctx.channel.id not in pinboards:
            await ctx.send("There is no pinboard in this channel.")
            return
        # Get the message ID of the pinboard
        message_id = pinboards[ctx.channel.id]
        # Try to fetch the message from the channel history
        try:
            message = await ctx.channel.fetch_message(message_id)
            # Unpin and delete the message
            await message.unpin()
            await message.delete()
            await ctx.send("Pinboard removed.")
        except discord.NotFound:
            # The message was not found, so just delete the data
            await ctx.send("Pinboard not found. Deleting data.")
        # Delete the pinboard data for this channel
        del pinboards[ctx.channel.id]
        await self.config.pinboards.set(pinboards)

    # Define a listener for reaction add events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Add a message to the pinboard when reacted with a push pin emoji"""
        # Check if the reaction is a push pin emoji
        if payload.emoji.name != "📌":
            return
        # Check if the reaction is in a channel with a pinboard
        pinboards = await self.config.pinboards()
        if payload.channel_id not in pinboards:
            return
        # Try to fetch the message that received the reaction from the channel history
        try:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            # Pass the message to the on_message listener
            await self.on_message(message)
        except discord.NotFound:
            # The message was not found, so do nothing
            return

    # Define a listener for message events
    @commands.Cog.listener()
    async def on_message(self, message):
        """Add an embed of the message content to the pinboard"""
        # Check if the message is not from the bot and in a channel with a pinboard
        if message.author == self.bot.user:
            return
        pinboards = await self.config.pinboards()
        if message.channel.id not in pinboards:
            return
        # Get the message ID of the pinboard
        message_id = pinboards[message.channel.id]
        # Try to fetch the pinboard message from the channel history
        try:
            pin_message = await message.channel.fetch_message(message_id)
            # Create an embed of the original message content with author, timestamp, and attachments
            embed = discord.Embed(description=message.content, timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            if message.attachments:
                embed.set_image(url=message.attachments[0].url)
            # Edit the pinboard message and append the embed to the description
            pin_embed = pin_message.embeds[0]
            pin_embed.description += f"\n\n{embed.to_dict()}"
            await pin_message.edit(embed=pin_embed)
            # Send a confirmation message and react with a checkmark emoji
            confirm = await message.channel.send("Message added to the pinboard.")
            await confirm.add_reaction("✅")
            # Wait for 5 seconds and delete the last two messages in the channel history
            await asyncio.sleep(5)
            await message.channel.purge(limit=2)
            # Delete the original message
            await message.delete()
        except discord.NotFound:
            # The pinboard message was not found, so do nothing
            return
