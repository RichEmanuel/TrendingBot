# =========================================================
# TikTok Trend Finder – Discord Bot
# =========================================================
import os
import json
from datetime import datetime
import discord
from discord.ext import commands, tasks
from modules.data_structures import TrendItem
from modules.scoring import update_intent_score
from modules.report import save_report

# ---------------------------------------------------------
#  Configuration
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1435333379946975425  # 👈 replace with your channel ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================================================
#  Helper Function: build trends embed
# =========================================================
async def build_trends_embed() -> discord.Embed:
    """Load data from JSON, compute scores, and return a styled embed."""
    try:
        with open("data/trends.json", "r", encoding="utf-8") as f:
            raw_items = json.load(f)
    except Exception as e:
        return discord.Embed(
            title="⚠️ Error Loading Data",
            description=str(e),
            color=0xE74C3C,
        )

    items = []
    for entry in raw_items:
        item = TrendItem(
            item_name=entry["item_name"],
            hashtags=entry["hashtags"],
            caption_texts=entry["caption_texts"],
            view_count=entry["view_count"],
            like_count=entry["like_count"],
            comment_count=entry["comment_count"],
            share_count=entry["share_count"],
            creator_followers=entry["creator_followers"],
            post_time=datetime.now(),
        )
        update_intent_score(item)
        items.append(item)

    # Sort by score high → low
    items.sort(key=lambda x: x.intent_score, reverse=True)

    # Build the embed
    embed = discord.Embed(
        title="📊 Top Trending Products",
        description="Automatically refreshed leaderboard",
        color=0x00FF88,
    )

    medals = ["🥇", "🥈", "🥉"]
    for idx, item in enumerate(items):
        medal = medals[idx] if idx < len(medals) else f"{idx + 1}."
        embed.add_field(
            name=f"{medal} {item.item_name}",
            value=(
                f"💡 Score: {item.intent_score:.2f}\n"
                f"❤️ Likes: {item.like_count:,}  💬 Comments: {item.comment_count:,}"
            ),
            inline=False,
        )

    # Dynamic color bar
    top_score = items[0].intent_score if items else 0
    if top_score > 8:
        embed.color = 0x1ABC9C  # green
    elif top_score > 6:
        embed.color = 0xF1C40F  # yellow
    else:
        embed.color = 0xE74C3C  # red

    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4424/4424710.png")
    embed.set_footer(text=f"TrendingBot • Updated {datetime.now():%Y-%m-%d %H:%M}")
    return embed, items  # return items too so we can save them

# =========================================================
#  Commands
# =========================================================
@bot.command()
async def ping(ctx):
    """Check that the bot is responsive."""
    await ctx.send("🏓 Pong! TrendingBot is online and ready to spot trends.")


@bot.command()
async def trendtest(ctx):
    """Run a sample analysis on fake TikTok data."""
    test_item = TrendItem(
        item_name="Mini Blender",
        hashtags=["#TikTokMadeMeBuyIt"],
        caption_texts=[
            "I need this mini blender!",
            "Buying this right now 😍",
            "So cute, must have!",
        ],
        view_count=54000,
        like_count=7300,
        comment_count=480,
        share_count=210,
        creator_followers=12000,
        post_time=datetime.now(),
    )
    update_intent_score(test_item)

    message = (
        f"**{test_item.item_name}**\n"
        f"Likes: {test_item.like_count:,} | Comments: {test_item.comment_count:,}\n"
        f"💡 Intent Score: **{test_item.intent_score:.2f}**"
    )
    await ctx.send(message)


@bot.command()
async def trends(ctx):
    """Manually display the latest leaderboard and save a CSV report."""
    embed, items = await build_trends_embed()
    await ctx.send(embed=embed)

    # 💾 Save current trends to a CSV in data/reports/
    save_report(items)

# =========================================================
#  Events
# =========================================================
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now running!")
    if not hourly_update.is_running():
        hourly_update.start()

# =========================================================
#  Background task – automatic hourly updates
# =========================================================
@tasks.loop(hours=1)
async def hourly_update():
    """Post the latest trends every hour automatically."""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("⚠️ Channel ID not found – auto‑update skipped.")
        return

    embed, items = await build_trends_embed()
    await channel.send(embed=embed)
    save_report(items)  # save to CSV on every auto post
    print(f"[{datetime.now():%H:%M}] Auto‑update sent to {channel.name}")

# =========================================================
#  Run the bot
# =========================================================
try:
    bot.run(TOKEN)
except Exception as e:
    print("💥 Bot failed to start:", e)