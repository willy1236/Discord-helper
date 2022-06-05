import discord
from discord.ext import commands
from core.classes import Cog_Extension
from library import find
from BotLib.database import Database


class moderation(Cog_Extension):
    cdata = Database().cdata
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clean(self,ctx,num:int):
        await ctx.channel.purge(limit=num+1)
        await ctx.send(content=f'清除完成，清除了{num}則訊息',delete_after=5)

    @commands.group(invoke_without_command=True)
    async def set(self,ctx):
        raise commands.errors.ArgumentParsingError('參數錯誤:請輸入正確參數')

    @set.command()
    @commands.has_permissions(manage_channels=True)
    async def crass_chat(self,ctx,channel='remove'):
        if channel != 'remove':
            channel = await find.channel(ctx,channel)
        guild = str(ctx.guild.id)
        
        if channel == 'remove':
            if guild in self.cdata['crass_chat']:
                del self.cdata['crass_chat'][guild]
                Database().write('cdata',self.cdata)
                await ctx.send(f'設定完成，已移除跨群聊天頻道')
            else:
                await ctx.send('此伺服器還沒有設定頻道喔')

        elif channel != None:
            self.cdata['crass_chat'][guild] = channel.id
            Database().write('cdata',self.cdata)
            await ctx.send(f'設定完成，已將跨群聊天頻道設為{channel.mention}')

    @set.command()
    @commands.has_permissions(manage_channels=True)
    async def all_anno(self,ctx,channel='remove'):
        if channel != 'remove':
            channel = await find.channel(ctx,channel)
        guild = str(ctx.guild.id)
        
        if channel == 'remove':
            if guild in self.cdata['all_anno']:
                del self.cdata['all_anno'][guild]
                Database().write('cdata',self.cdata)
                await ctx.send(f'設定完成，已移除全群公告頻道')
            else:
                await ctx.send('此伺服器還沒有設定頻道喔')

        elif channel != None:
            self.cdata['all_anno'][guild] = channel.id
            Database().write('cdata',self.cdata)
            await ctx.send(f'設定完成，已將全群公告頻道設為{channel.mention}')

    @set.command()
    @commands.has_permissions(manage_channels=True)
    async def earthquake(self,ctx,channel='remove'):
        if channel != 'remove':
            channel = await find.channel(ctx,channel)
        guild = str(ctx.guild.id)
        
        if channel == 'remove':
            if guild in self.cdata['earthquake']:
                del self.cdata['earthquake'][guild]
                Database().write('cdata',self.cdata)
                await ctx.send(f'設定完成，已移除地震通知頻道')
            else:
                await ctx.send('此伺服器還沒有設定頻道喔')

        elif channel != None:
            self.cdata['earthquake'][guild] = channel.id
            Database().write('cdata',self.cdata)
            await ctx.send(f'設定完成，已將地震通知頻道設為{channel.mention}')
        
    @set.command()
    @commands.has_permissions(manage_channels=True)
    async def apex_crafting(self,ctx,channel='remove'):
        if channel != 'remove':
            channel = await find.channel(ctx,channel)
        guild = str(ctx.guild.id)
        
        if channel == 'remove':
            if guild in self.cdata['apex_crafting']:
                del self.cdata['apex_crafting'][guild]
                Database().write('cdata',self.cdata)
                await ctx.send(f'設定完成，已移除地震通知頻道')
            else:
                await ctx.send('此伺服器還沒有設定頻道喔')

        elif channel != None:
            self.cdata['apex_crafting'][guild] = channel.id
            Database().write('cdata',self.cdata)
            await ctx.send(f'設定完成，已將Apex合成器內容頻道設為{channel.mention}')

    @set.command()
    @commands.has_permissions(manage_channels=True)
    async def apex_map(self,ctx,channel='remove'):
        if channel != 'remove':
            channel = await find.channel(ctx,channel)
        guild = str(ctx.guild.id)
        
        if channel == 'remove':
            if guild in self.cdata['apex_map']:
                del self.cdata['apex_map'][guild]
                Database().write('cdata',self.cdata)
                await ctx.send(f'設定完成，已移除地震通知頻道')
            else:
                await ctx.send('此伺服器還沒有設定頻道喔')

        elif channel != None:
            self.cdata['apex_map'][guild] = channel.id
            Database().write('cdata',self.cdata)
            await ctx.send(f'設定完成，已將Apex地圖輪轉頻道設為{channel.mention}')

    @set.command()
    @commands.has_permissions(manage_channels=True)
    async def covid_update(self,ctx,channel='remove'):
        if channel != 'remove':
            channel = await find.channel(ctx,channel)
        guild = str(ctx.guild.id)
        
        if channel == 'remove':
            if guild in self.cdata['covid_update']:
                del self.cdata['covid_update'][guild]
                Database().write('cdata',self.cdata)
                await ctx.send(f'設定完成，已移除疫情通知頻道')
            else:
                await ctx.send('此伺服器還沒有設定頻道喔')

        elif channel != None:
            self.cdata['covid_update'][guild] = channel.id
            Database().write('cdata',self.cdata)
            await ctx.send(f'設定完成，已將疫情通知頻道設為{channel.mention}')

def setup(bot):
    bot.add_cog(moderation(bot))