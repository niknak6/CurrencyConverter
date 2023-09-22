import re
from redbot.core import commands
import discord
import requests
from io import BytesIO
from PIL import Image

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
        # Create a formatted message with the mention and modified url
        formatted_message = f"{message.author.mention} originally shared this embedded TikTok video.\n{new_url}"
        # Create a file object from the user's avatar url with requests and BytesIO
        response = requests.get(message.author.avatar.url)
        img = Image.open(BytesIO(response.content))
        # Resize the image to 32x32 pixels
        img_resize = img.resize((32, 32))
        # Save the resized image to another BytesIO object
        output = BytesIO()
        img_resize.save(output, format="PNG")
        file = discord.File(fp=output, filename="avatar.png")
        # Repost the formatted message and the file object as an attachment
        await message.channel.send(content=formatted_message, file=file)
        # Remove the original message
        await message.delete()
