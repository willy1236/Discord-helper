from datetime import datetime,timedelta
from starcord.utility import BotEmbed
from starcord.database import JsonDatabase

Jsondb = JsonDatabase()
jdict = Jsondb.jdict
lol_jdict = Jsondb.lol_jdict

class LOLPlayer():
    def __init__(self,data):
        self.name = data['name']
        self.summonerid = data['id']
        self.accountid = data['accountId']
        self.puuid = data['puuid']
        self.summonerLevel = data['summonerLevel']
        self.profileIconId = data['profileIconId']

    def desplay(self):
        embed = BotEmbed.general(self.name)
        #embed.add_field(name="玩家名稱", value=self.name, inline=False)
        embed.add_field(name="召喚師等級", value=self.summonerLevel, inline=False)
        embed.add_field(name="帳號ID", value=self.accountid, inline=False)
        embed.add_field(name="召喚師ID", value=self.summonerid, inline=False)
        embed.add_field(name="puuid", value=self.puuid, inline=False)
        try:
            embed.set_thumbnail(url=f'https://ddragon.leagueoflegends.com/cdn/13.15.1/img/profileicon/{self.profileIconId}.png')
        except:
            embed.set_thumbnail(url='https://i.imgur.com/B0TMreW.png')
        embed.set_footer(text="puuid是全球唯一的ID，不隨帳號移動地區而改變")
        
        return embed

class LOLPlayerInMatch():
    def __init__(self,data):
        #self.participantId = data['participantId']
        #self.profileIcon = data['profileIcon']
        #self.puuid = data['puuid']
        #self.summonerId = data['summonerId']
        self.summonerLevel = data['summonerLevel']
        self.summonerName = data['summonerName']

        self.assists = data['assists']
        self.deaths = data['deaths']
        self.kills = data['kills']
        self.lane = data['lane']
        self.visionScore = data['visionScore']
        self.role = data['role']
        self.kda = round((self.kills+self.assists)/self.deaths,2) if self.deaths > 0 else (self.kills+self.assists)

        self.doubleKills = data['doubleKills']
        self.tripleKills = data['tripleKills']
        self.quadraKills = data['quadraKills']
        self.pentaKills = data['pentaKills']
        self.largestMultiKill = data['largestMultiKill']
        self.soloKills = data['challenges']['soloKills']
        
        self.dragonKills = data['dragonKills']
        self.baronKills = data['baronKills']

        self.championId = data['championId']
        self.championName = data['championName']
        self.champLevel = data['champLevel']
        
        self.totalDamageDealt = data['totalDamageDealt']
        self.totalDamageDealtToChampions = data['totalDamageDealtToChampions']
        self.totalDamageTaken = data['totalDamageTaken']
        self.totalHeal = data['totalHeal']
        self.totalTimeCCDealt = data['totalTimeCCDealt']

        self.enemyMissingPings = data['enemyMissingPings']

        self.firstBloodKill = data['firstBloodKill']
        #self.firstBloodAssist = data['firstBloodAssist']
        self.firstTowerKill = data['firstTowerKill']
        #self.firstTowerAssist = data['firstTowerAssist']

        self.gameEndedInEarlySurrender = data['gameEndedInEarlySurrender']
        self.gameEndedInSurrender = data['gameEndedInSurrender']
        #self.teamEarlySurrendered = data['teamEarlySurrendered']
        self.goldEarned = data['goldEarned']
        self.goldSpent = data['goldSpent']
        self.totalMinionsKilled = data['totalMinionsKilled']
        self.laneMinionsFirst10Minutes = data['challenges']['laneMinionsFirst10Minutes']
        self.jungleCsBefore10Minutes = round(data['challenges']['jungleCsBefore10Minutes'])
        self.AllMinionsBefore10Minutes =self.laneMinionsFirst10Minutes + self.jungleCsBefore10Minutes *10
        self.bountyGold = data['challenges']['bountyGold']

        self.damagePerMinute = data['challenges']['damagePerMinute']
        self.damageTakenOnTeamPercentage = round(data['challenges']['damageTakenOnTeamPercentage']*100,1)
        self.goldPerMinute = round(data['challenges']['goldPerMinute'])

        self.teamDamagePercentage = round(data['challenges']['teamDamagePercentage']*100,1)
        self.visionScorePerMinute = round(data['challenges']['visionScorePerMinute'],2)
        #self.items = [ data['item0'],data['item1'],data['item2'],data['item3'],data['item4'],data['item5'],data['item6'] ]

    def desplaytext(self):
        text = f'`{self.summonerName}(LV. {self.summonerLevel})`\n'
        name = lol_jdict['champion'].get(self.championName) or self.championName
        text += f'{name}(LV. {self.champLevel})\n'
        lane = lol_jdict['road'].get(self.lane) or self.lane
        if self.role != "NONE":
            lane +=f" {self.role}"
        text += f'{lane}\n'
        text += f'{self.kills}/{self.deaths}/{self.assists} KDA: {self.kda} solokill：{self.soloKills}\n'
        text += f'視野分：{self.visionScore} ({self.visionScorePerMinute}/min)\n'
        text += f'連殺：{self.doubleKills}/{self.tripleKills}/{self.quadraKills}/{self.pentaKills}\n'
        text += f'輸出：{self.totalDamageDealtToChampions} ({self.teamDamagePercentage}%)\n'
        text += f'承受：{self.totalDamageTaken} ({self.damageTakenOnTeamPercentage}%)\n'
        #text += f'治療/CC：{self.totalHeal}/{self.totalTimeCCDealt}\n'
        text += f'經濟：{self.goldEarned} ({self.goldPerMinute}/min)\n'
        text += f'吃兵/前10分鐘：{self.totalMinionsKilled}/{self.AllMinionsBefore10Minutes}\n'
        text += f'小龍/巴龍：{self.dragonKills}/{self.baronKills}\n'
        text += f'個人賞金：{self.bountyGold}\n'
        text += f'Ping問號燈：{self.enemyMissingPings}\n'

        if self.firstBloodKill and self.firstTowerKill:
            text += f'首殺+首塔🔪 '
        elif self.firstBloodKill:
            text += f'首殺🔪 '
        elif self.firstTowerKill:
            text += f'首塔🔪 '

        if self.gameEndedInEarlySurrender:
            text += f'提早投降🏳️'
        elif self.gameEndedInSurrender:
            text += f'投降🏳️'
        text += '\n'
        
        return text

