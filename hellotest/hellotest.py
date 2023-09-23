from redbot.core import commands
import discord
import aiohttp

class HelloTest(commands.Cog):
    """A cog that creates a custom emoji with the user's avatar"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hellotest(self, ctx):
        """This creates a custom emoji with your avatar and posts it"""
        # Get the user's avatar URL
        # Replace this line
        # avatar_url = str(ctx.author.avatar_url_as(format="png"))
        # With this line
        avatar_url = str(ctx.author.avatar.url)

        # Create a temporary session to download the avatar image
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                # Read the image data as bytes
                image_data = await response.read()

        # Create a custom emoji with the name "hellotest" and the image data
        emoji = await ctx.guild.create_custom_emoji(name="hellotest", image=image_data)

        # Send the emoji in the chat
        await ctx.send(str(emoji))

        # Delete the emoji from the server
        await emoji.delete()
