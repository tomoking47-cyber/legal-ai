#!/usr/bin/env python3
"""
translation_checker.py — AI翻訳した英語記事を、機械的に検査する

AIに何度翻訳させても検出できない種類の間違いがある。

  ・薬機法や広告規制に触れる英語表現が混ざる
  ・アレルゲン（そば・小麦など）の記載が英語版から落ちる
  ・分量・温度・時間などの数字が原文とずれる
  ・法令名や「消費期限／賞味期限」の訳がぶれる

これらは「意味は通っているが、公開してはいけない」状態なので、
AIに読ませても問題として指摘されないことがある。だから機械で検査する。

使い方:
    python translation_checker.py --ja 記事_日本語.md --en 記事_英語.md
    python translation_checker.py --en 記事_英語.md          （英語だけの記事）
    python translation_checker.py --demo                      （動作確認）
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

SEVERITY_ORDER = {"重大": 0, "警告": 1, "確認": 2}


@dataclass
class Finding:
    severity: str   # 重大 / 警告 / 確認
    category: str
    message: str
    detail: str = ""


# ---------------------------------------------------------------------------
# 用語集
# ---------------------------------------------------------------------------


def load_glossary(path: Path) -> dict[str, list[dict[str, str]]]:
    if not path.exists():
        print(f"エラー: 用語集 {path} が見つかりません。", file=sys.stderr)
        sys.exit(1)

    rows: dict[str, list[dict[str, str]]] = {
        "禁止": [], "禁止JA": [], "アレルゲン": [], "固定訳": [], "必須": [], "必須JA": [],
    }
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            kind = (row.get("区分") or "").strip()
            if kind in rows:
                rows[kind].append({
                    "ja": (row.get("日本語") or "").strip(),
                    "en": (row.get("英語") or "").strip(),
                    "note": (row.get("メモ") or "").strip(),
                })
    return rows


# ---------------------------------------------------------------------------
# 本文の準備
# ---------------------------------------------------------------------------


def strip_markdown_noise(text: str) -> str:
    """URL・コードブロック・編集部メモを検査対象から外す"""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    # 「編集部向けメモ」以降は社内向けなので検査しない
    text = re.split(r"##\s*【編集部向けメモ", text)[0]
    return text


def norm_en(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[\s　]+", " ", text)


NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")


def extract_numbers(text: str) -> list[str]:
    """数字を取り出す。見出しの連番などノイズは呼び出し側で許容する"""
    out = []
    for m in NUMBER_RE.finditer(text):
        value = m.group(0).replace(",", "")
        # 小数点以下の余分な0を落として比較しやすくする
        if "." in value:
            value = value.rstrip("0").rstrip(".")
        out.append(value)
    return out


# ---------------------------------------------------------------------------
# 各検査
# ---------------------------------------------------------------------------


def check_forbidden(en_text: str, glossary) -> list[Finding]:
    """公開してはいけない英語表現が混ざっていないか"""
    findings = []
    hay = norm_en(en_text)
    for row in glossary["禁止"]:
        term = norm_en(row["en"])
        if not term:
            continue
        # 単語境界で照合する（treats が treatstore に反応しないように）
        pattern = r"(?<![a-z])" + re.escape(term) + r"(?![a-z])"
        if re.search(pattern, hay):
            findings.append(Finding(
                severity="重大",
                category="禁止表現",
                message=f'英語版に「{row["en"]}」が含まれています',
                detail=row["note"],
            ))
    return findings


def check_forbidden_ja(ja_text: str, glossary) -> list[Finding]:
    """日本語版に、断定・優良誤認にあたる言い切り表現がないか"""
    findings = []
    hay = unicodedata.normalize("NFKC", ja_text)
    seen: set[str] = set()
    for row in glossary["禁止JA"]:
        term = unicodedata.normalize("NFKC", row["ja"])
        # 全角と半角は同じ語として扱うので、重複した指摘は出さない
        if term in seen:
            continue
        if term and term in hay:
            seen.add(term)
            findings.append(Finding(
                severity="重大",
                category="言い切り表現",
                message=f'日本語版に「{row["ja"]}」が含まれています',
                detail=row["note"],
            ))
    return findings


def check_required(text: str, rows: list[dict[str, str]], key: str, label: str) -> list[Finding]:
    """全記事に必須の記述（自己判断の免責など）が入っているか"""
    if not text.strip():
        return []
    hay = norm_en(text) if key == "en" else unicodedata.normalize("NFKC", text)
    findings = []
    for row in rows:
        needle = norm_en(row[key]) if key == "en" else unicodedata.normalize("NFKC", row[key])
        if needle and needle not in hay:
            findings.append(Finding(
                severity="重大",
                category="必須記述の欠落",
                message=f'{label}に「{row[key]}」に相当する記述がありません',
                detail=row["note"],
            ))
    return findings


def check_allergens(ja_text: str, en_text: str, glossary) -> list[Finding]:
    """日本語にあるアレルゲンが、英語版から落ちていないか"""
    findings = []
    en_hay = norm_en(en_text)
    seen: set[str] = set()
    for row in glossary["アレルゲン"]:
        if not row["ja"] or row["ja"] not in ja_text:
            continue
        term = norm_en(row["en"])
        if term in seen:
            continue
        if term and term not in en_hay:
            seen.add(term)
            findings.append(Finding(
                severity="重大",
                category="アレルゲン欠落",
                message=f'日本語版に「{row["ja"]}」があるのに、英語版に "{row["en"]}" がありません',
                detail="誤訳・記載漏れは健康被害に直結します。必ず人が確認してください。",
            ))
    return findings


def check_fixed_terms(ja_text: str, en_text: str, glossary) -> list[Finding]:
    """法令名や期限表示など、訳がぶれてはいけない語"""
    findings = []
    en_hay = norm_en(en_text)
    for row in glossary["固定訳"]:
        if not row["ja"] or row["ja"] not in ja_text:
            continue
        if norm_en(row["en"]) not in en_hay:
            findings.append(Finding(
                severity="警告",
                category="固定訳の不一致",
                message=f'日本語版の「{row["ja"]}」に対し、英語版に "{row["en"]}" がありません',
                detail=row["note"],
            ))
    return findings


def check_numbers(ja_text: str, en_text: str) -> list[Finding]:
    """分量・温度・時間などの数字が原文とずれていないか"""
    ja_nums = extract_numbers(ja_text)
    en_nums = extract_numbers(en_text)

    ja_set, en_set = set(ja_nums), set(en_nums)
    only_ja = sorted(ja_set - en_set, key=lambda v: -len(v))
    only_en = sorted(en_set - ja_set, key=lambda v: -len(v))

    findings = []
    if only_ja:
        findings.append(Finding(
            severity="確認",
            category="数字の不一致",
            message="日本語版にあって英語版にない数字があります",
            detail=", ".join(only_ja[:20]),
        ))
    if only_en:
        findings.append(Finding(
            severity="確認",
            category="数字の不一致",
            message="英語版にあって日本語版にない数字があります",
            detail=", ".join(only_en[:20]) + "（単位換算による追加なら問題ありません）",
        ))
    return findings


DISCLAIMER_HINTS = [
    "consult", "healthcare", "doctor", "professional",
    "vary from person to person", "general information",
]


def check_disclaimer(en_text: str, require: bool) -> list[Finding]:
    """健康・食品を扱う記事に、注記が入っているか"""
    if not require:
        return []
    hay = norm_en(en_text)
    if any(hint in hay for hint in DISCLAIMER_HINTS):
        return []
    return [Finding(
        severity="警告",
        category="注記の欠落",
        message="英語版に、注記（医療機関への相談・個人差）に相当する記述が見つかりません",
        detail="健康・食品を扱う記事では必須です。",
    )]


HEALTH_TOPIC_HINTS_JA = ["健康", "医療", "症状", "肌", "食べ", "食品", "栄養", "睡眠", "アレル", "摂取"]


def looks_health_related(ja_text: str, en_text: str) -> bool:
    if any(h in ja_text for h in HEALTH_TOPIC_HINTS_JA):
        return True
    hay = norm_en(en_text)
    return any(h in hay for h in ["skin", "health", "food", "eat", "drink", "sleep", "allergy", "nutrition"])


# ---------------------------------------------------------------------------
# 実行
# ---------------------------------------------------------------------------


def run_checks(ja_text: str, en_text: str, glossary) -> list[Finding]:
    findings: list[Finding] = []

    if ja_text:
        findings += check_forbidden_ja(ja_text, glossary)
        findings += check_required(ja_text, glossary["必須JA"], "ja", "日本語版")

    if en_text:
        findings += check_forbidden(en_text, glossary)
        findings += check_required(en_text, glossary["必須"], "en", "英語版")
        findings += check_disclaimer(en_text, looks_health_related(ja_text, en_text))

    if ja_text and en_text:
        findings += check_allergens(ja_text, en_text, glossary)
        findings += check_fixed_terms(ja_text, en_text, glossary)
        findings += check_numbers(ja_text, en_text)

    return sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 9))


MARKS = {"重大": "🛑", "警告": "⚠️ ", "確認": "🔎"}


def report(findings: list[Finding]) -> int:
    print()
    print("=" * 64)
    print("  翻訳チェック結果")
    print("=" * 64)

    if not findings:
        print()
        print("  ✅ 機械チェックで見つかった問題はありません。")
        print()
        print("  ただし、これは「文章として自然か」を見たものではありません。")
        print("  自然さの確認は、別途 逆翻訳（バックトランスレーション）で行ってください。")
        print()
        return 0

    counts = {"重大": 0, "警告": 0, "確認": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
        print()
        print(f"  {MARKS.get(f.severity, '')}[{f.severity}] {f.category}")
        print(f"     {f.message}")
        if f.detail:
            print(f"     → {f.detail}")

    print()
    print("-" * 64)
    print(f"  重大 {counts['重大']} 件 ／ 警告 {counts['警告']} 件 ／ 要確認 {counts['確認']} 件")
    if counts["重大"]:
        print()
        print("  🛑 重大が1件でもある記事は、公開しないでください。")
    print()
    return 1 if counts["重大"] else 0


DEMO_JA = """# おやき — 長野県の郷土料理

