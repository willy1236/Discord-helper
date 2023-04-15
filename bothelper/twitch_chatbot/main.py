import twitchio,secrets
from twitchio.ext import commands,eventsub
from bothelper.database import Jsondb
from main import bot as discord_bot

tokens = Jsondb.get_token('twitch_chatbot')
initial_channels = Jsondb.cache.get('twitch_initial_channels')

esbot = commands.Bot.from_client_credentials(client_id=tokens.get('id'),client_secret=tokens.get('secret'))
esclient = eventsub.EventSubClient(esbot,webhook_secret=secrets.token_hex(12),callback_route='https://willy1236.loca.lt/twitch_eventsub')

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=tokens.get('token'), prefix='!!', initial_channels=initial_channels,client_id=tokens.get('id'),nick='bot')
        self.channel = discord_bot.get_channel(1096717312297533510)
        #self.loop.run_until_complete(bot.__ainit__())

    async def __ainit__(self):
        self.loop.create_task(esclient.listen(port=14000))

        try:
            await esclient.subscribe_channel_follows_v2(broadcaster='sakagawa_0309', moderator='helper_chatbot')
        except twitchio.HTTPException:
            pass


    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        #await bot.connected_channels[0].send('...')

    async def event_reconnect(self):
        print(f'reconnect as | {self.nick}')

    @commands.command()
    async def hi(self, ctx: commands.Context):
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('pong')

    async def event_message(self,message:twitchio.Message):
        if hasattr(message.author, 'name'):
            #print(message.content)
            self.channel.send(message.content)
            #await bot.handle_commands(message)

bot = Bot()
bot.loop.run_until_complete(bot.__ainit__())

@esbot.event()
async def event_eventsub_notification_follow(payload: eventsub.ChannelFollowData) -> None:
    print('Received event!')
    #channel = bot.get_channel('channel')
    print(f'{payload.data.user.name} followed woohoo!')
    #await channel.send(f'{payload.data.user.name} followed woohoo!')

if __name__ == '__main__':
    bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
