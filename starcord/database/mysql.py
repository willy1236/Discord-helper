import mysql.connector,datetime
from mysql.connector.errors import Error as sqlerror
from starcord.types import DBGame,Coins

class MySQLBaseModel(object):
    """MySQL資料庫基本模型"""
    def __init__(self,settings:dict):
        '''MySQL 資料庫連接\n
        settings = {"host": "","port": ,"user": "","password": "","db": "","charset": ""}
        '''
        #建立連線
        self.connection = mysql.connector.connect(**settings)
        self.cursor = self.connection.cursor(dictionary=True)
        self.connection.get_server_info()

    def truncate_table(self,table:str,database="database"):
        self.cursor.execute(f"USE `{database}`;")
        self.cursor.execute(f"TRUNCATE TABLE `{table}`;")
    
    def set_userdata(self,discord_id:int,table:str,column:str,value):
        """設定或更新用戶資料（只要PK為discord_id的皆可）"""
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `{table}` SET discord_id = {discord_id}, {column} = {value} ON DUPLICATE KEY UPDATE discord_id = {discord_id}, {column} = {value};")
        self.connection.commit()

    def get_userdata(self,discord_id:int,table:str='user_discord'):
        """取得用戶資料（只要PK為discord_id的皆可）"""
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT * FROM `{table}` WHERE discord_id = %s;',(discord_id,))
        records = self.cursor.fetchall()
        if records:
            return records[0]

    def remove_userdata(self,discord_id:int,table:str='user_discord'):
        """移除用戶資料（只要PK為discord_id的皆可）"""
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"DELETE FROM `{table}` WHERE `discord_id` = %s;",(discord_id,))
        self.connection.commit()

    def add_userdata_value(self,discord_id:int,table:str,column:str,value):
        """增加用戶數值資料的值（只要PK為discord_id的皆可）"""
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `{table}` SET discord_id = {discord_id}, {column} = {value} ON DUPLICATE KEY UPDATE `discord_id` = {discord_id}, `{column}` = CASE WHEN `{column}` IS NOT NULL THEN `{column}` + {value} ELSE {value} END;")
        self.connection.commit()
    
    # def add_data(self,table:str,*value,db="database"):
    #     self.cursor.execute(f"USE `{db}`;")
    #     self.cursor.execute(f"INSERT INTO `{table}` VALUES(%s)",value)
    #     self.connection.commit()

    # def replace_data(self,table:str,*value,db="database"):
    #     self.cursor.execute(f"USE `{db}`;")
    #     self.cursor.execute(f"REPLACE INTO `{table}` VALUES(%s)",value)
    #     self.connection.commit()

    # def get_data(self,table:str):
    #     db = "database"
    #     self.cursor.execute(f"USE `{db}`;")
    #     self.cursor.execute(f'SELECT * FROM `{table}` WHERE id = %s;',("1",))
        
    #     records = self.cursor.fetchall()
    #     for r in records:
    #          print(r)
    
    # def remove_data(self,table:str,*value):
    #     db = "database"
    #     self.cursor.execute(f"USE `{db}`;")
    #     #self.cursor.execute(f'DELETE FROM `{table}` WHERE `id` = %s;',("3",))
    #     self.cursor.execute(f'DELETE FROM `{table}` WHERE `id` = %s;',value)
    #     self.connection.commit()

class MySQLUserSystem(MySQLBaseModel):
    """用戶資料系統"""
    def create_user(self,discord_id:int):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `user_discord` SET discord_id = {discord_id};")
        self.connection.commit()

    def get_user(self,discord_id:int):
        """取得基本用戶"""

    def get_dcuser(self,discord_id:int):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT * FROM `user_discord` LEFT JOIN `user_point` ON `user_discord`.`discord_id` = `user_point`.`discord_id` WHERE `user_discord`.`discord_id` = %s;',(discord_id,))
        record = self.cursor.fetchall()
        if record:
            return record[0]
        
    def set_staruser_data(self,discord_id:int,emailAddress=None,drive_share_id=None):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `user_data` SET `discord_id` = %s, `email` = %s, `drive_share_id` = %s ON DUPLICATE KEY UPDATE `email` = %s, `drive_share_id` = %s;",(discord_id,emailAddress,drive_share_id,emailAddress,drive_share_id))
        self.connection.commit()