class LOLTeamInMatch():
    def __init__(self,data):
        #100 = blue, 200 = red
        self.teamId = data['teamId']
        self.win = data['win']
        self.bans = data['bans']
        
        self.baronKill = data['objectives']['baron']['kills']
        self.dragonKill = data['objectives']['dragon']['kills']
        #riftHerald = 預示者
        self.riftHeraldKill = data['objectives']['riftHerald']['kills']
        
        self.championKill = data['objectives']['champion']['kills']
        #inhibitor = 水晶兵營
        self.inhibitorKill = data['objectives']['inhibitor']['kills']
        self.towerKill = data['objectives']['tower']['kills']


class LOLMatch():
    def __init__(self,data):
        self.matchId = data['metadata']['matchId']

        self.gameStartTimestamp = data['info']['gameStartTimestamp']
        self.gameDuration = data['info']['gameDuration']
        self.gameEndTimestamp = data['info']['gameEndTimestamp']

        self.gameId = data['info']['gameId']
        self.gameMode = data['info']['gameMode']
        self.gameVersion = data['info']['gameVersion']
        self.mapId = data['info']['mapId']
        self.platformId = data['info']['platformId']
        self.tournamentCode = data['info']['tournamentCode']

        self.participants = data['info']['participants']
        self.teams = data['info']['teams']

        self.players:list[LOLPlayerInMatch] = []
        for i in self.participants:
            self.players.append(LOLPlayerInMatch(i))

        self.team = []
        for i in self.teams:
            self.team.append(LOLTeamInMatch(i))
    
    def desplay(self):
        embed = BotEmbed.simple("LOL對戰")
        gamemode = lol_jdict['mod'].get(self.gameMode) or self.gameMode
        embed.add_field(name="遊戲模式", value=gamemode, inline=False)
        embed.add_field(name="對戰ID", value=self.matchId, inline=False)
        #embed.add_field(name="遊戲版本", value=self.gameVersion, inline=False)
        blue = ''
        red = ''
        i = 0
        for player in self.players:
            if i < 5:
                blue += player.desplaytext()
                if i != 4:
                    blue += '\n'
            else:
                red += player.desplaytext()
                if i != 9:
                    red += '\n'
            i+=1
        if self.team[0].win:
            embed.add_field(name="藍方👑", value=blue, inline=True)
            embed.add_field(name="紅方", value=red, inline=True)
        else:
            embed.add_field(name="藍方", value=blue, inline=True)
            embed.add_field(name="紅方👑", value=red, inline=True)
        return embed


