from modules.data_structures import TrendItem
from datetime import datetime

t = TrendItem(
    item_name="Mini Blender",
    hashtags=["#TikTokMadeMeBuyIt"],
    caption_texts=["Need this! Buying now!"],
    view_count=54000,
    like_count=7300,
    comment_count=480,
    share_count=210,
    creator_followers=12000,
    post_time=datetime.now()
)

print(t.summary())