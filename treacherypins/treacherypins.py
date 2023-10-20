# treacherypins.py

from redbot.core import commands, checks, Config
import discord

class TreacheryPins(commands.Cog):
    """A cog that allows users to pin messages to a channel-specific pinboard."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        # Register the default settings for each guild
        self.config.register_guild(
            pinboard=None, # The message ID of the pinboard
            emoji="📌" # The emoji used to react and pin messages
        )

    @commands.group()
    @checks.admin_or_permissions(administrator=True)
    async def treacherypins(self, ctx):
        """Manage the settings for the treacherypins cog."""
        pass

    @treacherypins.command(name="createpinboard")
    async def create_pinboard(self, ctx):
        """Create a pinboard message in the current channel and pin it."""
        # Check if there is already a pinboard in this channel
        pinboard = await self.config.guild(ctx.guild).pinboard()
        if pinboard is not None:
            return await ctx.send("There is already a pinboard in this channel. Use `removepinboard` to delete it first.")
        # Create a new message with the title "Treachery Pin Board"
        message = await ctx.send("Treachery Pin Board")
        # Pin the message
        await message.pin()
        # Save the message ID as the pinboard for this channel
        await self.config.guild(ctx.guild).pinboard.set(message.id)
        # Notify the user that the pinboard has been created
        await ctx.send("The pinboard has been created and pinned in this channel.")

    @treacherypins.command(name="removepinboard")
    async def remove_pinboard(self, ctx):
        """Remove the pinboard message from the current channel and unpin it."""
        # Check if there is a pinboard in this channel
        pinboard = await self.config.guild(ctx.guild).pinboard()
        if pinboard is None:
            return await ctx.send("There is no pinboard in this channel. Use `createpinboard` to create one.")
        # Fetch the message with the pinboard ID
        try:
            message = await ctx.channel.fetch_message(pinboard)
        except discord.NotFound:
            return await ctx.send("The pinboard message could not be found. It may have been deleted manually.")
        # Unpin the message
        await message.unpin()
        # Delete the message
        await message.delete()
        # Clear the pinboard setting for this channel
        await self.config.guild(ctx.guild).pinboard.clear()
        # Notify the user that the pinboard has been removed
        await ctx.send("The pinboard has been removed and unpinned from this channel.")

    @treacherypins.command(name="pinboardemoji")
    async def set_pinboard_emoji(self, ctx, emoji: str):
        """Set the emoji used to react and pin messages to the pinboard. Default is 📌."""
        # Check if the emoji is valid
        try:
            await ctx.message.add_reaction(emoji)
            await ctx.message.remove_reaction(emoji, ctx.me)
        except discord.HTTPException:
            return await ctx.send("That is not a valid emoji. Please use a standard or custom emoji.")
        # Save the emoji as the setting for this guild
        await self.config.guild(ctx.guild).emoji.set(emoji)
        # Notify the user that the emoji has been changed
        await ctx.send(f"The emoji used to react and pin messages has been changed to {emoji}.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle reactions to messages and add pins to the pinboard."""
        # Ignore reactions from bots
        if payload.member.bot:
            return
        # Ignore reactions in DMs
        if not payload.guild_id:
            return
        # Get the guild and channel objects
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        # Check if there is a pinboard in this channel
        pinboard = await self.config.guild(guild).pinboard()
        if pinboard is None:
            return
        # Check if the reaction emoji matches the setting for this guild
        emoji = await self.config.guild(guild).emoji()
        if str(payload.emoji) != emoji:
            return