class MySQLNotifySystem(MySQLBaseModel):
    def set_notify_channel(self,guild_id:int,notify_type:str,channel_id:int,role_id:int=None):
        """設定自動通知頻道"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"INSERT INTO `notify_channel` VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `guild_id` = %s, `notify_type` = %s, `channel_id` = %s, `role_id` = %s",(guild_id,notify_type,channel_id,role_id,guild_id,notify_type,channel_id,role_id))
        self.connection.commit()

    def remove_notify_channel(self,guild_id:int,notify_type:str):
        """移除自動通知頻道"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'DELETE FROM `notify_channel` WHERE `guild_id` = %s AND `notify_type` = %s;',(guild_id,notify_type))
        self.connection.commit()

    def get_notify_channel_by_type(self,notify_type:str):
        """取得自動通知頻道（依據通知種類）"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT * FROM `notify_channel` WHERE notify_type = %s;',(notify_type,))
        return self.cursor.fetchall()

    def get_notify_channel(self,guild_id:str,notify_type:str):
        """取得自動通知頻道"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT * FROM `notify_channel` WHERE guild_id = %s AND notify_type = %s;',(guild_id,notify_type))
        records = self.cursor.fetchall()
        if records:
            return records[0]
    
    def get_all_notify_channel(self,guild_id:str):
        """取得伺服器的所有自動通知頻道"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT * FROM `notify_channel` WHERE guild_id = %s;',(guild_id,))
        return self.cursor.fetchall()
    
    def set_dynamic_voice(self,channel_id,discord_id,guild_id,created_at=None):
        """設定動態語音"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"INSERT INTO `dynamic_channel` VALUES(%s,%s,%s,%s)",(channel_id,discord_id,guild_id,created_at))
        self.connection.commit()

    def remove_dynamic_voice(self,channel_id):
        """移除動態語音"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"DELETE FROM `dynamic_channel` WHERE `channel_id` = %s",(channel_id,))
        self.connection.commit()

    def get_all_dynamic_voice(self):
        """取得目前所有的動態語音"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT `channel_id` FROM `dynamic_channel`;')
        records = self.cursor.fetchall()
        list = []
        for data in records:
            list.append(data['channel_id'])
        return list

    def set_notify_community(self,notify_type:str,notify_name:str,guild_id:int,channel_id:int,role_id:int=None):
        """設定社群通知"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"INSERT INTO `notify_community` VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `notify_type` = %s, `notify_name` = %s, `guild_id` = %s, `channel_id` = %s, `role_id` = %s",(notify_type,notify_name,guild_id,channel_id,role_id,notify_type,notify_name,guild_id,channel_id,role_id))
        self.connection.commit()

    def remove_notify_community(self,notify_type:str,notify_name:str,guild_id:int):
        """移除社群通知"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'DELETE FROM `notify_community` WHERE `notify_type` = %s AND `notify_name` = %s AND `guild_id` = %s;',(notify_type,notify_name,guild_id))
        self.connection.commit()

    def get_notify_community(self,notify_type:str):
        """取得社群通知（依據社群）"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT * FROM `notify_community` WHERE `notify_type` = %s;',(notify_type,))
        return self.cursor.fetchall()
    
    def get_notify_community_guild(self,notify_type:str,notify_name:str):
        """取得指定的所有社群通知"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT `guild_id`,`channel_id`,`role_id` FROM `notify_community` WHERE `notify_type` = %s AND `notify_name` = %s;',(notify_type,notify_name))
        records = self.cursor.fetchall()
        dict = {}
        for i in records:
            dict[i['guild_id']] = [i['channel_id'],i['role_id']]
        return dict

    def get_notify_community_user(self,notify_type:str,notify_name:str,guild_id:int):
        """取得伺服器內的指定社群通知"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT `channel_id`,`role_id` FROM `notify_community` WHERE `notify_type` = %s AND `notify_name` = %s AND `guild_id` = %s;',(notify_type,notify_name,guild_id))
        return self.cursor.fetchall()

    def get_notify_community_userlist(self,notify_type:str):
        """取得指定類型的社群通知清單"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT DISTINCT `notify_name` FROM `notify_community` WHERE `notify_type` = %s;',(notify_type,))
        records = self.cursor.fetchall()
        list = []
        for i in records:
            list.append(i.get('notify_name'))
        return list

    def get_notify_community_list(self,notify_type:str,guild_id:int):
        """取得伺服器內指定種類的所有通知"""
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT * FROM `notify_community` WHERE `notify_type` = %s AND `guild_id` = %s;',(notify_type,guild_id))
        return self.cursor.fetchall()

