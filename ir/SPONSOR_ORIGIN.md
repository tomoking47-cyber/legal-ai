# 6法人はSPAC時代から存在したのか ─ 株式の出所の調査

## 0. 調査の限界（先に明記する）

**SEC EDGAR（sec.gov）は本セッションのネットワーク制限により直接アクセスできない。**
以下のうち、EDGAR の原文で確認した事項は**ひとつもない**。
Web検索の結果は二次情報であり、**弁護士による EDGAR 原文の確認が必須**である。

**ただし、当社が保有する Transfer Journal（Continental Stock Transfer 作成）が、
EDGAR を見るまでもなく答えの大部分を示している。**

---

## 1. Transfer Journal が示す事実 ─ 2026-07-24（上場当日）

**取引種別が2つに分かれている。この区別が決定的である。**

### A群：「制限解除」＝ 上場前から株式を保有していた

| 法人 | 数量 | 形態 |
|---|---:|---|
| RELATIVITY II ACQUISITION SPONSOR LLC | 1,435,000 | RESTRICTED BOOK → DRS |
| MGMTT LLC | 1,289,000 | RESTRICTED BOOK → DRS |
| RELATIVITY ACQUISITION SPONSOR LLC | 131,381 | RESTRICTED BOOK → DRS |
| **計** | **2,855,381** | |

**→ 制限付（RESTRICTED BOOK）の残高が既に存在した。
   すなわち SPAC（Purchaser）の証券保有者であり、1対1で Pubco 株に転換された。
   この3社は SPAC 時代から存在した。**

### B群：「新規発行（ISSUE）」＝ 上場当日に初めて発行された

| 受領者 | 数量 | 形態 |
|---|---:|---|
| CHARDAN CAPITAL MARKETS LLC | 1,615,385 | DRS | ← Fee Waiver Agreement（BCA Recital H）で説明がつく |
| **BRACS CAPITAL SPONSOR LLC** | **1,003,175** | **DRS（制限なし）** | ← **説明がつかない** |
| **PARAMOUNT MERGER CORP SPONSOR LLC** | **1,003,175** | **DRS（制限なし）** | ← **説明がつかない** |
| EVERISE CONCEPTS PLT | 450,000 | DRS | |
| RELATIVITY ACQUISITION SPONSOR LLC | 500,001 | DRS | |
| HITHOS II LLC | 150,000 | DRS | |
| MGMTT LLC | 3,749 | DRS | |
| CEDE & CO | 6,870 | BOOK ENTRY | |
| **計** | **4,732,356** | |

**→ BRACS と PARAMOUNT には、上場前の制限付残高が存在しない。
   SPAC の証券保有者ではなかった。上場当日に、新株を、しかも制限なしで受け取っている。**

---

## 2. これが最大の問いになる

**BRACS Capital Sponsor LLC と Paramount Merger Corp Sponsor LLC は、
上場当日に 1,003,175 株ずつ ── 合計 2,006,350 株 ── を新規発行で受領し、
4〜5日後（7/28・7/29）に全量を DTC へ移し、8/24 の NOBO リストから消えている。**

確認すべき事項：

1. **誰が発行を承認したのか。**
2. **対価は何か。** 両社は SPAC の証券保有者ではない。
3. **F-4 の登録範囲に含まれていたか。**
   含まれていなければ、**Securities Act Section 5 の問題**となる。
4. **なぜ制限付（RESTRICTED BOOK）ではなく DRS（制限なし）で発行されたのか。**
   アフィリエイトへの新株発行が制限なしで行われるのは通常ではない。
5. **なぜ両社とも 1,003,175 株で完全に同額なのか。**

### ⚠️ 重要 ── この論点は当社にも向く

**発行したのは当社（Pubco）である。** スポンサー側だけの問題ではない。

- 有効な登録・免除がないまま 2,006,350 株を発行していれば、**発行体である当社の問題**
- **F-4 は当社が署名した登録届出書**

**したがって、この論点は外部に出す前に、必ず社内と米国証券弁護士で先に固めること。
順序を誤れば、相手を撃つはずの弾が当社に当たる。**

---

## 3. Web検索で得られた情報（すべて二次情報・要検証）

2023-02-27 付 Relativity Acquisition Corp の Form 8-K に関する報道によれば、
Class B から Class A への転換 3,593,749 株を受領したのは次の4者とされる：

- Relativity Acquisition Sponsor LLC（転換後 3,033,905 株 + Class B 1株）
- A.G.P./Alliance Global Partners
- George Syllantavos
- Anastasios Chrysostomidis

その後、Sponsor は **533,525 株を「certain members of the Sponsor」へ移転**したとされる。

**この記載に BRACS・Paramount・MGMTT・Hithos II・Relativity II は登場しない。**
また、これら5社の名称を対象とした Web 検索では、Relativity 関連の SEC 提出書類との
結びつきを示す結果は得られなかった。

**※ Web 検索は EDGAR 全文検索ではない。「出てこなかった」ことは「存在しない」ことの
証明ではない。弁護士による EDGAR 全文検索が必要。**

（参考：登録株主名簿に GEORGIOS SYLLANTAVOS 176,094 株が存在し、上記の記載と整合する。）

---

## 4. 弁護士への依頼事項（EDGAR 原文確認）

対象：Relativity Acquisition Corp（CIK 1860484）および Instinct Bio Technical
Company Holdings Inc.（CIK 0002072188）

1. **IPO 時の S-1 / S-1A の "Principal Stockholders" セクション**
   → 6法人のうち、どれが記載されているか
2. **2023-02-27 付 8-K**（Class B → Class A 転換）
   → 533,525 株の移転先である "certain members of the Sponsor" の氏名・名称
3. **延長（extension）関連の 8-K・non-redemption agreement**
   → BRACS・Paramount への株式付与を説明する契約があるか
4. **F-4 の登録株式の内訳**
   → BRACS・Paramount の 1,003,175 株ずつが登録範囲に含まれるか
5. **EDGAR 全文検索**（efts.sec.gov）で以下の名称を検索
   - "Relativity II Acquisition Sponsor"
   - "BRACS Capital Sponsor"
   - "Paramount Merger Corp Sponsor"
   - "MGMTT"
   - "Hithos II"

---

## 5. 当社側で直ちに確認できるもの（EDGAR不要）

1. **クロージング時の資本構成表（cap table）** ── BRACS・Paramount の欄に何と書いてあるか
2. **新株発行の承認記録** ── 取締役会決議、発行指示書
3. **Continental への発行指示書** ── 誰の署名で 2,006,350 株の発行を指示したか
4. **Form 20-F Item 7.A の数値の出所** ── 6社分を合算した数字を誰が提供したか
