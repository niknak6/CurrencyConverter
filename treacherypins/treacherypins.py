import discord
from discord.ext import commands

class TreacheryPins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Check if the reaction is a pushpin emoji
        if payload.emoji.name == "📌":
            # Get the message that was reacted to
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            # Get the user who reacted
            user = self.bot.get_user(payload.user_id)
            # Check if the user also replied to the message with a summary
            reply = await channel.fetch_message(payload.message_id + 1)
            if reply.author == user and reply.reference and reply.reference.message_id == message.id:
                # Get the summary from the reply content
                summary = reply.content
                # Get the message link
                link = message.jump_url
                # Format the pin entry
                pin_entry = f"{summary}\n{link}\n"
                # Check if there is an existing Treachery Pins message in the channel
                pins_message = None
                async for msg in channel.history(limit=100):
                    if msg.author == self.bot and msg.content.startswith("Treachery Pins"):
                        pins_message = msg
                        break
                # If there is no Treachery Pins message, create one
                if pins_message is None:
                    pins_content = "Treachery Pins\n\n" + pin_entry
                    await channel.send(pins_content)
                # If there is a Treachery Pins message, edit it and add the new pin entry
                else:
                    pins_content = pins_message.content + pin_entry
                    await pins_message.edit(content=pins_content)
