import discord
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import humanize_list

class hellotest(commands.Cog):
    """A cog that allows you to create custom pins for messages in your server."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_guild(
            pinned_messages={},
            trigger_emoji="📌"
        )

    @commands.command()
    @commands.mod_or_permissions(manage_messages=True)
    async def pin(self, ctx, message_id: int, channel: discord.TextChannel = None):
        """Pin a message to a specific channel."""
        message = await self.bot.get_message(message_id)
        if not message or message.guild != ctx.guild:
            return await ctx.send("Invalid message ID.")
        channel = channel or ctx.channel
        if not channel or channel.guild != ctx.guild:
            return await ctx.send("Invalid channel.")
        pinned_messages = await self.config.guild(ctx.guild).pinned_messages()
        if channel.id in pinned_messages:
            old_message = await self.bot.get_message(pinned_messages[channel.id])
            if old_message:
                await old_message.unpin()
        await message.pin()
        await self.config.guild(ctx.guild).pinned_messages.set_raw(channel.id, value=message.id)
        await ctx.send("Message pinned successfully.")

    @commands.command()
    @commands.mod_or_permissions(manage_messages=True)
    async def unpin(self, ctx, channel: discord.TextChannel = None):
        """Unpin the message in a specific channel."""
        channel = channel or ctx.channel
        if not channel or channel.guild != ctx.guild:
            return await ctx.send("Invalid channel.")
        pinned_messages = await self.config.guild(ctx.guild).pinned_messages()
        if channel.id not in pinned_messages:
            return await ctx.send("There is no pinned message in this channel.")
        message = await self.bot.get_message(pinned_messages[channel.id])
        if message:
            await message.unpin()
        await self.config.guild(ctx.guild).pinned_messages.clear_raw(channel.id)
        await ctx.send("Message unpinned successfully.")

    @commands.command()
    async def setemoji(self, ctx, emoji: discord.Emoji = None):
        """Set the emoji that triggers the custom pinning."""
        emoji = emoji or "📌"
        if not emoji.is_usable():
            return await ctx.send("Invalid emoji.")
        await self.config.guild(ctx.guild).trigger_emoji.set(emoji.id or emoji.name)
        await ctx.send(f"Emoji set to {emoji} successfully.")

    @commands.command()
    async def listpins(self, ctx):
        """Show a list of all the channels that have a pinned message and the emoji that triggers the custom pinning."""
        pinned_messages = await self.config.guild(ctx.guild).pinned_messages()
        trigger_emoji = await self.config.guild(ctx.guild).trigger_emoji()
        channels = []
        for channel_id, message_id in pinned_messages.items():
            channel = self.bot.get_channel(channel_id)
            if channel and channel.permissions_for(ctx.author).read_messages:
                channels.append(channel.name)
        channels.sort()
        channels = humanize_list(channels)
        await ctx.send(f"The channels with pinned messages are: {channels}. The emoji for custom pinning is {trigger_emoji}.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle adding messages to the pinned message as links with summaries."""
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        trigger_emoji = await self.config.guild(guild).trigger_emoji()
        if payload.emoji.id != trigger_emoji and payload.emoji.name != trigger_emoji:
            return
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        pinned_messages = await self.config.guild(guild).pinned_messages()
        if payload.channel_id not in pinned_messages:
            return
        pinned_message = await self.bot.get_message(pinned_messages[payload.channel_id])
        if not pinned_message:
            return
        reacted_message = await self.bot.get_message(payload.message_id)
        if not reacted_message or reacted_message.author == guild.me:
            return
        summary = reacted_message.content.split(".")[0]
        description = f"{reacted_message.author.mention}: {summary}"
