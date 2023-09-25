# Import discord.py and commands from redbot.core
import discord
from redbot.core import commands
import os

# Create a class for your cog and inherit from commands.Cog
class HelloTest(commands.Cog):
  # Define the __init__ method and pass the bot as an argument
  def __init__(self, bot):
    self.bot = bot

  # Create a command decorator and name your command hellotest
  @commands.command()
  # Define the hellotest method and pass the context as an argument
  async def hellotest(self, ctx):
    # Get the author of the message that invoked the command
    author = ctx.author
    # Get the avatar URL of the author
    avatar_url = author.avatar_url
    # Use aiohttp to get the avatar image as bytes
    async with self.bot.session.get(avatar_url) as response:
      avatar_bytes = await response.read()
    # Use discord.File to create a file object from the bytes
    avatar_file = discord.File(avatar_bytes, filename="avatar.png")
    # Use discord.Guild.create_custom_emoji to create a custom emoji from the file on the server
    emoji = await ctx.guild.create_custom_emoji(name="hellotest", image=avatar_file.read(), reason="Hellotest command")
    # Send the emoji as a message
    await ctx.send(str(emoji))
    # Use discord.Guild.delete_custom_emoji to delete the custom emoji from the server
    await ctx.guild.delete_custom_emoji(emoji, reason="Hellotest command")
    # Remove the avatar.png file from your cogs folder
    os.remove("cogs/avatar.png")
