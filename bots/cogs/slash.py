import discord
from discord import app_commands
from discord.ui import View, Button
from datetime import datetime
from core.classes import Cog_Extension
from process.get import get_title
from data.APIComments import API
from bots.data.analyze_pipeline import analyze_comments
from bots.utils.embed_builder import build_summary_embed

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
        await interaction.response.defer()  # 防止 timeout

        title = get_title(video_url)
        if title is None:
            embed = discord.Embed(
                title='Error',
                description='Invalid video URL or unable to retrieve title.',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        # 抓留言
        comments = API().get_comments(video_url)
        print("📥 原始留言：", comments[:5])
        if not comments:
            embed = discord.Embed(
                title='Error',
                description='No comments found or unable to fetch comments.',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        # 執行分析（預處理 + 模型）
        print("🔍 開始分析留言...")
        try:
            comments_text = [c['原留言'] for c in comments if '原留言' in c]
            result = analyze_comments(comments_text)
            print("✅ 分析完成，結果：", result)
        except Exception as e:
            print("❌ 分析過程發生錯誤：", str(e))
            embed = discord.Embed(
                title='Error',
                description='分析留言時發生錯誤，請稍後再試。',
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        # 建立 embed 卡片
        embed = build_summary_embed(title, result)
        view = View()
        view.add_item(Button(label='👉點我看影片!', url=video_url, style=discord.ButtonStyle.link))

        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Slash(bot))