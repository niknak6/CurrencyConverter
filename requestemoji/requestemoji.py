# Import the necessary modules
from redbot.core import commands, checks
import discord, asyncio

# Define the cog class
class RequestEmoji(commands.Cog):
    """A cog that allows users to request custom stickers"""

    def __init__(self, bot):
        self.bot = bot
        # A dictionary that stores the requests as (message_id, channel_id): (requester_id, sticker_name, sticker_url)
        self.requests = {}

    @commands.command()
    async def requeststicker(self, ctx, sticker_name: str):
        """Request a custom sticker with an attachment"""
        # Check if the message has an attachment
        if not ctx.message.attachments:
            return await ctx.send("You need to attach an image file to request a sticker.")
        
        # Get the attachment url
        sticker_url = ctx.message.attachments[0].url

        # Send the request message with reactions
        request_msg = await ctx.send(f"{ctx.author.mention} has requested a sticker named {sticker_name}.\n{sticker_url}")
        for emoji in ("✅", "❌"): # Checkmark and X emojis
            await request_msg.add_reaction(emoji)

        # Store the request in the dictionary
        self.requests[(request_msg.id, request_msg.channel.id)] = (ctx.author.id, sticker_name, sticker_url)

        # Start a timer to delete the request after 30 minutes
        self.bot.loop.create_task(self.delete_request(request_msg))

    async def delete_request(self, request_msg):
        """Delete a request after 30 minutes"""
        await asyncio.sleep(1800) # Wait for 30 minutes
        # Check if the request is still in the dictionary and delete it
        self.requests.pop((request_msg.id, request_msg.channel.id), None)
        # Delete the request message if it still exists
        try:
            await request_msg.delete()
        except discord.NotFound:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle the reactions on the request messages"""
        # Check if the reaction is on a request message and from an admin
        if (payload.message_id, payload.channel_id) in self.requests and await commands.has_any_guild_permissions(administrator=True, manage_messages=True, manage_roles=True).predicate(await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id), self.bot.get_user(payload.user_id)): # Use this decorator instead of checks.admin_or_permissions().predicate
            # Get the channel and message objects
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            # Get the requester id, sticker name and url from the dictionary
            requester_id, sticker_name, sticker_url = self.requests[(payload.message_id, payload.channel_id)]
            # Get the user who reacted
            user = self.bot.get_user(payload.user_id)
            # Check if the reaction is a checkmark or an x
            if payload.emoji.name == "✅":
                # Approve the request and create the sticker
                await message.channel.send(f"{user.mention} has approved the sticker request from <@{requester_id}>.")
                try:
                    await message.guild.create_custom_emoji(name=sticker_name, image=await self.bot.session.get(sticker_url).read())
                    await message.channel.send(f"The sticker {sticker_name} has been created.")
                except discord.HTTPException as e:
                    await message.channel.send(f"An error occurred while creating the sticker: {e}")
            elif payload.emoji.name == "❌":
                # Deny the request and send a message
                await message.channel.send(f"{user.mention} has denied the sticker request from <@{requester_id}>.")
            
            # Delete the request message and remove it from the dictionary
            await message.delete()
            del self.requests[(payload.message_id, payload.channel_id)]

# Add the cog to the bot
def setup(bot):
    bot.add_cog(RequestEmoji(bot))
