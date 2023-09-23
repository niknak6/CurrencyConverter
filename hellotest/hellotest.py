import discord
from redbot.core import commands

class HelloTest(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def hellotest(self, ctx):
        """Creates a custom emoji out of the user's avatar, posts it, and then removes the custom emoji from the server."""

        # Get the user's avatar.
        avatar = ctx.author.avatar

        # Create a temporary file to store the avatar image.
        with open("avatar.png", "wb") as f:
            async for chunk in avatar.read():
                f.write(chunk)

        # Create a custom emoji from the avatar image.
        emoji = await ctx.guild.create_custom_emoji(name="hellotest", image=open("avatar.png", "rb"))

        # Post the custom emoji.
        await ctx.send(emoji)

        # Remove the custom emoji from the server.
        await emoji.delete()

