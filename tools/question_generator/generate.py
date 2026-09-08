#!/usr/bin/env python3
"""
generate.py — カテゴリー別に質問候補を大量生成する

話題リスト × 質問フレーム の総当たりで候補を作り、カテゴリーごとにCSVに出す。
出てくるのは「質問候補」であって、そのまま公開できる質問文ではない。
編集部が選び、書き直し、3ソース原則を通したうえで記事にすること。

使い方:
    python generate.py              各カテゴリー500件
    python generate.py --n 1000     各カテゴリー1000件
"""
import argparse, csv, unicodedata
from pathlib import Path
from topics import CATEGORIES, SEQUENCE_TOPICS, SEQ_FRAME, topic_type

# 薬機法・健康増進法・景表法のチェックが要る話題
LEGAL_KEYWORDS = [
    "化粧水","乳液","美容液","クリーム","日焼け止め","洗顔","毛穴","角質","肌","肌荒れ",
    "シャンプー","頭皮","制汗","入浴剤","サプリ","ビタミン","鉄分","たんぱく質","腸内",
    "発酵","睡眠","体温","血圧","健康診断","医療","塩分","糖分","脂質","カフェイン",
    "アルコール","花粉","紫外線","冷え","むくみ","肩こり","疲れ","不調","体調","バテ",
    "medicine","pharmacy","allergy","sunscreen","spf","skincare","cosmetics","ingredient",
    "vegetarian","halal","first aid","supplement","health",
]

# 特に慎重に扱う話題（制度・安全）
CAUTION_KEYWORDS = [
    "賞味期限","消費期限","食品ロス","保存","冷凍","解凍","包丁","揚げ物","カビ",
    "customs","tax","medicine","allergy","emergency","earthquake","waste","rubbish",
    "cleaning","mould","insect",
]


def flag(text: str, words: list[str]) -> bool:
    t = unicodedata.normalize("NFKC", text).lower()
    return any(w.lower() in t for w in words)


def build(cat: dict, n: int) -> list[dict]:
    """フレームを外側で回して話題の偏りを防ぐ。話題の種類に合わないフレームは使わない。"""
    seen, rows = set(), []
    frames = list(cat["frames"])
    if cat["lang"] == "ja":
        frames.insert(0, SEQ_FRAME)   # 順番フレームは対象話題が少ないので先に

    for frame, allowed in frames:
        for topic in cat["topics"]:
            if cat["lang"] == "ja":
                ttype = topic_type(topic)
                if allowed and ttype not in allowed:
                    continue
                if frame is SEQ_FRAME[0]:
                    if topic not in SEQUENCE_TOPICS or "順番" in topic:
                        continue
            q = frame.format(t=topic)
            key = unicodedata.normalize("NFKC", q).lower()
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "質問候補": q,
                "話題": topic,
                "棚": cat["shelf"],
                "言語": cat["lang"],
                "法務チェック": "必須" if flag(topic, LEGAL_KEYWORDS) else "",
                "要注意": "制度・安全" if flag(topic, CAUTION_KEYWORDS) else "",
                "状態": "未確認",
            })
            if len(rows) >= n:
                return rows
    return rows


HEADER = ["No","質問候補","話題","棚","言語","法務チェック","要注意","状態","3ソース確認日","担当"]


def write(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["質問候補"], r["話題"], r["棚"], r["言語"],
                        r["法務チェック"], r["要注意"], r["状態"], "", ""])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500, help="各カテゴリーの件数（既定500）")
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()

    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    total, all_rows = 0, []

    print(f"{'カテゴリー':<10}{'棚':<10}{'件数':>6}{'法務必須':>10}{'要注意':>8}")
    print("-" * 46)
    for key, cat in CATEGORIES.items():
        rows = build(cat, args.n)
        write(rows, out / f"questions_{key}.csv")
        legal = sum(1 for r in rows if r["法務チェック"])
        caution = sum(1 for r in rows if r["要注意"])
        print(f"{key:<10}{cat['shelf']:<10}{len(rows):>6}{legal:>10}{caution:>8}")
        total += len(rows); all_rows += rows

    write(all_rows, out / "questions_all.csv")
    print("-" * 46)
    print(f"{'合計':<20}{total:>6}")
    print(f"\n出力先: {out.resolve()}")


if __name__ == "__main__":
    main()
