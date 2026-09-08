#!/usr/bin/env python3
"""
rank.py — 生成した質問候補から「先に書くべき100件」を選ぶ

選定の考え方:
  1) フレームの質      … 記事にしたとき中身が出るフレームを高く
  2) 話題の需要        … 検索・AI検索で繰り返し問われる話題を高く
  3) 法務リスク        … 薬機法等のレビューが要るものは後ろへ（除外はしない）
  4) 棚のバランス      … 5カテゴリーから均等に取り、偏りを防ぐ

使い方: python rank.py            上位100件
        python rank.py --n 200    上位200件
"""
import argparse, csv, unicodedata
from pathlib import Path

# フレームの質（記事にしたとき中身が出るか）
FRAME_SCORE = {
    "どの順番でやればいいの": 3.2, "よくある誤解は": 3.0, "なぜ起こるの": 3.0,
    "なぜ必要なの": 2.9, "目安はどれくらい": 2.8, "何を見ればいいの": 2.7,
    "正しい使い方は": 2.7, "どう見分ければいい": 2.6, "人によって違うの": 2.5,
    "気になるときは": 2.5, "本当に意味があるの": 2.4, "やりすぎるとどうなる": 2.4,
    "どう保管すれば": 2.3, "決まりはあるの": 2.3, "何が原因で変わる": 2.2,
    "季節で変えたほうが": 2.2, "いつやるのがいいの": 2.1, "放っておいても": 2.1,
    "やめるとどうなるの": 2.0, "どこまでやればいいの": 1.9, "毎日やったほうがいいの": 1.7,
    "What do people get wrong": 3.1, "Why are things different": 3.0,
    "What surprises visitors": 2.9, "What is the etiquette": 2.7,
    "What do people in Japan actually do": 2.6, "practical way to handle": 2.5,
    "How do I deal with": 2.4, "worth knowing about": 2.3,
    "Do I need to think about": 2.2, "Is {t} something": 2.1,
    "What should I know": 2.0, "What has changed": 1.6,
}

# 需要が大きい話題（検索・AI検索で繰り返し問われるもの）
HIGH_DEMAND = [
    "スキンケアの順番","化粧水","日焼け止め","洗顔の回数","クレンジング","毛穴ケア",
    "化粧品の使用期限","化粧品の保管","肌質の見分け方","乾燥肌のケア","敏感肌のケア",
    "衣類の毛玉","洗濯表示の読み方","部屋干しの工夫","ニットの洗濯","革靴の手入れ",
    "睡眠時間","寝る前のスマホ","朝の光","体内時計","昼寝","枕の高さ","寝室の温度",
    "水分補給","カフェイン","入浴の温度","湯船とシャワー","肩こり","目の疲れ","むくみ",
    "冷え","梅雨の不調","夏バテ","デスクワークの姿勢","サプリメントの選び方",
    "賞味期限","消費期限","野菜の保存","冷凍のコツ","解凍のコツ","作り置き","食品ロス",
    "だしの取り方","米の保存","パンの保存","卵の保存","冷蔵庫の使い方","電子レンジ活用",
    "包丁の研ぎ方","フライパンの手入れ","コーヒーの淹れ方","旬の食材","郷土料理",
    "drugstores","tax-free shopping","sunscreen labels","SPF and PA","cosmetics labels",
    "expiry dates on cosmetics","skincare product names","bringing food home",
    "customs on the way home","tap water","rubbish bins","sorting rubbish",
    "convenience stores","allergy labelling","cash and cards","packing for summer",
    "humidity","onsen etiquette","tattoos and bathing","100-yen shops","souvenir choices",
    "taking shoes off indoors","storage in narrow spaces","refill packs","furoshiki",
    "tenugui","single-purpose kitchen tools","the rainy season","mould prevention",
    "cleaning order","waste separation","seasonal food","dashi","the concept of shun",
    "repair over replace","earthquake preparation","indoor drying",
]

CATS = ["fashion", "health", "trend", "inbound", "wisdom"]


def norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).lower()


def score(row: dict) -> float:
    q, topic = row["質問候補"], row["話題"]
    s = 1.0
    for key, val in FRAME_SCORE.items():
        if norm(key) in norm(q):
            s = max(s, val)
    if any(norm(h) == norm(topic) for h in HIGH_DEMAND):
        s += 3.0
    if row["法務チェック"]:
        s -= 1.0            # 除外はしない。レビュー工数のぶんだけ後ろへ
    if row["要注意"]:
        s -= 0.4
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--outdir", default="output")
    args = ap.parse_args()
    out = Path(args.outdir)

    per_cat = {}
    for cat in CATS:
        rows = list(csv.DictReader((out / f"questions_{cat}.csv").open(encoding="utf-8-sig")))
        for r in rows:
            r["score"] = round(score(r), 2)
        per_cat[cat] = sorted(rows, key=lambda r: -r["score"])

    # 棚が偏らないようカテゴリーを順番に取り、
    # 同じ言い回しばかりにならないようフレームごとに上限をかける
    def frame_of(row: dict) -> str:
        return norm(row["質問候補"]).replace(norm(row["話題"]), "{t}")

    cap = max(2, args.n // (len(CATS) * 10))  # 1フレームあたりの上限
    used, picked, idx = {}, [], {c: 0 for c in CATS}

    while len(picked) < args.n:
        added = False
        for cat in CATS:
            rows = per_cat[cat]
            while idx[cat] < len(rows):
                r = rows[idx[cat]]
                idx[cat] += 1
                f = frame_of(r)
                if used.get((cat, f), 0) >= cap:
                    continue
                used[(cat, f)] = used.get((cat, f), 0) + 1
                picked.append((cat, r))
                added = True
                break
            if len(picked) >= args.n:
                break
        if not added:
            break

    # 上限で弾かれて件数が足りない場合は、上限をゆるめて埋める
    if len(picked) < args.n:
        chosen = {id(r) for _, r in picked}
        for i in range(max(len(v) for v in per_cat.values())):
            for cat in CATS:
                rows = per_cat[cat]
                if i < len(rows) and id(rows[i]) not in chosen and len(picked) < args.n:
                    picked.append((cat, rows[i]))
                    chosen.add(id(rows[i]))
            if len(picked) >= args.n:
                break

    path = out / f"priority_top{args.n}.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["優先順位","質問候補","話題","棚","言語","優先スコア",
                    "法務チェック","要注意","3ソース確認日","担当","公開日"])
        for n, (cat, r) in enumerate(picked, 1):
            w.writerow([n, r["質問候補"], r["話題"], r["棚"], r["言語"], r["score"],
                        r["法務チェック"], r["要注意"], "", "", ""])

    print(f"上位{len(picked)}件を選定 → {path}\n")
    print(f"{'#':>3} {'棚':<9}{'ス':>5}  質問候補")
    print("-" * 76)
    for n, (cat, r) in enumerate(picked[:20], 1):
        q = r["質問候補"][:44]
        print(f"{n:>3} {cat:<9}{r['score']:>5}  {q}")
    print("-" * 76)
    from collections import Counter
    c = Counter(cat for cat, _ in picked)
    print("棚の内訳: " + " / ".join(f"{k} {v}件" for k, v in c.items()))
    legal = sum(1 for _, r in picked if r["法務チェック"])
    print(f"法務チェック必須: {legal}件（{legal*100//len(picked)}%）")


if __name__ == "__main__":
    main()