class OsuPlayer():
    def __init__(self,data):
        self.name = data['username']
        self.id = data['id']
        self.global_rank = data['statistics']['global_rank']
        self.country_rank = data['statistics']['country_rank']
        self.pp = data['statistics']['pp']
        self.avatar_url = data['avatar_url']
        self.country = data['country']["code"]
        self.is_online = data['is_online']
        self.level = data['statistics']['level']['current']
        self.max_level = data['statistics']['level']['progress']
        self.max_combo = data['statistics']['maximum_combo']
        #self.last_visit = datetime.datetime.strptime(data['last_visit'],"%Y-%m-%dT%H:%M:%S%Z")
        self.oragin_last_visit = datetime.strptime(data['last_visit'],"%Y-%m-%dT%H:%M:%S%z")
        self.e8_last_visit = self.oragin_last_visit + timedelta(hours = 8)
        self.last_visit = self.e8_last_visit.strftime('%Y-%m-%d %H:%M:%S')
        self.url = f'https://osu.ppy.sh/users/{self.id}'

    def desplay(self):
        embed = BotEmbed.general("Osu玩家資訊",url=self.url)
        embed.add_field(name="名稱",value=self.name)
        embed.add_field(name="id",value=self.id)
        embed.add_field(name="全球排名",value=self.global_rank)
        embed.add_field(name="地區排名",value=self.country_rank)
        embed.add_field(name="pp",value=self.pp)
        embed.add_field(name="國家",value=self.country)
        embed.add_field(name="等級",value=f'{self.level}({self.max_level}%)')
        embed.add_field(name="最多連擊數",value=self.max_combo)
        if self.is_online:
            embed.add_field(name="最後線上",value='Online')
        else:
            embed.add_field(name="最後線上",value=self.last_visit)
        embed.set_thumbnail(url=self.avatar_url)
        return embed

class OsuBeatmap():
    def __init__(self,data):
        self.id = data['id']
        self.beatmapset_id = data['beatmapset_id']
        self.mode = data['mode']
        self.status = data['status']
        self.url = data['url']
        self.time = data['total_length']
        self.title = data['beatmapset']['title']
        self.cover = data['beatmapset']['covers']['cover']
        self.max_combo = data['max_combo']
        self.pass_rate = round(data['passcount'] / data['playcount'],3)
        self.checksum = data['checksum']
        self.bpm = data['bpm']
        self.star = data['difficulty_rating']
        self.ar = data['ar']
        self.cs = data['cs']
        self.od = data['accuracy']
        self.hp = data['drain']
        self.version = data['version']

    def desplay(self):
        embed = BotEmbed.simple(title="Osu圖譜資訊")
        embed.add_field(name="名稱",value=self.title)
        embed.add_field(name="歌曲長度(秒)",value=self.time)
        embed.add_field(name="星數",value=self.star)
        embed.add_field(name="模式",value=self.mode)
        embed.add_field(name="combo數",value=self.max_combo)
        embed.add_field(name="圖譜狀態",value=self.status)
        embed.add_field(name="圖譜id",value=self.id)
        embed.add_field(name="圖譜組id",value=self.beatmapset_id)
        embed.add_field(name="通過率",value=self.pass_rate)
        embed.add_field(name="BPM",value=self.bpm)
        embed.add_field(name='網址', value='[點我]({0})'.format(self.url))
        embed.set_image(url=self.cover)
        return embed

class OsuMultiplayer:
    def __init__(self,data):
        print(data)


