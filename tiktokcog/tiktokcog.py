import os
import re
import requests
from PIL import Image, ImageOps, ImageDraw # Import PIL library
from redbot.core import commands
import discord # Import discord library
import io # Import io library
import random

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

        # Get the user object from the message
        user = message.author

        # Get the avatar URL from the user object
        avatar_url = user.avatar.url

        # Download the image from the URL and save it as avatar.png
        response = requests.get(avatar_url)
        with open("avatar.png", "wb") as file:
            file.write(response.content)

        # Open the avatar image file
        image = Image.open("avatar.png")

        # Resize the image to 128x128 pixels
        image = image.resize((128, 128))

        # Create a mask image with the same size and RGBA mode
        mask = Image.new("RGBA", image.size)

        # Create a Draw object for the mask image
        draw = ImageDraw.Draw(mask)

        # Draw a black circle on the mask image using the ellipse method
        draw.ellipse([0, 0, *image.size], fill=(0, 0, 0, 255))

        # Apply the mask to the avatar image using the Image.composite method
        image = Image.composite(image, Image.new("RGBA", image.size), mask)

        # Create a discord.File object from the avatar image in memory
        file = discord.File(io.BytesIO(image.tobytes()), filename="avatar_cropped.png") # Modified line

        # Get the guild object from the message
        guild = message.guild

        # Create a custom emoji with a random name and the file object
        emoji_name = f"user_avatar_{random.randint(0, 9999)}"
        emoji = await guild.create_custom_emoji(name=emoji_name, image=file.read()) # Simplified line

        # Create a formatted message with the custom emoji, the mention and modified url
        formatted_message = f"{emoji} {user.mention} originally shared this embedded TikTok video.\n{new_url}" 

        # Repost the formatted message and remove the original message
        await message.channel.send(formatted_message)
        await message.delete()

        # Delete the custom emoji
        await emoji.delete()

        # Delete the avatar.png file
        os.remove("avatar.png")
