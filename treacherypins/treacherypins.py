from redbot.core import commands
from discord import Embed

class TreacheryPins(commands.Cog):
    """A cog that allows users to create a pinboard of messages."""

    def __init__(self, bot):
        self.bot = bot
        self.pinboards = {} # A dictionary that maps channel IDs to pinboard message IDs

    @commands.command()
    async def pinboard(self, ctx, message_id: int):
        """Designates a message as a Treachery Pinboard."""
        try:
            message = await ctx.channel.fetch_message(message_id) # Fetch the message by ID
            if message.author != ctx.me: # Check if the message is sent by the bot
                await ctx.send("I can only designate my own messages as pinboards.")
                return
            await message.edit(content="Treachery Pinboard") # Edit the message content
            await message.add_reaction("📌") # Add a push pin emoji as a reaction
            self.pinboards[ctx.channel.id] = message.id # Store the pinboard message ID in the dictionary
            await ctx.send("The message has been designated as a pinboard.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handles the reaction events."""
        if payload.user_id == self.bot.user.id: # Ignore reactions from the bot
            return
        if payload.emoji.name == "📌": # Check if the reaction is a push pin emoji
            if payload.channel_id in self.pinboards: # Check if the channel has a pinboard
                if payload.message_id == self.pinboards[payload.channel_id]: # Check if the reaction is on the pinboard message
                    channel = self.bot.get_channel(payload.channel_id) # Get the channel object
                    user = self.bot.get_user(payload.user_id) # Get the user object
                    await channel.send(f"{user.mention}, please reply with the subject of the message you want to pin.") # Prompt the user for the message subject

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handles the message events."""
        if message.author == self.bot.user: # Ignore messages from the bot
            return
        if message.channel.id in self.pinboards: # Check if the channel has a pinboard
            pinboard_id = self.pinboards[message.channel.id] # Get the pinboard message ID
            pinboard = await message.channel.fetch_message(pinboard_id) # Fetch the pinboard message object
            embeds = pinboard.embeds # Get the list of embeds in the pinboard message
            embed = Embed(title=message.content, url=message.jump_url) # Create a new embed with the message subject and link
            embeds.append(embed) # Append the new embed to the list of embeds
            await pinboard.edit(embeds=embeds) # Edit the pinboard message with the updated list of embeds
