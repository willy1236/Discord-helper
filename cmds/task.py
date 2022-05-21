import discord, asyncio, datetime
from datetime import datetime, timezone, timedelta,time
from discord.ext import commands,tasks
from cmds.weather import EarthquakeReport
from core.classes import Cog_Extension
from BotLib.database import Database
from BotLib.gamedata import ApexData

class task(Cog_Extension):
    def __init__(self,*args,**kwargs):
        #jevent = Database().jevent
        super().__init__(*args,**kwargs)
        #await self.bot.wait_until_ready()
    tz = timezone(timedelta(hours=+8))
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.sign_reset.start()
        self.earthquake_check.start()
        self.apex_crafting_update.start()
        self.apex_map_update.start()
    
    def _get_next_hour():
        tz = timezone(timedelta(hours=+8))
        time = datetime.now(tz=tz)+timedelta(hours=1)
        return time.hour
    
    def _get_next_half_minute():
        tz = timezone(timedelta(hours=+8))
        time = datetime.now(tz=tz).minute
        if time >= 0 and time <30:
            return 30
        else:
            return 0
    
    @tasks.loop(time=time(hour=00,minute=0,second=0,tzinfo=tz))
    async def sign_reset(self):
        task_report_channel = self.bot.get_channel(self.jdata['task_report'])
        reset = []
        Database().write('jdsign',reset)
        await task_report_channel.send('簽到已重置')

    @tasks.loop(minutes=5)
    async def earthquake_check(self):
        jdata = Database().jdata
        timefrom = jdata['timefrom']
        data = EarthquakeReport.get_report_auto(timefrom)
        if data:
            embed = data.desplay
            time = datetime.strptime(data.originTime, "%Y-%m-%d %H:%M:%S")+timedelta(seconds=1)
            jdata['timefrom'] = time.strftime("%Y-%m-%dT%H:%M:%S")
            Database().write('jdata',jdata)
            
            ch_list = Database().cdata['earthquake']
            for i in ch_list:
                channel = self.bot.get_channel(ch_list[i])
                if channel:
                    await channel.send('地震報告',embed=embed)

    @tasks.loop(time=time(hour=1,minute=5,second=0,tzinfo=tz))
    async def apex_crafting_update(self):
        cdata = Database().cdata
        embed = ApexData.get_crafting().desplay
        for i in cdata["apex_crafting"]:
            channel = self.bot.get_channel(cdata["apex_crafting"][i])
            try:
                id = channel.last_message_id
                msg = await channel.fetch_message(id)
            except:
                msg = None

            if msg and msg.author == self.bot.user:
                await msg.edit('Apex合成台內容自動更新資料',embed=embed)
            else:
                await channel.send('Apex合成台內容自動更新資料',embed=embed)
            await asyncio.sleep(1)
    
    @tasks.loop(time=time(hour=_get_next_hour(),minute=_get_next_half_minute(),second=0,tzinfo=tz))
    async def apex_map_update(self):
        cdata = Database().cdata
        embed = ApexData.get_map_rotation().desplay
        for i in cdata["apex_map"]:
            channel = self.bot.get_channel(cdata["apex_map"][i])
            try:
                id = channel.last_message_id
                msg = await channel.fetch_message(id)
            except:
                msg = None

            if msg and msg.author == self.bot.user:
                await msg.edit('Apex地圖輪替自動更新資料',embed=embed)
            else:
                await channel.send('Apex地圖輪替自動更新資料',embed=embed)
            await asyncio.sleep(1)

    def get_time(tz):
        zt = datetime.now().astimezone(tz)
        zt = zt+timedelta(seconds=20)
        now_time = time(hour=zt.hour, minute=zt.minute, second=zt.second,tzinfo=tz)
        return now_time
    now_time = get_time(tz)

    @tasks.loop(time=now_time)
    async def test_task(self):
        print('task_worked')

    @tasks.loop(seconds=1)
    async def time_task(self):
        now_time_hour = datetime.now().strftime('%H%M%S')
        #now_time_day = datetime.datetime.now().strftime('%Y%m%d')

def setup(bot):
    bot.add_cog(task(bot))