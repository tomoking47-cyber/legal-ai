from dotenv import load_dotenv
import json
import os
from datetime import datetime

load_dotenv()

DATA_FILE = "collected_persons.json"
CALC_FILE = "calculated_persons.json"

STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
STEM_ELEMENT = ["木","木","火","火","土","土","金","金","水","水"]
STEM_YIN_YANG = ["陽","陰","陽","陰","陽","陰","陽","陰","陽","陰"]
BRANCH_ELEMENT = ["水","土","木","木","土","火","火","土","金","金","土","水"]

def get_stem_branch(year, month, day):
    """命式（年柱・月柱・日柱）を計算する"""
    year_offset = year - 1900
    stem_idx = (6 + year_offset) % 10
    branch_idx = year_offset % 12
    month_stem = (stem_idx * 2 + month) % 10
    month_branch = (month + 1) % 12
    day_base = int((year - 1900) * 365.25) + day
    day_stem = (day_base + 10) % 10
    day_branch = (day_base + 10) % 12
    return {
        "year_stem": STEMS[stem_idx],
        "year_branch": BRANCHES[branch_idx],
        "month_stem": STEMS[month_stem % 10],
        "month_branch": BRANCHES[month_branch],
        "day_stem": STEMS[day_stem % 10],
        "day_branch": BRANCHES[day_branch % 12],
    }

def get_element_balance(sb):
    """五行バランスを計算する"""
    balance = {"木":0,"火":0,"土":0,"金":0,"水":0}
    for s in [sb["year_stem"], sb["month_stem"], sb["day_stem"]]:
        idx = STEMS.index(s)
        balance[STEM_ELEMENT[idx]] += 1
    for b in [sb["year_branch"], sb["month_branch"], sb["day_branch"]]:
        idx = BRANCHES.index(b)
        balance[BRANCH_ELEMENT[idx]] += 1
    return balance

def extract_birth_date(person):
    """Wikipedia情報から生年月日を抽出する"""
    summary = person.get("wikipedia_summary", "")
    import re
    # 西暦パターン
    patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, summary)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            if 1800 <= year <= 2010:
                return year, month, day
    return None, None, None

def calculate_all():
    """収集済み人物全員の命式を計算する"""
    print(f"\n計算開始：{datetime.now()}")

    if not os.path.exists(DATA_FILE):
        print("収集データがありません。先にエージェント1号を実行してください。")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        persons = json.load(f)

    calculated = []
    success = 0
    skip = 0

    for person in persons:
        name = person.get("name", "不明")
        year, month, day = extract_birth_date(person)

        if not year:
            skip += 1
            continue

        try:
            sb = get_stem_branch(year, month, day)
            balance = get_element_balance(sb)
            dominant = max(balance, key=balance.get)
            weak = min(balance, key=balance.get)

            result = {
                "name": name,
                "category": person.get("category", ""),
                "birth_year": year,
                "birth_month": month,
                "birth_day": day,
                "stem_branch": sb,
                "element_balance": balance,
                "dominant_element": dominant,
                "weak_element": weak,
                "wikipedia_summary": person.get("wikipedia_summary", ""),
                "calculated_at": datetime.now().isoformat(),
            }
            calculated.append(result)
            success += 1
            print(f"✅ {name}：{sb['year_stem']}{sb['year_branch']}年 五行主：{dominant}")

        except Exception as e:
            print(f"⚠️ {name}：エラー {e}")
            skip += 1

    with open(CALC_FILE, 'w', encoding='utf-8') as f:
        json.dump(calculated, f, ensure_ascii=False, indent=2)

    print(f"\n完了！計算成功：{success}人 スキップ：{skip}人")
    print(f"calculated_persons.jsonに保存しました")

if __name__ == "__main__":
    print("エージェント2号：計算エージェント起動！")
    calculate_all()
    