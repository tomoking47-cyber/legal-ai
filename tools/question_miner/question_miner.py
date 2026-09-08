#!/usr/bin/env python3
"""
question_miner.py — 自社データから「読者が知りたがっている質問」を自動抽出する

VVメディア連載『世界の質問箱』『世界のいいニュース』『世界にひらく郷土レシピ』の
質問候補を、他社サイトではなく "自社が権利を持つデータ" から取り出すためのツール。

対応する情報源:
  1. Google Search Console の検索クエリ（API経由）
  2. サイト内検索ログ（CSV）
  3. カスタマーサポートの問い合わせログ（CSV）

出力:
  - questions_YYYY-MM-DD.csv   … 優先度順の質問候補一覧（編集部に渡すもの）
  - report_YYYY-MM-DD.md       … 上位30件のサマリー（会議で見るもの）

使い方は同じフォルダの README.md を参照。
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# 質問らしさの判定に使う語
# ---------------------------------------------------------------------------

# これが1つでもあれば「質問」とみなす語
STRONG_MARKERS = [
    "とは", "なぜ", "どうして", "どうやって", "どっち", "どちら", "違い",
    "いつ", "どこ", "だれ", "誰", "いくら", "どれくらい", "どのくらい",
    "どんな", "どう", "ですか", "ますか", "べき", "理由", "原因", "根拠",
    "大丈夫", "必要", "本当", "ほんと", "正しい", "正解", "教えて",
    "知りたい", "あるの", "ないの", "のか", "かな", "だめ", "ダメ",
    "平気", "危険", "?", "？",
]

# 日本語クエリでよく出る、質問を示す形（正規表現）
STRONG_PATTERNS = [
    re.compile(r"何"),        # 何回・何杯・何が・何を…
    re.compile(r"の$"),       # 「〜いいの」「〜なの」で終わる口語の疑問
    re.compile(r"って$"),     # 「〜って」で終わる問いかけ
]

# これが2つ以上あれば「質問」とみなす語
MEDIUM_MARKERS = [
    "方法", "やり方", "使い方", "選び方", "順番", "目安", "頻度", "意味",
    "効果", "おすすめ", "比較", "vs", "できる", "できない", "注意",
    "コツ", "タイミング", "毎日", "決まり", "いい", "良い", "悪い",
    "安全", "対策", "対処", "影響", "ある", "ない",
]

# 英語クエリの疑問詞（先頭に来たら質問とみなす）
EN_QUESTION_HEAD = re.compile(
    r"^(what|why|how|when|where|which|who|whose|whom|is|are|was|were|"
    r"can|could|should|would|does|do|did|will|difference|any|anyone)\b",
    re.IGNORECASE,
)

# 英語クエリで、文中にあれば質問とみなす言い回し
EN_QUESTION_PHRASES = [
    "do i need", "can i", "should i", "is it ok", "is it safe", "is it worth",
    "worth it", "how much", "how many", "how long", "how to", "where to",
    "what to", "best time", "difference between", " vs ", " or ",
    "do they", "can you", "is there", "are there", "need to bring",
    "allowed", "recommend", "reddit",
]

# ---------------------------------------------------------------------------
# 棚（カテゴリー）の判定に使う語
# ---------------------------------------------------------------------------

SHELF_KEYWORDS: dict[str, list[str]] = {
    # 訪日外国人向け。他の棚より先に判定する（旅行文脈が最優先のため）
    "inbound": [
        "japan", "japanese", "tokyo", "kyoto", "osaka", "hokkaido", "okinawa",
        "narita", "haneda", "jr pass", "suica", "pasmo", "ic card", "shinkansen",
        "tax free", "tax-free", "duty free", "konbini", "convenience store",
        "drugstore", "drug store", "pharmacy", "don quijote", "donki",
        "onsen", "ryokan", "hostel", "airbnb", "yen", "cash", "atm",
        "luggage", "suitcase", "carry on", "customs", "visa", "sim",
        "esim", "wifi", "pocket wifi", "translate", "english menu",
        "訪日", "インバウンド", "外国人", "免税", "旅行者", "観光客",
    ],
    "fashion": [
        "化粧", "コスメ", "スキンケア", "化粧水", "乳液", "美容液", "クリーム",
        "日焼け", "ファンデ", "クレンジング", "洗顔", "肌", "毛穴", "角質",
        "香水", "フレグランス", "服", "洋服", "洗濯", "毛玉", "ニット",
        "素材", "靴", "バッグ", "アクセサリー", "時計", "ヘア", "髪",
        "シャンプー", "ネイル", "メイク", "リップ", "まつげ", "眉",
    ],
    "health": [
        "睡眠", "眠", "寝", "疲れ", "疲労", "ストレス", "運動", "ストレッチ",
        "姿勢", "体温", "水分", "サプリ", "ビタミン", "免疫", "腸", "自律神経",
        "冷え", "むくみ", "呼吸", "入浴", "風呂", "湯船", "肩こり", "腰",
        "目の疲れ", "体調", "生活習慣", "健康", "リラックス", "瞑想",
    ],
    "trend": [
        "食べ", "料理", "レシピ", "保存", "冷凍", "解凍", "賞味", "消費期限",
        "栄養", "野菜", "果物", "肉", "魚", "調味料", "コーヒー", "紅茶",
        "お茶", "酒", "ワイン", "発酵", "弁当", "作り置き", "家電", "掃除",
        "収納", "旅行", "ペット", "郷土", "特産", "だし", "米", "パン",
    ],
}

# 法務チェックが必須になる語（薬機法・健康増進法・景表法まわり）
LEGAL_FLAG_KEYWORDS = [
    "効果", "効く", "効能", "治る", "治す", "改善", "予防", "痩", "ダイエット",
    "免疫", "アトピー", "ニキビ", "シミ", "しみ", "シワ", "しわ", "たるみ",
    "育毛", "抜け毛", "薬", "サプリ", "病", "症状", "痛", "妊娠", "授乳",
    "赤ちゃん", "子供", "こども", "アレルギー", "無添加", "安全", "副作用",
]

# ---------------------------------------------------------------------------
# データ構造
# ---------------------------------------------------------------------------


@dataclass
class Candidate:
    """質問候補1件"""

    query: str
    sources: set[str] = field(default_factory=set)
    impressions: int = 0
    clicks: int = 0
    position_sum: float = 0.0
    position_weight: float = 0.0
    hits: int = 0  # サイト内検索・CS問い合わせでの出現件数
    countries: set[str] = field(default_factory=set)

    @property
    def avg_position(self) -> float:
        if self.position_weight <= 0:
            return 0.0
        return self.position_sum / self.position_weight

    @property
    def ctr(self) -> float:
        if self.impressions <= 0:
            return 0.0
        return self.clicks / self.impressions


# ---------------------------------------------------------------------------
# 文字列処理
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """全角半角・大文字小文字・空白のゆれを吸収する"""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_question(query: str) -> bool:
    """質問らしいクエリかどうかを判定する"""
    q = normalize(query)
    if not q:
        return False

    for marker in STRONG_MARKERS:
        if marker in q:
            return True

    for pattern in STRONG_PATTERNS:
        if pattern.search(q):
            return True

    if EN_QUESTION_HEAD.search(q):
        return True

    if any(phrase in q for phrase in EN_QUESTION_PHRASES):
        return True

    medium_hits = sum(1 for marker in MEDIUM_MARKERS if marker in q)
    return medium_hits >= 2


def assign_shelf(query: str) -> str:
    """どの棚に置く質問かを推定する（最終判断は編集部）"""
    q = normalize(query)
    scores = {
        shelf: sum(1 for kw in keywords if kw in q)
        for shelf, keywords in SHELF_KEYWORDS.items()
    }
    # 旅行文脈の語が1つでもあれば inbound を優先する
    if scores.get("inbound", 0) > 0:
        return "inbound"
    best = max(scores, key=lambda s: scores[s])
    return best if scores[best] > 0 else "要判断"


def needs_legal_review(query: str) -> bool:
    """法務チェックが必須になる質問かどうか"""
    q = normalize(query)
    return any(kw in q for kw in LEGAL_FLAG_KEYWORDS)


def position_factor(position: float) -> float:
    """
    平均掲載順位から「伸びしろ」の重みを出す。

    考え方:
      すでに1位なら伸びしろは小さい。
      表示はされているのに10〜30位あたりに沈んでいるものが、いちばん惜しい。
      50位より下は、そもそも別の問題（まだ記事がない等）なので重みを下げる。
    """
    if position <= 0:
        return 0.8  # 順位データがない情報源（サイト内検索など）
    if position <= 3:
        return 0.1
    if position <= 10:
        return 0.6
    if position <= 20:
        return 1.0
    if position <= 30:
        return 0.9
    if position <= 50:
        return 0.6
    return 0.3


def opportunity_score(c: Candidate) -> float:
    """
    優先スコア = 需要の大きさ × 伸びしろ + 自社への直接の声

    「表示回数はあるのに順位が低い」＝
    「読者が求めているのに、VVがまだ十分に答えられていない」質問を上位に出す。
    """
    search_part = c.impressions * position_factor(c.avg_position)
    # サイト内検索・CS問い合わせは件数こそ少ないが、VVに来た人の生の声なので重く見る
    direct_part = c.hits * 30
    multi_source_bonus = 1.3 if len(c.sources) >= 2 else 1.0
    return (search_part + direct_part) * multi_source_bonus


# ---------------------------------------------------------------------------
# 情報源1: Google Search Console
# ---------------------------------------------------------------------------


def fetch_search_console(config: dict, start: str, end: str, verbose: bool = True) -> list[dict]:
    """Search Console API から検索クエリを取得する"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print(
            "エラー: Google関連のライブラリが入っていません。\n"
            "        次のコマンドを実行してください:\n"
            "            pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    token_path = Path(config.get("token_file", "token.json"))
    secrets_path = Path(config.get("client_secrets_file", "client_secrets.json"))

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not secrets_path.exists():
                print(
                    f"エラー: {secrets_path} が見つかりません。\n"
                    "        README.md の STEP 2 を見て、認証ファイルを置いてください。",
                    file=sys.stderr,
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), scopes)
            print("ブラウザが開きます。VVのGoogleアカウントでログインして許可してください。")
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    service = build("searchconsole", "v1", credentials=creds)
    site_url = config["site_url"]

    dimensions = ["query"]
    if config.get("include_country", False):
        dimensions.append("country")

    rows: list[dict] = []
    start_row = 0
    page_size = 25000

    while True:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": dimensions,
            "rowLimit": page_size,
            "startRow": start_row,
            "type": "web",
        }
        response = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        batch = response.get("rows", [])
        rows.extend(batch)
        if verbose:
            print(f"  Search Console から {len(rows)} 件取得...")
        if len(batch) < page_size:
            break
        start_row += page_size

    return rows


