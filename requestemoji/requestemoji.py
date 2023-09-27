import discord
from discord.ext import commands
from PIL import Image
from io import BytesIO
import asyncio

class RequestEmoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def requeststicker(self, ctx, *, name: str):
        if len(ctx.message.attachments) == 0:
            await ctx.send("Please attach an image.")
            return

        image = await ctx.message.attachments[0].read()
        image = Image.open(BytesIO(image))

        # Resize the image if it's too big
        if image.size != (320, 320):
            image.thumbnail((320, 320))

        # Save the image as a PNG
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        # Check if the file size is under 500KB
        if buffer.getbuffer().nbytes > 500 * 1024:
            await ctx.send("The file size is too large.")
            return

        # Send the sticker request message
        message = await ctx.send(f"Sticker request: {name}", file=discord.File(fp=buffer, filename="sticker.png"))
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user.guild_permissions.administrator and reaction.message.id == message.id and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=1800.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Request timed out.")
        else:
            if str(reaction.emoji) == "✅":
                # Create the sticker
                guild = ctx.guild
                buffer.seek(0)
                sticker = await guild.create_sticker(name=name, image=buffer.read(), description="")
                await ctx.send(f"Sticker {sticker.name} has been created.")
            else:
                await ctx.send("Request denied.")

def setup(bot):
    bot.add_cog(RequestEmoji(bot))
