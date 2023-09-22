import re
import discord
import requests
from redbot.core import commands

class TikTokCog(commands.Cog):
    """A custom cog that reposts tiktok urls"""

    def __init__(self, bot):
        self.bot = bot
        # Compile the tiktok pattern only once
        self.tiktok_pattern = re.compile(r"(?i)(https?://)?((\w+)\.)?tiktok.com/(.+)")
        # Create a dictionary to store the temporary emojis
        self.temp_emojis = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        """A listener that triggers when a message is sent"""
        # Check if the message is from a user and contains a tiktok url
        if message.author.bot:
            return
        tiktok_url = self.tiktok_pattern.search(message.content)
        if not tiktok_url:
            return
        # Add vx in front of tiktok.com in the url, while preserving the protocol, subdomain, and path parts
        new_url = tiktok_url.expand(r"\1\2vxtiktok.com/\4")
        # Create a temporary emoji from the user's avatar and store it in the dictionary
        avatar_bytes = requests.get(message.author.avatar.url).content
        temp_emoji = await message.guild.create_custom_emoji(name=f"temp_{message.author.id}", image=avatar_bytes)
        self.temp_emojis[message.id] = temp_emoji
        # Create a formatted message with the emoji and modified url
        formatted_message = f"{temp_emoji} {message.author.display_name} originally shared this embedded TikTok video.\n{new_url}"
        # Repost the formatted message and remove the original message
        await message.channel.send(formatted_message)
        await message.delete()

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """A listener that triggers when a message is deleted"""
        # Check if the message has a temporary emoji associated with it and delete it
        temp_emoji = self.temp_emojis.pop(message.id, None)
        if temp_emoji:
            await temp_emoji.delete()