class MySQLGameSystem(MySQLBaseModel):
    """遊戲資料系統"""
    def set_game_data(self,discord_id:int,game:DBGame,player_name:str=None,player_id:str=None,account_id:str=None,other_id:str=None):
        """設定遊戲資料"""
        game = DBGame(game)
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"REPLACE INTO `game_data` VALUES(%s,%s,%s,%s,%s,%s);",(discord_id,game.value,player_name,player_id,account_id,other_id))
        self.connection.commit()

    def remove_game_data(self,discord_id:int,game:DBGame):
        """移除遊戲資料"""
        game = DBGame(game)
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"DELETE FROM `game_data` WHERE `discord_id` = %s AND `game` = %s;",(discord_id,game.value))
        self.connection.commit()

    def get_game_data(self,discord_id:int,game:DBGame=None):
        """獲取遊戲資料"""
        self.cursor.execute(f"USE `stardb_user`;")
        if game:
            game = DBGame(game)
            self.cursor.execute(f"SELECT * FROM `game_data` WHERE `discord_id` = %s AND `game` = %s;",(discord_id,game.value))
            records = self.cursor.fetchone()
        else:
            self.cursor.execute(f"SELECT * FROM `game_data` WHERE `discord_id` = %s;",(discord_id,))
            records = self.cursor.fetchall()
        return records

class MySQLRoleSaveSystem(MySQLBaseModel):
    def get_role_save(self,discord_id:int):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT * FROM `role_save` WHERE discord_id = %s ORDER BY `time` DESC;',(discord_id,))
        records = self.cursor.fetchall()
        return records

    def get_role_save_count(self,discord_id:int) -> int | None:
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT COUNT(*) FROM `role_save` WHERE discord_id = %s;',(discord_id,))
        records = self.cursor.fetchall()
        if records:
            return records[0]['COUNT(*)']

    def add_role_save(self,discord_id:int,role_id:str,role_name:str,time:datetime.date):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `role_save` VALUES(%s,%s,%s,%s)",(discord_id,role_id,role_name,time))
        self.connection.commit()

