import discord
import config


class DiscordBot(discord.Client):
    conf = config.load_config()
    channel = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('Logged on as', self.user)
        try:
            self.channel = self.get_channel(int(self.conf['reporting']['discord']['channel_id']))
        except Exception as err:
            print(err)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

    def msg(self, msg):
        if self.channel:
            self.loop.create_task(self.channel.send(msg))

    def msg_file(self, file):
        if self.channel:
            self.loop.create_task(self.channel.send(file=discord.File(file)))

