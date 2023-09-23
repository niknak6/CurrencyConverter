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
        # Get the user's avatar URL with a smaller size
        avatar_url = ctx.author.avatar.url(size=128)
        # Read the image data as bytes
        image_data = await avatar_url.read()

        # Create a custom emoji with the name "hellotest" and the image data
        emoji = await ctx.guild.create_custom_emoji(name="hellotest", image=image_data)

        # Send the emoji in the chat
        await ctx.send(str(emoji))

        # Delete the emoji from the server
        await emoji.delete()
