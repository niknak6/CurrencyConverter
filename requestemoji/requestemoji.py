import discord
from redbot.core import commands, checks, errors
from redbot.core.utils.chat_formatting import pagify
from discord.ext.commands.converter import EmojiConverter
from PIL import Image
import io

class RequestEmoji(commands.Cog):
  """A cog that allows users to request custom emojis."""

  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="requestemoji", aliases=["reqemoji"], help="Request a custom emoji to be added to the server.", usage="<name> [attachment]", cooldown_after_parsing=True)
  @commands.guild_only()
  @commands.cooldown(1, 60, commands.BucketType.user)
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
    
    try: # Try to open the image data with PIL and check its size and format
      image = Image.open(io.BytesIO(image_data))
      width, height = image.size
      format = image.format
      if width > 128 or height > 128 or format not in ["PNG", "JPEG"]: # If the image is too large or not in PNG or JPG format, try to resize or convert it
        image = image.resize((128, 128), Image.LANCZOS) # Resize the image to 128x128 pixels using LANCZOS algorithm
        image = image.convert("RGBA") # Convert the image to RGBA mode
        format = "PNG" # Set the format to PNG
        output = io.BytesIO() # Create a BytesIO object to store the output
        image.save(output, format=format) # Save the image to the output
        output.seek(0) # Seek to the beginning of the output
        image_data = output.read() # Read the output as bytes
        output.close() # Close the output
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
    embed.set_footer(text="This request will expire in 60 seconds.") # Set the embed footer to show the expiration time
    file = discord.File(io.BytesIO(image_data), filename="emoji.png") # Create a discord File object from the image data with filename emoji.png
    message = await ctx.send(embed=embed, file=file) # Send the embed message with the file attachment
    
    # Add a checkmark and x emoji as reactions to the embed message
    await self.bot.add_reaction(message, "\u2705") # Checkmark emoji
    await self.bot.add_reaction(message, "\u274c") # X emoji
    
    # Wait for a reaction from an Officer or Guild Master
    def check(reaction, user): # Define a check function that returns True if the reaction is valid and False otherwise
      return (reaction.message.id == message.id and user != self.bot.user and checks.is_mod_or_superior(self.bot, user) and reaction.emoji in ["\u2705", "\u274c"])
    
    try: # Try to wait for a reaction that passes the check function within 60 seconds
      reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError: # If no reaction is received within the time limit, send a message to inform that the request expired
      await ctx.send(f"The emoji request for {name} has expired.")
      return
    
    # If the reaction is a checkmark, try to create the emoji and send a message to confirm
    if reaction.emoji == "\u2705":
      try: # Try to create the emoji using ctx.guild.create_custom_emoji()
        emoji = await ctx.guild.create_custom_emoji(name=name, image=image_data)
        await ctx.send(f"The emoji {emoji} was added successfully.")
      except Exception as e: # If something goes wrong, raise an error and send a message
        raise errors.UserFeedbackCheckFailure(f"Something went wrong while creating the emoji: {e}")
        await ctx.send(f"There was an error while creating the emoji. Please try again later.")
        return
    
    # If the reaction is an x, send a message to inform that the request was denied
    if reaction.emoji == "\u274c":
      await ctx.send(f"The emoji request for {name} was denied by {user.mention}.")
