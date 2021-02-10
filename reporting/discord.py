import discord
import config


class DiscordBot(discord.Client):
    config = config.load_config()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

    def msg(self, msg):
        channel = self.get_channel(self.config['reporting']['discord']['channel_id'])
        self.loop.create_task(channel.send(msg))
        channel.send()

    def msg_file(self, file):
        channel = self.get_channel(self.config['reporting']['discord']['channel_id'])
        self.loop.create_task(channel.send(file=discord.File(file)))

