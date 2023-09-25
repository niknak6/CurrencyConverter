import os
import random
import requests
from PIL import Image # Import the PIL library
from redbot.core import commands

# Create a class for the cog
class HelloTest(commands.Cog):

    # Initialize the cog with the bot object
    def __init__(self, bot):
        self.bot = bot

    # Create a command called hellotest
    @commands.command()
    async def hellotest(self, ctx):

        # Get the user object from the context
        user = ctx.author

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

        # Save the resized image as avatar_resized.png
        image.save("avatar_resized.png")

        # Get the guild object from the context
        guild = ctx.guild

        # Open the resized image file in binary mode
        with open("avatar_resized.png", "rb") as image:

            # Create a custom emoji with the name "user_avatar" and the image file
            emoji = await guild.create_custom_emoji(name="user_avatar", image=image.read())

        # Send a message with the custom emoji
        await ctx.send(f"Here is your custom emoji: <:{emoji.name}:{emoji.id}>")

        # Delete the custom emoji
        await emoji.delete()

        # Delete the avatar.png and avatar_resized.png files
        os.remove("avatar.png")
        os.remove("avatar_resized.png")
