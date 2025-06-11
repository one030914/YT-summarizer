import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv(verbose=True)
with open('./bots/data.json', 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    for filename in os.listdir('./bots/cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    
    slash = await bot.tree.sync()
    print(f"loaded {len(slash)} slash commands.")
    print('Bot is online!')

if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))