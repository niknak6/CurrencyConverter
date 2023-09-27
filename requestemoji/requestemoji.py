# Import discord.py and Redbot
import discord
from redbot.core import commands, checks, Config

# Import PIL for image resizing
from PIL import Image

# Import io for bytes manipulation
import io

class RequestEmoji (commands.Cog):
    """A cog that allows users to request emojis and stickers."""

    def __init__ (self, bot):
        self.bot = bot
        # Create a Config object for this cog
        self.config = Config.get_conf (self, identifier=1234567890)
        # Register some default settings
        self.config.register_global (
            # The emoji used for approval
            approve_emoji = "✅",
            # The emoji used for denial
            deny_emoji = "❌",
            # The timeout in seconds for requests
            timeout = 1800
        )

    @commands.Cog.listener ()
    async def on_raw_reaction_add (self, payload):
        """A listener that handles the reactions on request messages."""
        # Get the reaction emoji, message ID, user ID, and guild ID from the payload
        emoji = payload.emoji
        message_id = payload.message_id
        user_id = payload.user_id
        guild_id = payload.guild_id

        # Get the guild object from the bot
        guild = self.bot.get_guild (guild_id)

        # Check if the guild is valid
        if guild is None:
            return

        # Get the user object from the guild
        user = guild.get_member (user_id)

        # Check if the user is valid and not a bot
        if user is None or user.bot:
            return

        # Get the message object from the channel
        channel = guild.get_channel (payload.channel_id)
        message = await channel.fetch_message (message_id)

        # Check if the message is valid and has an embed
        if message is None or not message.embeds:
            return

        # Get the embed object from the message
        embed = message.embeds[0]

        # Check if the embed has an author field with a valid ID
        if not embed.author or not embed.author.url:
            return

        # Get the author ID from the embed URL
        author_id = int(embed.author.url.split('/')[-1])

        # Check if the user is an administrator or the author of the request
        if not await checks.admin_or_permissions().predicate(ctx) and user.id != author_id:
            return

        # Get the approve and deny emojis from the config
        approve_emoji = await self.config.approve_emoji()
        deny_emoji = await self.config.deny_emoji()

        # Check if the reaction emoji matches either of them
        if emoji.name == approve_emoji or emoji.name == deny_emoji:
            # Get the request information from the config using the message ID as a key
            request = await self.config.custom("REQUESTS", message_id).all()

            # Check if the request is valid and has a name, file, and type
            if not request or not request["name"] or not request["file"] or not request["type"]:
                return

            # Create a discord.File object from the request file bytes
            file = discord.File(io.BytesIO(request["file"]), filename=request["name"])

            # Check if the reaction emoji is the approve emoji
            if emoji.name == approve_emoji:
                # Try to create the emoji or sticker in the guild using the request name and file
                try:
                    if request["type"] == "emoji":
                        result = await guild.create_custom_emoji(name=request["name"], image=file)
                    elif request["type"] == "sticker":
                        result = await guild.create_sticker(name=request["name"], file=file)
                    else:
                        return

                    # Send a confirmation message that mentions the requesting user and the approving administrator, along with the created emoji or sticker
                    await channel.send(f"{user.mention} has approved {self.bot.get_user(author_id).mention}'s request for {result}.")
                except Exception as e:
                    # Send an error message if something goes wrong
                    await channel.send(f"Something went wrong while creating {request['type']}: {e}")
            
            # Check if the reaction emoji is the deny emoji
            elif emoji.name == deny_emoji:
                # Send a denial message that mentions the requesting user and the denying administrator
                await channel.send(f"{user.mention} has denied {self.bot.get_user(author_id).mention}'s request for {request['name']}.")

            # Delete the request message and clear the config entry for it
            await message.delete()
            await self.config.custom("REQUESTS", message_id).clear()

    @commands.command ()
    async def requestemoji (self, ctx, name: str, *, attachment: discord.Attachment = None):
        """Request an emoji with a given name and an optional attachment."""
        # Check if the user has provided a valid name
        if not name.isalnum():
            await ctx.send("Please provide a valid name for your emoji. It should only contain letters and numbers.")
            return

        # Check if the user has provided a valid attachment
        if not attachment or not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            await ctx.send("Please provide a valid image file for your emoji. It should be in PNG, JPEG, or GIF format.")
            return

        # Check if the image size and file size meet the requirements for emojis
        if attachment.width < 32 or attachment.width > 128 or attachment.height < 32 or attachment.height > 128 or attachment.size > 256000:
            # If not, use PIL to resize the image accordingly, preserving the aspect ratio and quality as much as possible
            image = Image.open(io.BytesIO(await attachment.read()))
            image.thumbnail((128, 128), Image.LANCZOS)
            output = io.BytesIO()
            image.save(output, format=image.format)
            output.seek(0)
            # Create a new discord.File object from the resized image bytes
            file = discord.File(output, filename=attachment.filename)
        else:
            # If yes, use the original attachment as the file
            file = attachment

        # Create an embed message that shows the preview of the requested emoji, along with the name and author
        embed = discord.Embed(title=f"Request for {name}", color=discord.Color.blue())
        embed.set_image(url="attachment://" + file.filename)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url, url=f"https://discord.com/users/{ctx.author.id}")

        # Add the approve and deny emojis as reactions to the embed message
        approve_emoji = await self.config.approve_emoji()
        deny_emoji = await self.config.deny_emoji()
        message = await ctx.send(file=file, embed=embed)
        await message.add_reaction(approve_emoji)
        await message.add_reaction(deny_emoji)

        # Store some information about the request in your Config object, such as the message ID, author ID, name, file bytes, and type (emoji or sticker)
        await self.config.custom("REQUESTS", message.id).set({
            "author_id": ctx.author.id,
            "name": name,
            "file": output.getvalue() if output else await attachment.read(),
            "type": "emoji"
        })

    @commands.command ()
    async def requeststicker (self, ctx, name: str, *, attachment: discord.Attachment = None):
        """Request a sticker with a given name and an optional attachment."""
        # Check if the user has provided a valid name
        if not name.isalnum():
            await ctx.send("Please provide a valid name for your sticker. It should only contain letters and numbers.")
            return

        # Check if the user has provided a valid attachment
        if not attachment or not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            await ctx.send("Please provide a valid image file for your sticker. It should be in PNG or JPEG format.")
            return

        # Check if the image size and file size meet the requirements for stickers
        if attachment.width != 320 or attachment.height != 320 or attachment.size > 500000:
            # If not, use PIL to resize the image accordingly, preserving the aspect ratio and quality as much as possible
            image = Image.open(io.BytesIO(await attachment.read()))
            image = image.resize((320, 320), Image.LANCZOS)
            output = io.BytesIO()
            image.save(output, format=image.format)
            output.seek(0)
            # Create a new discord.File object from the resized image bytes
            file = discord.File(output, filename=attachment.filename)
        else:
            # If yes, use the original attachment as the file
            file = attachment

        # Create an embed message that shows the preview of the requested sticker, along with the name and author
        embed = discord.Embed(title=f"Request for {name}", color=discord.Color.blue())
        embed.set_image(url="attachment://" + file.filename)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url, url=f"https://discord.com/users/{ctx.author.id}")

        # Add the approve and deny emojis as reactions to the embed message
        approve_emoji = await self.config.approve_emoji()
        deny_emoji = await self.config.deny_emoji()
        message = await ctx.send(file=file, embed=embed)
        await message.add_reaction(approve_emoji)
        await message.add_reaction(deny_emoji)

        # Store some information about the request in your Config object, such as the message ID, author ID, name, file bytes, and type (emoji or sticker)
        await self.config.custom("REQUESTS", message.id).set({
            "author_id": ctx.author.id,
            "name": name,
            "file": output.getvalue() if output else await attachment.read(),
            "type": "sticker"
        })
