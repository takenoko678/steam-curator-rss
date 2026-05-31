# Steam Curator RSS Generator

Steamキュレーターページの新しいレコメンデーションをRSSフィードで配信するプロジェクト

## 概要

このプロジェクトは Steam キュレーターページから新しいゲームレコメンデーションを自動抽出し、RSS フィードとして配信します。

- **複数キュレーター対応**: 複数のキュレーターを同時に監視可能
- **自動更新**: GitHub Actions で毎日自動実行
- **RSS配信**: GitHub Pages で RSSフィードをホスト
- **増分更新**: 新しいゲームのみを検出

## セットアップ

### 1. リポジトリの初期化

```bash
git clone https://github.com/YOUR_USERNAME/steam-curator-rss.git
cd steam-curator-rss
```

### 2. キュレーター設定

`data/curators.json` に監視対象のキュレーターを追加:

```json
[
  {
    "id": "キュレーターID",
    "name": "キュレーター名",
    "url": "https://store.steampowered.com/curator/[ID]-[NAME]/",
    "rss_file": "output.xml"
  }
]
```

### 3. ローカルテスト

```bash
pip install -r requirements.txt
cd src
python main.py
```

## GitHub Pages 有効化

1. リポジトリの Settings → Pages を開く
2. Source を "Deploy from a branch" に設定
3. Branch を "main", folder を "/docs" に選択
4. Save

これで `https://YOUR_USERNAME.github.io/steam-curator-rss/` でフィード一覧が表示されます。

## ファイル構成

- `src/main.py`: メイン処理
- `src/scraper.py`: Steam スクレイピング機能
- `src/rss_generator.py`: RSS フィード生成
- `data/curators.json`: キュレーター設定
- `data/last_*.json`: 前回実行時のゲームID（自動生成）
- `docs/feeds/`: 生成されたRSSフィード
- `docs/index.html`: フィード一覧ページ
- `.github/workflows/update-rss.yml`: GitHub Actions ワークフロー

## RSS フィードの使用

各キュレーターの RSS フィード URL:
```
https://raw.githubusercontent.com/YOUR_USERNAME/steam-curator-rss/main/docs/feeds/[rss_file]
```

RSSリーダーアプリで上記 URL を購読すると、新しいゲームが追加されるたびに通知されます。

## カスタマイズ

### 更新スケジュール変更

`.github/workflows/update-rss.yml` の `cron` を編集:

```yaml
schedule:
  - cron: '0 */6 * * *'  # 6時間ごと
```

[Cron スケジュール参考](https://crontab.guru/)

## トラブルシューティング

- **RSSが生成されない場合**: Steam ページの HTML 構造が変わった可能性があります。`src/scraper.py` の CSS セレクタを更新してください。
- **GitHub Actions が失敗する場合**: Actions ログを確認してください。

## ライセンス

MIT
