import discord
import json
import threading 
import requests
import time
import cloudscraper

from discord import SyncWebhook
from discord.ext import commands

scraper = cloudscraper.create_scraper()
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix = ">",intents=intents)

token = "yoink"

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="# 943 #"))
    print('Logged in as')
    print(f'NAME: {client.user.name}')
    print(f'UID: {client.user.id}')
    print(f'VERSION: {discord.__version__}')

    print('GUILDS:')
    print ('--------')
    for guild in client.guilds:
        print(f"{guild.name} | {guild.owner_id}")
    print ('--------')

@client.command()
async def watch(ctx,uid):
    await watch_user(ctx.author,uid=uid)
    await ctx.send(f'Now Watching: `{get_username(uid)}`')

@client.command()
async def online(ctx):
    list = ""
    users = await get_watching()
    for user in users:
        watcher = users[user]["watchedby"]
        reason = users[user]["reason"]
        status = users[user]["status"]
        last_online = users[user]["last_online"]
        if status == "online" or status == "playing a game":
            list = list + convert_activity(status) + " **" + get_username(user) + "**" + " | Watcher: <@" + watcher + ">\n"
    embed = discord.Embed(title="Online Users", description=list)
    embed.set_footer(text="github.com/datadisruptor")
    await ctx.send(embed=embed)

@client.command()
async def offline(ctx):
    list = ""
    users = await get_watching()
    for user in users:
        watcher = users[user]["watchedby"]
        reason = users[user]["reason"]
        status = users[user]["status"]
        last_online = users[user]["last_online"]
        if status == "offline":
            list = list + convert_activity(status) + " **" + get_username(user) + "**" + " | Last Online: " + last_online + " Watcher: <@" + watcher + ">\n"
    embed = discord.Embed(title="Offline Users", description=list)
    embed.set_footer(text="# 943")
    await ctx.send(embed=embed)


def format(x):
    return f"{x:,}"
    

def get_username(uid):
    re = requests.get(f"https://users.roblox.com/v1/users/{uid}").text
    data = json.loads(re)
    return f'{data["displayName"]} (@{data["name"]})'

async def watch_user(user,uid):
    users = await get_watching()
    if str(uid) in users:
        return False
    else:
        users[str(uid)] = {}
        users[str(uid)]["watchedby"] = str(user.id)
        users[str(uid)]["reason"] = ""
        users[str(uid)]["status"] = "unknown"
        users[str(uid)]["last_online"] = "unknown"
    
    with open("Data/watching.json","w") as f:
        json.dump(users,f)

async def get_watching():
    with open("Data/watching.json","r") as f:
        users = json.load(f)
    return users



def convert_presence(p:int):
    if p == 0:
        return "offline"
    elif p== 1:
        return "online"
    elif p == 2:
        return "playing a game"
    else:
        return "unknown" 
    

def convert_activity(v:str):
    if v == "offline":
        return "⚪"
    elif v== "online":
        return "🔵"
    elif v == "playing a game":
        return " 🟢"
    else:
        return "❓" 
    
def send_active_alert(user,activity):
    username = get_username(user)
    webhook = SyncWebhook.from_url("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    webhook.send(f"{convert_activity(activity)} [{username}](https://www.roblox.com/users/{user}/profile) is now {activity}")

def start_watching():
    while(True): 
        time.sleep(5) 
        uids = []
        with open("Data/watching.json","r") as f:
            users = json.load(f)
        for key in users:
            uids.append(key)
        obj = {"userIds":uids}
        response = requests.post("https://presence.roblox.com/v1/presence/users",json=obj)
        re = json.loads(response.text)
        data = re["userPresences"]
        for user in data:
            last = user["lastOnline"].split("T")
            if convert_presence(user["userPresenceType"]) != users[str(user["userId"])]["status"]:
                send_active_alert(user=user["userId"],activity=convert_presence(user["userPresenceType"]))
            users[str(user["userId"])]["status"] = convert_presence(user["userPresenceType"])
            users[str(user["userId"])]["last_online"] = last[0]
        with open("Data/watching.json","w") as f:
            json.dump(users,f)

threading.Thread(target=start_watching).start()


client.run(token)