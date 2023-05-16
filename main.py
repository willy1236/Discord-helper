import discord, os,asyncio,time
from discord.ext import commands
from threading import Thread

from starcord.ui_element.button import *
from starcord import Jsondb,log,twitch_bot

#Bot1:dc小幫手, Bep:Bep, Bot2:RO
jdata = Jsondb.jdata
bot_code = jdata.get('bot_code')
token = Jsondb.tokens.get(bot_code)
start_website = jdata.get('start_website')
auto_update = jdata.get('auto_update')
debug_guild = jdata.get('debug_guild')
#commands.Bot
#shard_count=1,
#command_prefix=commands.when_mentioned_or('b!'),
#command_prefix='b!',
#case_insensitive=True,
#只有discord.Bot才有debug_guild

if bot_code == 'Bot1':
    bot = discord.Bot(
        owner_id=419131103836635136,
        intents=discord.Intents.all(),
        help_command=None
    )
elif bot_code == 'Bep':
    bot = discord.Bot(
        owner_id=419131103836635136,
        intents=discord.Intents.all(),
        help_command=None,
        debug_guilds = debug_guild
    )
elif bot_code == 'Bot2':
    bot = discord.Bot(
        owner_id=419131103836635136,
        debug_guilds = debug_guild
    )
else:
    raise ValueError("Invalid bot_code")

#啟動
@bot.event
async def on_ready():
    #print(">> Bot is online <<")
    log.info(f">> Bot online as {bot.user.name} <<")
    log.info(f">> Discord's version:{discord.__version__} <<")
    await bot.change_presence(activity=discord.Game(name=jdata.get("activity","/help")),status=discord.Status.online)
    # cogs = ""
    # for i in bot.cogs:
    #     cogs += f"{i} "
    # print(">> Cogs:",cogs,"<<")
    if len(os.listdir('./cmds'))-1 == len(bot.cogs):
        log.info(">> Cogs all loaded <<")
    else:
        log.warning(f">> Cogs not all loaded, {len(bot.cogs)}/{len(os.listdir('./cmds'))} loaded<<")
    if bot_code == 'Bot1':
        #bot.add_view(ReactRole_button())
        pass
    

#load
@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cmds.{extension}')
    await ctx.respond(f'Loaded {extension} done')

#unload
@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cmds.{extension}')
    await ctx.respond(f'Un - Loaded {extension} done')

#reload
@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.reload_extension(f'cmds.{extension}')
    await ctx.respond(f'Re - Loaded {extension} done')

#ping
@bot.command()
async def ping(ctx):
    await ctx.respond(f'延遲為:{round(bot.latency*1000)} ms')

for filename in os.listdir('./cmds'):
    if filename.endswith('.py'):
        bot.load_extension(f'cmds.{filename[:-3]}')


if __name__ == "__main__":
    if bot_code == 'Bot1' and auto_update:
        os.system('python ./app/update.py')
            
    if start_website:
        def run_website():
            os.system('uvicorn bot_website:app --port 14000')

        from bot_website import ltThread
        ltserver = ltThread()
        ltserver.start()
        time.sleep(2)

        try:
            server = Thread(target=run_website,name='bot_website')
            server.start()
            log.info('>> website: online <<')
            time.sleep(2)
        except:
            log.info('>> website: offline <<')
    else:
        log.info('>> website: off <<')

    if twitch_bot:
        loop = asyncio.get_event_loop()
        #loop.run_until_complete(twitch_bot.connect())
        loop.create_task(twitch_bot.connect())
        time.sleep(2)
    
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        log.error('>> Bot: Login failed <<')
    except Exception as e:
        log.error(e)