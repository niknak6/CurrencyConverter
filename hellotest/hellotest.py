import discord
from discord.ext import commands
from PIL import Image

class HelloTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = {}

    @commands.command()
    async def hellotest(self, ctx):
        # Get the user's avatar URL
        avatar_url = ctx.author.avatar_url

        # Download the avatar image and convert it to a PIL image object
        response = await aiohttp.ClientSession().get(avatar_url)
        image = Image.open(BytesIO(await response.read()))

        # Create a new emoji with the avatar image
        emoji = Image.new('RGBA', (64, 64), (255, 255, 255, 25
