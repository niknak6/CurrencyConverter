from .requestemoji import RequestEmoji

def setup(bot):
    bot.add_cog(RequestEmoji(bot))
