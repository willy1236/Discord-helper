import discord,genshin,re,asyncio
from discord.ext import commands,pages
from discord.commands import SlashCommandGroup
from datetime import timedelta,datetime

from starcord import Cog_Extension,BotEmbed,Jsondb,csvdb,ChoiceList,sclient
from starcord.DataExtractor import *
from starcord.types import DBGame
from starcord.ui_element.view import GameView

# def player_search(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     results = soup.find_all("h1",class_="row")

#     for result in results:
#         if result.div.string == None:
#             result2 = str(result.div)[166:]
#             lvl = ''.join([x for x in result2 if x.isdigit()])
#             return lvl

set_option = ChoiceList.set('game_set_option')
hoyo_game_option = [
    discord.OptionChoice(name='原神',value=genshin.Game.GENSHIN),
    discord.OptionChoice(name='崩壞3rd',value=genshin.Game.HONKAI),
    discord.OptionChoice(name='崩壞：星穹軌道',value=genshin.Game.STARRAIL)
]

debug_guild = Jsondb.jdata.get('debug_guild')
jdata = Jsondb.jdata

class system_game(Cog_Extension):
    game = SlashCommandGroup("game", "遊戲資訊相關指令")
    lol = SlashCommandGroup("lol", "League of Legends相關指令")
    osu = SlashCommandGroup("osu", "Osu相關指令")
    apex = SlashCommandGroup("apex", "Apex相關指令")
    dbd = SlashCommandGroup("dbd", "Dead by Daylight相關指令")
    steam = SlashCommandGroup("steam", "Steam相關指令")
    hoyo = SlashCommandGroup("hoyo", "MiHaYo相關指令")
    match_cmd = SlashCommandGroup("match", "聯賽相關指令")
        
    @game.command(description='設定遊戲資料')
    async def set(self,ctx,
                  game:discord.Option(str,name='遊戲',description='要設定的遊戲',required=True,choices=set_option),
                  value:discord.Option(str,name='資料',description='要設定的資料，留空以移除資料',default=None)):
        await ctx.defer()
        id = str(ctx.author.id)
        if not value:
            sclient.sqldb.remove_game_data(id,game)
            await ctx.respond(f'已將{game}資料移除')
            return

        player_name = None
        player_id = None
        account_id = None
        other_id = None

        game = DBGame(game)
        unneed_verify = []
        if game in unneed_verify:
            player_name = value
        
        elif game == DBGame.STEAM:
            APIdata = SteamInterface().get_user(value)
            if APIdata:
                player_name = APIdata.name
                player_id = APIdata.id,
            else:
                await ctx.respond(f'錯誤:找不到此用戶',ephemeral=True)
                return
        
        elif game == DBGame.LOL:
            APIdata = RiotAPI().get_riot_account_byname(value)
            if APIdata:
                APIdata = RiotAPI().get_player_bypuuid(value)
                player_name = APIdata.name
                player_id = APIdata.summonerid
                account_id = APIdata.accountid
                other_id = APIdata.puuid
            else:
                await ctx.respond(f'錯誤:找不到此用戶',ephemeral=True)
                return

        elif game == DBGame.APEX:
            APIdata = ApexInterface().get_player(value)
            if APIdata:
                player_name = APIdata.name
                player_id = APIdata.id
            else:
                await ctx.respond(f'錯誤:找不到此用戶',ephemeral=True)
                return

        elif game == DBGame.OSU:
            APIdata = OsuInterface().get_player(value)
            if APIdata:
                player_name = APIdata.name
                player_id = APIdata.id
            else:
                await ctx.respond(f'錯誤:找不到此用戶',ephemeral=True)
                return

        sclient.sqldb.set_game_data(id,game.value,player_name,player_id,account_id,other_id)
        await ctx.respond(f'已將用戶的 {game.name} 資料設定為 {player_name}')
            

    # @game.command(description='揪團找人')
    # async def find(self,
    #                ctx:discord.ApplicationContext,
    #                number_all:discord.Option(int,name='人數',description=''),
    #                game_option:discord.Option(str,name='遊戲',description='',choices=set_option),
    #                message:discord.Option(str,name='要留下的訊息',description='',default=None),
    #                number_now:discord.Option(int,name='現有人數',description='預設為1',default=1)):
    #     game = DBGame(game_option)
    #     creator = ctx.author
    #     view = GameView(creator,game,number_all,number_now,message)
    #     await ctx.respond(embed=view.embed,view=view)
    
    @game.command(description='查詢遊戲資料')
    async def player(self,ctx,
                   user:discord.Option(discord.Member,name='用戶',description='要查詢的用戶',default=None),
                   game:discord.Option(str,name='遊戲',description='若輸入此欄，將會用資料庫的資料查詢玩家',default=None,choices=set_option)):
        await ctx.defer()
        user = user or ctx.author
        userid = user.id
        
        if not game and not (user == ctx.author or self.bot.is_owner(ctx.author)):
            await ctx.respond('目前不開放查詢別人的綜合資料喔',ephemeral=True)
            return
        
        player_data = sclient.get_user_game(userid)

        if player_data:
            await ctx.respond(f'查詢成功',embed=player_data.embed(user))
        else:
            await ctx.respond(f'錯誤：找不到用戶或尚未註冊資料',ephemeral=True)

    # @lol.command(description='查詢League of Legends用戶資料')
    # async def user(self,ctx,userid:discord.Option(str,name='用戶',description='要查詢的用戶')):
    #     url = 'https://lol.moa.tw/summoner/show/'+userid
    #     lvl = player_search(url) or '讀取失敗'

    #     embed = discord.Embed(title="LOL玩家查詢", url=url, color=0xc4e9ff)
    #     embed.add_field(name="玩家名稱", value=userid, inline=False)
    #     embed.add_field(name="等級", value=lvl, inline=False)
    #     embed.add_field(name="查詢戰績", value="LOL戰績網(lol.moa.tw)", inline=False)
    #     embed.set_thumbnail(url='https://i.imgur.com/B0TMreW.png')
    #     await ctx.respond(embed=embed)

    @lol.command(description='查詢League of Legends用戶資料')
    async def user(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag，留空則使用資料庫查詢',required=False)):
        api = RiotAPI()
        user = api.get_riot_account_byname(riot_id)
        player = api.get_player_bypuuid(user.puuid)

        if player:
            await ctx.respond('查詢成功',embed=player.desplay())
        else:
            await ctx.respond('查詢失敗:查無此ID',ephemeral=True)

    @lol.command(description='查詢League of Legends對戰資料')
    async def match(self,ctx,matchid:discord.Option(str,name='對戰id',description='要查詢的對戰')):
        match = RiotAPI().get_match(matchid)
        if match:
            await ctx.respond('查詢成功',embed=match.desplay())
        else:
            await ctx.respond('查詢失敗:查無此ID',ephemeral=True)

    @lol.command(description='查詢最近一次的League of Legends對戰')
    async def playermatch(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag，留空則使用資料庫查詢',required=False)):
        api = RiotAPI()
        player = sclient.get_riot_player(riot_id,ctx.author.id)
        if not player:
            await ctx.respond('查詢失敗：查無此玩家',ephemeral=True)
            return
        puuid = player.puuid
        
        match_list = api.get_player_matchs(puuid,1)
        if not match_list:
            await ctx.respond('查詢失敗:此玩家查無對戰紀錄',ephemeral=True)
            return
        
        match = api.get_match(match_list[0])
        if match:
            await ctx.respond('查詢成功',embed=match.desplay())
        else:
            await ctx.respond('查詢失敗：出現未知錯誤',ephemeral=True)

    @lol.command(description='查詢League of Legends專精英雄')
    async def masteries(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag，留空則使用資料庫查詢',required=False)):
        api = RiotAPI()
        player = sclient.get_riot_player(riot_id,ctx.author.id if not riot_id else None)
        if not player:
            await ctx.respond('查詢失敗：查無此玩家',ephemeral=True)
            return
        
        masteries_list = api.get_summoner_masteries(player.puuid)
        if not masteries_list:
            await ctx.respond('查詢失敗：此玩家查無專精資料',ephemeral=True)
        
        embed = BotEmbed.simple(f"{player.name} 專精英雄")
        for data in masteries_list:
            text = ""
            text += f"專精等級： {data.championLevel}\n"
            text += f"專精分數： {data.championPoints}\n"
            if data.championLevel < 5:
                text += f"距離專精等級提升： {data.championPointsUntilNextLevel}\n"
            elif data.championLevel == 5 or data.championLevel == 6:
                text += f"專精代幣獲取數： {data.tokensEarned}\n"
            text += f"是否取得寶箱： {data.chestGranted}\n"
            #text += f"上次遊玩： {datetime.fromtimestamp(data.lastPlayTime/1000).isoformat(sep=' ')}\n"
            text += f"上次遊玩： <t:{int(data.lastPlayTime/1000)}>\n"
            champion_name = csvdb.get_row_by_column_value(csvdb.lol_champion,"champion_id",data.championId)
            embed.add_field(name=champion_name.loc["name_tw"] if not champion_name.empty else f"ID: {data.championId}",value=text,inline=False)
        await ctx.respond('查詢成功',embed=embed)

    @lol.command(description='查詢League of Legends的玩家積分資訊')
    async def rank(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag，留空則使用資料庫查詢',required=False)):
        api = RiotAPI()
        player = sclient.get_riot_player(riot_id,ctx.author.id if not riot_id else None)
        if not player:
            await ctx.respond('查詢失敗：查無此玩家',ephemeral=True)
            return
        
        rank_data = api.get_summoner_rank(player.summonerid)
        if rank_data:
            embed_list = [rank.desplay() for rank in rank_data]
        else:
            embed_list = [BotEmbed.simple(f"{player.name} 本季未進行過積分對戰")]
        await ctx.respond('查詢成功',embeds=embed_list)

    @lol.command(description='查詢最近的League of Legends對戰ID（僅取得ID，需另行用查詢對戰內容）')
    async def recentmatches(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag，留空則使用資料庫查詢',required=False)):
        api = RiotAPI()
        player = sclient.get_riot_player(riot_id,ctx.author.id if not riot_id else None)
        if not player:
            await ctx.respond('查詢失敗：查無此玩家',ephemeral=True)
            return
        puuid = player.puuid
        
        match_list = api.get_player_matchs(puuid,20)
        if not match_list:
            await ctx.respond('查詢失敗:此玩家查無對戰紀錄',ephemeral=True)
            return
        
        embed = BotEmbed.simple(f"{player.name} 的近期對戰","此排序由新到舊\n" + "\n".join(match_list))
        await ctx.respond('查詢成功',embed=embed)

    @lol.command(description='查詢正在進行的League of Legends對戰（無法查詢聯盟戰棋）')
    async def activematches(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag，留空則使用資料庫查詢',required=False)):
        api = RiotAPI()
        player = sclient.get_riot_player(riot_id,ctx.author.id if not riot_id else None)
        if not player:
            await ctx.respond('查詢失敗：查無此玩家',ephemeral=True)
            return
        
        active_match = api.get_summoner_active_match(player.summonerid)
        if not active_match:
            await ctx.respond(f'{riot_id} 沒有進行中的對戰',ephemeral=True)
            return
        
        await ctx.respond('查詢成功',embed=active_match.desplay())

    @lol.command(description='統計近20場League of Legends對戰的所有玩家牌位')
    @commands.cooldown(rate=60,per=1)
    async def recentplayer(self,ctx,riot_id:discord.Option(str,name='riot_id',description='名稱#tag')):
        await ctx.defer()
        api = RiotAPI()
        msg = await ctx.respond("查詢中，請稍待片刻，查詢過程需時約3~5分鐘")
        df = api.get_rank_dataframe(riot_id,1)
        if df is None:
            await msg.edit("查詢失敗:查無此玩家")
        counts = df['tier'].value_counts()
        await ctx.channel.send(embed=BotEmbed.simple(title="查詢結果",description=str(counts)))
        
        # dict = {
		#     "RANKED_FLEX_SR": "彈性積分",
		#     "RANKED_SOLO_5x5": "單/雙"
	    # }
        # page = []
        # lst = []
        # i = 0
        # for idx,data in df.iterrows():
        #     lst.append(f'{data["name"]} {dict.get(data["queueType"])} {data["tier"]} {data["rank"]}')
        #     if i % 20 == 9 or len(page) * 20 + i + 1 == len(df):
        #         page.append(BotEmbed.simple(title="玩家 積分種類 排名",description="\n".join(lst)))
        #         lst = []
        #         i = 0
        #     else:
        #         i += 1
        # paginator = pages.Paginator(pages=page, use_default_buttons=True)
        # await paginator.send(ctx, target=ctx.channel)


    @osu.command(description='查詢Osu用戶資料')
    @commands.cooldown(rate=1,per=1)
    async def user(self,ctx,
                   username:discord.Option(str,name='玩家名稱',description='要查詢的玩家',default=None)):
        player = OsuInterface().get_player(username)
        if player:
            await ctx.respond('查詢成功',embed=player.desplay())
        else:
            await ctx.respond('查詢失敗:查無此玩家',ephemeral=True)

    @osu.command(description='查詢Osu圖譜資料')
    @commands.cooldown(rate=1,per=1)
    async def map(self,ctx,
                  mapid:discord.Option(str,name='圖譜id',description='要查詢的圖譜ID',default=None)):
        map = OsuInterface().get_beatmap(mapid)
        if map:
            await ctx.respond('查詢成功',embed=map.desplay())
        else:
            await ctx.respond('查詢失敗:查無此圖譜',ephemeral=True)

    @apex.command(description='查詢Apex玩家資料')
    @commands.cooldown(rate=1,per=3)
    async def user(self,
                   ctx:discord.ApplicationContext,
                   username:discord.Option(str,name='玩家名稱',description='要查詢的玩家')):
        player = ApexInterface().get_player(username)
        if player:
            await ctx.respond(content='查詢成功',embed=player.desplay())
        else:
            await ctx.respond(content='查詢失敗:查無此ID',ephemeral=True)

    @apex.command(description='查詢Apex地圖資料')
    @commands.cooldown(rate=1,per=3)
    async def map(self,ctx):
        embed = ApexInterface().get_map_rotation().desplay()
        await ctx.respond(content='查詢成功',embed=embed)

    @apex.command(description='查詢Apex合成器內容資料')
    @commands.cooldown(rate=1,per=3)
    async def crafting(self,ctx):
        embed = ApexInterface().get_crafting().desplay()
        await ctx.respond(content='查詢成功',embed=embed)

    # @apex.command(description='查詢Apex伺服器資料',enabled=False)
    # @commands.cooldown(rate=1,per=3)
    # async def server(self,ctx):
    #     return await ctx.respond(content='暫未開放')
    #     embed = ApexInterface().get_server_status().desplay()
    #     await ctx.respond(content='查詢成功',embed=embed)

    @dbd.command(description='查詢Dead by daylight玩家資料')
    @commands.cooldown(rate=1,per=1)
    async def user(self,ctx,
                   userid:discord.Option(str,name='steamid',description='要查詢的玩家id',default=None)):        
        player = DBDInterface().get_player(userid)
        if player:
            await ctx.respond(content='查詢成功',embed=player.desplay())
        else:
            await ctx.respond(content='查詢失敗:查無此ID或個人資料設定私人',ephemeral=True)

    @steam.command(description='查詢Steam用戶資料')
    @commands.cooldown(rate=1,per=1)
    async def user(self,ctx,
                userid:discord.Option(str,name='用戶id',description='要查詢的用戶',default=None)):
        user = SteamInterface().get_user(userid)
        if user:
            await ctx.respond(content='查詢成功',embed=user.desplay())
        else:
            await ctx.respond(content='查詢失敗:查無此ID',ephemeral=True)


    @hoyo.command(description='如何設定cookies(需先設定才能使用其他功能)')
    @commands.cooldown(rate=1,per=1)
    async def help(self,ctx):
        embed = BotEmbed.simple(description="1.前往 https://www.hoyolab.com/ 並登入\n2.複製以下代碼```script:d=document.cookie; c=d.includes('account_id') || alert('過期或無效的Cookie,請先登出帳號再重新登入!'); c && document.write(d)```\n3.在網址列打上java後直接貼上複製的代碼\n4.找到`ltuid=`跟`ltoken=`並複製其中的內容\n5.使用指令 </hoyo set:1045323352421711947>")
        embed2 = BotEmbed.simple(description="擁有此cookie將可以使機器人以登入帳號的身分瀏覽與操作hoyolab的相關功能，但無法用於登入遊戲與改變遊戲中所持有的內容。\n若對此功能有疑慮，可隨時終止使用，cookie也可以隨時刪除，但米哈遊沒有官方正式API，故若不提供cookie將會無法使用相關功能。")
        await ctx.respond(embeds=[embed,embed2])

    @hoyo.command(description='設定cookies')
    @commands.cooldown(rate=1,per=1)
    async def set(self,ctx,
                  ltuid:discord.Option(str,name='ltuid',required=False),
                  ltoken:discord.Option(str,name='ltoken',required=False),
                  uid:discord.Option(str,name='uid',description="非必填 輸入後能在使用某些功能時自動套用 若輸入過可跳過",required=False),
                  #cookie_token:discord.Option(str,name='cookie_token',description="非必填 輸入後才能使用更多功能 如兌換序號",required=False,default=None),
                  remove:discord.Option(bool,name='若要移除資料請設為true',default=False)):
        if not remove:
            self.sqldb.set_hoyo_cookies(str(ctx.author.id),ltuid,ltoken,None)
            if uid:
                self.sqldb.set_game_data(str(ctx.author.id),DBGame.GENSHIN.value,player_id=uid)
            await ctx.respond(f'{ctx.author.mention} 設定完成',ephemeral=True)
        else:
            self.sqldb.remove_hoyo_cookies(str(ctx.author.id))
            self.sqldb.remove_game_data(str(ctx.author.id),DBGame.GENSHIN.value)
            await ctx.respond(f'{ctx.author.mention} cookies移除完成',ephemeral=True)

    @hoyo.command(description='取得每月原石來源統計（原神）')
    @commands.cooldown(rate=1,per=1)
    async def diary(self,ctx):
        await ctx.defer()
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        client = genshin.Client(cookies,lang='zh-tw')
        diary = await client.get_diary()

        embed_list = []
        primogems_gap = diary.data.current_primogems - diary.data.last_primogems
        if primogems_gap > 0:
            text = f'比上個月多{primogems_gap}顆'
        elif primogems_gap < 0:
            text = f'比上個月少{primogems_gap*-1}顆'
        else:
            text = f'與上個月相同'
        embed = BotEmbed.simple(title=f'本月總計：{diary.data.current_primogems} 顆原石',description=text)
        for category in diary.data.categories:
            name = category.name
            embed.add_field(name=name,value=f'{category.amount}({category.percentage}%)')
        embed_list.append(embed)
        
        mora_gap = diary.data.current_mora - diary.data.last_mora
        if primogems_gap > 0:
            text = f'比上個月多{mora_gap}個'
        elif primogems_gap < 0:
            text = f'比上個月少{mora_gap*-1}個'
        else:
            text = f'與上個月相同'
        embed = BotEmbed.simple(title=f'本月總計：{diary.data.current_mora} 個摩拉',description=text)
        embed_list.append(embed)

        await ctx.respond(ctx.author.mention,embeds=embed_list)

    @hoyo.command(description='尋找HoYoLab用戶')
    @commands.cooldown(rate=1,per=1)
    async def hoyolab(self,ctx,
                   hoyolab_name:discord.Option(str,name='hoyolab名稱',description='要查詢的用戶')):
        await ctx.defer()
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        client = genshin.Client(cookies,lang='zh-tw')

        hoyolab_user = None
        users = await client.search_users(hoyolab_name)
        #print(users)
        for user in users:
            if user.nickname == hoyolab_name:
                hoyolab_user = user
                break
        #print(user.hoyolab_uid)

        #自己搜不到自己
        if hoyolab_user:
            try:
                cards = await client.get_record_cards(user.hoyolab_id)
                embed_list= []
                for card in cards:
                    #print(card.uid, card.level, card.nickname)
                    #活躍天數days_active 獲得角色數characters 成就達成數achievements 深境螺旋spiral_abyss
                    if card.game == genshin.types.Game.GENSHIN:
                    #    print(card.data[0].value,card.data[1].value,card.data[2].value,card.data[3].value)
                        embed = BotEmbed.simple(title=f'{card.nickname}(LV.{card.level})')
                        embed.add_field(name="HoYOLab UID",value=hoyolab_user.hoyolab_id)
                        embed.add_field(name="角色UID",value=card.uid)
                        embed.add_field(name="活躍天數",value=card.data[0].value)
                        embed.add_field(name="獲得角色數",value=card.data[1].value)
                        embed.add_field(name="成就達成數",value=card.data[2].value)
                        embed.add_field(name="深境螺旋",value=card.data[3].value)
                        embed_list.append(embed)
                    await ctx.respond(embeds=embed_list)

            except genshin.errors.DataNotPublic:
                #if e.retcode == 10102:
                await ctx.respond('用戶資訊未公開')
            except genshin.errors.GenshinException as e:
                await ctx.respond(e.msg)
        else:
            hoyolab_user = await client.get_hoyolab_user()
            if hoyolab_user:
                #print(hoyolab_user)
                accounts = await client.get_game_accounts()

                embed = BotEmbed.general(name=f"{hoyolab_user.nickname}(LV.{hoyolab_user.level.level})",
                                         icon_url=hoyolab_user.icon,
                                         url=f"https://www.hoyolab.com/accountCenter/postList?id={hoyolab_user.hoyolab_id}",
                                         description=hoyolab_user.introduction)
                embed.add_field(name="HoYOLab ID",value=hoyolab_user.hoyolab_id)
                for account in accounts:
                    if account.game == genshin.types.Game.GENSHIN:
                        gamename = "原神"
                    elif account.game == genshin.types.Game.HONKAI:
                        gamename = "崩壞3rd"
                    embed.add_field(name=f"{account.nickname}({gamename})",value=f'{account.server_name} {account.uid} LV.{account.level}',inline=False)
                embed.set_image(url=hoyolab_user.bg_url)
                await ctx.respond(embed=embed)
            else:
                await ctx.respond('用戶未找到')

    @hoyo.command(description='尋找原神用戶')
    @commands.cooldown(rate=1,per=1)
    async def genshin(self,ctx,
                   genshin_id:discord.Option(str,name='原神uid',description='要查詢的用戶',default=None)):
        await ctx.defer()
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        client = genshin.Client(cookies,lang='zh-tw')

        user = await client.get_genshin_user(genshin_id)
        #print(user.characters)
        #print(user.info)
        #print(user.stats)
        embed = BotEmbed.simple(title=f'{user.info.nickname}({user.info.server})')
        embed.add_field(name="等級",value=user.info.level)
        embed.add_field(name="成就",value=user.stats.achievements)
        embed.add_field(name="活躍天數",value=user.stats.days_active)
        embed.add_field(name="角色",value=user.stats.characters)
        embed.add_field(name="本期深淵",value=user.stats.spiral_abyss)
        embed.set_image(url=user.info.icon)
        await ctx.respond(embed=embed)

    @hoyo.command(description='尋找崩壞3rd用戶')
    @commands.cooldown(rate=1,per=1)
    async def honkai(self,ctx,
                   honkai_id:discord.Option(str,name='崩壞uid',description='要查詢的用戶',default=None)):
        await ctx.defer()
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        client = genshin.Client(cookies,lang='zh-tw')

        user = await client.get_honkai_user(int(honkai_id))
        #print(user.characters)
        #print(user.info)
        #print(user.stats)
        #print(user)
        embed = BotEmbed.simple(title=f'{user.info.nickname}({user.info.server})')
        embed.add_field(name="等級",value=user.info.level)
        embed.add_field(name="成就",value=user.stats.achievements)
        embed.set_image(url=user.info.icon)
        await ctx.respond(embed=embed)

    @hoyo.command(description='查詢深境螺旋')
    @commands.cooldown(rate=1,per=1)
    async def spiral_abyss(self,ctx,
                           genshin_id:discord.Option(str,name='原神uid',description='要查詢的用戶',default=None),
                           previous:discord.Option(bool,name='是否查詢上期紀錄',description='',default=False)):
        await ctx.defer()
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        client = genshin.Client(cookies,lang='zh-tw')
        
        try:
            r_user = await client.get_genshin_user(genshin_id)
            r_spiral_abyss = await client.get_genshin_spiral_abyss(genshin_id,previous=previous)
        except genshin.errors.DataNotPublic:
            await ctx.respond('用戶資訊未公開')
            return
        
        start_time = (r_spiral_abyss.start_time+timedelta(hours=8)).strftime("%Y/%m/%d")
        end_time = (r_spiral_abyss.end_time+timedelta(hours=8)).strftime("%Y/%m/%d")
        
        embed = BotEmbed.simple(description=f"第{r_spiral_abyss.season}期 {start_time} 至 {end_time}\n挑戰{r_spiral_abyss.total_battles}場中獲勝{r_spiral_abyss.total_wins}場，最深至{r_spiral_abyss.max_floor}層，共獲得{r_spiral_abyss.total_stars}顆星")
        if r_user:
            embed.title=f"{r_user.info.nickname} 的深境螺旋紀錄"
        else:
            embed.title=f"深境螺旋紀錄"
        
        ranks = r_spiral_abyss.ranks
        dict = {
            "角色：最多上場":ranks.most_played,
            "角色：最多擊殺": ranks.most_kills,
            "角色：最痛一擊": ranks.strongest_strike,
            "角色：最多承傷": ranks.most_damage_taken,
            "角色：最多技能使用": ranks.most_skills_used,
            "角色：最多大招使用": ranks.most_bursts_used
        }
        for i in dict:
            text = ''
            for j in dict[i]:
                text += f'{j.name} {j.value}\n'
            if text:
                embed.add_field(name=i,value=text)

        #r_spiral_abyss.floors
        #print(r_spiral_abyss)
        await ctx.respond(embed=embed)

    @hoyo.command(description='兌換禮包碼')
    @commands.cooldown(rate=1,per=1)
    async def code(self,ctx,
                   game:discord.Option(str,name='遊戲',description='要簽到的遊戲',choices=hoyo_game_option),
                   code:discord.Option(str,name='禮包碼',description='要兌換的禮包碼'),
                   uid:discord.Option(str,name='uid',description='要兌換的用戶')):
        if not jdata.get("debug_mode"):
            cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        else:
            cookies = genshin.utility.get_browser_cookies("chrome")

        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        client = genshin.Client(cookies,lang='zh-tw')
        await client.redeem_code(code,uid,game=game)  
        await ctx.respond('兌換已完成')

    @hoyo.command(description='簽到設定（多個遊戲請個別設定）（尚在測試可能有bug）')
    @commands.cooldown(rate=1,per=1)
    async def reward(self,ctx,
                   game:discord.Option(str,name='遊戲',description='要簽到的遊戲',choices=hoyo_game_option),
                   need_mention:discord.Option(bool,name='成功簽到時是否要tag提醒',default=True),
                   remove:discord.Option(bool,name='若要移除資料請設為true',default=False)):
        if remove:
            self.sqldb.remove_hoyo_reward(ctx.author.id)
            await ctx.respond('設定已移除')
            return
        
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies或已過期")
        self.sqldb.add_hoyo_reward(ctx.author.id,game,ctx.channel.id,need_mention)
        await ctx.respond('設定已完成')
        
    
    @hoyo.command(description='測試',guild_ids=debug_guild)
    @commands.cooldown(rate=1,per=1)
    async def test(self,ctx,
                   hoyolab_uid:discord.Option(str,name='hoyolab_uid',description='要查詢的用戶',default=None)):
        cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
        if not cookies:
            raise commands.errors.ArgumentParsingError("沒有設定cookies")
        client = genshin.Client(cookies,lang='zh-tw')
        r = await client.get_genshin_spiral_abyss(hoyolab_uid)
        print(r)
        await ctx.respond('done')

    @commands.message_command(name="尋找序號",guild_ids=debug_guild)
    async def exchange_code_genshin(self,ctx,message:discord.Message):
        textline = message.content.splitlines()
        p = re.compile(r'[0-9A-Z]{10,}')
        code_list = []
        for i in textline:
            code = p.match(i)
            if code and code not in code_list:
                code_list.append(code.group())
        
        if code_list:
            codetext = ""
            for i in code_list:
                codetext+=f"\n[{i}](https://genshin.hoyoverse.com/zh-tw/gift?code={i})"
            #await ctx.respond(f"找到以下兌換碼{codetext}\n若有設定cookie及uid則將自動兌換",ephemeral=True)
            await ctx.respond(f"找到以下兌換碼{codetext}",ephemeral=True)

    #         cookies = self.sqldb.get_userdata(str(ctx.author.id),'game_hoyo_cookies')
    #         dbdata = self.sqldb.get_game_data(str(ctx.author.id),DatabaseGame.GENSHIN.value)
    #         if not cookies:
    #             await ctx.send("沒有設定cookies或已過期")
    #             return
    #         if dbdata:
    #             client = genshin.Client(cookies,lang='zh-tw')
    #             uid = dbdata['player_id']
    #             for code in code_list:
    #                 await client.redeem_code(code,uid,game=genshin.Game.GENSHIN)
    #                 asyncio.sleep(3)
    #             await ctx.send('兌換已完成')
        else:
            await ctx.respond(f"沒有找到兌換碼",ephemeral=True)

def setup(bot):
    bot.add_cog(system_game(bot))