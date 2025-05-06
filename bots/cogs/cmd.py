import discord
from discord.ext import commands
from core.classes import Cog_Extension

class Cmd(Cog_Extension):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def load(self, ctx, extension):
        await self.bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'Loaded {extension} done.')
    
    @commands.command()
    async def unload(self, ctx, extension):
        await self.bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Unoaded {extension} done.')

    @commands.command()
    async def reload(self, ctx, extension):
        await self.bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'Reoaded {extension} done.')

async def setup(bot):
    await bot.add_cog(Cmd(bot))