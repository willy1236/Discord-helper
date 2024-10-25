import asyncio
from pathlib import PurePath
from typing import TYPE_CHECKING
from uuid import UUID

from twitchAPI.chat import (Chat, ChatCommand, ChatMessage, ChatSub, EventData,
                            JoinedEvent, LeftEvent, NoticeEvent, WhisperEvent)
from twitchAPI.chat.middleware import ChannelRestriction
from twitchAPI.eventsub.webhook import EventSubWebhook
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.oauth import (UserAuthenticationStorageHelper,
                             UserAuthenticator, refresh_access_token,
                             validate_token)
from twitchAPI.object import eventsub
from twitchAPI.twitch import Twitch
from twitchAPI.type import (AuthScope, ChatEvent, EventSubSubscriptionError,
                            EventSubSubscriptionTimeout)

from starlib import BaseThread, BotEmbed, Jsondb, sclient, twitch_log
from starlib.dataExtractor import TwitchAPI
from starlib.types import NotifyCommunityType

twapi = TwitchAPI()

USER_SCOPE = [
    AuthScope.BITS_READ,
    AuthScope.CHANNEL_BOT,
    AuthScope.CHANNEL_MODERATE,
    AuthScope.CHANNEL_MANAGE_MODERATORS,
    AuthScope.CHANNEL_MANAGE_POLLS,
    AuthScope.CHANNEL_MANAGE_PREDICTIONS,
    AuthScope.CHANNEL_MANAGE_RAIDS,
    AuthScope.CHANNEL_MANAGE_REDEMPTIONS,
    AuthScope.CHANNEL_READ_GOALS,
    AuthScope.CHANNEL_READ_POLLS,
    AuthScope.CHANNEL_READ_PREDICTIONS,
    AuthScope.CHANNEL_READ_REDEMPTIONS,
    AuthScope.CHANNEL_READ_VIPS,
    AuthScope.CHAT_READ,
    AuthScope.CHAT_EDIT,
    AuthScope.MODERATION_READ,
    AuthScope.MODERATOR_MANAGE_BANNED_USERS,
    AuthScope.MODERATOR_MANAGE_BLOCKED_TERMS,
    AuthScope.MODERATOR_MANAGE_CHAT_MESSAGES,
    AuthScope.MODERATOR_MANAGE_CHAT_SETTINGS,
    AuthScope.MODERATOR_READ_CHATTERS,
    AuthScope.MODERATOR_READ_FOLLOWERS,
    AuthScope.USER_BOT,
    AuthScope.USER_EDIT_FOLLOWS,
    AuthScope.USER_MANAGE_BLOCKED_USERS,
    AuthScope.USER_MANAGE_WHISPERS,
    AuthScope.USER_READ_CHAT,
    AuthScope.USER_READ_EMAIL,
    AuthScope.USER_READ_MODERATED_CHANNELS,
    AuthScope.USER_READ_SUBSCRIPTIONS,
    AuthScope.USER_WRITE_CHAT,
    AuthScope.WHISPERS_READ,
    AuthScope.WHISPERS_EDIT,
    ]

TARGET_CHANNEL = sclient.sqldb.get_bot_join_channel_all()
TARGET_CHANNEL_IDS = [str(i) for i in TARGET_CHANNEL.keys()]

# eventsub
async def on_follow(event: eventsub.ChannelFollowEvent):
    #await chat.send_message(data.event.broadcaster_user_name,text = f'{data.event.user_name} now follows {data.event.broadcaster_user_name}!')
    twitch_log.info(f'{event.event.user_name}({event.event.user_login}) now follows {event.event.broadcaster_user_name}!')
    action_channel_id = TARGET_CHANNEL.get(int(event.event.broadcaster_user_id))
    if action_channel_id and sclient.bot:
        sclient.bot.send_message(action_channel_id, embed=BotEmbed.simple("新追隨",f'{event.event.user_name}({event.event.user_login}) 正在追隨 {event.event.broadcaster_user_name}!'))

