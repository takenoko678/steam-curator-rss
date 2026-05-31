import json
import os
from pathlib import Path
from datetime import datetime
import logging

from scraper import scrape_curator
from rss_generator import create_rss_feed, save_rss_feed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_curators() -> list:
    """キュレーター設定を読み込み"""
    with open('data/curators.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_last_ids(curator_id: str) -> set:
    """前回実行時のゲームIDを読み込み"""
    last_file = f'data/last_{curator_id}.json'
    if os.path.exists(last_file):
        try:
            with open(last_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            logger.warning(f"Failed to load {last_file}: {e}")
    return set()

def save_last_ids(curator_id: str, game_ids: set) -> None:
    """ゲームIDを保存"""
    last_file = f'data/last_{curator_id}.json'
    with open(last_file, 'w', encoding='utf-8') as f:
        json.dump(list(game_ids), f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(game_ids)} game IDs for curator {curator_id}")

def create_index_html(curators: list) -> str:
    """フィード一覧のHTMLを生成"""
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam Curator RSS Feeds</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 20px; }
        h1 { color: #1a1a1a; }
        .feed-list { list-style: none; padding: 0; }
        .feed-item { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        .feed-item a { color: #0066cc; text-decoration: none; }
        .feed-item a:hover { text-decoration: underline; }
        .feed-url { font-size: 0.9em; color: #666; word-break: break-all; }
    </style>
</head>
<body>
    <h1>Steam Curator RSS Feeds</h1>
    <p>新しいゲームレコメンデーションをRSSで購読</p>
    <ul class="feed-list">
"""

    for curator in curators:
        feed_url = f"https://raw.githubusercontent.com/{{GITHUB_USER}}/steam-curator-rss/main/docs/feeds/{curator['rss_file']}"
        html += f"""        <li class="feed-item">
            <strong>{curator['name']}</strong><br>
            <a href="{curator['url']}" target="_blank">キュレーターページ</a> |
            <a href="{feed_url}">RSS</a><br>
            <span class="feed-url">Feed: {feed_url}</span>
        </li>
"""

    html += """    </ul>
    <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
        最終更新: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    </p>
</body>
</html>
"""
    return html

def main():
    """メイン処理"""
    logger.info("Starting Steam Curator RSS update")

    os.makedirs('docs/feeds', exist_ok=True)

    curators = load_curators()

    for curator in curators:
        curator_id = curator['id']
        curator_name = curator['name']
        curator_url = curator['url']
        rss_file = curator['rss_file']

        last_ids = load_last_ids(curator_id)
        new_games, all_game_ids = scrape_curator(curator_id, curator_url, last_ids)

        if new_games:
            logger.info(f"Generating RSS for {curator_name}")
            feed = create_rss_feed(curator_name, curator_url, new_games)
            output_path = f'docs/feeds/{rss_file}'
            save_rss_feed(feed, output_path)
        else:
            logger.info(f"No new games for {curator_name}")

        save_last_ids(curator_id, all_game_ids)

    index_html = create_index_html(curators)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    logger.info("Updated docs/index.html")

    logger.info("Steam Curator RSS update completed")

if __name__ == '__main__':
    main()
