from redbot.core import commands
import discord
import aiohttp
import io

class HelloTest(commands.Cog):
    """A cog that creates a custom emoji with the user's avatar"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hellotest(self, ctx):
        """This creates a custom emoji with your avatar and posts it"""
        # Get the user's avatar URL
        avatar_url = ctx.author.avatar.url
        # Create a temporary session to download the avatar image
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                # Read the image data as bytes
                image_data = await response.read()
                # Create an in-memory file object from the image data
                image_file = io.BytesIO(image_data)

        # Resize the image to 128x128 pixels using discord.py's Asset class
        asset = discord.Asset(self.bot._connection, image_file)
        resized_asset = asset.resize(128)
        # Read the resized image data as bytes
        resized_image_data = await resized_asset.read()

        # Create a custom emoji with the name "hellotest" and the resized image data
        emoji = await ctx.guild.create_custom_emoji(name="hellotest", image=resized_image_data)

        # Send the emoji in the chat
        await ctx.send(str(emoji))

        # Delete the emoji from the server
        await emoji.delete()
