import os
import random
import requests
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

        # Get the guild object from the context
        guild = ctx.guild

        # Open the avatar image file in binary mode
        with open("avatar.png", "rb") as image:

            # Create a custom emoji with the name "user_avatar" and the image file
            emoji = await guild.create_custom_emoji(name="user_avatar", image=image.read())

        # Send a message with the custom emoji
        await ctx.send(f"Here is your custom emoji: <:{emoji.name}:{emoji.id}>")

        # Delete the custom emoji
        await emoji.delete()

        # Delete the avatar.png file
        os.remove("avatar.png")