class MySQLCurrencySystem(MySQLBaseModel):
    def get_scoin(self,discord_id:int) -> int:
        """取得用戶星幣數"""
        records = self.get_userdata(discord_id,"user_point")
        if records:
            return records.get("scoin",0)

    def getif_scoin(self,discord_id:int,point:int) -> int | None:
        """取得星幣足夠的用戶
        :return: 若足夠則回傳傳入的discord_id
        """
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT `discord_id` FROM `user_point` WHERE discord_id = %s AND point >= %s;',(discord_id,point))
        records = self.cursor.fetchall()
        if records:
            return records[0].get("discord_id")

    def transfer_scoin(self,giver_id:int,given_id:int,amount:int):
        """轉移星幣
        :param giver_id: 給予點數者
        :param given_id: 被給予點數者
        :param amount: 轉移的點數數量
        """
        records = self.getif_scoin(giver_id,amount)
        if records:
            self.cursor.execute(f"UPDATE `user_point` SET point = point - %s WHERE discord_id = %s;",(amount,giver_id))
            self.cursor.execute(f"INSERT INTO `user_point` SET discord_id = %s, point = %s ON DUPLICATE KEY UPDATE discord_id = %s, point = point + %s",(given_id,amount,given_id,amount))
            self.connection.commit()
            #self.cursor.execute(f"UPDATE `user_point` SET `point` = REPLACE(`欄位名`, '要被取代的欄位值', '取代後的欄位值') WHERE `欄位名` LIKE '%欄位值%';",(giver_id,amount))
        else:
            return "點數不足"

    def update_coins(self,discord_id:str,mod,coin_type:Coins,amount:int):
        """更改用戶的點數數量"""
        coin_type = Coins(coin_type)
        self.cursor.execute(f"USE `stardb_user`;")
        if mod == 'set':
            self.cursor.execute(f"REPLACE INTO `user_point`(discord_id,{coin_type.value}) VALUES(%s,%s);",(discord_id,amount))
        elif mod == 'add':
            self.cursor.execute(f"UPDATE `user_point` SET {coin_type.value} = {coin_type.value} + %s WHERE discord_id = %s;",(amount,discord_id))
        else:
            raise ValueError("mod must be 'set' or 'add'")
        self.connection.commit()

    def user_sign(self,discord_id:int):
        '''新增簽到資料'''
        time = datetime.date.today()
        yesterday = time - datetime.timedelta(days=1)
        self.cursor.execute(f"USE `stardb_user`;")

        #檢測是否簽到過
        self.cursor.execute(f"SELECT `discord_id` FROM `user_sign` WHERE `discord_id` = {discord_id} AND `date` = '{time}';")
        record = self.cursor.fetchall()
        if record:
            return '已經簽到過了喔'

        #更新最後簽到日期+計算連續簽到
        self.cursor.execute(f"INSERT INTO `user_sign` VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE `consecutive_days` = CASE WHEN `date` = %s THEN `consecutive_days` + 1 ELSE 1 END, `date` = %s;",(discord_id,time,1,yesterday.isoformat(),time))
        #更新最大連續簽到日
        self.cursor.execute(f"UPDATE `user_discord` AS `data` JOIN `user_sign` AS `sign` ON `data`.`discord_id` = `sign`.`discord_id` SET `data`.`max_sign_consecutive_days` = `sign`.`consecutive_days` WHERE `sign`.`discord_id` = {discord_id} AND (`data`.`max_sign_consecutive_days` < `sign`.`consecutive_days` OR `data`.`max_sign_consecutive_days` IS NULL);")
        self.connection.commit()

    def sign_add_coin(self,discord_id:int,scoin:int=0,Rcoin:int=0):
        """簽到獎勵點數"""
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `user_point` SET discord_id = %s, scoin = %s,rcoin = %s ON DUPLICATE KEY UPDATE scoin = scoin + %s, rcoin = rcoin + %s",(discord_id,scoin,Rcoin,scoin,Rcoin))
        self.connection.commit()

class MySQLHoYoLabSystem(MySQLBaseModel):
    def set_hoyo_cookies(self,discord_id:int,ltuid:str,ltoken:str,cookie_token:str):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"INSERT INTO `game_hoyo_cookies` VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `discord_id` = %s, `ltuid` = %s, `ltoken` = %s, `cookie_token` = %s",(discord_id,ltuid,ltoken,cookie_token,discord_id,ltuid,ltoken,cookie_token))
        self.connection.commit()

    def remove_hoyo_cookies(self,discord_id:int):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"DELETE FROM `game_hoyo_cookies` WHERE discord_id = {discord_id}")
        self.connection.commit()

    def get_hoyo_reward(self):
        self.cursor.execute(f"USE `database`;")
        #self.cursor.execute(f'SELECT * FROM `game_hoyo_reward` LEFT JOIN `game_hoyo_cookies` ON game_hoyo_reward.discord_id = game_hoyo_cookies.discord_id WHERE game_hoyo_reward.discord_id IS NOT NULL;')
        self.cursor.execute(f'SELECT * FROM `game_hoyo_reward`;')
        records = self.cursor.fetchall()
        return records
    
    def add_hoyo_reward(self,discord_id:int,game:str,channel_id:str,need_mention:bool):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"INSERT INTO `game_hoyo_reward` VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `channel_id` = {channel_id}, `need_mention` = {need_mention}",(discord_id,game,channel_id,need_mention))
        self.connection.commit()

    def remove_hoyo_reward(self,discord_id:int):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"DELETE FROM `game_hoyo_reward` WHERE discord_id = {discord_id}")
        self.connection.commit()