async def on_stream_online(event: eventsub.StreamOnlineEvent):
    stream = await first(sclient.twitch.get_streams(user_id=event.event.broadcaster_user_id))
    twitch_log.info(f'{event.event.broadcaster_user_name} starting stream!')
    if sclient.bot:
        sclient.bot.send_message(content=f'{event.event.broadcaster_user_name} 正在直播 {stream.game_name}!')
        is_live = Jsondb.get_cache('twitch').get(event.event.broadcaster_user_id)
        if is_live is False:
            embed = twapi.get_lives(event.event.broadcaster_user_id)[event.event.broadcaster_user_id].embed()
            asyncio.run_coroutine_threadsafe(sclient.bot.send_notify_communities(embed, NotifyCommunityType.TwitchLive, event.event.broadcaster_user_id), sclient.bot.loop)
            Jsondb.set_cache('twitch', event.event.broadcaster_user_id, True)
    
    action_channel_id = TARGET_CHANNEL.get(int(event.event.broadcaster_user_id))
    if action_channel_id:
        await chat.send_message(event.event.broadcaster_user_login, f'{event.event.broadcaster_user_name} 正在直播 {stream.game_name}! {stream.title}')

async def on_stream_offline(event: eventsub.StreamOfflineEvent):
    twitch_log.info(f'{event.event.broadcaster_user_name} ending stream.')
    if sclient.bot:
        sclient.bot.send_message(content=f'{event.event.broadcaster_user_name} ending stream.')
        is_live = Jsondb.get_cache('twitch').get(event.event.broadcaster_user_id)
        if is_live is True:
            Jsondb.set_cache('twitch', event.event.broadcaster_user_id, False)

async def on_channel_points_custom_reward_redemption_add(event: eventsub.ChannelPointsCustomRewardRedemptionAddEvent):
    text = f'{event.event.user_name}({event.event.user_login}) 兌換了 {event.event.reward.title}!'
    if event.event.user_input:
        text += f' ({event.event.user_input})'
    twitch_log.info(text)
    action_channel_id = TARGET_CHANNEL.get(int(event.event.broadcaster_user_id))
    if action_channel_id and sclient.bot:
        sclient.bot.send_message(action_channel_id, embed=BotEmbed.simple("兌換自訂獎勵",text))
    
async def on_channel_points_custom_reward_redemption_update(event: eventsub.ChannelPointsCustomRewardRedemptionUpdateEvent):
    twitch_log.info(f"{event.event.user_name}'s redemption of {event.event.reward.title} has been updated!")
    
async def on_channel_raid(event:eventsub.ChannelRaidEvent):
    twitch_log.info(f"{event.event.from_broadcaster_user_name} 帶了 {event.event.viewers} 位觀眾來 {event.event.to_broadcaster_user_name} 的頻道!")

async def on_channel_subscribe(event: eventsub.ChannelSubscribeEvent):
    twitch_log.info(f"{event.event.user_name} 在 {event.event.broadcaster_user_name} 的層級{event.event.tier[0]}新訂閱")
    action_channel_id = TARGET_CHANNEL.get(int(event.event.broadcaster_user_id))
    if action_channel_id and not event.event.is_gift:
        # await chat.send_message(event.event.broadcaster_user_login, f"感謝 {event.event.user_name} 的訂閱！")
        if sclient.bot:
            sclient.bot.send_message(embed=BotEmbed.simple("subscribe", f"感謝 {event.event.user_name} 的訂閱！"))

async def on_channel_subscription_message(event: eventsub.ChannelSubscriptionMessageEvent):
    texts = [
        f"{event.event.user_name} 在 {event.event.broadcaster_user_name} 的{event.event.duration_months}個月 層級{event.event.tier[0]}訂閱",
        f"他已經訂閱 {event.event.cumulative_months} 個月了",
    ]
    if event.event.message:
        texts.append(f"訊息：{event.event.message.text}")
    
    for text in texts:
        twitch_log.info(text)
    
    action_channel_id = TARGET_CHANNEL.get(int(event.event.broadcaster_user_id))
    if action_channel_id:
        chat_text = f"感謝 {event.event.user_name} 的{event.event.duration_months}個月訂閱！"
        if event.event.cumulative_months:
            chat_text += f"累積訂閱{event.event.cumulative_months}個月！"
        await chat.send_message(event.event.broadcaster_user_login, chat_text)

        if sclient.bot:
            sclient.bot.send_message(action_channel_id, embed=BotEmbed.simple("新訂閱","\n".join(texts)))
            sclient.bot.send_message(embed=BotEmbed.simple("subscription_message", "\n".join(texts)))

