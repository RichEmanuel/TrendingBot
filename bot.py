# =========================================================
# TikTok Trend Finder – Discord Bot
# =========================================================
import os
import json
import logging
from datetime import datetime
import discord
from discord.ext import commands, tasks

from modules.data_structures import TrendItem
from modules.scoring import update_intent_score
from modules.report import save_report
from modules.movement import load_last_scores, compare_movement
from modules.chart import make_chart
from modules.sources.tiktok_loader import get_latest_trends
from modules.sources.update_cache import update_local_cache
from modules.database import init_db, save_trends
from modules.analytics import get_top_movers
from modules.insights import get_summary

# ---------------------------------------------------------
#  Configuration
# ---------------------------------------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1435333379946975425  # ← replace with your real channel ID

# Logging setup
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================================================
#  Helper Function: build trends embed
# =========================================================
async def build_trends_embed():
    """Load trend data via source loader, compute scores, and build an embed."""
    try:
        update_local_cache()
    except Exception as err:
        logging.warning("Cache update failed: %s", err)

    try:
        raw_items = get_latest_trends()
    except Exception as e:
        logging.exception("Failed to load trend data: %s", e)
        embed = discord.Embed(
            title="⚠️ Error Loading Data",
            description=str(e),
            color=0xE74C3C,
        )
        return embed, []

    items = []
    for entry in raw_items:
        try:
            item = TrendItem(
                item_name=entry.get("item_name", "Unknown Item"),
                hashtags=entry.get("hashtags", []),
                caption_texts=entry.get("caption_texts", []),
                view_count=entry.get("view_count", 0),
                like_count=entry.get("like_count", 0),
                comment_count=entry.get("comment_count", 0),
                share_count=entry.get("share_count", 0),
                creator_followers=entry.get("creator_followers", 0),
                post_time=datetime.now(),
            )
            update_intent_score(item)
            items.append(item)
        except Exception as err:
            logging.warning("Skipping bad entry: %s", err)

    items.sort(key=lambda x: x.intent_score, reverse=True)
    previous_scores = load_last_scores()
    movement_icons = compare_movement(items, previous_scores)

    embed = discord.Embed(
        title="📊 Top Trending Products",
        description="Movement vs previous leaderboard",
        color=0x00FF88,
    )

    medals = ["🥇", "🥈", "🥉"]
    for idx, item in enumerate(items):
        medal = medals[idx] if idx < len(medals) else f"{idx + 1}."
        arrow = movement_icons.get(item.item_name, "")
        embed.add_field(
            name=f"{medal} {item.item_name} {arrow}",
            value=(
                f"💡 Score: {item.intent_score:.2f}\n"
                f"❤️ Likes: {item.like_count:,}  💬 Comments: {item.comment_count:,}"
            ),
            inline=False,
        )

    top_score = items[0].intent_score if items else 0
    if top_score > 8:
        embed.color = 0x1ABC9C
    elif top_score > 6:
        embed.color = 0xF1C40F
    else:
        embed.color = 0xE74C3C

    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4424/4424710.png")
    embed.set_footer(text=f"TrendingBot • Updated {datetime.now():%Y-%m-%d %H:%M}")
    return embed, items

# =========================================================
#  Commands
# =========================================================
@bot.command()
async def ping(ctx):
    """Check that the bot is responsive."""
    await ctx.send("🏓 Pong! TrendingBot is online and ready to spot trends.")


@bot.command()
async def trendtest(ctx):
    """Run a quick analysis of a single fake item."""
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
    """Generate, display, and save the latest leaderboard."""
    embed, items = await build_trends_embed()
    await ctx.send(embed=embed)
    save_report(items)
    save_trends(items)
    logging.info("Manual !trends report saved (%d items).", len(items))


@bot.command()
async def graph(ctx, *, item: str = None):
    """Generate a trend‑over‑time chart for the given item name."""
    if not item:
        await ctx.send("⚠️ Please include an item name, e.g. `!graph Mini Blender`")
        return
    try:
        chart_path = make_chart(item)
        if not chart_path:
            await ctx.send(f"❌ No history found for '{item}'.")
            return
        await ctx.send(file=discord.File(chart_path))
        logging.info("Sent chart for %s", item)
    except Exception as e:
        logging.exception("Error in !graph command: %s", e)
        await ctx.send(f"⚠️ Failed to create chart for '{item}': {e}")