class MySQLBetSystem(MySQLBaseModel):
    def get_bet_data(self,bet_id:int):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'SELECT `bet_id`,`IsOn` FROM `bet_data` WHERE `bet_id` = %s;',(bet_id,))
        records = self.cursor.fetchone()
        return records

    def place_bet(self,bet_id:int,choice:str,money:int):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'INSERT INTO `user_bet` VALUES(%s,%s,%s);',(bet_id,choice,money))
        self.connection.commit()

    def create_bet(self,bet_id:int,title:str,pink:str,blue:str):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f'INSERT INTO `bet_data` VALUES(%s,%s,%s,%s,%s);',(bet_id,title,pink,blue,True))
        self.connection.commit()

    def update_bet(self,bet_id:int):
        self.cursor.execute(f"USE `database`;")
        self.cursor.execute(f"UPDATE `bet_data` SET IsOn = %s WHERE bet_id = %s;",(False,bet_id))
        self.connection.commit()

    def get_bet_total(self,bet_id:int):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT SUM(money) FROM `user_bet` WHERE `bet_id` = %s AND `choice` = %s;',(bet_id,'pink'))
        total_pink = self.cursor.fetchone()
        self.cursor.execute(f'SELECT SUM(money) FROM `user_bet` WHERE `bet_id` = %s AND `choice` = %s;',(bet_id,'blue'))
        total_blue = self.cursor.fetchone()
        return [int(total_pink['SUM(money)'] or 0),int(total_blue['SUM(money)'] or 0)]

    def get_bet_winner(self,bet_id:int,winner:str):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT * FROM `user_bet` WHERE `bet_id` = %s AND `choice` = %s;',(bet_id,winner))
        records = self.cursor.fetchall()
        return records

    def remove_bet(self,bet_id:int):
        self.cursor.execute(f'DELETE FROM `stardb_user`.`user_bet` WHERE `bet_id` = %s;',(bet_id,))
        self.cursor.execute(f'DELETE FROM `database`.`bet_data` WHERE `bet_id` = %s;',(bet_id,))
        self.connection.commit()

class MySQLPetSystem(MySQLBaseModel):
    def get_user_pet(self,discord_id:int):
        records = self.get_userdata(discord_id,"user_pet")
        return records

    def create_user_pet(self,discord_id:int,pet_species:str,pet_name:str):
        try:
            self.cursor.execute(f"USE `stardb_user`;")
            self.cursor.execute(f'INSERT INTO `user_pet` VALUES(%s,%s,%s,%s);',(discord_id,pet_species,pet_name,20))
            self.connection.commit()
        except sqlerror as e:
            if e.errno == 1062:
                return '你已經擁有寵物了'
            else:
                raise

    def delete_user_pet(self,discord_id:int):
        self.remove_userdata(discord_id,"user_pet")

