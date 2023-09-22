import discord
import re
from redbot.core import commands

class TikTokCog(commands.Cog):
    """A custom cog that reposts tiktok urls"""

    def __init__(self, bot):
        self.bot = bot
        # Compile the tiktok pattern only once
        self.tiktok_pattern = re.compile(r"(?i)(https?://)?((\w+)\.)?tiktok.com/(.+)")

    @commands.Cog.listener()
    async def on_message(self, message):
        """A listener that triggers when a message is sent"""
        # Check if the message is from a user and contains a tiktok url
        if message.author.bot:
            return
        tiktok_url = self.tiktok_pattern.search(message.content)
        if not tiktok_url:
            return
        # Add vx in front of tiktok.com in the url, while preserving the protocol, subdomain, and path parts
        new_url = tiktok_url.expand(r"\1\2vxtiktok.com/\4")
        # Create an embed with the user's name and avatar as the author field
        embed = discord.Embed(description=f"Originally shared this embedded TikTok video.\n{new_url}")
        # Use member.avatar.url instead of member.avatar_url
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
        # Repost the embed and remove the original message
        await message.channel.send(embed=embed)
        await message.delete()
