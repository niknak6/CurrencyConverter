# Import the discord and commands modules from discord.py
import discord
from discord.ext import commands

# Define a constant for the number of messages to send and pin
NUM_MESSAGES = 50

# Create a class that inherits from commands.Cog
class TreacheryPins(commands.Cog):
    # Define the constructor
    def __init__(self, bot):
        # Assign the bot instance to self.bot
        self.bot = bot

    # Define a command decorator with the name pintest
    @commands.command(name="pintest")
    # Define an async function that takes self and ctx as parameters
    async def pintest(self, ctx):
        # Loop from 1 to NUM_MESSAGES
        for i in range(1, NUM_MESSAGES + 1):
            # Try to send and pin a message
            try:
                # Send a message with the current number to the channel
                message = await ctx.send(i)
                # Pin the message to the channel
                await message.pin()
            # Catch any possible errors
            except discord.HTTPException as e:
                # Print the error message to the console
                print(e)
                # Break out of the loop
                break

# Define a setup function that takes bot as a parameter
def setup(bot):
    # Add the cog instance to the bot
    bot.add_cog(TreacheryPins(bot))
