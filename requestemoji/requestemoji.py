from redbot.core import commands
import discord
from redbot.core import commands, checks, Config
from PIL import Image
import cv2
import io
import asyncio

class RequestEmoji(commands.Cog):
    """A cog that allows users to request custom emojis and stickers."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def request(self, ctx):
        """Request a custom emoji or sticker."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

@request.command()
async def sticker(self, ctx, name: str, image: discord.Attachment):
    """Request a custom sticker."""
    # Check if the name is valid and not already taken
    if not name.isalnum():
        await ctx.send("The name must be alphanumeric.")
        return
    if any(sticker.name == name for sticker in ctx.guild.stickers):
        await ctx.send("There is already a sticker with that name in this guild.")
        return

    # Check if the image is valid and has a supported format
    if image.size > 500 * 1024:
        await ctx.send("The image is too large. The maximum file size is 500 KB.")
        return
    if image.filename.split(".")[-1].lower() not in ["jpg", "jpeg", "png"]:
        await ctx.send("The image format is not supported. The supported formats are JPEG and PNG.")
        return

    # Download the image and resize it to 320x320
    image_bytes = io.BytesIO()
    await image.save(image_bytes)
    image_bytes.seek(0)
    pil_image = Image.open(image_bytes)
    pil_image = pil_image.resize((320, 320), Image.LANCZOS)
    image_bytes = io.BytesIO()
    pil_image.save(image_bytes, format=image.filename.split(".")[-1].upper())
    image_bytes.seek(0)

    # Create a request message and send it to the same channel as the command
    embed = discord.Embed(title=f"Sticker Request: {name}", description=f"Requested by {ctx.author.mention}", color=discord.Color.blue())
    embed.set_image(url="attachment://sticker.png")
    request_message = await ctx.send(embed=embed, file=discord.File(image_bytes, filename="sticker.png"))

    # Add reactions for approval and denial
    await request_message.add_reaction("\u2705") # check mark
    await request_message.add_reaction("\u274c") # cross mark

    # Wait for an administrator to react to the message
    def check(reaction, user):
        return user.guild_permissions.administrator and reaction.message.id == request_message.id and str(reaction.emoji) in ["\u2705", "\u274c"]

    try:
        reaction, user = await self.bot.wait_for("reaction_add", timeout=1800.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, your sticker request has timed out. Please try again later.")
        return

    # Handle the approval or denial accordingly
    if str(reaction.emoji) == "\u2705": # check mark
        try:
            sticker = await ctx.guild.create_sticker(name=name, image=image_bytes.read(), reason=f"Approved by {user}")
            await ctx.send(f"{ctx.author.mention}, your sticker request has been approved by {user.mention}. You can use it with {sticker.name}.")
        except discord.HTTPException as e:
            await ctx.send(f"{ctx.author.mention}, your sticker request has failed due to an error: {e}")
            return
    elif str(reaction.emoji) == "\u274c": # cross mark
        await ctx.send(f"{ctx.author.mention}, your sticker request has been denied by {user.mention}.")
