# Lovable に貼り付けるプロンプト（コピペ用）

> 数値の `[ ]` 部分を確定値に置き換えてから貼ってください。

---

In the "04 — Capital Structure & Ownership" section, replace the
"Principal shareholders (greater than 5%)" card list with a comparison table
titled "Principal shareholders — change since listing".

Keep the existing design language exactly: warm off-white background,
serif headings, gold (#b8894a) accent for ownership percentages, uppercase
letter-spaced column labels, and the gold left-bordered SOURCE box.

The table has four columns:
1. Shareholder
2. "At listing / Jul 23, 2026" — shares and ownership %
3. "Current / [基準日]" — shares and ownership %
4. "Change" — shares and percentage-point delta

Rows (in this order):
- Tomoki Nagano: 10,425,365 (36.21%) -> [現在株数] ([現在%]) -> [増減]
- Relativity Acquisition Sponsor, LLC: 5,515,481 (19.15%) -> [現在株数] ([現在%]) -> [増減]
- Chardan Capital Markets LLC: 1,615,385 (5.61%) -> [現在株数] ([現在%]) -> [増減]

Formatting rules for the Change column:
- A decrease must render in bold red (#c0281f) with a leading "▲".
- An increase renders in green (#2f6d4f) with a leading "+".
- No change renders in muted gray as "±0".
- Any row with a decrease gets a very light red row background (#fdf3f2)
  and a 3px red left border on the first cell.

SOURCE box text:
"Form 20-F, Item 7.A (Major Shareholders) | As of July 23, 2026  →
 [直近の出典書類名] | As of [基準日]"
"Transcribed from SEC filings; not a forward-looking statement."

Add footnotes below the table:
1. "At listing" figures are as disclosed in Form 20-F, Item 7.A, as of July 23, 2026.
2. "Current" figures are as disclosed in [出典書類名・提出日].
3. Figures shown in red indicate a decrease, following standard accounting presentation.
4. Percentages are based on shares outstanding as of each respective date.

Do not add any commentary, opinion, or editorial language about any
shareholder. Present the figures only. Make the table horizontally
scrollable on mobile.

---

## 参考実装
`ir/shareholding-table.html` をブラウザで開くと、上記の完成イメージが確認できます。
Lovable がうまく再現しない場合は、このHTMLの `<style>` と `<table>` を
そのまま渡してください。
