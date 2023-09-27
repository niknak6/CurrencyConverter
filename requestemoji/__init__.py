from .requestemoji import RequestEmoji

async def setup(bot):
    bot.add_cog(RequestEmoji(bot))