class ApexPlayer():
    def __init__(self,data):
        #basic information
        self.name = data['global']['name']
        self.id = data['global']['uid']
        self.platform = data['global']['platform']
        self.level = data['global']['level']
        self.avatar = data['global']['avatar']
        #bans
        self.bans = data['global']['bans']
        #rank
        self.rank = data['global']['rank']['rankName']
        if data['global']['rank']['rankName'] != "Unranked":
            self.rank += " "+str(data['global']['rank']['rankDiv'])
        self.rank_score = data['global']['rank']['rankScore']
        self.arena_rank = data['global']['arena']['rankName']
        if data['global']['arena']['rankName'] != "Unranked":
            self.arena_rank += " "+str(data['global']['arena']['rankDiv'])
        self.arena_score = data['global']['arena']['rankScore']
        #state
        self.now_state =  data['realtime']['currentStateAsText']
        #selected
        self.legends_selected_name = data['legends']['selected']['LegendName']
        self.legends_selected_tacker = data['legends']['selected']['data']
        self.legends_selected_banner = data['legends']['selected']['ImgAssets']['banner'].replace(" ","%20")

    def desplay(self):
        embed = BotEmbed.simple("Apex玩家資訊")
        embed.add_field(name="名稱",value=self.name)
        embed.add_field(name="id",value=self.id)
        embed.add_field(name="平台",value=self.platform)
        embed.add_field(name="等級",value=self.level)
        embed.add_field(name="牌位階級",value=self.rank)
        embed.add_field(name="牌位分數",value=self.rank_score)
        embed.add_field(name="競技場牌位階級",value=self.arena_rank)
        embed.add_field(name="競技場牌位分數",value=self.arena_score)
        embed.add_field(name="目前狀態",value=self.now_state)
        if self.bans['isActive']:
            embed.add_field(name="目前ban狀態",value=self.bans['remainingSeconds'])
        else:
            embed.add_field(name="目前ban狀態",value=self.bans['isActive'])
        embed.add_field(name="目前選擇角色",value=self.legends_selected_name)
        embed.set_image(url=self.legends_selected_banner)
        return embed

class ApexCrafting():
    def __init__(self,data):
        self.daily = data[0]
        self.weekly = data[1]

        self.daily_start = self.daily['startDate']
        self.daily_end = self.daily['endDate']
        self.item1 = self.daily['bundleContent'][0]
        self.item1_cost = self.item1['cost']
        self.item1_name = self.item1['itemType']['name']
        self.item1_id = self.item1['item']
        self.item2 = self.daily['bundleContent'][1]
        self.item2_cost = self.item2['cost']
        self.item2_name = self.item2['itemType']['name']
        self.item2_id = self.item2['item']

        self.weekly_start = self.weekly['startDate']
        self.weekly_end = self.weekly['endDate']
        self.item3 = self.weekly['bundleContent'][0]
        self.item3_cost = self.item3['cost']
        self.item3_name = self.item3['itemType']['name']
        self.item3_id = self.item3['item']
        self.item4 = self.weekly['bundleContent'][1]
        self.item4_cost = self.item4['cost']
        self.item4_name = self.item4['itemType']['name']
        self.item4_id = self.item4['item']
    
    def desplay(self):
        embed = BotEmbed.simple("Apex合成器內容")
        tl = jdict['ApexCraftingItem']
        item_name = []
        item_name.append(tl.get(self.item1_name,self.item1_name))
        item_name.append(tl.get(self.item2_name,self.item2_name))
        item_name.append(tl.get(self.item3_name,self.item3_name))
        item_name.append(tl.get(self.item4_name,self.item4_name))

        embed.add_field(name="每日物品1",value=f"{item_name[0]} {self.item1_cost}",inline=False)
        embed.add_field(name="每日物品2",value=f"{item_name[1]} {self.item2_cost}",inline=False)
        embed.add_field(name="每週物品1",value=f"{item_name[2]} {self.item3_cost}",inline=False)
        embed.add_field(name="每週物品2",value=f"{item_name[3]} {self.item4_cost}",inline=False)
        embed.timestamp = datetime.now()
        embed.set_footer(text='更新時間')
        return embed

class ApexMapRotation():
    def __init__(self,data):
        self.nowmap = data["current"]['map']
        self.nowstart = datetime.strptime(data['current']['readableDate_start'],"%Y-%m-%d %H:%M:%S")+timedelta(hours=8)
        self.nowend = datetime.strptime(data['current']['readableDate_end'],"%Y-%m-%d %H:%M:%S")+timedelta(hours=8)
        self.remaining = data['current']['remainingTimer']
        self.mapimage = data['current']['asset']

        self.nextmap = data["next"]['map']
        self.nextstart = datetime.strptime(data['next']['readableDate_start'],"%Y-%m-%d %H:%M:%S")+timedelta(hours=8)
        self.nextend = datetime.strptime(data['next']['readableDate_end'],"%Y-%m-%d %H:%M:%S")+timedelta(hours=8)

    def desplay(self):
        tl = jdict['ApexMap']
        embed = BotEmbed.simple("Apex地圖輪替")
        embed.add_field(name="目前地圖",value=tl.get(self.nowmap,self.nowmap))
        embed.add_field(name="開始時間",value=self.nowstart)
        embed.add_field(name="結束時間",value=self.nowend)
        embed.add_field(name="下張地圖",value=tl.get(self.nextmap,self.nextmap))
        embed.add_field(name="開始時間",value=self.nextstart)
        embed.add_field(name="結束時間",value=self.nextend)
        embed.add_field(name="目前地圖剩餘時間",value=self.remaining)
        embed.set_image(url=self.mapimage)
        embed.timestamp = datetime.now()
        embed.set_footer(text='更新時間')
        return embed

