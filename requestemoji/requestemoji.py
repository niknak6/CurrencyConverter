# Import the necessary modules
from redbot.core import commands, checks
from redbot.core.bot import Red
from PIL import Image
import discord
import io

# Define the cog class
class RequestEmoji(commands.Cog):
    """A cog that allows users to request custom emojis and stickers."""

    def __init__(self, bot: Red):
        self.bot = bot

    # Define the command group
    @commands.group()
    async def request(self, ctx: commands.Context):
        """Request a custom emoji or sticker."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    # Define the subcommand for requesting an emoji
    @request.command()
    async def emoji(self, ctx: commands.Context, name: str):
        """Request a custom emoji with a given name."""
        # Check if the user attached an image file
        if not ctx.message.attachments:
            await ctx.send("Please attach an image file to your message.")
            return

        # Get the first attachment and its filename
        attachment = ctx.message.attachments[0]
        filename = attachment.filename

        # Check if the filename has a valid extension
        if not filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
            await ctx.send("Please use a valid image format (.png, .jpg, .jpeg, or .gif).")
            return

        # Check if the file size is within the limit
        if attachment.size > 256 * 1024:
            await ctx.send("Please use an image file that is less than 256 KB.")
            return

        # Download the image file as bytes
        image_bytes = await attachment.read()

        # Open the image file with PIL and get its size
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size

        # Check if the image size is within the range
        if not (32 <= width <= 128 and 32 <= height <= 128):
            # Resize the image to fit within the range, preserving the aspect ratio and quality
            image.thumbnail((128, 128), Image.ANTIALIAS)
            # Save the resized image as bytes in PNG format
            resized_bytes = io.BytesIO()
            image.save(resized_bytes, format="PNG")
            resized_bytes.seek(0)
            # Create a new discord.File object with the resized bytes and the same filename
            resized_file = discord.File(resized_bytes, filename=filename)
        else:
            # Use the original file as it is
            resized_file = attachment.to_file()

        # Send the request message with the file and the reactions
        request_message = await ctx.send(f"{ctx.author.mention} has requested a custom emoji named {name}.", file=resized_file)
        await request_message.add_reaction("✅")
        await request_message.add_reaction("❌")

        # Wait for an administrator to react with either checkmark or x
        def check(reaction: discord.Reaction, user: discord.Member):
            return user.guild_permissions.administrator and reaction.message.id == request_message.id and str(reaction.emoji) in ("✅", "❌")

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=1800.0, check=check)
        except asyncio.TimeoutError:
            # If no one reacts within 30 minutes, delete the request message and notify the user
            await request_message.delete()
            await ctx.send(f"{ctx.author.mention}, your request has timed out. Please try again later.")
        else:
            # If someone reacts, check which emoji they used
            if str(reaction.emoji) == "✅":
                # If they used checkmark, try to create the emoji and notify the user and the administrator
                try:
                    emoji = await ctx.guild.create_custom_emoji(name=name, image=resized_bytes.getvalue())
                    await ctx.send(f"{ctx.author.mention}, your request has been approved by {user.mention}. The custom emoji {emoji} has been created.")
                except discord.HTTPException as e:
                    # If there is an error in creating the emoji, notify the user and the administrator
                    await ctx.send(f"{ctx.author.mention}, your request has been approved by {user.mention}, but there was an error in creating the custom emoji: {e}")
            elif str(reaction.emoji) == "❌":
                # If they used x, delete the request message and notify the user and the administrator
                await request_message.delete()
                await ctx.send(f"{ctx.author.mention}, your request has been denied by {user.mention}.")
