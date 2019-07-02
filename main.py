import discord, configparser, asyncio, aiohttp, json, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

dConfig = configparser.ConfigParser()
dConfig.read('discordconfig.ini')
twitchConfig = configparser.ConfigParser()
twitchConfig.read('twitchconfig.ini')

live = False
debug = True
liveCheck = False

class discordClient(discord.Client):
    async def on_ready(self):
        print('Logged in as ', self.user)
    async def on_message(self, message):
        if str(message.author.id) == dConfig['discord']['adminid']:
            if message.content == 'aka!livetest':
                global live
                global debug
                global liveCheck
                embed = discord.Embed(color=discord.Color(0xff0000), timestamp=datetime.datetime.now())
                embed.set_footer(text="bot by Woovie#5555 | https://github.com/woovie")
                embed.add_field(name="live?", value=live)
                embed.add_field(name="debug?", value=debug)
                embed.add_field(name="last live check", value=liveCheck)
                await message.channel.send(embed=embed, content="")

async def checkIfLive():
    global live
    global debug
    async with aiohttp.ClientSession() as session:
        headers = {'Client-ID': twitchConfig['twitch']['clientid']}
        async with session.get(f"{twitchConfig['twitch']['apiurl']}{twitchConfig['twitch']['streamer']}", headers=headers) as r:
            if r.status == 200:
                text = await r.json()
    jsonData = text
    if len(jsonData['data']) > 0 and live == False:
        live = True
        await client.get_channel(int(dConfig['discord']['channelid'])).send(dConfig['discord']['message'])
    elif len(jsonData['data']) == 0 and live == True:
        live = False
    if debug:
        global liveCheck
        liveCheck = f"[{datetime.datetime.now()}] [DEBUG] Checked if live, result: {live}"
        print(liveCheck)

sched = AsyncIOScheduler()
sched.add_job(checkIfLive, 'interval', minutes=1)#TODO: Somehow load the `minutes=1` from the twitchconfig.
sched.start()

client = discordClient()

client.run(dConfig['discord']['token'])
