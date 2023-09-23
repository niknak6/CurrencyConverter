from .hellotest import HelloTest


async def setup(bot):
    await bot.add_cog(HelloTest(bot))