@bot.command()
async def topmovers(ctx, hours: int = 24):
    """Show items with the largest score increase in the past N hours (default 24)."""
    movers = get_top_movers(hours)
    if not movers:
        await ctx.send("⚠️ Not enough data yet to calculate top movers.")
        return

    embed = discord.Embed(
        title=f"📈 Top Movers (last {hours} h)",
        color=0x0099FF,
        description="Items gaining the most Intent Score recently.",
    )
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, diff, latest) in enumerate(movers):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        embed.add_field(
            name=f"{medal} {name}",
            value=f"⬆️ Change: +{diff:.2f}\n💡 Current: {latest:.2f}",
            inline=False,
        )

    embed.set_footer(text=f"TrendingBot • Updated {datetime.now():%Y-%m-%d %H:%M}")
    await ctx.send(embed=embed)


@bot.command()
async def summary(ctx, hours: int = 24):
    """Provide a short summary for the last N hours (default 24)."""
    data = get_summary(hours)
    if not data:
        await ctx.send("⚠️ Not enough data to summarize yet.")
        return

    top_item, avg_score, total_items = data
    embed = discord.Embed(
        title=f"🧾 Trend Summary (last {hours} h)",
        color=0xFFD700,
        description=(
            f"**Top Item:** {top_item}\n"
            f"**Average Score:** {avg_score:.2f}\n"
            f"**Unique Items Tracked:** {total_items}"
        ),
    )
    embed.set_footer(text=f"TrendingBot • {datetime.now():%Y-%m-%d %H:%M}")
    await ctx.send(embed=embed)


@bot.command()
async def daily(ctx):
    """Manually trigger the daily report (for testing)."""
    await post_daily_report()
    await ctx.send("✅ Daily report triggered manually.")

# =========================================================
#  Events
# =========================================================
@bot.event
async def on_ready():
    init_db()  # ensure trends.db and table exist
    print(f"✅ {bot.user} is now running!")
    logging.info("Bot started as %s", bot.user)
    if not hourly_update.is_running():
        hourly_update.start()
    if not daily_report.is_running():
        daily_report.start()

# =========================================================
#  Background task – hourly leaderboard update
# =========================================================
@tasks.loop(hours=1)
async def hourly_update():
    """Post the latest trends every hour automatically."""
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            logging.warning("Channel ID not found – auto‑update skipped.")
            return

        embed, items = await build_trends_embed()
        await channel.send(embed=embed)
        save_report(items)
        save_trends(items)
        logging.info("Auto‑update sent to %s (%d items).", channel.name, len(items))
    except Exception as e:
        logging.exception("Error in hourly_update: %s", e)

# =========================================================
#  Background task – daily report
# =========================================================
async def post_daily_report():
    """Generate and send a daily summary embed."""
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            logging.warning("Channel ID not found – daily report skipped.")
            return

        summary = get_summary(24)
        movers = get_top_movers(24)

        if not summary:
            await channel.send("⚠️ Not enough data to produce today’s summary.")
            return

        top_item, avg_score, total_items = summary

        embed = discord.Embed(
            title="📰 Daily Trending Report",
            color=0x2ECC71,
            description=(
                f"**Top Item:** {top_item}\n"
                f"**Average Score:** {avg_score:.2f}\n"
                f"**Unique Items:** {total_items}"
            ),
        )

        if movers:
            mover_lines = [f"• {name} (+{diff:.2f})" for name, diff, _ in movers[:5]]
            embed.add_field(
                name="📈 Top Movers (24 h)",
                value="\n".join(mover_lines),
                inline=False,
            )

        embed.set_footer(
            text=f"TrendingBot • Daily Report • {datetime.now():%Y‑%m‑%d}"
        )
        await channel.send(embed=embed)
        logging.info("Daily report posted to %s", channel.name)
    except Exception as e:
        logging.exception("Error in daily report: %s", e)


@tasks.loop(hours=24)
async def daily_report():
    """Automatically post the daily trending summary every 24h."""
    await post_daily_report()

# =========================================================
#  Run the bot
# =========================================================
try:
    bot.run(TOKEN)
except Exception as e:
    logging.exception("Bot failed to start: %s", e)
    print("💥 Bot failed to start:", e)