class MySQLRPGSystem(MySQLBaseModel):
    def get_rpguser(self,discord_id:int):   
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f'SELECT * FROM `rpg_user`,`user_point` WHERE rpg_user.discord_id = %s;',(discord_id,))
        records = self.cursor.fetchone()
        return records

    def set_rpguser(self,discord_id:int):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `rpg_user` VALUES(%s);",(discord_id,))
        self.connection.commit()
    
    def get_activities(self,discord_id:int):
        records = self.get_userdata(discord_id,"rpg_activities")
        return records or {}

    def get_bag(self,discord_id:int,item_id:str=None):
        self.cursor.execute(f"USE `stardb_user`;")
        if item_id:
            self.cursor.execute(f"SELECT * FROM `rpg_user_bag` WHERE discord_id = {discord_id} AND item_id = {item_id};")
            records = self.cursor.fetchone()
        else:
            self.cursor.execute(f"SELECT item_id,amount FROM `rpg_user_bag` WHERE discord_id = {discord_id};")
            records = self.cursor.fetchall()
        return records
    
    def get_bag_desplay(self,discord_id:int):
        # data = self.get_bag(str(discord_id))
        # self.cursor.execute(f"USE `checklist`;")
        # bag_list = []
        # for item in data:
        #     self.cursor.execute(f"SELECT name FROM `rpg_item` WHERE item_id = {item['item_id']};")
        #     records = self.cursor.fetchone()
        #     bag_list.append((records['name'],item['amount']))

        # return bag_list
        self.cursor.execute(f"SELECT rpg_item.item_id,name,amount FROM `stardb_user`.`rpg_user_bag` JOIN `checklist`.`rpg_item` ON rpg_user_bag.item_id = rpg_item.item_id WHERE discord_id = {discord_id};")
        #self.cursor.execute(f"SELECT rpg_item.item_id,name,amount FROM `database`.`rpg_user_bag`,`checklist`.`rpg_item` WHERE discord_id = {discord_id};")
        records = self.cursor.fetchall()
        return records

    def update_bag(self,discord_id:int,item_id:int,amount:int):
        self.cursor.execute(f"INSERT INTO `stardb_user`.`rpg_user_bag` SET discord_id = {discord_id}, item_id = {item_id}, amount = {amount} ON DUPLICATE KEY UPDATE amount = amount + {amount};")
        self.connection.commit()

    def remove_bag(self,discord_id:int,item_id:int,amount:int):
        r = self.get_bag(discord_id,item_id)
        if r['amount'] < amount:
            raise ValueError('此物品數量不足')
        
        self.cursor.execute(f"USE `stardb_user`;")
        if r['amount'] == amount:
            self.cursor.execute(f"DELETE FROM `rpg_user_bag` WHERE `discord_id` = %s AND `item_id` = %s;",(discord_id,item_id))
        else:
            self.cursor.execute(f'UPDATE `rpg_user_bag` SET `discord_id` = {discord_id}, `item_id` = {item_id}, amount = amount - {amount}')
        self.connection.commit()

class MySQLBusyTimeSystem(MySQLBaseModel):
    def add_busy(self, discord_id, date, time):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"INSERT INTO `busy_time` VALUES(%s,%s,%s);",(discord_id,date,time))
        self.connection.commit()

    def remove_busy(self, discord_id, date, time):
        self.cursor.execute(f"USE `stardb_user`;")
        self.cursor.execute(f"DELETE FROM `busy_time` WHERE `discord_id` = %s AND `date` = %s AND `time` = %s;",(discord_id,date,time))
        self.connection.commit()

    def get_busy(self,date):
        self.cursor.execute(f"SELECT * FROM `stardb_user`.`busy_time` WHERE date = {date};")
        records = self.cursor.fetchall()
        return records
    
    def get_statistics_busy(self,discord_id:int):
        self.cursor.execute(f"SELECT count(*) FROM `stardb_user`.`busy_time` WHERE `discord_id` = {discord_id};")
        records = self.cursor.fetchone()
        return records

class MySQLWarningSystem(MySQLBaseModel):
    def add_warning(self,discord_id:int,moderate_type:str,moderate_user:str,create_guild:str,create_time:datetime.datetime,reason:str=None,last_time:str=None):
        self.cursor.execute(f"INSERT INTO `stardb_user`.`user_moderate` VALUES(%s,%s,%s,%s,%s,%s,%s,%s);",(None,discord_id,moderate_type,moderate_user,create_guild,create_time,reason,last_time))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_warning(self,warning_id:int):
        self.cursor.execute(f"SELECT * FROM `stardb_user`.`user_moderate` WHERE `warning_id` = {warning_id};")
        records = self.cursor.fetchone()
        return records
    
    def get_warnings(self,discord_id:int):
        self.cursor.execute(f"SELECT * FROM `stardb_user`.`user_moderate` WHERE `discord_id` = {discord_id};")
        records = self.cursor.fetchall()
        return records
    
    def remove_warning(self,warning_id:int):
        self.cursor.execute(f"DELETE FROM `stardb_user`.`user_moderate` WHERE warning_id = {warning_id};")
        self.connection.commit()
