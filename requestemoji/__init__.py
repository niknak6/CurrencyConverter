from .RequestEmoji import RequestEmoji


async def setup(bot):
    await bot.add_cog(RequestEmoji(bot))
