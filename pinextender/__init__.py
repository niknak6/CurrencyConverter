# Import the cog class
from .treacherypins import TreacheryPins

# Define the setup function
async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(TreacheryPins(bot))
