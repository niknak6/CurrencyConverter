from discord.ext import commands
from PIL import Image
import io
import requests
import asyncio

# Inherit from commands.Cog base class
class RequestEmoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Use commands.group decorator to create a command group
    @commands.group()
    async def request(self, ctx):
        # Check if a subcommand was invoked
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid request type passed...')

    # Use commands.command decorator to create a subcommand
    @request.command()
    async def sticker(self, ctx, name: str):
        # Call the handle_request method with the appropriate parameters
        await self.handle_request(ctx, name, 'sticker', 320, 500)

    # Use commands.command decorator to create another subcommand
    @request.command()
    async def emoji(self, ctx, name: str):
        # Call the handle_request method with the appropriate parameters
        await self.handle_request(ctx, name, 'emoji', 128, 256)

    # Define a helper method to handle the request logic
    async def handle_request(self, ctx, name: str, request_type: str, size: int, max_kb: int):
        # Check if the message has an attachment
        if not ctx.message.attachments:
            await ctx.send('Please attach an image.')
            return

        # Get the image URL from the attachment
        image_url = ctx.message.attachments[0].url
        # Make a GET request to the image URL and get the response content as bytes
        response = requests.get(image_url)
        # Open the image using PIL.Image module
        image = Image.open(io.BytesIO(response.content))

        # Check the file size in KB
        file_size_kb = len(response.content) / 1024
        # Compare it with the max KB allowed for the request type
        if file_size_kb > max_kb:
            await ctx.send(f'The file size is too large. It must be under {max_kb}KB.')
            return

        # Resize the image using the helper method
        image = self.resize_image(image, size)

        # Save the resized image to a buffer object in PNG format
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='PNG')
        # Seek to the beginning of the buffer object
        output_buffer.seek(0)

        # Send the resized image as a file attachment with the given name
        await ctx.send(file=discord.File(fp=output_buffer, filename=f'{name}.png'))

        # Ask for approval from an administrator using reactions
        msg = await ctx.send('React to approve or deny this request.')
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        # Define a check function to filter reactions by administrators and message ID
        def check(reaction, user):
            return user.guild_permissions.administrator and reaction.message.id == msg.id

        try:
            # Wait for a reaction that passes the check function within 30 minutes (1800 seconds)
            reaction, user = await self.bot.wait_for('reaction_add', timeout=1800.0, check=check)
            # Check if the reaction emoji is a check mark
            if str(reaction.emoji) == '✅':
                # Add the emoji or sticker to the guild using the buffer object and the name provided by the user
                if request_type == 'emoji':
                    await ctx.guild.create_custom_emoji(name=name, image=output_buffer.getvalue())
                else:
                    await ctx.guild.create_custom_sticker(name=name, image=output_buffer.getvalue())
                # Notify the user that their request has been approved and added by an administrator
                await ctx.send(f'Your request has been approved and added by {user.mention}!')
            else:
                # Notify the user that their request has been denied by an administrator
                await ctx.send(f'Your request has been denied by {user.mention}.')
        except asyncio.TimeoutError:
            # Notify the user that their request has timed out after 30 minutes of no reaction
            await ctx.send('Your request has timed out.')

    # Define another helper method to resize images while preserving aspect ratio and quality
    def resize_image(self, image: Image.Image, size: int) -> Image.Image:
        # Calculate the aspect ratio of width and height relative to the desired size
        width_ratio = size / image.width
        height_ratio = size / image.height
        # Choose the smaller ratio to avoid stretching or cropping the image
        ratio = min(width_ratio, height_ratio)

        # Calculate the new width and height based on the ratio
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)

        # Resize the image using the ANTIALIAS filter to reduce distortion
        return image.resize((new_width, new_height), Image.ANTIALIAS)

# Use setup function to register the cog with the bot
def setup(bot):
    bot.add_cog(RequestEmoji(bot))