そば粉と小麦粉で作った皮に、野菜のあんを包みます。
生地は30分ほど休ませ、フライパンで5分焼いてください。
加熱してください。賞味期限は製造から3日です。
この方法なら100%失敗しません。肌荒れも治ります。
肌の調子が気になる方は医療機関にご相談ください。
"""

DEMO_EN = """# Oyaki — a local dish from Nagano

A dough of wheat flour is wrapped around a vegetable filling.
Rest the dough for 30 minutes and pan-fry for 15 minutes.
This traditional food treats fatigue and is 100% safe.
Best-before date is 3 days from production.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="AI翻訳した英語記事を機械的に検査する")
    parser.add_argument("--ja", help="日本語版のファイル")
    parser.add_argument("--en", help="英語版のファイル")
    parser.add_argument("--glossary", default="glossary.csv", help="用語集（既定: glossary.csv）")
    parser.add_argument("--demo", action="store_true", help="サンプルで動作確認する")
    args = parser.parse_args()

    glossary = load_glossary(Path(args.glossary))

    if args.demo:
        print("=== デモモード（わざと問題のある訳文を検査します）===")
        ja_text, en_text = DEMO_JA, DEMO_EN
    else:
        if not args.en and not args.ja:
            parser.error("--ja か --en の少なくとも一方を指定してください")

        def read(path_str: str) -> str:
            path = Path(path_str)
            if not path.exists():
                print(f"エラー: {path} が見つかりません。", file=sys.stderr)
                sys.exit(1)
            return strip_markdown_noise(path.read_text(encoding="utf-8"))

        ja_text = read(args.ja) if args.ja else ""
        en_text = read(args.en) if args.en else ""

        if not en_text:
            print("※ 日本語版のみを検査します（言い切り表現・必須記述）。")
        elif not ja_text:
            print("※ 英語版のみを検査します（アレルゲン照合と数字照合はできません）。")

    sys.exit(report(run_checks(ja_text, en_text, glossary)))


if __name__ == "__main__":
    main()
