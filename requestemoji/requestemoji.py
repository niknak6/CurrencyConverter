import discord
from redbot.core import commands, checks, errors
from redbot.core.utils.chat_formatting import pagify
from discord.ext.commands.converter import EmojiConverter
from PIL import Image
import io
import asyncio # Import asyncio for handling timeout error

# Import CogLoadError from redbot.core.errors
from redbot.core.errors import CogLoadError

class RequestEmoji(commands.Cog):
  """A cog that allows users to request custom emojis and stickers."""

  def __init__(self, bot):
    self.bot = bot

  # Define a helper function that handles the common logic for requesting custom assets
  async def request_custom_asset(self, ctx, name: str, asset_type: str, max_size: int, resize_size: tuple):
    # Check if the name argument is valid for an asset name
    if not (2 <= len(name) <= 32 and name.isalnum() or "_"):
      raise commands.BadArgument(f"The name must be between 2 and 32 characters long and consist of alphanumeric characters and underscores only.")
    
    # Check if the attachment argument is valid for an asset image
    attachment = ctx.message.attachments[0] if ctx.message.attachments else None # Get the first attachment or None
    if not attachment: # If no attachment, use the author's avatar as a fallback
      attachment = ctx.author.avatar_url_as(format="png", size=resize_size[0])
    try: # Try to get the image data from the attachment
      image_data = await attachment.read()
    except Exception as e: # If something goes wrong, raise an error and send a message
      raise CogLoadError(f"Something went wrong while reading the image: {e}")
      await ctx.send("There was an error while reading the image. Please try again with a valid PNG or JPG file.")
      return
    
    try: # Try to resize the image using thumbnail algorithm with resize_size as desired size
      image_data = resize_image(image_data, resize_size)
      if len(image_data) > max_size: # If the image is still too large, raise an error and send a message
        raise CogLoadError(f"The image is too large. It must be smaller than {max_size // 1024} KB.")
        await ctx.send(f"The image is too large. It must be smaller than {max_size // 1024} KB.")
        return
    except Exception as e: # If something goes wrong, raise an error and send a message
      raise CogLoadError(f"Something went wrong while processing the image: {e}")
      await ctx.send("There was an error while processing the image. Please try again with a valid PNG or JPG file.")
      return
    
    # Create an embed message that contains the name and image of the requested asset and send it to the same channel
    embed = discord.Embed(title=f"{asset_type.capitalize()} request: {name}", description=f"{ctx.author.mention} has requested a custom {asset_type} with this name and image. An Officer or Guild Master can approve or deny this request by reacting with a checkmark or x emoji.", color=discord.Color.blue())
    embed.set_image(url=f"attachment://{asset_type}.png") # Set the embed image to the attachment with filename asset_type.png
    embed.set_footer(text="This request will expire in 30 minutes.") # Set the embed footer to show the new expiration time
    file = discord.File(io.BytesIO(image_data), filename=f"{asset_type}.png") # Create a discord File object from the image data with filename asset_type.png
    message = await ctx.send(embed=embed, file=file) # Send the embed message with the file attachment
    
    # Add a checkmark and x emoji as reactions to the embed message using message.add_reaction()
    await message.add_reaction("\u2705") # Checkmark emoji
    await message.add_reaction("\u274c") # X emoji
    
    # Wait for a reaction from an Officer or Guild Master
    # Use a lambda expression to create an anonymous check function
    check = lambda reaction, user: (reaction.message.id == message.id and user != self.bot.user and user.top_role.name in ["Officer", "Guild Master"] and reaction.emoji in ["\u2705", "\u274c"]) # Use user.top_role.name to check if the user has a mod or permissions role
    
    try: # Try to wait for a reaction that passes the check function within 30 minutes
      reaction, user = await self.bot.wait_for("reaction_add", timeout=1800.0, check=check) # Change the timeout to 30 minutes
    except asyncio.TimeoutError: # If no reaction is received within the time limit, send a message to inform that the request expired
      await ctx.send(f"The {asset_type} request for {name} has expired after 30 minutes.") # Change the message to include the new expiration time and the asset type
      return
    
    # If the reaction is a checkmark, try to create the asset and send a message to confirm
    if reaction.emoji == "\u2705":
      try: # Try to create the asset using ctx.guild.create_custom_emoji() or ctx.guild.create_custom_sticker() depending on the asset type
        if asset_type == "emoji":
          asset = await ctx.guild.create_custom_emoji(name=name, image=image_data)
        elif asset_type == "sticker":
          asset = await ctx.guild.create_custom_sticker(name=name, image=image_data)
        await ctx.send(f"The {asset_type} {asset} was added successfully.")
      except Exception as e: # If something goes wrong, raise an error and send a message
        raise CogLoadError(f"Something went wrong while creating the {asset_type}: {e}")
        await ctx.send(f"There was an error while creating the {asset_type}. Please try again later.")
        return
    
    # If the reaction is an x, send a message to inform that the request was denied
    if reaction.emoji == "\u274c":
      await ctx.send(f"The {asset_type} request for {name} was denied by {user.mention}.")

  @commands.command(name="requestemoji", aliases=["reqemoji"], help="Request a custom emoji to be added to the server.", usage="<name> [attachment]", cooldown_after_parsing=True)
  @commands.guild_only()
  @commands.cooldown(1, 1800, commands.BucketType.user) # Change the cooldown to 30 minutes
  async def request_emoji(self, ctx, name: str):
    # Call the helper function with emoji parameters
    await self.request_custom_asset(ctx, name, "emoji", 256 * 1024, (128, 128))

  @commands.command(name="requeststicker", aliases=["reqsticker"], help="Request a custom sticker to be added to the server.", usage="<name> [attachment]", cooldown_after_parsing=True)
  @commands.guild_only()
  @commands.cooldown(1, 1800, commands.BucketType.user) # Change the cooldown to 30 minutes
  async def request_sticker(self, ctx, name: str):
    # Call the helper function with sticker parameters
    await self.request_custom_asset(ctx, name, "sticker", 500 * 1024, (320, 320))

# Define a function that resizes an image using thumbnail algorithm
def resize_image(image_data, size):
    # Create an Image object from the image data
    image = Image.open(io.BytesIO(image_data))
    # Resize the image using thumbnail algorithm with the desired size
    image.thumbnail(size)
    # Save the image to a BytesIO object and return its value
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()
