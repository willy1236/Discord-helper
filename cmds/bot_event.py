import discord,datetime
from discord.ext import commands
from core.classes import Cog_Extension
from library import BRS
from BotLib.database import Database

class ScamChack:
    def __init__(self,text:str):
        self.text = text
        self.keyword =self.__keyword()

    def __keyword(self):
        keywords = ['Free','免費','Nitro','premiums-nitro','discerd.gift','disceord.gift']
        if self.text in keywords:
            return True
        else:
            return False


class event(Cog_Extension):
    cdata = Database().cdata
    voice_updata = False
    #跨群聊天Ver.1.0
    @commands.Cog.listener()
    async def on_message(self,msg):
        if msg.channel.id in self.cdata['crass_chat'] and msg.author.bot == False:
            await msg.delete()

            embed=discord.Embed(description=f'{msg.content}',color=0x4aa0b5)
            embed.set_author(name=f'{msg.author}',icon_url=f'{msg.author.display_avatar.url}')
            embed.set_footer(text=f'來自: {msg.guild}')

            for i in self.cdata['crass_chat']:
                channel = self.bot.get_channel(i)
                if channel != None:
                    await channel.send(embed=embed)

    # @commands.Cog.listener()
    # async def send_bot_help():
    #     return

    @commands.Cog.listener()
    async def on_message(self, message):
        #if message.content == '小幫手':
        #    pass
        #if message.mention_everyone == True:
        #    await message.reply('你tag所有人了')
        ScamChack = False
        for i in ['Free','free','FREE']:
            if i in message.content:
                for j in ['Nitro','nitro','NITRO']:
                    if j in message.content:
                        ScamChack = True
        
        if ScamChack:
            channel = self.bot.get_channel(message.channel.id)
            await BRS.scam(self,message)
            #await message.delete()
            await channel.send('溫馨提醒:這可能是有關詐騙的訊息\n若要點擊連結請先確認是否安全',reference=message)
        if type(message.channel) == discord.channel.DMChannel:
            await BRS.dm(self,message)

    @commands.Cog.listener()
    async def on_voice_state_update(self,user, before, after):
            if self.voice_updata:
                NowTime = datetime.datetime.now()
                if before.channel != None and after.channel != None and before.channel != after.channel:
                    embed=discord.Embed(description=f'{user.mention} 更換語音',color=0x4aa0b5,timestamp=NowTime)
                elif before.channel == None and after.channel != None:
                    embed=discord.Embed(description=f'{user.mention} 進入語音',color=0x4aa0b5,timestamp=NowTime)
                elif before.channel != None and after.channel == None:
                    embed=discord.Embed(description=f'{user.mention} 離開語音',color=0x4aa0b5,timestamp=NowTime)
                else:
                    return
                embed.set_author(name=user,icon_url=user.display_avatar.url)

                if before.channel:
                    embed.set_footer(text=before.channel.guild.name)
                elif after.channel:
                    embed.set_footer(text=after.channel.guild.name)
                
                if before.channel != None:
                    embed.add_field(name='頻道', value=f'{before.channel.mention}', inline=False)
                if after.channel != None:
                    embed.add_field(name='頻道', value=f'{after.channel.mention}', inline=False)
                
                await self.bot.get_channel(950039715879464970).send(embed=embed)
            

def setup(bot):
    bot.add_cog(event(bot))