# Create another listener function that listens for the on_message event
@commands.Cog.listener()
async def on_message(self, message):
    """This event is triggered when a user sends a message in any channel."""

    # Get the guild, channel, and author objects from the message
    guild = message.guild
    channel = message.channel
    author = message.author

    # Check if the message author is tagged by the bot in the previous message in this channel, and if the message content is not empty, and if the message is in the same channel as the reaction, and if the message is a reply to the bot's request
    previous_message = await channel.history(limit=1, before=message).next()
    if author in previous_message.mentions and previous_message.author == self.bot and message.content and channel.id == self.push_pin_channel.get(author.id) and message.reference.message_id == previous_message.id:
        # Get the message link and summary from the message object
        message_link = message.jump_url
        summary = f"{author.display_name}: {message.content}"

        # Get the "Pinnable Message" by its ID, which is stored in the variable or database
        pinnable_message_id = self.pinnable_message_id.get(channel.id)
        if pinnable_message_id is not None:
            pinnable_message = await channel.fetch_message(pinnable_message_id)

            # Append the message link and summary to the "Pinnable Message" in a well formatted way
            await pinnable_message.edit(content=pinnable_message.content + "\n" + f"📌 {summary}")

        # Delete both messages that contain the summary and the bot's request, so that they do not clutter the channel
        await message.delete()
        await previous_message.delete()
