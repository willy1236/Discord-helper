import asyncio,discord,genshin,logging
#from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta,date
from discord.ext import commands,tasks
from requests.exceptions import ConnectTimeout

from core.classes import Cog_Extension
from starcord import Jsondb,sclient
from starcord.DataExtractor import *


apsc_log = logging.getLogger('apscheduler')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.WARNING)
consoleHandler.setFormatter(formatter)
apsc_log.addHandler(consoleHandler)

class task(Cog_Extension):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #await self.bot.wait_until_ready()
    tz = timezone(timedelta(hours=8))
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not Jsondb.jdata.get("debug_mode",True):
            global scheduler
            scheduler = AsyncIOScheduler()
            #scheduler.add_job(self.sign_reset,'cron',hour=4,minute=0,second=0,jitter=30,misfire_grace_time=60)
            scheduler.add_job(self.apex_info_update,'cron',minute='00,15,30,45',second=1,jitter=30,misfire_grace_time=60)
            scheduler.add_job(self.apex_crafting_update,'cron',hour=1,minute=5,second=0,jitter=30,misfire_grace_time=60)
            scheduler.add_job(self.forecast_update,'cron',hour='00,03,06,09,12,15,18,21',minute=0,second=1,jitter=30,misfire_grace_time=60)
            scheduler.add_job(self.auto_hoyo_reward,'cron',hour=19,minute=0,second=0,jitter=30,misfire_grace_time=60)
            #scheduler.add_job(self.update_channel_dict,'cron',hour='*',minute="0,30",second=0,jitter=30,misfire_grace_time=60)

            scheduler.add_job(self.earthquake_check,'interval',minutes=1,jitter=30,misfire_grace_time=40)
            #scheduler.add_job(self.get_mongodb_data,'interval',minutes=3,jitter=30,misfire_grace_time=40)

            scheduler.add_job(sclient.init_NoticeClient,"date")

            scheduler.start()
            self.twitch.start()
        else:
            pass

    # async def sign_reset(self):
    #     sqldb.truncate_table('user_sign')
    #     task_report_channel = self.bot.get_channel(Jsondb.jdata['task_report'])
    #     await task_report_channel.send('簽到已重置')

    async def earthquake_check(self):
        timefrom = Jsondb.read_cache('timefrom')
        try:
            data = CWBClient().get_earthquake_report_auto(timefrom)
        except ConnectTimeout:
            print("earthquake_check timeout.")
            return
        
        if data:
            embed = data.desplay()
            time = datetime.strptime(data.originTime, "%Y-%m-%d %H:%M:%S")+timedelta(seconds=1)
            Jsondb.write_cache('timefrom',time.strftime("%Y-%m-%dT%H:%M:%S"))

            if data.auto_type == 'E-A0015-001':
                text = '顯著有感地震報告'
            elif data.auto_type == 'E-A0016-001':
                text = '小區域地震報告'
            else:
                text = '地震報告'
            
            records = sclient.get_notify_channel_by_type('earthquake')
            for i in records:
                channel = self.bot.get_channel(i['channel_id'])
                if channel:
                    if i.get('role_id'):
                        try:
                            role = self.bot.get_guild(i['guild_id']).get_role(i['role_id'])
                            text += f' {role.mention}'
                        except:
                            pass
                    await channel.send(text,embed=embed)
                    await asyncio.sleep(0.5)
                else:
                    print(f"earthquake_check: {i['guild_id']}/{i['channel_id']}")

    async def apex_info_update(self):
        aclient = ApexInterface()
        map = aclient.get_map_rotation()
        crafting = aclient.get_crafting_from_chche()
        if map:
            embed_list = []
            if crafting:
                embed_list.append(crafting.desplay())
            embed_list.append(map.desplay())
            
            records = sclient.get_notify_channel_by_type('apex_info')
            for i in records:
                channel = self.bot.get_channel(i['channel_id'])
                if channel:
                    try:
                        id = channel.last_message_id
                        msg = await channel.fetch_message(id)
                    except:
                        msg = None

                    if msg and msg.author == self.bot.user:
                        await msg.edit('Apex資訊自動更新資料',embeds=embed_list)
                    else:
                        await channel.send('Apex資訊內容自動更新資料',embeds=embed_list)
                    await asyncio.sleep(0.5)
                
                else:
                    print(f"apex_info_update: {i['guild_id']}/{i['channel_id']}")

    async def apex_crafting_update(self):
        today = date.today()
        apex_crafting = Jsondb.read_cache("apex_crafting")
        if not apex_crafting or apex_crafting.get("date") != today.isoformat():
            apex_crafting = ApexInterface().get_raw_crafting()
            apex_crafting_dict = {
                "date": today.isoformat(),
                "data": apex_crafting[0:2]
            }
            Jsondb.write_cache("apex_crafting",apex_crafting_dict)


    async def forecast_update(self):
        forecast = CWBClient().get_forecast()
        if forecast:
            records = sclient.get_notify_channel_by_type('forecast')
            for i in records:
                channel = self.bot.get_channel(i['channel_id'])
                if channel:
                    try:
                        id = channel.last_message_id
                        msg = await channel.fetch_message(id)
                    except:
                        msg = None

                    if msg and msg.author == self.bot.user:
                        await msg.edit('台灣各縣市天氣預報',embed=forecast.desplay())
                    else:
                        await channel.send('台灣各縣市天氣預報',embed=forecast.desplay())
                    await asyncio.sleep(0.5)
                
                else:
                    print(f"forecast_update: {i['guild_id']}/{i['channel_id']}")

    @tasks.loop(minutes=3)
    async def twitch(self):
        users = sclient.get_notice_dict("twitch")
        if not users:
            return
        twitch_cache = Jsondb.read_cache('twitch')
        data = TwitchAPI().get_lives(users)
        for user in users:
            user_cache = twitch_cache.get(user)
            
            if data[user] and not user_cache:
                twitch_cache[user] = True
                embed = data[user].desplay()
                guilds = sclient.get_notify_community_guild('twitch',user)
                for guildid in guilds:
                    guild = self.bot.get_guild(guildid)
                    channel = self.bot.get_channel(guilds[guildid][0])
                    role = guild.get_role(guilds[guildid][1])
                    if channel:
                        if role:
                            await channel.send(f'{role.mention} 開台啦~',embed=embed)
                        else:
                            await channel.send(f'開台啦~',embed=embed)
                        await asyncio.sleep(0.5)
                    else:
                        print(f"twitch: {guild.id}/{channel.id}")
            elif not data[user] and user_cache:
                #cache['twitch'][user] = False
                del twitch_cache[user]

        Jsondb.write_cache('twitch',twitch_cache)

    async def auto_hoyo_reward(self):
        list = sclient.get_hoyo_reward()
        for user in list:
            user_id = user['user_id']
            user_dc = self.bot.get_user(int(user_id))
            channel_id = user['channel_id']
            channel = self.bot.get_channel(int(channel_id))
            cookies = sclient.get_userdata(user_id,'game_hoyo_cookies')
            if not channel:
                print(f"auto_hoyo_reward: {user_id}/{channel_id}")
            if not cookies:
                await channel.send(f'{user_dc.mention} 沒有設定cookies或已過期')
            else:
                try:
                    client = genshin.Client(cookies,lang='zh-tw')
                    game = genshin.Game(user['game'])

                    reward = await client.claim_daily_reward(game=game,reward=True)
                    if channel and user['need_mention']:
                        await channel.send(f'{user_dc.mention} 簽到完成！獲得{reward.name}x{reward.amount}')
                    elif channel and not user['need_mention']:
                        await channel.send(f'{user_dc.name} 簽到完成！獲得{reward.name}x{reward.amount}')
                except Exception as e:
                    await channel.send(f'{user_dc.mention} 簽到時發生錯誤：{e}')
            
            await asyncio.sleep(30)

    # async def get_mongodb_data(self):
    #     dbdata = mongedb.get_apidata()

    async def update_pubsubhubbub_data(self):
        pass


def setup(bot):
    bot.add_cog(task(bot))