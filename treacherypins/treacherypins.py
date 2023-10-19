# Import discord, pickle, os and the commands extension
import discord
import pickle
import os
from redbot.core import commands

# Define a variable to store the file name
data_file = "pinboard_data.pkl"

# Create a class for the cog
class TreacheryPins(commands.Cog):
    """A cog that allows users to pin messages to a channel-specific pinboard."""

    # Initialize the cog with the bot instance
    def __init__(self, bot):
        self.bot = bot
        # Open the file with the mode "a+"
        with open(data_file, "a+") as f:
            # Move the file pointer to the beginning
            f.seek(0)
            # Try to load the data from the file
            try:
                self.data = pickle.load(f)
            except EOFError:
                # If the file is empty, write an empty dictionary with the guilds key to the file
                pickle.dump({"guilds": {}}, f)
                # Load the data from the file again
                self.data = pickle.load(f)

    # Create a command to create a pinboard message in the current channel
    @commands.command()
    @commands.has_permissions(administrator=True) # Check for Administrator permission
    async def createpinboard(self, ctx):
        """Create a pinboard message in the current channel."""
        # Check if there is already a pinboard message in the current channel
        if ctx.channel.id in self.data["guilds"].get(str(ctx.guild.id), {})["pinboards"]: # Use dict.get method with default value
            # If yes, send an error message
            await ctx.send("There is already a pinboard message in this channel.")
        else:
            # If no, create a new message with the title "Treachery Pin Board"
            pinboard = await ctx.send("Treachery Pin Board")
            # Pin the message
            await pinboard.pin()
            # Save the message id in the dictionary by channel id
            self.data["guilds"].setdefault(str(ctx.guild.id), {})["pinboards"][str(ctx.channel.id)] = pinboard.id # Use dict.setdefault method to avoid KeyError 
            # Save the data to the file
            with open(data_file, "w") as f:
                pickle.dump(self.data, f)
            # Send a confirmation message
            await ctx.send("Pinboard message created and pinned.")

    # Create a command to remove the pinboard message from the current channel
    @commands.command()
    @commands.has_permissions(administrator=True) # Check for Administrator permission
    async def removepinboard(self, ctx):
        """Remove the pinboard message from the current channel."""
        # Check if there is a pinboard message in the current channel
        if ctx.channel.id in self.data["guilds"].get(str(ctx.guild.id), {})["pinboards"]: # Use dict.get method with default value
            # If yes, get the message object by id
            pinboard = await ctx.channel.fetch_message(self.data["guilds"][str(ctx.guild.id)]["pinboards"][str(ctx.channel.id)])
            # Unpin the message
            await pinboard.unpin()
            # Delete the message
            await pinboard.delete()
            # Remove the channel id from the dictionary
            del self.data["guilds"][str(ctx.guild.id)]["pinboards"][str(ctx.channel.id)]
            # Save the data to the file
            with open(data_file, "w") as f:
                pickle.dump(self.data, f)
            # Send a confirmation message
            await ctx.send("Pinboard message removed and unpinned.")
        else:
            # If no, send an error message
            await ctx.send("There is no pinboard message in this channel.")

    # Create a command to set the pinboard emoji for the current guild
    @commands.command()
    @commands.has_permissions(administrator=True) # Check for Administrator permission
    async def pinboardemoji(self, ctx, emoji: str): # Change type annotation to str 
        """Set the pinboard emoji for the current guild."""
        # Save the emoji in the dictionary by guild id
        self.data["guilds"].setdefault(str(ctx.guild.id), {})["pinboard_emoji"] = emoji  # Use dict.setdefault method to avoid KeyError 
        # Save the data to the file 
        with open(data_file, "w") as f: 
            pickle.dump(self.data, f) 
        # Send a confirmation message 
        await ctx.send(f"Pinboard emoji set to {emoji}.")

    # Create a listener for reaction add events 
    @commands.Cog.listener() 
    async def on_reaction_add(self, reaction, user):  # Change event name to on_reaction_add 
        """Handle reactions to messages.""" 
        # Get the channel object from the reaction 
        channel = reaction.message.channel  # Change payload to reaction 
        # Check if the channel has a pinboard message 
        if channel.id in self.data["guilds"].get(str(channel.guild.id), {})["pinboards"]:  # Use dict.get method with default value 
            # Get the guild object from the channel 
            guild = channel.guild  # Change payload to channel 
            # Check if the guild has a pinboard emoji 
            if guild.id in self.data["guilds"]: 
                # Get the emoji object by name 
                emoji = self.data["guilds"][str(guild.id)]["pinboard_emoji"]  # Change this line 
                # Check if the reaction emoji matches the pinboard emoji 
                if reaction.emoji.name == emoji.strip(":"):  # Change payload to reaction 
                    # Check if the user is not a bot and not an admin 
                    if not user.bot and not user.guild_permissions.administrator if user else False:  # Use user object directly and handle DM case
                        # Get the message object from the reaction 
                        message = reaction.message  # Change payload to reaction 
                        # Get the pinboard message object by id 
                        pinboard = await channel.fetch_message(self.data["guilds"][str(channel.guild.id)]["pinboards"][str(channel.id)]) 
                        # Send a prompt message to the user for a description of the message to pin 
                        prompt = await user.send(f"You reacted to a message with {emoji}. Please provide a description of the message to pin.") 
                        # Wait for the user's response 
                        try: 
                            response = await self.bot.wait_for("message", check=lambda m: m.author == user and m.channel == prompt.channel, timeout=60) 
                        except asyncio.TimeoutError: 
                            # If the user does not respond in time, send an error message 
                            await user.send("You did not provide a description in time. Pin aborted.") 
                        else: 
                            # If the user responds, get the description from the message content 
                            description = response.content 
                            # Edit the pinboard message to add a new line with the description and the message link 
                            await pinboard.edit(content=pinboard.content + f"\n{description}: {message.jump_url}") 
                            # Send a confirmation message to the user
                            await user.send("Pin successfully added!")
