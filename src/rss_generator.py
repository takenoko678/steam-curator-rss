from feedgen.feed import FeedGenerator
from typing import List, Dict
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def create_rss_feed(curator_name: str, curator_url: str, games: List[Dict[str, str]]) -> FeedGenerator:
    """RSS フィードを生成"""
    fg = FeedGenerator()
    fg.id(curator_url)
    fg.title(f'{curator_name} - New Recommendations')
    fg.link(href=curator_url, rel='alternate')
    fg.description(f'New game recommendations from {curator_name}')
    fg.language('ja')

    for game in games:
        fe = fg.add_entry()
        fe.id(game['url'])
        fe.title(game['title'])
        fe.link(href=game['url'])
        fe.description(f'<img src="{game["image_url"]}" />')
        fe.published(datetime.now(timezone.utc))

    return fg

def save_rss_feed(feed: FeedGenerator, output_path: str) -> None:
    """RSS フィードをファイルに保存"""
    try:
        feed.rss_file(output_path, pretty=True)
        logger.info(f"Saved RSS feed to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save RSS feed to {output_path}: {e}")
