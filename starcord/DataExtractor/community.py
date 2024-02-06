import requests,os.path,feedparser
from starcord.FileDatabase import Jsondb
from starcord.models.community import *
from starcord.errors import Forbidden

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CommunityInterface():
    """社群資料交互"""

class TwitchAPI(CommunityInterface):
    '''
    與Twitch api交互相關
    '''
    def __init__(self):
        self.__headers = self.__get_headers()
        self.url = "https://api.twitch.tv/helix"

    def __get_headers(self):
        #客戶端憑據僅能使用API
        TOKENURL = "https://id.twitch.tv/oauth2/token"
        #headers = {"Content-Type": "application/x-www-form-urlencoded"}
        tokens = Jsondb.get_token('twitch')
        params = {
            'client_id':tokens[0],
            'client_secret':tokens[1],
            'grant_type':'client_credentials'
            }

        r = requests.post(TOKENURL, params=params)
        apidata = r.json()
        if r.status_code == 200:
            headers = {
                'Authorization': f"Bearer {apidata['access_token']}",
                'Client-Id':tokens[0]
            }
            return headers
        else:
            raise Forbidden(f"在讀取Twitch API時發生錯誤",f"[{r.status_code}] {apidata['message']}")

    def get_lives(self,users:str|list):
        """
        取得twitch用戶的直播資訊
        :param users: list of users
        :return: dict: {username: TwitchStream | None（如果無正在直播）}
        """
        params = {
            "user_login": users,
            "first": 1
        }
        r = requests.get(f"{self.url}/streams", params=params,headers=self.__headers)
        apidata = r.json()
        dict = {}
        for user in users:
            dict[user] = None

        for data in apidata['data']:
            dict[data.get('user_login')] = TwitchStream(data)
        
        return dict

    def get_user(self,username:str):
        """
        取得Twitch用戶
        :param username: 用戶名稱（user_login）
        """
        params = {
            "login": username,
            "first": 1
        }
        r = requests.get(f"{self.url}/users", params=params,headers=self.__headers)
        apidata = r.json()
        if apidata.get('data'):
            return TwitchUser(apidata['data'][0])
        else:
            return None

    def get_videos(self,users:str) -> list[TwitchVideo]:
        """
        取得twitch用戶的影片資訊
        :param users: list of users
        :return: list[TwitchVideo]
        """
        params = {
            "user_id": users,
            "sort": "time",
            "first": 5
        }
        r = requests.get(f"{self.url}/videos", params=params,headers=self.__headers)
        apidata = r.json()
        print(apidata)
        if apidata.get('data'):
            return [TwitchVideo(i) for i in apidata['data']]
        else:
            return None

class TwitterInterface:
    pass

class YoutubeAPI(CommunityInterface):
    def __init__(self):
        self.__token = Jsondb.get_token('youtube')
        self.__headers = {
            'Authorization': f'Bearer {self.__token}',
            'Accept': 'application/json'
        }

    def get_channel_id(self,channel_name:str):
        params = {
            'key': self.__token,
            'forUsername': channel_name,
            'part': 'id',
            'maxResults':1
        }
        r = requests.get('https://youtube.googleapis.com/youtube/v3/channels',params=params)
        if r.ok:
            data = r.json()
            print(data)
            if data['pageInfo']['totalResults']:
                print(data["pageInfo"])
            else:
                return None
                
        else:
            print(r.text)
            print(r.status_code)

    def get_channel_content(self,channel_id:str):
        '''獲取Youtube頻道資訊'''
        params = {
            'key': self.__token,
            'id':channel_id,
            #'forUsername': channel_name,
            'part': 'statistics,snippet',
            'maxResults':1
        }
        r = requests.get('https://youtube.googleapis.com/youtube/v3/channels',params=params)
        if r.ok and r.json().get('items'):
            return YoutubeChannel(r.json().get('items')[0])
        else:
            return None

    def get_channelsection(self,channel_id:str):
        params = {
            'key': self.__token,
            'channelId': channel_id,
            'part': 'contentDetails'
        }
        r = requests.get('https://www.googleapis.com/youtube/v3/channelSections',params=params)
        if r.status_code == 200:
            print(r)
            print(r.json())
        else:
            print(r.text)
            print(r.status_code)

    def get_streams(self,channel_ids:list):
        print(','.join(channel_ids))
        params ={
            'key': self.__token,
            'part': 'snippet',
            'channelId': ','.join(channel_ids),
            'eventType':'live',
            'type': 'video'
        }
        r = requests.get('https://www.googleapis.com/youtube/v3/search',params=params)
        if r.status_code == 200:
            print(r)
            print(r.json())
        else:
            print(r.text)
            print(r.status_code)

    def get_stream(self,channel_id:str):
        '''取得Youtube直播資訊（若無正在直播則回傳None）'''
        params ={
            'key': self.__token,
            'part': 'snippet',
            'channelId': channel_id,
            'eventType':'live',
            'type': 'video'
        }
        r = requests.get('https://www.googleapis.com/youtube/v3/search',params=params)
        if r.status_code == 200 and r.json()['items']:
            return YouTubeStream(r.json()['items'][0])
        else:
            print(r.text)
            print(r.status_code)
            return None

class YoutubeRSS(CommunityInterface):
    def get_videos(self,channel_id) -> list[dict]:
        youtube_feed = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
        feed = feedparser.parse(youtube_feed)
        # for entry in feed['entries']:
        #     print(entry)
        return feed['entries']

class GoogleCloud():
    def __init__(self):
        self.creds = self.get_creds()
    
    def get_creds(self):
        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/drive']
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        if os.path.exists('database/google_token.json'):
            creds = Credentials.from_authorized_user_file('database/google_token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'database/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('database/google_token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
    
    def list_drive_files(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """

        try:
            service = build('drive', 'v3', credentials=self.creds)

            # Call the Drive v3 API
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print('No files found.')
                return
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
            return results
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print(f'An error occurred: {error}')

    def list_file_permissions(self,fileId):
        service = build('drive', 'v3', credentials=self.creds)
        results = service.permissions().list(fileId=fileId).execute()
        print(results)
        return results

    def add_file_permissions(self,fileId,emailAddress):
        service = build('drive', 'v3', credentials=self.creds)
        permission_dict = {
        "role": "reader",
        'type': 'user',
        'emailAddress': emailAddress
        }
        results = service.permissions().create(fileId=fileId,body=permission_dict).execute()
        print(results)
        return results
    
    def remove_file_permissions(self,fileId,permissionId):
        service = build('drive', 'v3', credentials=self.creds)
        results = service.permissions().delete(fileId=fileId,permissionId=permissionId).execute()
        print(results)
        return results

class NotionAPI(CommunityInterface):
    def __init__(self):
        self.headers = self._get_headers()
        self.url = "https://api.notion.com/v1"

    def _get_headers(self):
        token = Jsondb.get_token("notion_api")
        return {
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    def get_page(self,page_id:str):
        r = requests.get(f"{self.url}/pages/{page_id}",headers=self.headers)
        apidata = r.json()
        if r.status_code == 200:
            print(apidata)
        else:
            print(apidata['message'])
    
    def get_block(self,block_id:str):
        r = requests.get(f"{self.url}/blocks/{block_id}",headers=self.headers)
        apidata = r.json()
        if r.status_code == 200:
            print(apidata)
        else:
            print(apidata['message'])
    
    def search(self,title:str):
        """search by title"""
        data = {
            "query": title
        }
        r = requests.post(f"{self.url}/search",json=data,headers=self.headers)
        apidata = r.json()
        if r.status_code == 200:
            print(apidata)
        else:
            print(apidata['message'])