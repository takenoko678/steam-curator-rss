from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import List, Dict, Set
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_curator_page(url: str) -> str:
    """Steamキュレーターページを取得（JavaScript実行あり）"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until='networkidle')
            page.wait_for_load_state('load')
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""

def extract_games(html: str, url: str) -> List[Dict[str, str]]:
    """HTMLからゲーム情報を抽出"""
    soup = BeautifulSoup(html, 'html.parser')
    games = []

    # /app/ を含むすべてのリンクを探す
    app_links = soup.find_all('a', href=re.compile(r'/app/\d+'))

    seen_app_ids = set()

    for link in app_links:
        try:
            href = link.get('href', '')

            # app ID を抽出
            match = re.search(r'/app/(\d+)', href)
            if not match:
                continue

            app_id = match.group(1)

            # 重複を避ける
            if app_id in seen_app_ids:
                continue
            seen_app_ids.add(app_id)

            # ゲームURL
            app_url = f"https://store.steampowered.com/app/{app_id}"

            # タイトルを取得（祖先要素を探す）
            parent = link.parent
            title = 'Unknown'
            for _ in range(5):
                if parent is None:
                    break
                title_elem = parent.find('div', class_='recommendation_item_title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
                img_elem = parent.find('img')
                if img_elem and img_elem.get('alt'):
                    title = img_elem.get('alt')
                    break
                parent = parent.parent

            # 画像を取得
            image_url = ''
            img_parent = link.parent
            for _ in range(5):
                if img_parent is None:
                    break
                img_elem = img_parent.find('img')
                if img_elem and img_elem.get('src'):
                    image_url = img_elem.get('src', '')
                    break
                img_parent = img_parent.parent

            games.append({
                'app_id': app_id,
                'title': title,
                'url': app_url,
                'image_url': image_url
            })
        except Exception as e:
            logger.warning(f"Error extracting game info: {e}")
            continue

    logger.info(f"Extracted {len(games)} games from HTML")
    return games

def get_new_games(curator_id: str, games: List[Dict[str, str]], last_ids: Set[str]) -> List[Dict[str, str]]:
    """新規ゲームを抽出"""
    new_games = [game for game in games if game['app_id'] not in last_ids]
    return new_games

def scrape_curator(curator_id: str, url: str, last_ids: Set[str]):
    """キュレーターをスクレイプして新規ゲームを返す"""
    logger.info(f"Scraping curator {curator_id}: {url}")
    html = fetch_curator_page(url)
    if not html:
        return [], set()

    games = extract_games(html, url)
    logger.info(f"Found {len(games)} games for curator {curator_id}")

    new_games = get_new_games(curator_id, games, last_ids)
    logger.info(f"Found {len(new_games)} new games for curator {curator_id}")

    current_ids = {game['app_id'] for game in games}
    return new_games, current_ids
