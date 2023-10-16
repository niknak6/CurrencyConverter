import os
import re
import requests
from PIL import Image, ImageOps, ImageDraw # Import PIL library
from redbot.core import commands
import discord # Import discord library
import io # Import io library
import random # Import random library

class TikTokCog(commands.Cog):
    """A custom cog that reposts tiktok urls"""

    def __init__(self, bot):
        self.bot = bot
        # Compile the tiktok pattern only once
        self.tiktok_pattern = re.compile(r"(?i)https?://(\w+\.)?tiktok.com/(.+)") # Simplified line

    @commands.Cog.listener()
    async def on_message(self, message):
        """A listener that triggers when a message is sent"""
        # Check if the message is from a user and contains a tiktok url
        if message.author.bot:
            return
        tiktok_url = self.tiktok_pattern.search(message.content)
        if not tiktok_url:
            return

        # Replace the tiktok.com part of the url with vxtiktok.com, while preserving the protocol, subdomain, and path parts
        new_url = self.tiktok_pattern.sub(r"\g<0>".replace("tiktok.com", "vxtiktok.com"), message.content) # Simplified line

        # Get the user object from the message using the discord.utils.get function
        user = discord.utils.get(message.guild.members, id=message.author.id) # Modified line

        # Get the avatar URL from the user object
        avatar_url = user.avatar.url

        # Create an asset object from the avatar URL
        asset = discord.Asset(self.bot._connection, url=avatar_url) # Modified line

        # Resize the asset to 128x128 pixels
        asset = asset.resize(128, 128) # Modified line

        # Create a file object from the asset's read method
        file = discord.File(await asset.read(), filename="avatar_cropped.png") # Modified line

        # Get the guild object from the message
        guild = message.guild

        # Create a custom emoji with a random name and the file object's fp attribute
        emoji_name = f"user_avatar_{random.randint(0, 9999)}" 
        emoji = await guild.create_custom_emoji(name=emoji_name, image=file.fp.read()) # Modified line

        # Create a formatted message with the custom emoji, the mention and modified url
        formatted_message = f"{emoji} {user.mention} shared this TikTok. {new_url}" 

        # Repost the formatted message and remove the original message
        await message.channel.send(formatted_message)
        await message.delete()

        # Delete the custom emoji
        await emoji.delete()
