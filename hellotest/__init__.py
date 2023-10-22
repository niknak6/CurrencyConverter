# Import the cog class
from .hellotest import HelloTest

# Define the setup function
async def setup(bot):
    # Add the cog to the bot
    await bot.add_cog(HelloTest(bot))
