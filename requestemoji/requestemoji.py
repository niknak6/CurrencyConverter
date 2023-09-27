from discord.ext import commands
from PIL import Image
import io
import requests
import asyncio

# Inherit from commands.Cog base class
class RequestEmoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def request(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid request type passed...')

    @request.command()
    async def sticker(self, ctx, name: str):
        await self.handle_request(ctx, name, 'sticker', 320, 500)

    @request.command()
    async def emoji(self, ctx, name: str):
        await self.handle_request(ctx, name, 'emoji', 128, 256)

    async def handle_request(self, ctx, name: str, request_type: str, size: int, max_kb: int):
        if not ctx.message.attachments:
            await ctx.send('Please attach an image.')
            return

        image_url = ctx.message.attachments[0].url
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))

        # Check the file size
        file_size_kb = len(response.content) / 1024
        if file_size_kb > max_kb:
            await ctx.send(f'The file size is too large. It must be under {max_kb}KB.')
            return

        # Resize the image
        image = self.resize_image(image, size)

        # Save the resized image
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='PNG')
        output_buffer.seek(0)

        # Send the resized image
        await ctx.send(file=discord.File(fp=output_buffer, filename=f'{name}.png'))

        # Ask for approval
        msg = await ctx.send('React to approve or deny this request.')
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check(reaction, user):
            return user.guild_permissions.administrator and reaction.message.id == msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=1800.0, check=check)
            if str(reaction.emoji) == '✅':
                # Add the emoji or sticker to the guild
                if request_type == 'emoji':
                    await ctx.guild.create_custom_emoji(name=name, image=output_buffer.getvalue())
                else:
                    await ctx.guild.create_custom_sticker(name=name, image=output_buffer.getvalue())
                await ctx.send(f'Your request has been approved and added by {user.mention}!')
            else:
                await ctx.send(f'Your request has been denied by {user.mention}.')
        except asyncio.TimeoutError:
            await ctx.send('Your request has timed out.')

    def resize_image(self, image: Image.Image, size: int) -> Image.Image:
        # Calculate the aspect ratio
        width_ratio = size / image.width
        height_ratio = size / image.height
        ratio = min(width_ratio, height_ratio)

        # Calculate the new width and height
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)

        # Resize the image
        return image.resize((new_width, new_height), Image.ANTIALIAS)

# Use setup function to register the cog with the bot
def setup(bot)
    bot.add_cog(RequestEmoji(bot))
