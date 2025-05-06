import discord
from discord import app_commands
from discord.ui import View, Button
from core.classes import Cog_Extension
from process.get import get_title

class Slash(Cog_Extension):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='ping', description='Check the bot\'s latency')
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title='Pong!',
            description=f'Latency: {round(self.bot.latency*1000)} ms',
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name='summarize', description='summarize the video\'t comments.')
    async def summarize(self, interaction: discord.Interaction, video_url: str):
        title = get_title(video_url)
        if title is None:
            embed = discord.Embed(
                title='Error',
                description='Invalid video URL or unable to retrieve title.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        embed = discord.Embed(
            title=title,
            description=f'{title}\'s comments are summarized.',
            color=discord.Color.blue()
        )
        view = View()
        view.add_item(Button(label='👉點我看影片!', url=video_url, style=discord.ButtonStyle.link))
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Slash(bot))