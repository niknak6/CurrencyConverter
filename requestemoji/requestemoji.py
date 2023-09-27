import discord
from discord.ext import commands
from PIL import Image
import io

class RequestEmoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def requeststicker(self, ctx, name=None):
        # Check if message has attachment
        if not ctx.message.attachments:
            await ctx.send("Please attach an image file.")
            return
        
        # Get attachment and save to file-like object
        attachment = ctx.message.attachments[0]
        file = io.BytesIO()
        await attachment.save(file)

        # Open image and check format, size, and mode
        image = Image.open(file)
        format = image.format
        size = image.size
        mode = image.mode

        # Convert format if needed
        if format not in ["PNG", "APNG", "LOTTIE"]:
            image = image.convert("RGBA")
            format = "PNG"

        # Resize image if needed
        if size != (320, 320):
            image = image.resize((320, 320), Image.LANCZOS)
            size = (320, 320)

        # Reduce file size if needed
        file_size = file.getbuffer().nbytes
        if file_size > 500 * 1024:
            image.save(file, format=format, optimize=True, quality=85)
            file_size = file.getbuffer().nbytes

        # Seek to beginning of file and create discord.File object
        file.seek(0)
        name = name or attachment.filename.rsplit(".", 1)[0]
        discord_file = discord.File(file, filename=name + ".png")

        # Send file to channel
        message = await ctx.send(file=discord_file)

        # Add reactions to message
        await message.add_reaction("\u2705") # Checkmark
        await message.add_reaction("\u274C") # X

        # Define check function for reaction
        def check(reaction, user):
            return reaction.message.id == message.id and user.guild_permissions.administrator and str(reaction.emoji) in ["\u2705", "\u274C"]

        # Wait for reaction
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=1800)
        except asyncio.TimeoutError:
            # No reaction within 30 minutes
            await ctx.send("Sticker request timed out.")
        else:
            # Reaction added
            if str(reaction.emoji) == "\u2705":
                # Checkmark reaction
                # Create sticker in server
                file.seek(0)
                await self.bot.create_guild_sticker(guild=ctx.guild, name=name, image=file.read(), reason=f"Requested by {ctx.author}")
                await ctx.send(f"Sticker {name} created.")
            elif str(reaction.emoji) == "\u274C":
                # X reaction
                # Deny request
                await ctx.send(f"Sticker {name} denied.")
