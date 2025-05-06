import discord
from discord.ext import commands
from core.classes import Cog_Extension

class Main(Cog_Extension):
    def __init__(self, bot):
        self.bot = bot
    # main entry

async def setup(bot):
    await bot.add_cog(Main(bot))