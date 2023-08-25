import discord
from redbot.core import commands, Config, utils, checks, bot
# Import the discord.ext.threads module
import discord.ext.threads

class PictureOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild_settings = {
            "picture_only_channel": None
        }
        self.config.register_guild(**default_guild_settings)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = message.guild.id
        picture_only_channel = await self.config.guild(message.guild).picture_only_channel()

        if picture_only_channel and message.channel.id == picture_only_channel:
            if not message.attachments:
                await message.delete()
                # Send a DM to the user when their message is deleted
                await message.author.send(f"Your message was removed from {message.channel.mention} because it did not have a picture attached. You can either post in another channel or post a message with a picture in {message.channel.mention}.")
                # Delete the line that sends a message in the channel to inform other users
                # await message.channel.send(f"{message.author.mention}, messages without pictures are automatically removed from this channel. If you wish to comment on someone else's picture, please start a thread from their message! *This message will be automatically removed in 30 seconds.*", delete_after=30)
            else:
                # Create a thread from the message with a picture
                await message.create_thread(name=f"{message.author.name}'s picture", auto_archive_duration=60)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def enable_picture_only(self, ctx):
        """Enables the picture-only mode in the current channel."""
        channel = ctx.channel
        await self.config.guild(ctx.guild).picture_only_channel.set(channel.id)
        # Set permissions for threads
        await channel.set_permissions(ctx.guild.default_role, send_messages=False, view_channel=True, read_message_history=True, view_threads=True, send_messages_in_threads=True)
        await ctx.send("The channel has been set to picture-only mode.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def disable_picture_only(self, ctx):
        """Disables the picture-only mode in the current channel."""
        channel = ctx.channel
        await self.config.guild(ctx.guild).picture_only_channel.clear()
        # Revert permissions for threads
        await channel.set_permissions(ctx.guild.default_role, send_messages=True, view_channel=True, read_message_history=True, view_threads=None, send_messages_in_threads=None)
        await ctx.send("The channel is no longer in picture-only mode.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def set_picture_only_channel(self, ctx, channel: discord.TextChannel):
        """Sets the picture-only channel for the guild."""
        await self.config.guild(ctx.guild).picture_only_channel.set(channel.id)
        await ctx.send(f"The picture-only channel has been set to {channel.mention}.")

def setup(bot):
    bot.add_cog(PictureOnly(bot))