class ApexStatus():
    def __init__(self,data):
        for i in data:
            print(i)
            for j in data[i]:
                print(j)

    def desplay(self):
        pass

class SteamUser():
    def __init__(self,data):
        self.id = data['steamid']
        self.name = data['personaname']
        self.profileurl = data['profileurl']
        self.avatar = data['avatarfull']
    
    def desplay(self):
        embed = BotEmbed.simple("Stean用戶資訊")
        embed.add_field(name="用戶名稱",value=self.name)
        embed.add_field(name="用戶id",value=self.id)
        embed.add_field(name="個人檔案連結",value='[點我]({0})'.format(self.profileurl))
        embed.set_thumbnail(url=self.avatar)
        return embed

class DBDPlayer(SteamUser):
    def __init__(self,data,name=None):
        #基本資料
        self.steamid = data["steamid"]
        self.name = name
        self.bloodpoints = data["bloodpoints"]
        self.survivor_rank = data["survivor_rank"]
        self.killer_rank = data["killer_rank"]
        self.killer_perfectgames = data["killer_perfectgames"]
        self.evilwithintierup = data["evilwithintierup"]
        
        #遊戲表現類
        self.cagesofatonement = data["cagesofatonement"]
        self.condemned = data["condemned"]
        self.sacrificed = data["sacrificed"]
        self.dreamstate = data["dreamstate"]
        self.rbtsplaced = data["rbtsplaced"]
        
        #命中、陷阱類
        self.blinkattacks = data["blinkattacks"]
        self.chainsawhits = data["chainsawhits"]
        self.shocked = data["shocked"]
        self.hatchetsthrown = data["hatchetsthrown"]
        self.lacerations = data["lacerations"]
        self.possessedchains = data["possessedchains"]
        self.lethalrushhits = data["lethalrushhits"]
        self.uncloakattacks = data["uncloakattacks"]
        self.beartrapcatches = data["beartrapcatches"]
        self.phantasmstriggered = data["phantasmstriggered"]

    def desplay(self):
        embed = BotEmbed.simple("DBD玩家資訊")
        embed.add_field(name="玩家名稱",value=self.name)
        embed.add_field(name="血點數",value=self.bloodpoints)
        embed.add_field(name="倖存者等級",value=self.survivor_rank)
        embed.add_field(name="殺手等級",value=self.killer_rank)
        embed.add_field(name="升階次數",value=self.evilwithintierup)
        embed.add_field(name="完美殺手場次",value=self.killer_perfectgames)

        embed.add_field(name="勞改次數",value=self.cagesofatonement)
        embed.add_field(name="詛咒次數",value=self.condemned)
        embed.add_field(name="獻祭次數",value=self.sacrificed)
        embed.add_field(name="送入夢境數",value=self.dreamstate)
        embed.add_field(name="頭套安裝數",value=self.rbtsplaced)
        
        embed.add_field(name="鬼影步命中",value=self.blinkattacks)
        embed.add_field(name="電鋸衝刺命中",value=self.chainsawhits)
        embed.add_field(name="電擊命中",value=self.shocked)
        embed.add_field(name="斧頭命中",value=self.hatchetsthrown)
        embed.add_field(name="飛刀命中",value=self.lacerations)
        embed.add_field(name="鎖鏈命中",value=self.possessedchains)
        embed.add_field(name="致命衝刺命中",value=self.lethalrushhits)
        embed.add_field(name="喪鐘襲擊",value=self.uncloakattacks)
        embed.add_field(name="陷阱捕捉",value=self.beartrapcatches)
        embed.add_field(name="汙泥陷阱觸發",value=self.phantasmstriggered)
        return embed