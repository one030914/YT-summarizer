import discord
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
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
            title=f'🎥 影片標題：{title}',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(
            name="**📌 摘要：**",
            value=(
                "1. [summary 1]\n"
                "2. [summary 2]\n"
                "3. [summary 3]"
            ),
            inline=False
        )
        embed.add_field(
            name="**🔑 關鍵詞：**",
            value="[keyword 1]、[keyword 2]、[keyword 3]",
            inline=False
        )
        embed.add_field(
            name="**🌐 語言佔比：**",
            value=(
                "🥇 中文 XX%\n"
                "🥈 英文 YY%\n"
                "🥉 其他語言 ZZ%"
            ),
            inline=False
        )
        view = View()
        view.add_item(Button(label='👉點我看影片!', url=video_url, style=discord.ButtonStyle.link))
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Slash(bot))