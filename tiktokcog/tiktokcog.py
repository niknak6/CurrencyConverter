import discord
import re
import requests # Import requests module
import io # Import io module
from redbot.core import commands

class TikTokCog(commands.Cog):
    """A custom cog that reposts tiktok urls"""

    def __init__(self, bot):
        self.bot = bot
        # Compile the tiktok pattern only once
        self.tiktok_pattern = re.compile(r"(?i)(https?://)?((\w+)\.)?tiktok.com/(.+)")

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
        # Download the file from the user's avatar url using requests
        # Change the size argument to a lower value, such as 256 or 128
        response = requests.get(message.author.avatar_url_as(size=256))
        # Create a BytesIO object from the response content using io
        file_data = io.BytesIO(response.content)
        # Create a file object from the BytesIO object using discord.File
        file = discord.File(file_data)
        # Set the file name to the user's display name
        file.filename = f"{message.author.display_name}.png"
        # Create a formatted message with the mention and modified url
        formatted_message = f"{message.author.mention} originally shared this embedded TikTok video.\n{new_url}"
        # Repost the formatted message and the file object as an attachment
        await message.channel.send(formatted_message, file=file)
        # Remove the original message
        await message.delete()
