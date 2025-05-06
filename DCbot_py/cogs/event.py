import discord
from discord.ext import commands
from core.classes import Cog_Extension

class Event(Cog_Extension):
    def __init__(self, bot):
        self.bot = bot
    # your events
    # @commands.Cog.listener()
    # async def fun(self, arg):

async def setup(bot):
    await bot.add_cog(Event(bot))