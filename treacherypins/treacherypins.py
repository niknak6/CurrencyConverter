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

    @commands.command()
    @checks.admin_or_permissions(administrator=True)
    async def createpinboard(self, ctx):
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

    @commands.command()
    @checks.admin_or_permissions(administrator=True)
    async def removepinboard(self, ctx):
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

    @commands.command()
    @checks.admin_or_permissions(administrator=True)
    async def pinboardemoji(self, ctx, emoji: str):
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
         # Get the user object from the payload 
         user = self.bot.get_user(payload.user_id)  # Changed from payload.member 
         if user is None: 
             return 
         # Get the guild and channel objects 
         guild = self.bot.get_guild(payload.guild_id) 
         if guild is None: 
             return 
         channel = guild.get_channel(payload.channel_id) 
         if channel is None: 
             return 
         # Check if there is a pinboard in this channel 
         pinboard = await self.config.guild(guild).pinboard() 
         if pinboard is None: 
             return 
         # Check if the reaction emoji matches the setting for this guild 
         emoji = await self.config.guild(guild).emoji() 
         if str(payload.emoji) != emoji: 
             return 
         # Fetch the message that was reacted to 
         try: 
             message = await channel.fetch_message(payload.message_id) 
         except discord.NotFound: 
             return 
         # Check if the message is not the pinboard message 
         if message.id == pinboard: 
             return 
         # Prompt the user for a description of the message to pin 
         await channel.send(f"{user.mention}, please provide a description of the message you want to pin.")  # Changed from payload.member.mention 
         # Wait for the user's response 
         try: 
             response = await self.bot.wait_for( 
                 "message", 
                 check=lambda m: m.author == user and m.channel == channel,  # Changed from payload.member 
                 timeout=30.0, 
             ) 
         except asyncio.TimeoutError: 
             return await channel.send("You did not provide a description in time. Pin cancelled.") 
         except Exception as e:  # Added this clause to handle other exceptions 
             self.bot.logger.error(e)  # Log the error message 
             return await channel.send("An error occurred while waiting for your response. Pin cancelled.") 
         # Fetch the pinboard message 
         try: 
             pinboard_message = await channel.fetch_message(pinboard) 
         except discord.NotFound: 
             return await channel.send("The pinboard message could not be found. It may have been deleted manually.") 
         # Edit the pinboard message with the new pin 
         description = response.content 
         link = message.jump_url 
         content = pinboard_message.content + f"\n{description} - {link}" 
         # Check if the content is too long for a single message 
         if len(content) > 2000:  # Added this clause to handle length limit 
             # Truncate the content to fit the limit 
             content = content[:2000]  # You can also use other methods to handle long content, such as creating a new message or using a paginator 
         await pinboard_message.edit(content=content) 
         # Notify the user that the pin has been added 
         await channel.send("Pin successfully added!")
