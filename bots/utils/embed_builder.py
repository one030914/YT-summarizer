import discord

def build_summary_embed(video_title: str, analysis: dict) -> discord.Embed:
    embed = discord.Embed(
        title="YT留言摘要機器人",
        description=f"📽️ 影片標題：**{video_title}**",
        color=0x5865F2
    )

    # 🧠 摘要段落
    summary = analysis.get("summary", [])
    summary_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(summary)]) if summary else "（無）"
    embed.add_field(name="📌 摘要：", value=summary_text, inline=False)

    # 🔑 關鍵字段落
    keywords = analysis.get("keywords", [])
    keyword_text = "、".join([f"`{k}`" for k in keywords]) if keywords else "（無）"
    embed.add_field(name="🔑 關鍵詞：", value=keyword_text, inline=False)

    # 🌍 語言比例
    lang = analysis.get("lang_ratio", {})
    zh = lang.get("zh", 0.0)
    en = lang.get("en", 0.0)
    other = lang.get("other", 0.0)
    lang_text = f"🌐 中文 {zh:.1f}%\n🗽 英文 {en:.1f}%\n🌐 其他語言 {other:.1f}%"
    embed.add_field(name="🌍 語言佔比", value=lang_text, inline=False)

    return embed