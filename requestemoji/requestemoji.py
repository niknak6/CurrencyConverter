import discord
from redbot.core import commands, checks, errors
from redbot.core.utils.chat_formatting import pagify
from discord.ext.commands.converter import EmojiConverter
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter # Import the PIL modules for image processing
import io
import asyncio # Import asyncio for handling timeout error

class RequestEmoji(commands.Cog):
  """A cog that allows users to request custom emojis."""

  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="requestemoji", aliases=["reqemoji"], help="Request a custom emoji to be added to the server.", usage="<name> [attachment]", cooldown_after_parsing=True)
  @commands.guild_only()
  @commands.cooldown(0, 1800, commands.BucketType.user) # Change the cooldown to zero
  async def request_emoji(self, ctx, name: str):
    # Check if the name argument is valid for an emoji name
    if not (2 <= len(name) <= 32 and name.isalnum() or "_"):
      raise commands.BadArgument("The name must be between 2 and 32 characters long and consist of alphanumeric characters and underscores only.")
    
    # Check if the attachment argument is valid for an emoji image
    attachment = ctx.message.attachments[0] if ctx.message.attachments else None # Get the first attachment or None
    if not attachment: # If no attachment, use the author's avatar as a fallback
      attachment = ctx.author.avatar_url_as(format="png", size=128)
    try: # Try to get the image data from the attachment
      image_data = await attachment.read()
    except Exception as e: # If something goes wrong, raise an error and send a message
      raise errors.UserFeedbackCheckFailure(f"Something went wrong while reading the image: {e}")
      await ctx.send("There was an error while reading the image. Please try again with a valid PNG or JPG file.")
      return
    
    try: # Try to resize the image using thumbnail algorithm with 128x128 pixels as desired size
      image_data = resize_image(image_data, (128, 128))
      if len(image_data) > 256 * 1024: # If the image is still too large, raise an error and send a message
        raise errors.UserFeedbackCheckFailure("The image is too large. It must be smaller than 256 KB.")
        await ctx.send("The image is too large. It must be smaller than 256 KB.")
        return
    except Exception as e: # If something goes wrong, raise an error and send a message
      raise errors.UserFeedbackCheckFailure(f"Something went wrong while processing the image: {e}")
      await ctx.send("There was an error while processing the image. Please try again with a valid PNG or JPG file.")
      return
    
    # Create an embed message that contains the name and image of the requested emoji and send it to the same channel
    embed = discord.Embed(title=f"Emoji request: {name}", description=f"{ctx.author.mention} has requested a custom emoji with this name and image. An Officer or Guild Master can approve or deny this request by reacting with a checkmark or x emoji.", color=discord.Color.blue())
    embed.set_image(url="attachment://emoji.png") # Set the embed image to the attachment with filename emoji.png
    embed.set_footer(text="This request will expire in 30 minutes.") # Set the embed footer to show the new expiration time
    file = discord.File(io.BytesIO(image_data), filename="emoji.png") # Create a discord File object from the image data with filename emoji.png
    message = await ctx.send(embed=embed, file=file) # Send the embed message with the file attachment
    
    # Add a checkmark and x emoji as reactions to the embed message using message.add_reaction()
    await message.add_reaction("\u2705") # Checkmark emoji
    await message.add_reaction("\u274c") # X emoji
    
    # Wait for a reaction from an Officer or Guild Master
    def check(reaction, user): # Define a check function that returns True if the reaction is valid and False otherwise
      return (reaction.message.id == message.id and user != self.bot.user and user.top_role.name in ["Officer", "Guild Master"] and reaction.emoji in ["\u2705", "\u274c"]) # Use user.top_role.name to check if the user has a mod or permissions role
    
    try: # Try to wait for a reaction that passes the check function within 30 minutes
      reaction, user = await self.bot.wait_for("reaction_add", timeout=1800.0, check=check) # Change the timeout to 30 minutes
    except asyncio.TimeoutError: # If no reaction is received within the time limit, send a message to inform that the request expired
      await ctx.send(f"The emoji request for {name} has expired after 30 minutes.") # Change the message to include the new expiration time
      return
    
    # If the reaction is a checkmark, try to create the emoji and send a message to confirm
    if reaction.emoji == "\u2705":
      try: # Try to create the emoji using ctx.guild.create_custom_emoji()
        emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
        await ctx.send(f"The emoji {emoji} was added successfully by {user.mention} for {ctx.author.mention}.") # Change the message to include the mention of the requester and the approver
      except discord.HTTPException as e: # If something goes wrong, raise an error and send a message
        if e.code == 30008: # If the error code is 30008, it means that the maximum number of emojis has been reached
          raise errors.UserFeedbackCheckFailure("The server has reached the maximum number of emojis.")
          await ctx.send("The server has reached the maximum number of emojis. Please delete some existing emojis before requesting a new one.")
        elif e.code == 50035: # If the error code is 50035, it means that the name or image is invalid
          raise errors.UserFeedbackCheckFailure("The name or image is invalid.")
          await ctx.send("The name or image is invalid. Please try again with a valid name and image.")
        else: # If the error code is something else, it means that there is an unknown error
          raise errors.UserFeedbackCheckFailure(f"Something went wrong while creating the emoji: {e}")
          await ctx.send(f"There was an error while creating the emoji. Please try again later.")
        return
    
    # If the reaction is an x, send a message to inform that the request was denied
    if reaction.emoji == "\u274c":
      await ctx.send(f"The emoji request for {name} was denied by {user.mention} for {ctx.author.mention}.") # Change the message to include the mention of the requester and the approver

# Define a function that resizes the image using thumbnail algorithm and preserves the aspect ratio
def resize_image(image_data, size):
    # Open the image data with PIL
    image = Image.open(io.BytesIO(image_data))
    # Resize the image using thumbnail algorithm
    image.thumbnail(size, Image.LANCZOS)
    # Convert the image to RGBA mode
    image = image.convert("RGBA")
    # Save the image to a BytesIO object
    output = io.BytesIO()
    image.save(output, format="PNG")
    # Seek to the beginning of the output
    output.seek(0)
    # Read the output as bytes
    resized_image_data = output.read()
    # Close the output
    output.close()
    # Return the resized image data
    return resized_image_data

