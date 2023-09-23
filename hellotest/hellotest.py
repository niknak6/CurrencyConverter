import discord
from redbot.core import commands

class HelloTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hellotest(self, ctx):
        """Creates a custom emoji out of the user's avatar and posts it."""

        avatar_url = ctx.author.avatar_url
        emoji = await ctx.guild.create_custom_emoji(avatar_url, name=ctx.author.name)
        await ctx.send(f"Hello, {ctx.author.name}! Here is your custom emoji: {emoji}")
        await emoji.delete()

async def setup(bot):
    await bot.add_cog(HelloTestCog(bot))