# ---------------------------------------------------------------------------
# 情報源2/3: CSV（サイト内検索ログ・CS問い合わせログ）
# ---------------------------------------------------------------------------


def load_csv_source(path: Path, column: str, source_name: str) -> list[tuple[str, str]]:
    """CSVから1列を読み出して (テキスト, 情報源名) のリストにする"""
    if not path.exists():
        return []

    out: list[tuple[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or column not in reader.fieldnames:
            print(
                f"警告: {path.name} に「{column}」という列が見つかりません。"
                f"（この列名は config.json で変更できます）実際の列: {reader.fieldnames}",
                file=sys.stderr,
            )
            return []
        for row in reader:
            text = (row.get(column) or "").strip()
            if text:
                out.append((text, source_name))
    return out


# ---------------------------------------------------------------------------
# 集計
# ---------------------------------------------------------------------------


def build_candidates(
    gsc_rows: list[dict],
    csv_items: list[tuple[str, str]],
    min_impressions: int,
    exclude_countries: set[str] | None = None,
    only_countries: set[str] | None = None,
) -> list[Candidate]:
    """各情報源のデータを1つの質問候補リストにまとめる"""
    table: dict[str, Candidate] = {}

    def get(key: str, display: str) -> Candidate:
        if key not in table:
            table[key] = Candidate(query=display)
        return table[key]

    # Search Console
    for row in gsc_rows:
        keys = row["keys"]
        raw = keys[0]
        country = keys[1].lower() if len(keys) > 1 else ""

        if only_countries and country and country not in only_countries:
            continue
        if exclude_countries and country and country in exclude_countries:
            continue
        if not is_question(raw):
            continue
        impressions = int(row.get("impressions", 0))
        if impressions < min_impressions:
            continue
        c = get(normalize(raw), raw)
        c.sources.add("検索")
        if country:
            c.countries.add(country)
        c.impressions += impressions
        c.clicks += int(row.get("clicks", 0))
        position = float(row.get("position", 0))
        if position > 0:
            c.position_sum += position * impressions
            c.position_weight += impressions

    # サイト内検索・CS問い合わせ
    for text, source_name in csv_items:
        if not is_question(text):
            continue
        c = get(normalize(text), text)
        c.sources.add(source_name)
        c.hits += 1

    return sorted(table.values(), key=opportunity_score, reverse=True)


# ---------------------------------------------------------------------------
# 出力
# ---------------------------------------------------------------------------

CSV_HEADER = [
    "順位",
    "質問候補",
    "推定棚",
    "優先スコア",
    "表示回数",
    "クリック",
    "CTR",
    "平均掲載順位",
    "直接の声",
    "情報源",
    "主な国",
    "法務チェック",
]


def write_csv(candidates: list[Candidate], path: Path, limit: int) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for i, c in enumerate(candidates[:limit], start=1):
            writer.writerow([
                i,
                c.query,
                assign_shelf(c.query),
                round(opportunity_score(c)),
                c.impressions,
                c.clicks,
                f"{c.ctr * 100:.1f}%",
                f"{c.avg_position:.1f}" if c.avg_position else "-",
                c.hits,
                " / ".join(sorted(c.sources)),
                " ".join(sorted(c.countries)[:5]),
                "必須" if needs_legal_review(c.query) else "",
            ])


def write_report(candidates: list[Candidate], path: Path, start: str, end: str, top: int) -> None:
    lines: list[str] = []
    lines.append(f"# 質問候補レポート（{start} 〜 {end}）\n")
    lines.append(f"- 抽出件数：**{len(candidates)} 件**")
    lines.append(f"- 生成日時：{dt.datetime.now():%Y-%m-%d %H:%M}")
    lines.append("- 出力元：自社データのみ（Search Console／サイト内検索／CS問い合わせ）\n")

    lines.append("## 棚ごとの内訳\n")
    per_shelf: dict[str, int] = defaultdict(int)
    for c in candidates:
        per_shelf[assign_shelf(c.query)] += 1
    lines.append("| 棚 | 件数 |")
    lines.append("|---|---|")
    for shelf in ["inbound", "fashion", "health", "trend", "要判断"]:
        lines.append(f"| {shelf} | {per_shelf.get(shelf, 0)} |")
    lines.append("")

    lines.append(f"## 優先度 上位{top}件\n")
    lines.append("| # | 質問候補 | 棚 | スコア | 表示 | 順位 | 情報源 | 法務 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(candidates[:top], start=1):
        pos = f"{c.avg_position:.1f}" if c.avg_position else "-"
        flag = "⚠️必須" if needs_legal_review(c.query) else ""
        lines.append(
            f"| {i} | {c.query} | {assign_shelf(c.query)} | {round(opportunity_score(c))} "
            f"| {c.impressions} | {pos} | {' / '.join(sorted(c.sources))} | {flag} |"
        )
    lines.append("")

    lines.append("## この表の読み方\n")
    lines.append(
        "- **優先スコア**：需要の大きさ（表示回数）と伸びしろ（順位の低さ）を掛け合わせた値。\n"
        "  「読者が求めているのに、VVがまだ十分に答えられていない」質問ほど高くなります。\n"
        "- **表示はあるのに順位が20位前後**のものが、いちばん取りに行く価値があります。\n"
        "- **情報源が2つ以上**あるものは、需要が確かなので優先してください。\n"
        "- **法務「必須」**は、薬機法・健康増進法・景表法に触れる可能性がある質問です。\n"
        "  執筆前に `docs/plans/sekai-no-shitsumonbako/02_legal_guard.md` を必ず確認してください。\n"
    )
    lines.append("## 次にやること\n")
    lines.append(
        "1. 上位から、棚が偏らないように選ぶ（fashion → health → trend の順で回す）\n"
        "2. 質問文を、編集部の言葉で読みやすく書き直す\n"
        "3. 出典（一次情報）を2件以上確保する\n"
        "4. `03_editorial_workflow.md` の公開前チェックリストを通す\n"
    )

    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# デモ用データ
# ---------------------------------------------------------------------------


def demo_rows() -> list[dict]:
    """認証なしで動作を確認するための擬似データ"""
    samples = [
        ("化粧水 重ね付け 意味 あるの", 4200, 38, 18.4),
        ("日焼け止め 室内 必要", 3800, 21, 22.1),
        ("洗顔 1日 何回 が いい", 2900, 15, 26.7),
        ("水 1日 2リットル 根拠", 5100, 44, 19.2),
        ("賞味期限 消費期限 違い", 9800, 310, 8.4),
        ("寝る前 スマホ 影響 本当", 2600, 12, 31.5),
        ("野菜 加熱 栄養 なくなる の", 3300, 27, 24.9),
        ("化粧品 冷蔵庫 保存 いい の", 1900, 9, 28.3),
        ("スキンケア 順番 決まり ある", 6400, 190, 6.1),
        ("無添加 意味 安全 なの", 2200, 11, 33.8),
        ("コーヒー 1日 何杯 まで", 7300, 250, 5.2),
        ("オリーブオイル 加熱 だめ なぜ", 1500, 8, 29.4),
        ("毛玉 できる 理由", 1700, 14, 21.7),
        ("湯船 シャワー 違い", 2100, 19, 20.3),
        ("発酵食品 毎日 いい の", 1800, 10, 27.6),
        ("VALUE VILLAGE 送料", 12000, 3100, 1.2),  # 質問ではないので除外される
        ("ヴァリューヴィレッジ 店舗", 8000, 2400, 1.1),  # 同上
    ]
    # 訪日外国人からの英語クエリ（国コード付き）
    inbound = [
        ("do i need to bring toiletries to japan", 2400, 4, 41.2, "usa"),
        ("japanese sunscreen for sensitive skin", 5600, 31, 27.8, "usa"),
        ("is tax free shopping worth it in japan", 4100, 12, 35.4, "gbr"),
        ("what to buy at japanese drugstore", 8900, 60, 24.1, "usa"),
        ("can i drink tap water in japan", 6200, 18, 33.6, "aus"),
        ("how much cash should i bring to japan", 7400, 22, 29.9, "can"),
        ("japanese skincare routine order", 3300, 15, 31.0, "sgp"),
        ("best souvenirs from japan food", 2800, 9, 38.5, "twn"),
    ]
    rows = [
        {"keys": [q, "jpn"], "impressions": imp, "clicks": clicks, "position": pos}
        for q, imp, clicks, pos in samples
    ]
    rows += [
        {"keys": [q, country], "impressions": imp, "clicks": clicks, "position": pos}
        for q, imp, clicks, pos, country in inbound
    ]
    return rows


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------


def load_config(path: Path) -> dict:
    if not path.exists():
        print(
            f"エラー: 設定ファイル {path} が見つかりません。\n"
            "        config.example.json をコピーして config.json を作ってください。",
            file=sys.stderr,
        )
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="自社データから質問候補を抽出する（VVメディア連載用）"
    )
    parser.add_argument("--config", default="config.json", help="設定ファイル（既定: config.json）")
    parser.add_argument("--days", type=int, default=90, help="何日ぶんを対象にするか（既定: 90）")
    parser.add_argument("--limit", type=int, default=300, help="CSVに出す最大件数（既定: 300）")
    parser.add_argument("--top", type=int, default=30, help="レポートに出す件数（既定: 30）")
    parser.add_argument("--outdir", default="output", help="出力先フォルダ（既定: output）")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="認証なしで、サンプルデータを使って動作確認する",
    )
    parser.add_argument(
        "--inbound",
        action="store_true",
        help="訪日外国人モード。日本以外の国からの検索だけを対象にする",
    )
    parser.add_argument(
        "--country",
        default="",
        help="特定の国だけを対象にする（例: usa,gbr,aus）。国コードはISO3文字",
    )
    args = parser.parse_args()

    only_countries: set[str] | None = None
    exclude_countries: set[str] | None = None
    if args.country:
        only_countries = {c.strip().lower() for c in args.country.split(",") if c.strip()}
    elif args.inbound:
        exclude_countries = {"jpn"}

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    today = dt.date.today()
    # Search Console のデータは反映まで2〜3日かかるため、3日前を終了日にする
    end_date = today - dt.timedelta(days=3)
    start_date = end_date - dt.timedelta(days=args.days)
    start, end = start_date.isoformat(), end_date.isoformat()

    if args.demo:
        print("=== デモモード（サンプルデータを使用します）===")
        config: dict = {}
        gsc_rows = demo_rows()
        csv_items = [
            ("化粧水 重ね付け 何回", "サイト内検索"),
            ("日焼け止め 家の中 でも 必要ですか", "CS問い合わせ"),
            ("賞味期限 切れた 大丈夫", "サイト内検索"),
            ("スキンケア 順番 教えて", "CS問い合わせ"),
            ("スキンケア 順番 どっち が 先", "サイト内検索"),
        ]
        min_impressions = 0
    else:
        config = load_config(Path(args.config))
        min_impressions = int(config.get("min_impressions", 10))
        if args.inbound or args.country:
            # 国で絞り込むには、Search Console に国ディメンションを要求する必要がある
            config["include_country"] = True

        print(f"Search Console からデータを取得します（{start} 〜 {end}）")
        gsc_rows = fetch_search_console(config, start, end)

        csv_items = []
        site_search = config.get("site_search_csv")
        if site_search:
            items = load_csv_source(
                Path(site_search),
                config.get("site_search_column", "query"),
                "サイト内検索",
            )
            print(f"  サイト内検索ログ: {len(items)} 件")
            csv_items += items

        support_log = config.get("support_csv")
        if support_log:
            items = load_csv_source(
                Path(support_log),
                config.get("support_column", "body"),
                "CS問い合わせ",
            )
            print(f"  CS問い合わせログ: {len(items)} 件")
            csv_items += items

    candidates = build_candidates(
        gsc_rows, csv_items, min_impressions,
        exclude_countries=exclude_countries,
        only_countries=only_countries,
    )

    stamp = today.isoformat()
    suffix = "_inbound" if (args.inbound or args.country) else ""
    csv_path = outdir / f"questions_{stamp}{suffix}.csv"
    report_path = outdir / f"report_{stamp}{suffix}.md"

    if args.inbound:
        print("=== 訪日外国人モード（日本以外の国からの検索のみ）===")
    elif args.country:
        print(f"=== 国を限定（{args.country}）===")

    write_csv(candidates, csv_path, args.limit)
    write_report(candidates, report_path, start, end, args.top)

    print()
    print(f"完了しました。質問候補 {len(candidates)} 件を抽出しました。")
    print(f"  一覧（Excelで開けます）: {csv_path}")
    print(f"  サマリー             : {report_path}")
    if candidates:
        print()
        print("上位5件:")
        for i, c in enumerate(candidates[:5], start=1):
            print(f"  {i}. {c.query}  [{assign_shelf(c.query)}] score={round(opportunity_score(c))}")


if __name__ == "__main__":
    main()
