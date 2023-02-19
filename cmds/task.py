import asyncio,discord
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
from discord.ext import commands,tasks

from core.classes import Cog_Extension
from bothelper import Jsondb
from bothelper.interface import *

class task(Cog_Extension):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #await self.bot.wait_until_ready()
    tz = timezone(timedelta(hours=+8))
    
    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.user.id == 589744540240314368:
            scheduler = AsyncIOScheduler()
            scheduler.add_job(self.sign_reset,'cron',hour=4,minute=0,second=0)
            scheduler.add_job(self.covid_update,'cron',hour=14,minute='30,40',second=0)
            scheduler.add_job(self.apex_crafting_update,'cron',hour=1,minute=5,second=0)
            scheduler.add_job(self.apex_map_update,'cron',minute='00,15,30,45',second=0)
            scheduler.add_job(self.forecast_update,'cron',hour='00,03,06,09,12,15,18,21',minute=0,second=1)
            
            scheduler.start()
            self.earthquake_check.start()
            self.twitch.start()
        if self.bot.user.id == 870923985569861652:
            pass

    # @commands.command()
    # async def task(self,ctx,task_name):
    #     if task_name == 'apex_map_update' or task_name == 'all':
    #         await self.apex_map_update.__call__()
    #         await ctx.message.add_reaction('✅')
    #     if task_name == 'apex_crafting_update' or task_name == 'all':
    #         await self.apex_crafting_update.__call__()
    #         await ctx.message.add_reaction('✅')
    #     if task_name == 'earthquake_check' or task_name == 'all':
    #         await self.earthquake_check.__call__()
    #         await ctx.message.add_reaction('✅')
    #     if task_name == 'covid_update' or task_name == 'all':
    #         await self.covid_update.__call__()
    #         await ctx.message.add_reaction('✅')
    #     if task_name == 'forecast_update' or task_name == 'all':
    #         await self.forecast_update.__call__()
    #         await ctx.message.add_reaction('✅')

    async def sign_reset(self):
        task_report_channel = self.bot.get_channel(Jsondb.jdata['task_report'])
        self.sqldb.truncate_table('user_sign')
        await task_report_channel.send('簽到已重置')
        await asyncio.sleep(10)

    @tasks.loop(minutes=1)
    async def earthquake_check(self):
        cache = Jsondb.cache
        timefrom = cache['timefrom']
        data = CWBInterface().get_report_auto(timefrom)
        if data:
            embed = data.desplay()
            time = datetime.strptime(data.originTime, "%Y-%m-%d %H:%M:%S")+timedelta(seconds=1)
            cache['timefrom'] = time.strftime("%Y-%m-%dT%H:%M:%S")
            Jsondb.write('cache',cache)

            if data.auto_type == 'E-A0015-001':
                text = '顯著有感地震報告'
            elif data.auto_type == 'E-A0016-001':
                text = '小區域地震報告'
            else:
                text = '地震報告'
            
            records = self.sqldb.get_notice_channel('earthquake')
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
    
    async def covid_update(self):
        CovidReport = Covid19Interface.get_covid19()
        if CovidReport:
            records = self.sqldb.get_notice_channel('covid_update')
            for i in records:
                channel = self.bot.get_channel(i["channel_id"])
                try:
                    id = channel.last_message_id
                    msg = await channel.fetch_message(id)
                except:
                    msg = None

                if msg and msg.author == self.bot.user:
                    await msg.edit('Covid 疫情資訊',embed=CovidReport.desplay())
                else:
                    await channel.send('Covid 疫情資訊',embed=CovidReport.desplay())
                await asyncio.sleep(0.5)
        await asyncio.sleep(10)

    
    async def apex_crafting_update(self):
        crafting = ApexInterface().get_crafting()
        if crafting:
            records = self.sqldb.get_notice_channel('apex_crafting')
            for i in records:
                channel = self.bot.get_channel(i['channel_id'])
                try:
                    id = channel.last_message_id
                    msg = await channel.fetch_message(id)
                except:
                    msg = None

                if msg and msg.author == self.bot.user:
                    await msg.edit('Apex合成台內容自動更新資料',embed=crafting.desplay())
                else:
                    await channel.send('Apex合成台內容自動更新資料',embed=crafting.desplay())
                await asyncio.sleep(0.5)
        await asyncio.sleep(10)
        #self.apex_crafting_update.stop()

    async def apex_map_update(self):
        map = ApexInterface().get_map_rotation()
        if map:
            records = self.sqldb.get_notice_channel('apex_map')
            for i in records:
                channel = self.bot.get_channel(i['channel_id'])
                try:
                    id = channel.last_message_id
                    msg = await channel.fetch_message(id)
                except:
                    msg = None

                if msg and msg.author == self.bot.user:
                    await msg.edit('Apex地圖輪替自動更新資料',embed=map.desplay())
                else:
                    await channel.send('Apex地圖輪替自動更新資料',embed=map.desplay())
                await asyncio.sleep(0.5)
        #self.apex_map_update.change_interval(time=task.__gettime_15min())
        await asyncio.sleep(10)
    
    
    async def forecast_update(self):
        forecast = CWBInterface().get_forecast()
        if forecast:
            records = self.sqldb.get_notice_channel('forecast')
            for i in records:
                channel = self.bot.get_channel(i['channel_id'])
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
        #self.forecast_update.change_interval(time=task.__gettime_3hr())
        await asyncio.sleep(10)
    
    # @tasks.loop(seconds=1)
    # async def time_task(self):
    #     now_time_hour = datetime.now().strftime('%H%M%S')
    #     #now_time_day = datetime.datetime.now().strftime('%Y%m%d')
    
    @tasks.loop(minutes=2)
    async def twitch(self):
        cache = Jsondb.cache
        users = self.sqldb.get_notice_community_userlist('twitch')
        if not users:
            return
        
        data = Twitch().get_lives(users)
        for user in users:
            if data[user] and not cache['twitch'].get(user,False):
                cache['twitch'][user] = True
                embed = data[user].desplay()
                guilds = self.sqldb.get_notice_community_guild('twitch',user)
                for guildid in guilds:
                    guild = self.bot.get_guild(guildid)
                    channel = self.bot.get_channel(guilds[guildid][0])
                    role = guild.get_role(guilds[guildid][1])
                    if channel:
                        if role:
                            await channel.send(f'{role.mention} 開台啦~',embed=embed)
                        else:
                            await channel.send(f'開台啦~',embed=embed)
                    await asyncio.sleep(1)
            elif not data[user] and cache['twitch'].get(user,False):
                cache['twitch'][user] = False
            
        Jsondb.write('cache',cache)

def setup(bot):
    bot.add_cog(task(bot))