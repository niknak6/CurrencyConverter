# Import the necessary modules
import discord
from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import humanize_list
from PIL import Image
import io

# Define a class for the cog
class RequestEmoji(commands.Cog):
    """A cog for requesting custom stickers and emojis."""

    # Initialize the cog with the bot instance and a Config object
    def __init__(self, bot):
        self.bot = bot
        # Create a Config object to store the requests and approvals
        self.config = Config.get_conf(self, identifier=1234567890)
        # Register a guild-level config with default values
        default_guild = {"requests": {}, "approvals": {}}
        self.config.register_guild(**default_guild)

    # Define a command group for requesting stickers or emojis
    @commands.group()
    async def request(self, ctx):
        """Request a custom sticker or emoji."""
        # If no subcommand is invoked, show the help message
        if ctx.invoked_subcommand is None:
            await ctx.send_help()

    # Define a subcommand for requesting stickers
    @request.command()
    @commands.cooldown(1, 60, commands.BucketType.user)  # Limit to one request per minute per user
    async def sticker(self, ctx, name: str):
        """Request a sticker with a given name."""
        # Check if the name is valid (at least 2 characters)
        if len(name) < 2:
            await ctx.send("The sticker name must be at least 2 characters.")
            return

        # Check if there is an attachment in the message
        if not ctx.message.attachments:
            await ctx.send("You must attach an image file for the sticker.")
            return

        # Get the attachment and check if it is an image file
        attachment = ctx.message.attachments[0]
        if not attachment.content_type.startswith("image/"):
            await ctx.send("The attachment must be an image file.")
            return

        # Download the attachment as bytes
        image_bytes = await attachment.read()

        # Open the image with PIL and check its size and format
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        format = image.format

        # Check if the image size is exactly 320x320
        if width != 320 or height != 320:
            # Resize the image using Image.thumbnail method with size (320, 320)
            # This will preserve the aspect ratio and not exceed the original size or the given size
            image.thumbnail((320, 320))

        # Check if the image format is PNG or APNG
        if format not in ["PNG", "APNG"]:
            # Convert the image format to PNG
            image = image.convert("RGBA")

        # Save the image as bytes again
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # Create a discord.File object from the bytes and the filename
        file = discord.File(image_bytes, filename="sticker.png")

        # Send a confirmation message with the sticker preview and reactions
        message = await ctx.send(
            f"{ctx.author.mention} has requested a sticker with name {name}. Here is a preview:",
            file=file,
        )
        await message.add_reaction("\u2705")  # Checkmark emoji
        await message.add_reaction("\u274c")  # Cross emoji

        # Store the request information in the config object
        await self.config.guild(ctx.guild).requests.set_raw(
            message.id, value={"name": name, "file": file}
        )

    # Define a subcommand for requesting emojis
    @request.command()
    @commands.cooldown(1, 60, commands.BucketType.user)  # Limit to one request per minute per user
    async def emoji(self, ctx, name: str):
        """Request an emoji with a given name."""
        # Check if the name is valid (at least 2 characters)
        if len(name) < 2:
            await ctx.send("The emoji name must be at least 2 characters.")
            return

        # Check if there is an attachment in the message
        if not ctx.message.attachments:
            await ctx.send("You must attach an image file for the emoji.")
            return

        # Get the attachment and check if it is an image file
        attachment = ctx.message.attachments[0]
        if not attachment.content_type.startswith("image/"):
            await ctx.send("The attachment must be an image file.")
            return

        # Download the attachment as bytes
        image_bytes = await attachment.read()

        # Open the image with PIL and check its size and format
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        format = image.format

        # Check if the image size is between 32x32 and 128x128
        if width < 32 or height < 32 or width > 128 or height > 128:
            # Resize the image using Image.thumbnail method with size (128, 128)
            # This will preserve the aspect ratio and not exceed the original size or the given size
            image.thumbnail((128, 128))

        # Check if the image format is PNG or GIF
        if format not in ["PNG", "GIF"]:
            # Convert the image format to PNG
            image = image.convert("RGBA")

        # Save the image as bytes again
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # Create a discord.File object from the bytes and the filename
        file = discord.File(image_bytes, filename="emoji.png")

        # Send a confirmation message with the emoji preview and reactions
        message = await ctx.send(
            f"{ctx.author.mention} has requested an emoji with name {name}. Here is a preview:",
            file=file,
        )
        await message.add_reaction("\u2705")  # Checkmark emoji
        await message.add_reaction("\u274c")  # Cross emoji

        # Store the request information in the config object
        await self.config.guild(ctx.guild).requests.set_raw(
            message.id, value={"name": name, "file": file}
        )

    # Define an event listener for reaction add
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle approvals or denials of requests."""
        # Check if the reaction is on a message sent by the bot itself
        if payload.user_id != self.bot.user.id:
            try:
                # Get the guild, member, message, and emoji from the payload
                guild = self.bot.get_guild(payload.guild_id)
                member = guild.get_member(payload.user_id)
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                emoji = payload.emoji

                # Check if the member has administrator permission
                if member.guild_permissions.administrator:
                    # Check if the emoji is a checkmark or a cross
                    if emoji.name == "\u2705":  # Checkmark emoji
                        # Approve the request
                        try:
                            # Get the request information from the config object
                            request_data = await self.config.guild(guild).requests.get_raw(
                                message.id
                            )
                            name = request_data["name"]
                            file = request_data["file"]
                        except KeyError:
                            return

                        # Create a custom sticker or emoji with the request information
                        if file.filename == "sticker.png":
                            sticker = await guild.create_sticker(
                                name=name,
                                description=f"Requested by {member}",
                                emoji="\u2705",  # Checkmark emoji as expression
                                file=file,
                                reason=f"Approved by {member}",
                            )
                            # Send a success message with the sticker
                            embed = discord.Embed(
                                title=f"Sticker approved",
                                description=f"{member.mention} has approved {message.author.mention}'s request for a sticker with name {name}.",
                                color=discord.Color.green(),
                            )
                            embed.set_image(url=sticker.url)
                            await channel.send(embed=embed)
                        elif file
