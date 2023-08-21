import asyncio
from .CurrencyConverter import CurrencyConverter

__author__ = "Your name or username"
__version__ = "1.0.0"
__description__ = "A cog that converts currencies using API Ninjas"

@asyncio.coroutine
def setup(bot):
    bot.add_cog(CurrencyConverter(bot))
