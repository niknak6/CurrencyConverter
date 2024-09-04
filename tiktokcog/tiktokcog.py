import os
import random
import re
import requests
from PIL import Image, ImageDraw
from redbot.core import commands
import discord

class TikTokCog(commands.Cog):
    """A custom cog that reposts tiktok, x, and twitter urls"""

    def __init__(self, bot):
        self.bot = bot
        self.url_patterns = {
            'tiktok': re.compile(r"(https?://)?((\w+\.)?(\w+)\.)?tiktok.com/(\S*)"),
            'twitter': re.compile(r"(https?://)?((\w+\.)?(\w+)\.)?twitter.com/(\S*)"),
            'x': re.compile(r"(https?://)?((\w+\.)?(\w+)\.)?x.com/(\S*)"),
            'instagram': re.compile(r"(https?://)?((\w+\.)?(\w+)\.)?instagram.com/reel/(\S*)")
        }
        self.new_domains = {
            'tiktok': 'tnktok.com/',
            'twitter': 'vxtwitter.com/',
            'x': 'fixvx.com/',
            'instagram': 'ddinstagram.com/reel/'
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        """A listener that triggers when a message is sent"""
        if message.author.bot:
            return

        if message.reference:
            await self.handle_reply(message)
            return

        for platform, pattern in self.url_patterns.items():
            if (url_match := pattern.search(message.content)):
                new_url, memo_text = self.process_message_content(message.content, url_match, platform)
                avatar_path = self.download_and_process_avatar(message.author.avatar.url)
                await self.repost_message(message, new_url, memo_text, avatar_path)

    def process_message_content(self, content, url_match, platform):
        new_url = self.construct_new_url(url_match, platform)
        memo_text = self.extract_memo_text(content)
        return new_url, memo_text

    def construct_new_url(self, url_match, platform):
        if platform == 'instagram' and 'reel' in url_match.group(5):
            return url_match.group(0).replace('instagram.com', 'ddinstagram.com')
        else:
            return (url_match.group(1) or 'https://') + (url_match.group(2) or '') + self.new_domains[platform] + url_match.group(5)

    def extract_memo_text(self, content):
        return " ".join([part for part in content.split() if not part.lower().startswith(("https://", "http://"))])

    def download_and_process_avatar(self, avatar_url):
        avatar_path = "avatar.png"
        self.download_image(avatar_url, avatar_path)
        self.process_avatar(avatar_path)
        return avatar_path

    def download_image(self, url, path):
        response = requests.get(url)
        with open(path, "wb") as file:
            file.write(response.content)

    def process_avatar(self, path):
        image = Image.open(path).resize((128, 128))
        mask = Image.new("RGBA", image.size)
        ImageDraw.Draw(mask).ellipse([0, 0, *image.size], fill=(0, 0, 0, 255))
        Image.composite(image, Image.new("RGBA", image.size), mask).save(path)

    async def repost_message(self, message, new_url, memo_text, avatar_path):
        emoji = await self.create_custom_emoji(message.guild, avatar_path)
        formatted_message = self.format_message(message.author, emoji, new_url, memo_text)
        await message.channel.send(formatted_message)
        await message.delete()
        await emoji.delete()
        os.remove(avatar_path)

    async def create_custom_emoji(self, guild, avatar_path):
        emoji_name = f"user_avatar_{random.randint(0, 9999)}"
        with open(avatar_path, "rb") as image:
            return await guild.create_custom_emoji(name=emoji_name, image=image.read())

    def format_message(self, author, emoji, new_url, memo_text):
        return f"{emoji} Shared By: {author.mention}\n{new_url}\n{memo_text}"

    async def handle_reply(self, reply):
        referenced_message = await reply.channel.fetch_message(reply.reference.message_id)
        if referenced_message.author == self.bot.user:
            original_poster = self.extract_original_poster(referenced_message.content)
            if original_poster:
                replier_name = reply.author.display_name
                await reply.channel.send(f"{original_poster.mention}, {replier_name} has replied to your reposted message.")

    def extract_original_poster(self, content):
        match = re.search(r'Shared By: <@!?(\d+)>', content)
        if match:
            user_id = int(match.group(1))
            return self.bot.get_user(user_id)
        return None