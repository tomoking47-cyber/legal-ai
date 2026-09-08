#!/usr/bin/env python3
"""
scaffold.py — priority_top100.csv から記事ファイルを一括生成する

中身は空だが、以下が最初から正しく入った状態で作られる:
  ・タイトルと通し番号   ・棚とタグ   ・URLスラッグ
  ・棚に応じた定型の注記（17_standard_disclaimers.md の正本どおり）
  ・法務チェックの要否   ・公開前チェックリスト

執筆者は本文だけを書けばよく、注記や体裁で事故が起きない。
"""
import argparse, csv, re, unicodedata
from pathlib import Path

SERIES = {
    "fashion": ("世界の質問箱", "/questions/", "スキンケア"),
    "health":  ("世界の質問箱", "/questions/", "ウェルネス"),
    "trend":   ("世界の質問箱", "/questions/", "フード"),
    "inbound": ("Japan Questions", "/en/questions/", "Inbound"),
    "wisdom":  ("Japanese Everyday Wisdom", "/en/wisdom/", "Wisdom"),
}

BASE_JA = """### この記事について

本記事で紹介しているのは、**日本の生活者の間で受け継がれてきた工夫やアイデア**です。
公的機関による推奨や、専門家による指導ではありません。

内容は一般的な情報として提供しているもので、効果や結果には個人差があり、条件や環境によって異なります。

**実際に取り入れるかどうかは、ご自身の状況に応じてご自身の判断で決めてください。**
本記事の内容を実行したことにより生じた損害・不具合・怪我について、当社は責任を負いかねます。"""

BASE_EN = """### About this article

What we share here are **ideas and everyday practices passed down among people living in Japan.**
They are not official recommendations, and they are not professional instruction.

This is general information. Results vary from person to person and depend on your own conditions and surroundings.

**Please decide for yourself, using your own judgement, whether any of this suits your situation.**
We cannot accept responsibility for any damage, loss or injury arising from following this article."""

EXTRA = {
    "fashion": "\n\n化粧品は疾病の治療・予防を目的とするものではありません。\n肌に異常を感じた際は使用を中止し、皮膚科専門医にご相談ください。",
    "health":  "\n\n本記事は、特定の症状の診断・治療・予防を目的としたものではありません。\n体調に不安がある場合は、自己判断せず医療機関にご相談ください。",
    "trend":   "\n\n食材によっては十分な加熱が必要です。生食は、生食用として流通しているものに限ってください。\nアレルギーのある方は、原材料をご確認ください。",
    "inbound": "\n\nRules and procedures can change. Please confirm the latest official information before you act.",
    "wisdom":  "\n\nAlways follow the instructions on any product you use, and never mix cleaning products.\nIf you rent your home, check with your landlord before making any changes.",
}

ROMA = {
    "クレンジング":"cleansing","昼寝":"napping","作り置き":"batch-cooking","スキンケアの順番":"skincare-order",
    "枕の高さ":"pillow-height","冷蔵庫の使い方":"using-the-fridge","化粧品の保管":"storing-cosmetics",
    "寝室の温度":"bedroom-temperature","だしの取り方":"making-dashi","化粧品の使用期限":"cosmetics-expiry",
    "寝る前のスマホ":"phone-before-bed","フライパンの手入れ":"pan-care","日焼け止め":"sunscreen",
    "洗顔の回数":"how-often-to-wash-face","水分補給":"hydration","賞味期限":"best-before",
    "消費期限":"use-by","野菜の保存":"storing-vegetables","冷凍のコツ":"freezing-tips",
    "解凍のコツ":"defrosting-tips","睡眠時間":"sleep-length","朝の光":"morning-light",
    "体内時計":"body-clock","入浴の温度":"bath-temperature","湯船とシャワー":"bath-vs-shower",
    "肩こり":"stiff-shoulders","目の疲れ":"eye-strain","むくみ":"swelling","冷え":"feeling-cold",
    "衣類の毛玉":"pilling","洗濯表示の読み方":"care-labels","部屋干しの工夫":"indoor-drying",
    "毛穴ケア":"pore-care","乾燥肌のケア":"dry-skin","敏感肌のケア":"sensitive-skin",
    "カフェイン":"caffeine","米の保存":"storing-rice","卵の保存":"storing-eggs",
    "包丁の研ぎ方":"sharpening-knives","コーヒーの淹れ方":"brewing-coffee","旬の食材":"seasonal-food",
    "電子レンジ活用":"microwave-tips","食品ロス":"food-waste","梅雨の不調":"rainy-season",
    "夏バテ":"summer-fatigue","サプリメントの選び方":"choosing-supplements","間食":"snacking",
}


def slug(topic: str, n: int) -> str:
    if topic in ROMA:
        return ROMA[topic]
    s = unicodedata.normalize("NFKC", topic).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s if s else f"q{n:03d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="output/priority_top100.csv")
    ap.add_argument("--outdir", default="../../docs/plans/sekai-no-shitsumonbako/articles")
    args = ap.parse_args()

    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(Path(args.csv).open(encoding="utf-8-sig")))
    made = 0

    for r in rows:
        n = int(r["優先順位"]); shelf = r["棚"]; topic = r["話題"]
        series, url, tag = SERIES[shelf]
        is_ja = r["言語"] == "ja"
        legal = r["法務チェック"] == "必須"
        sl = slug(topic, n)
        path = out / f"{n:03d}_{shelf}_{sl}.md"
        if path.exists():
            continue

        title = f"Q. {r['質問候補']}｜{series} #{n}" if is_ja else f"Q. {r['質問候補']}｜{series} #{n}"
        notice = (BASE_JA if is_ja else BASE_EN) + EXTRA[shelf]

        body = f"""# {title}

- 棚：`{shelf}` ／ タグ：`{series}` `{tag}`
- URL：`{url}{sl}`
- 優先順位：{n} ／ 優先スコア：{r['優先スコア']}
- ステータス：**未執筆**
- 法務チェック：{"**必須（薬機法・景表法）**" if legal else "不要（ただし表現は要確認）"}

---

<!-- ① 冒頭：世界で議論されている文脈を1〜2文 -->

## A. <!-- ② 結論を1文で言い切る。40〜80字 -->

<!-- 結論の補足を2〜3文 -->

## <!-- ③ 見出し1 -->

<!-- 理由・背景。出典付き -->

## <!-- ③ 見出し2 -->

## VVの考え方

<!-- ④ 該当時のみ。3本に1本以下。書かない場合はこの節ごと削除する -->

---

### 出典

<!-- 一次情報を2件以上。機関名『資料名』（公表年）URL の形式 -->
- 
- 

{notice}

---

## 公開前チェック（執筆者が記入）

- [ ] 3ソース原則を確認した（確認日：　　／確認者：　　）
- [ ] **出典URLを実際に開き、記載内容と一致することを確認した**
- [ ] 「ご自身の判断」の一文が入っている
- [ ] 言い切り表現（数値の断定・治癒の断定・優良誤認）がない
- [ ] 他社・他製品の固有名詞での比較がない
{"- [ ] **法務レビューを通した（担当：　　／日付：　　）**" if legal else ""}
- [ ] `python translation_checker.py --ja この記事.md` で重大0件
"""
        path.write_text(body, encoding="utf-8")
        made += 1

    print(f"記事ファイルを {made} 本作成しました → {out.resolve()}")
    from collections import Counter
    c = Counter(r["棚"] for r in rows)
    print("棚の内訳: " + " / ".join(f"{k} {v}本" for k, v in c.items()))


if __name__ == "__main__":
    main()