async def on_channel_subscription_gift(event: eventsub.ChannelSubscriptionGiftEvent):
    twitch_log.info(f"{event.event.user_name} 在 {event.event.broadcaster_user_name} 送出的{event.event.total}份層級{event.event.tier[0]}訂閱")
    action_channel_id = TARGET_CHANNEL.get(int(event.event.broadcaster_user_id))
    if action_channel_id and not event.event.is_anonymous:
        await chat.send_message(event.event.broadcaster_user_login, f"感謝 {event.event.user_name} 送出的{event.event.total}份訂閱！")

async def on_channel_poll_begin(event: eventsub.ChannelPollBeginEvent):
    twitch_log.info(f"{event.event.broadcaster_user_name} 開始了投票：{event.event.title}")
    if sclient.bot:
        sclient.bot.send_message(embed=BotEmbed.general(event.event.broadcaster_user_name,description=f"{event.event.title}\n{event.event.choices}"))

async def on_channel_prediction_begin(event: eventsub.ChannelPredictionEvent):
    twitch_log.info(f"{event.event.broadcaster_user_name} 開始了預測：{event.event.title}\n{event.event.outcomes[0].title} V.S. {event.event.outcomes[1].title}")
    if sclient.bot:
        sclient.bot.send_message(embed=BotEmbed.general(event.event.broadcaster_user_name,description=f"{event.event.title}\n{event.event.outcomes[0].title} V.S. {event.event.outcomes[1].title}"))

async def on_channel_prediction_end(event: eventsub.ChannelPredictionEndEvent):
    if event.event.status == "resolved":
        twitch_log.info(f"{event.event.broadcaster_user_name} 結束了預測：{event.event.title}")
        for outcome in event.event.outcomes:
            if outcome.id == event.event.winning_outcome_id:
                twitch_log.info(f"{outcome.title} ({outcome.color}) 獲勝！{outcome.users}個人成功預測")
                if sclient.bot:
                    sclient.bot.send_message(embed=BotEmbed.general(event.event.broadcaster_user_name,description=f"{event.event.title}\n{outcome.title} 獲勝！{outcome.users}個人成功預測"))
    else:
        twitch_log.info(f"{event.event.broadcaster_user_name} 取消了預測：{event.event.title}")


