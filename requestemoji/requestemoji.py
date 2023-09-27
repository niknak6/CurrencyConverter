import discord
from discord.ext import commands
from PIL import Image
import io
import requests

# Define a constant for the sticker size limit (500 KB)
STICKER_SIZE_LIMIT = 500 * 1024

# Define a constant for the sticker dimensions (320 x 320 pixels)
STICKER_WIDTH = 320
STICKER_HEIGHT = 320

# Define a function to resize an image file to a given width and height,
# preserving the aspect ratio and quality
def resize_image(file, width, height):
    # Open the image file as a PIL Image object
    image = Image.open(file)
    # Get the original width and height of the image
    orig_width, orig_height = image.size
    # Calculate the resize ratio by taking min (width/orig_width, height/orig_height)
    ratio = min(width / orig_width, height / orig_height)
    # Calculate the new width and height by multiplying orig_width and orig_height by ratio
    new_width = int(orig_width * ratio)
    new_height = int(orig_height * ratio)
    # Resize the image using PIL's resize method with ANTIALIAS filter
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    # Create a new io.BytesIO object for saving the resized image
    resized_file = io.BytesIO()
    # Save the resized image as a JPEG file with 90% quality
    resized_image.save(resized_file, format='JPEG', quality=90)
    # Seek to the beginning of the resized file
    resized_file.seek(0)
    # Return the resized file object
    return resized_file

# Define a function to compress an image file to a given size limit,
# reducing quality if necessary
def compress_image(file, size_limit):
    # Open the image file as a PIL Image object
    image = Image.open(file)
    # Create a new io.BytesIO object for saving the compressed image
    compressed_file = io.BytesIO()
    # Initialize a variable for quality level (start from 100%)
    quality = 100
    # Loop until break condition is met
    while True:
        # Save the image as a JPEG file with current quality level
        image.save(compressed_file, format='JPEG', quality=quality)
        # Get size of the compressed file in bytes
        file_size = compressed_file.tell()
        # Check if file size is less than or equal to size limit
        if file_size <= size_limit:
            # Break out of the loop
            break
        # Check if quality level is greater than or equal to 10%
        elif quality >= 10:
            # Reduce quality level by 10%
            quality -= 10
            # Seek to the beginning of the compressed file
            compressed_file.seek(0)
            # Truncate the compressed file
            compressed_file.truncate()
        else:
            # Return None to indicate compression failure
            return None
    # Seek to the beginning of the compressed file
    compressed_file.seek(0)
    # Return the compressed file object
    return compressed_file

# Create a bot instance with command prefix "!"
bot = commands.Bot(command_prefix="!")

# Define a command called requeststicker that takes the name of the sticker and the attached attachment to turn into a sticker as arguments
@bot.command()
async def requeststicker(ctx, name, attachment):
    # Check if the user has attached an image file to their message
    if attachment is None or not attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        # Send an error message and return
        await ctx.send("Please attach an image file (jpg, jpeg, or png) to your message.")
        return
    # Get the image file content as bytes
    file_content = requests.get(attachment.url).content
    # Create a new io.BytesIO object from the file content
    file = io.BytesIO(file_content)
    # Check if the image file is larger than the sticker size limit
    if len(file_content) > STICKER_SIZE_LIMIT:
        # Use the compress function to reduce its size
        file = compress_image(file, STICKER_SIZE_LIMIT)
        # Check if the compression was successful
        if file is None:
            # Send an error message and return
            await ctx.send("The image file is too large and cannot be compressed. Please use a smaller image.")
            return
    # Check if the image file has different dimensions than the sticker dimensions
    image = Image.open(file)
    width, height = image.size
    if width != STICKER_WIDTH or height != STICKER_HEIGHT:
        # Use the resize function to adjust its width and height
        file = resize_image(file, STICKER_WIDTH, STICKER_HEIGHT)
        # Check if the resizing was successful
        if file is None:
            # Send an error message and return
            await ctx.send("The image file cannot be resized. Please use an image with dimensions 320 x 320 pixels.")
            return
    # Save the resized and compressed image file as a temporary file on disk with a unique name based on ctx.message.id
    temp_filename = f"{ctx.message.id}.jpg"
    with open(temp_filename, 'wb') as temp_file:
        temp_file.write(file.read())
    # Post a message in chat with the name of the sticker, the image file, and a prompt for approval or denial by an administrator. Add two reactions to the message: a checkmark and an x emoji.
    sticker_message = await ctx.send(f"Sticker request: {name}", file=discord.File(temp_filename))
    await sticker_message.add_reaction("\u2705") # checkmark emoji
    await sticker_message.add_reaction("\u274C") # x emoji

    # Define a check function to validate the reaction and user for waiting for approval or denial
    def check(reaction, user):
        # Return True if the reaction is either checkmark or x emoji, 
        # and the user is an administrator of the guild, 
        # and the reaction is on the same message as sticker_message
        return (str(reaction.emoji) == "\u2705" or str(reaction.emoji) == "\u274C") \
               and user.guild_permissions.administrator \
               and reaction.message.id == sticker_message.id

    try:
        # Wait for 30 minutes for an administrator to react to the message with either emoji. 
        reaction, user = await bot.wait_for('reaction_add', timeout=1800.0, check=check)
    except asyncio.TimeoutError:
        # If no reaction is received within that time, delete the temporary file, remove the reactions from the message, and send a message to the user informing them that their request has timed out and asking them to try again later.
        os.remove(temp_filename)
        await sticker_message.clear_reactions()
        await ctx.send(f"Sorry {ctx.author.mention}, your sticker request has timed out. Please try again later.")
    else:
        # If an administrator reacts with the checkmark emoji, use the create_sticker method of the Guild class to create a new sticker with the name and image file provided by the user.
        if str(reaction.emoji) == "\u2705":
            # Get the guild from the context
            guild = ctx.guild
            # Try to create a sticker using the guild's create_sticker method
            try:
                # Create a sticker using the name and temp_filename as arguments
                sticker = await guild.create_sticker(name=name, file=discord.File(temp_filename), reason=f"Created by {ctx.author}")
                # Delete the temporary file
                os.remove(temp_filename)
                # Remove the reactions from the message
                await sticker_message.clear_reactions()
                # Send a confirmation message to the user and the administrator who approved the request
                await ctx.send(f"Sticker created successfully! Name: {sticker.name}, ID: {sticker.id}\nRequested by {ctx.author.mention}, approved by {user.mention}")
            # Handle any errors that may occur
            except discord.Forbidden:
                # The bot does not have the manage_emojis_and_stickers permission
                await ctx.send("Sorry, I don't have permission to create stickers.")
            except discord.HTTPException as e:
                # An error occurred creating a sticker
                await ctx.send(f"Sorry, something went wrong. Error: {e}")
        # If an administrator reacts with the x emoji, delete the temporary file, remove the reactions from the message, and send a denial message to the user and the administrator who denied the request.
        elif str(reaction.emoji) == "\u274C":
            # Delete the temporary file
            os.remove(temp_filename)
            # Remove the reactions from the message
            await sticker_message.clear_reactions()
            # Send a denial message to the user and the administrator who denied the request
            await ctx.send(f"Sticker request denied.\nRequested by {ctx.author.mention}, denied by {user.mention}")
