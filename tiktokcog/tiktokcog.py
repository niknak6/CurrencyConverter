# mycog.py
import re
from redbot.core import commands
from discord import Embed, utils

class TikTokCog(commands.Cog):
    """A custom cog that reposts tiktok urls"""

    def __init__(self, bot):
        self.bot = bot
        self.tiktok_pattern = re.compile(r"(?i)(https?://)?((\w+)\.)?tiktok.com/(.+)")

    @commands.Cog.listener()
    async def on_message(self, message):
        """A listener that triggers when a message is sent"""
        # Check if the message is from a user and contains a tiktok url
        if not message.author.bot and self.tiktok_pattern.search(message.content):
            # Extract the tiktok url from the message
            tiktok_url = self.tiktok_pattern.search(message.content)
            if tiktok_url:
                tiktok_url = tiktok_url.group(0)
                # Add vx in front of tiktok.com in the url, while preserving the protocol, subdomain, and path parts
                new_url = re.sub(self.tiktok_pattern, r"\1\2vxtiktok.com/\4", tiktok_url)
                # Get the discord display name and display picture of the person who posted the tiktok url
                display_name = utils.escape_markdown(message.author.display_name)
                display_picture = message.author.avatar.url
                # Create a formatted message with the display name, display picture, and modified url
                formatted_message = f"**{display_name}** shared the following TikTok!\n{new_url}"
                # Repost the formatted message
                await message.channel.send(formatted_message)
                # Remove the original message
                await message.delete()