class MySQLPollSystem(MySQLBaseModel):
    def add_poll(self,title:str,created_user:int,created_at:datetime,message_id,guild_id):
        self.cursor.execute(f"INSERT INTO `database`.`poll_data` VALUES(%s,%s,%s,%s,%s,%s,%s);",(None,title,created_user,created_at,True,message_id,guild_id))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def remove_poll(self,poll_id:int):
        self.cursor.execute(f"DELETE FROM `database`.`poll_data` WHERE `poll_id` = {poll_id};")
        self.cursor.execute(f"DELETE FROM `stardb_user`.`user_poll` WHERE `poll_id` = {poll_id};")
        self.cursor.execute(f"DELETE FROM `database`.`poll_options` WHERE `poll_id` = {poll_id};")
        self.connection.commit()

    def get_poll(self,poll_id:int):
        self.cursor.execute(f"SELECT * FROM `database`.`poll_data` WHERE `poll_id` = {poll_id};")
        records = self.cursor.fetchall()
        return records[0]
    
    def update_poll(self,poll_id:int,column:str,value):
        self.cursor.execute(f"UPDATE `database`.`poll_data` SET {column} = %s WHERE `poll_id` = %s;",(value,poll_id))
        self.connection.commit()

    def get_all_active_polls(self):
        self.cursor.execute(f"SELECT * FROM `database`.`poll_data` WHERE `is_on` = 1;")
        records = self.cursor.fetchall()
        return records

    def get_poll_options(self,poll_id:int):
        self.cursor.execute(f"SELECT * FROM `database`.`poll_options` WHERE `poll_id` = {poll_id};")
        records = self.cursor.fetchall()
        return records

    def get_poll_option(self,poll_id:int,option_id:int):
        self.cursor.execute(f"SELECT * FROM `database`.`poll_options` WHERE `poll_id` = {poll_id} AND `option_id` = {option_id};")
        records = self.cursor.fetchall()
        if records:
            return records[0]

    def add_poll_option(self,poll_id:int,options:list):
        list = []
        count = 0
        for option in options:
            count += 1
            list.append([poll_id, count, option])
        self.cursor.executemany(f"INSERT INTO `database`.`poll_options` VALUES(%s,%s,%s);",list)
        self.connection.commit()

    def add_user_poll(self,poll_id:int,discord_id:int,vote_option:int,vote_at:datetime):
        self.cursor.execute(f"INSERT INTO `stardb_user`.`user_poll` VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `vote_option` = %s, `vote_at` = %s;",(poll_id,discord_id,vote_option,vote_at,vote_option,vote_at))
        self.connection.commit()
    
    def remove_user_poll(self,poll_id:int,discord_id:int):
        self.cursor.execute(f"DELETE FROM `stardb_user`.`user_poll` WHERE `poll_id` = {poll_id} AND `discord_id` = {discord_id};")
        self.connection.commit()
    
    def get_user_poll(self,poll_id:int,discord_id:int):
        self.cursor.execute(f"SELECT * FROM `stardb_user`.`user_poll` WHERE poll_id = {poll_id} AND `discord_id` = {discord_id};")
        records = self.cursor.fetchall()
        if records:
            return records[0]
    
    def get_users_poll(self,poll_id:int):
        self.cursor.execute(f"SELECT * FROM `stardb_user`.`user_poll` WHERE poll_id = {poll_id};")
        records = self.cursor.fetchall()
        return records
    
    def get_poll_vote_count(self,poll_id:int):
        self.cursor.execute(f"SELECT vote_option,COUNT(*) as count FROM  `stardb_user`.`user_poll` WHERE `poll_id` = {poll_id} GROUP BY vote_option;")
        records = self.cursor.fetchall()
        dict = {}
        if records:
            for i in records:
                dict[str(i["vote_option"])] = i["count"]
        return dict

class MySQLDatabase(
    MySQLUserSystem,
    MySQLGameSystem,
    MySQLRoleSaveSystem,
    MySQLCurrencySystem,
    MySQLHoYoLabSystem,
    MySQLBetSystem,
    MySQLPetSystem,
    MySQLRPGSystem,
    MySQLBusyTimeSystem,
    MySQLWarningSystem,
    MySQLPollSystem,
):
    """Mysql操作"""