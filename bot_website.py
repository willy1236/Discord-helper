import os,time
from fastapi import FastAPI,BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import HTMLResponse,JSONResponse,PlainTextResponse
import xml.etree.ElementTree as ET

from main import bot
from bothelper.model.push import Youtube_Push

app = FastAPI()

@app.route('/')
def main(request:Request):
    return HTMLResponse('test')

@app.route('/keep_alive',methods=['GET'])
def keep_alive(request:Request):
    r = HTMLResponse(content='Bot is aLive!')
    return r

@app.post('/twitch_eventsub',response_class=PlainTextResponse)
def twitch_eventsub(request:Request):
    try:
        if request.method == "POST":
            data = Request.json()
            challenge = data['challenge']
            print('status:',data['subscription']['status'])

            r = HTMLResponse(
                content = challenge,
                media_type = 'text/plain',
                status_code = 200
            )
            return r
        else:
            print("[Warning] Server Received & Refused!")
            return "Refused", 400

    except Exception as e:
        print("[Warning] Error:", e)
        return "Server error", 400
    
async def get_yt_push(content):
    # 解析XML文件
    # tree = ET.parse(content)
    # root = tree.getroot()
    print(content)
    root = ET.fromstring(content)

    # 创建一个空字典来存储结果
    result = {}

    # 解析entry元素並存入字典中
    entry = root.find('{http://www.w3.org/2005/Atom}entry')
    result['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text
    result['videoId'] = entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text
    result['channelId'] = entry.find('{http://www.youtube.com/xml/schemas/2015}channelId').text
    result['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text
    result['link'] = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
    result['author_name'] = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name').text
    result['author_uri'] = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}uri').text
    result['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text
    result['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text

    # 輸出結果
    print(result)
    #{'id': 'yt:video:L3pnOeAea80', 'videoId': 'L3pnOeAea80', 'channelId': 'UCbh7KHPMgYGgpISdbF6l0Kw', 'title': '【輕聲細語】全肯定。溫柔。哄睡。🌼 #瑪格麗特諾爾絲 #箱箱TheBox', 'link': 'https://www.youtube.com/watch?v=L3pnOeAea80', 'author_name': '瑪格麗特 · 諾爾絲 / Margaret North【箱箱The Box所屬】', 'author_uri': 'https://www.youtube.com/channel/UCbh7KHPMgYGgpISdbF6l0Kw', 'published': '2023-04-07T17:15:34+00:00', 'updated': '2023-04-07T17:15:56.88236001+00:00'}
    embed = Youtube_Push(result).desplay()
    channel = bot.get_channel(566533708371329026)
    await channel.send(embed=embed)

@app.get('/youtube_push')
def youtube_push_get(request:Request):
    params = dict(request.query_params)
    print(params)
    if 'hub.challenge' in params:
        return HTMLResponse(content=params['hub.challenge'])  
    else:
        return HTMLResponse('OK')

@app.post('/youtube_push')
async def youtube_push_post(request:Request,background_task: BackgroundTasks):
    body = await request.body()
    body = body.decode('UTF-8')
    print(body)
    background_task.add_task(get_yt_push,body)
    return HTMLResponse('OK')

@app.get('/book/{book_id}',response_class=JSONResponse)
def get_book_by_id(book_id: int):
    return {
        'book_id': book_id
    }

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    html_file = open().read()
    return html_file


def run():
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=14000)

if __name__ == '__main__':
    #os.system('uvicorn bot_website:app --reload')
    from cmds.task import ltThread
    server = ltThread()
    server.start()

    run()