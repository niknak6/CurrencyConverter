import re
from redbot.core import commands
import discord
import requests
from io import BytesIO

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
        
        # Create a file object from the user's avatar url with requests and BytesIO
        response = requests.get(message.author.avatar.url) 
        file = discord.File(fp=BytesIO(response.content), filename="avatar.png")
        
        # Create a custom emoji from the file object with a random name
        emoji_name = "temp" + str(message.id) # Use message id as part of the name to avoid conflicts
        emoji = await message.guild.create_custom_emoji(name=emoji_name, image=file.content) # Use content attribute to get bytes-like object
        
        # Create a formatted message with the emoji, mention and modified url
        formatted_message = f"{emoji} {message.author.mention} originally shared this embedded TikTok video.\n{new_url}"
        
        # Repost the formatted message 
        await message.channel.send(content=formatted_message)
        
        # Remove the original message and the custom emoji
        await message.delete()
        await emoji.delete()
