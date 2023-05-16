from datetime import datetime,timezone,timedelta
from starcord.utility import BotEmbed

class Youtube_Push:
    def __init__(self,data:dict):
        tz = timezone(timedelta(hours=8))
        #{'id': 'yt:video:L3pnOeAea80', 'videoId': 'L3pnOeAea80', 'channelId': 'UCbh7KHPMgYGgpISdbF6l0Kw', 'title': '【輕聲細語】全肯定。溫柔。哄睡。🌼 #瑪格麗特諾爾絲 #箱箱TheBox', 'link': 'https://www.youtube.com/watch?v=L3pnOeAea80', 'author_name': '瑪格麗特 · 諾爾絲 / Margaret North【箱箱The Box所屬】', 'author_uri': 'https://www.youtube.com/channel/UCbh7KHPMgYGgpISdbF6l0Kw', 'published': '2023-04-07T17:15:34+00:00', 'updated': '2023-04-07T17:15:56.88236001+00:00'}
        self.id = data.get('id')
        self.video_id = data.get('videoId')
        self.channelid = data.get('channelId')
        self.title = data.get('title')
        self.link = data.get('link')
        self.author_name = data.get('author_name')
        self.author_url = data.get('author_uri')
        self.published = datetime.fromisoformat(data.get('published')).replace(tzinfo=tz)
        self.updated = datetime.strptime(data.get('updated')[:-10],'%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=tz)
        self.updated = self.updated + timedelta(hours=8)
        
    def desplay(self):
        embed = BotEmbed.simple(title=self.title,
                                url=self.link,
                                description=f'[{self.author_name}]({self.author_url})')
        return embed