# bot
async def on_ready(ready_event: EventData):
    twitch_log.info(f'Bot is ready as {ready_event.chat.username}, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    if users_login:
        await ready_event.chat.join_room(users_login)

# this will be called whenever a message in a channel was send by either the bot OR another user
async def on_message(msg: ChatMessage):
    twitch_log.info(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

async def on_sub(sub: ChatSub):
    twitch_log.info(f'New subscription in {sub.room.name}:')
    twitch_log.info(f'Type: {sub.sub_plan_name}')
    twitch_log.info(f'Message: {sub.sub_message}')
    twitch_log.info(f"System message: {sub.system_message}")

async def on_bot_joined(event: JoinedEvent):
    await asyncio.sleep(1)
    text = f'Joined bot in {event.room_name}'
    if event.chat.is_mod(event.room_name):
        text += " as mod"
    twitch_log.info(text)
        
async def on_bot_leaved(event: LeftEvent):
    twitch_log.info(f'Leaved bot in {event.room_name}')

async def on_server_notice(event: NoticeEvent):
    if event.room:
        twitch_log.info(f'Notice from server: {event.message} in {event.room.name}')
    else:
        twitch_log.info(f'Notice from server: {event.message}')

async def on_whisper(event: WhisperEvent):
    twitch_log.info(f'Whisper from {event.user.name}: {event.message}')
    if sclient.bot:
        sclient.bot.send_message(embed=BotEmbed.general(event.user.name, Jsondb.get_picture("twitch_001"),description=event.message))

async def on_raid(event:dict):
    print(event)
    try:
        twitch_log.info(f'Raid from {event["tags"]["display-name"]} with {event["tags"]["msg-param-viewerCount"]} viewers')
    except:
        twitch_log.info(event)

# this will be called whenever the !reply command is issued
async def test_command(cmd: ChatCommand):
    if len(cmd.parameter) == 0:
        await cmd.reply('you did not tell me what to reply with')
    else:
        await cmd.reply(f'{cmd.user.name}: {cmd.parameter}')

async def run():
    jtoken = Jsondb.get_token("twitch_chatbot")
    APP_ID = jtoken.get('id')
    APP_SECRET = jtoken.get('secret')

    # validate_data = await validate_token(token)
    # if validate_data.get("client_id") != APP_ID:
    #     token, refresh_token = await refresh_access_token(refresh_token, APP_ID, APP_SECRET)
    #     jtoken['token'] = token
    #     jtoken['refresh'] = refresh_token
    #     Jsondb.set_token("twitch_chatbot", jtoken)
    
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(APP_ID, APP_SECRET)
    # auth = UserAuthenticator(twitch, USER_SCOPE)
    # token, refresh_token = await auth.authenticate()
    # print(token, refresh_token)
    #  await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # 使用自帶的函式處理token
    helper = UserAuthenticationStorageHelper(twitch, USER_SCOPE, storage_path=PurePath('./database/twitch_token.json'))
    await helper.bind()

    me = await first(twitch.get_users())
    users = [user async for user in twitch.get_users(user_ids=TARGET_CHANNEL_IDS)]
    global users_login
    users_login = [user.login for user in users]

    # create chat instance
    global chat
    chat = await Chat(twitch)

    # register the handlers for the events you want
    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)
    # listen to channel subscriptions
    chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation
    chat.register_event(ChatEvent.JOINED, on_bot_joined)
    chat.register_event(ChatEvent.LEFT, on_bot_leaved)
    chat.register_event(ChatEvent.NOTICE, on_server_notice)
    chat.register_event(ChatEvent.WHISPER, on_whisper)
    chat.register_event(ChatEvent.RAID, on_raid)
    
    chat.register_command_middleware(ChannelRestriction(allowed_channel=['sakagawa_0309']))
    # you can directly register commands and their handlers, this will register the !reply command
    # chat.register_command('reply', test_command)
    # TODO: modify_channel_information
    
    chat.start()
    await asyncio.sleep(5)

    # # create eventsub websocket instance and start the client.
    # eventsub = EventSubWebsocket(twitch)
    # eventsub.start()
    # # subscribing to the desired eventsub hook for our user
    # # the given function (in this example on_follow) will be called every time this event is triggered
    # # the broadcaster is a moderator in their own channel by default so specifying both as the same works in this example
    # # We have to subscribe to the first topic within 10 seconds of eventsub.start() to not be disconnected.
    # for user in users:
    #     await eventsub.listen_stream_online(user.id, on_stream_online)
    #     await eventsub.listen_stream_offline(user.id, on_stream_offline)
    #     if chat.is_mod(user.login):
    #         await eventsub.listen_channel_follow_v2(user.id, me.id, on_follow)
    
    eventsub = EventSubWebhook(jtoken.get('callback_uri'), 14001, twitch)
    # unsubscribe from all old events that might still be there
    # this will ensure we have a clean slate
    await eventsub.unsubscribe_all()
    # start the eventsub client
    eventsub.start()
    await asyncio.sleep(3)
    for user in users:
        twitch_log.debug(f"eventsub:{user.login}")
        try:
            await eventsub.listen_stream_online(user.id, on_stream_online)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing stream online: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing stream online: timeout.")
            
        try:
            await eventsub.listen_stream_offline(user.id, on_stream_offline)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing stream offline: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing stream offline: timeout.")
        
        try:
            await eventsub.listen_channel_raid(on_channel_raid, to_broadcaster_user_id=user.id)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing channel raid: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing channel raid: timeout.")
            
        
        twitch_log.debug(f"eventsub:{user.login} done.")

        if not chat.is_mod(user.login):
            continue
        
        try:
            twitch_log.debug("listening to channel points custom reward redemption add")
            await eventsub.listen_channel_points_custom_reward_redemption_add(user.id, on_channel_points_custom_reward_redemption_add)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing to channel points custom reward redemption add: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing to channel points custom reward redemption add: timeout.")

        try:
            twitch_log.debug("listening to channel follow")
            await eventsub.listen_channel_follow_v2(user.id, me.id, on_follow)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing to channel follow: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing to channel follow: timeout.")
        
        try:
            twitch_log.debug("listening to channel points custom reward redemption update")
            await eventsub.listen_channel_points_custom_reward_redemption_update(user.id, on_channel_points_custom_reward_redemption_update)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing to channel points custom reward redemption update: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing to channel points custom reward redemption update: timeout.")

        try:
            twitch_log.debug("listening to channel subscribe")
            await eventsub.listen_channel_subscribe(user.id, on_channel_subscribe)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing to channel subscribe: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing to channel subscribe: timeout.")

        try:
            twitch_log.debug("listening to channel subscription message")
            await eventsub.listen_channel_subscription_message(user.id, on_channel_subscription_message)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing to channel subscription message: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing to channel subscription message: timeout.")

        try:
            twitch_log.debug("listening to channel subscription gift")
            await eventsub.listen_channel_subscription_gift(user.id, on_channel_subscription_gift)
            await asyncio.sleep(1)
        except EventSubSubscriptionError as e:
            twitch_log.warning(f"Error subscribing to channel subscription gift: {e}")
        except EventSubSubscriptionTimeout:
            twitch_log.warning(f"Error subscribing to channel subscription gift: timeout.")

        # try:
        #     twitch_log.debug("listening to channel poll begin")
        #     await eventsub.listen_channel_poll_begin(user.id, on_channel_poll_begin)
        # except EventSubSubscriptionError as e:
        #     twitch_log.warning(f"Error subscribing to channel poll begin: {e}")
        
        # try:
        #     twitch_log.debug("listening to channel prediction begin")
        #     await eventsub.listen_channel_prediction_begin(user.id, on_channel_prediction_begin)
        # except EventSubSubscriptionError as e:
        #     twitch_log.warning(f"Error subscribing to channel prediction begin: {e}")
        
        # try:
        #     twitch_log.debug("listening to channel prediction end")
        #     await eventsub.listen_channel_prediction_end(user.id, on_channel_prediction_end)
        # except EventSubSubscriptionError as e:
        #     twitch_log.warning(f"Error subscribing to channel prediction end: {e}")
        
    sclient.twitch = twitch
    # we are done with our setup, lets start this bot up!
    return chat, twitch
    
async def run_sakagawa():
    USER_SCOPE_SAKAGAWA = [AuthScope.CHANNEL_READ_REDEMPTIONS]
    jtoken = Jsondb.get_token("twitch_sakagawa")
    token = jtoken['token']
    refresh_token = jtoken['refresh']
    client_id = jtoken['client_id']

    validate_data = await validate_token(token)
    if validate_data.get("client_id") != client_id:
        raise ValueError(validate_data)
    
    twitch_sakagawa = await Twitch(client_id, authenticate_app=False)
    await twitch_sakagawa.set_user_authentication(token, USER_SCOPE_SAKAGAWA, refresh_token)
    target_user = await first(twitch_sakagawa.get_users(logins=TARGET_CHANNEL))

    eventsub_sakagawa = EventSubWebsocket(twitch_sakagawa)
    eventsub_sakagawa.start()
    await eventsub_sakagawa.listen_channel_points_custom_reward_redemption_add(target_user.id, on_channel_points_custom_reward_redemption_add)
    twitch_log.debug("listening to channel points custom reward redemption add")
    await eventsub_sakagawa.listen_channel_points_custom_reward_redemption_update(target_user.id, on_channel_points_custom_reward_redemption_update)
    twitch_log.debug("listening to channel points custom reward redemption update")

class TwitchBotThread(BaseThread):
    if TYPE_CHECKING:
        chat:Chat | None
        twitch:Twitch | None
        
    def __init__(self):
        super().__init__(name='TwitchBotThread')
        self.chat = None
        self.twitch = None

    def run(self):
        chat, twitch = asyncio.run(run())
        self.chat = chat
        self.twitch = twitch
        
        self._stop_event.wait()
        chat.stop()
        asyncio.run(twitch.close())

class SakagawaEventsubThread(BaseThread):
    def __init__(self):
        super().__init__(name='SakagawaEventsubThread')

    def run(self):
        asyncio.run(run_sakagawa())
        self._stop_event.wait()

if __name__ == '__main__':
    # lets run our setup
    chat, twitch = asyncio.run(run())
    chat:Chat
    twitch:Twitch
    # asyncio.run(run_sakagawa())
    # auth = UserAuthenticator(twitch, [AuthScope.CHANNEL_READ_REDEMPTIONS])
    # print(auth.return_auth_url())

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        asyncio.run(twitch.close())
        