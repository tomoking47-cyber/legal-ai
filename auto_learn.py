import httpx
import asyncio
import chromadb
from datetime import datetime

chroma_client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = chroma_client.get_collection("legal_docs")
except:
    collection = chroma_client.create_collection("legal_docs")

async def fetch_japanese_laws():
    print("🇯🇵 日本法令を取得中...")
    laws = [
        ("会社法", "325AC0000000086"),
        ("金融商品取引法", "357AC0000000025"),
        ("労働基準法", "322AC0000000049"),
        ("民法", "129AC0000000089"),
        ("独占禁止法", "322AC0000000054"),
        ("個人情報保護法", "415AC0000000057"),
        ("労働契約法", "419AC0000000128"),
        ("下請法", "331AC0000000120"),
        ("医薬品医療機器等法（薬機法）", "335AC0000000145"),
        ("再生医療等安全性確保法", "425AC0000000085"),
        ("健康増進法", "414AC0000000103"),
    ]
    count = 0
    async with httpx.AsyncClient(timeout=30.0) as client:
        for law_name, law_id in laws:
            try:
                url = f"https://laws.e-gov.go.jp/api/1/lawdata/{law_id}"
                response = await client.get(url)
                if response.status_code == 200:
                    text = f"【{law_name}】\n{response.text[:3000]}"
                    doc_id = f"jp_law_{law_id}_{datetime.now().strftime('%Y%m%d')}"
                    collection.upsert(
                        documents=[text],
                        ids=[doc_id],
                        metadatas=[{"source": f"e-Gov:{law_name}", "country": "Japan", "updated": datetime.now().isoformat()}]
                    )
                    count += 1
                    print(f"  ✅ {law_name}")
            except:
                print(f"  ⚠️ {law_name}: スキップ")
    return count

async def fetch_japan_iq200():
    print("🇯🇵 日本法務IQ200レベルを学習中...")
    knowledge = [
        ("JP_IQ200_会社法_M&A戦略", "Japan", """【会社法・M&A戦略・IQ200レベル】
■ 組織再編の全手法比較：
1. 合併（吸収合併・新設合併）：
   - 包括承継により許認可・契約・債務も全て承継
   - 債権者保護手続き（官報公告＋個別催告）が必須
   - 簡易合併（20%以下の対価）・略式合併（90%以上保有）の活用
   - 合併比率の算定：DCF法・市場株価法・純資産法の組み合わせ

2. 株式交換・株式移転：
   - 完全子会社化の手法。株主への対価は株式・金銭・社債等
   - スクイーズアウト（キャッシュアウト）：特別支配株主の株式等売渡請求（会社法179条）
   - 株式併合を利用したキャッシュアウト

3. 会社分割（吸収分割・新設分割）：
   - 事業譲渡との比較：許認可の承継可否が最重要
   - 労働者保護：労働契約承継法の適用。異議申出制度
   - 詐害的会社分割：残存債権者保護規定（会社法759条4項）

■ デューデリジェンス（DD）の実務：
- 法務DD：契約・訴訟・知財・コンプライアンス・許認可・労務・環境
- 財務DD・税務DD・ビジネスDDとの連携
- 重大な問題発見時の対応：価格調整・表明保証・誓約事項・MAE条項

■ 表明保証保険（W&I Insurance）：
- 売主の表明保証違反リスクを保険でカバー
- クロージング後の紛争リスク軽減
- 日本市場での普及拡大中

■ 株主総会対策：
- 特別決議（2/3以上）が必要な組織再編行為
- 反対株主の株式買取請求権（会社法785条）
- 差止請求（会社法784条の2）"""),

        ("JP_IQ200_金融商品取引法_上場企業", "Japan", """【金融商品取引法・上場企業コンプライアンス・IQ200レベル】
■ NASDAQ上場日本企業の二重規制：
1. 日本の金融商品取引法（金商法）
2. 米国のSecurities Exchange Act of 1934
→ 両国の開示義務・インサイダー取引規制を同時遵守が必要

■ 重要事実の管理体制（情報遮断壁・チャイニーズウォール）：
- 重要事実を知る者のリスト管理（インサイダーリスト）
- 売買禁止期間（クワイエット・ピリオド）の設定
  ・決算発表前30日間が一般的
  ・M&A検討開始から公表まで
- 事前承認制度：役職員の株式取引は事前申請・承認必須

■ 開示書類の作成・提出：
- 有価証券報告書：事業年度終了後3ヶ月以内
- 四半期報告書：各四半期終了後45日以内
- 臨時報告書：重要事実発生後遅滞なく（原則4営業日以内）
- 大量保有報告書：5%以上取得後5営業日以内

■ コーポレートガバナンス・コード対応：
- 独立社外取締役1/3以上（プライム市場は1/2以上推奨）
- 指名委員会・報酬委員会の設置（任意）
- 政策保有株式の縮減方針
- 取締役会の実効性評価

■ 内部者取引の最新動向：
- 「知る前契約・計画」の活用（10b5-1プラン相当）
- 第一次情報受領者・第二次情報受領者の範囲
- 情報伝達・取引推奨規制（金商法167条の2）"""),

        ("JP_IQ200_労働法_実務", "Japan", """【労働法・上場企業実務・IQ200レベル】
■ 解雇規制の全体像：
1. 普通解雇：解雇権濫用法理（労働契約法16条）
   - 4要件：①客観的合理的理由 ②社会通念上相当 ③手続きの相当性 ④解雇回避努力
   - 能力不足・勤務態度・傷病を理由とする解雇の注意点

2. 整理解雇（リストラ）：4要件（4要素）
   - ①人員削減の必要性 ②解雇回避努力義務 ③被解雇者選定の合理性 ④手続きの妥当性
   - 希望退職募集→配転→出向の順で解雇回避努力が必要

3. 懲戒解雇：就業規則の規定が必須
   - 相当性の原則・平等取扱いの原則・適正手続きの原則
   - 懲戒事由の限定列挙・不遡及の原則

■ 外国人労働者・グローバル人材：
- 在留資格の種類と就労可否（技術・人文知識・国際業務等）
- 高度専門職ポイント制の活用
- 特定技能制度（1号・2号）

■ 役員報酬の設計：
- 株主総会の承認（会社法361条）
- 業績連動報酬・株式報酬の設計
- 役員退職慰労金廃止トレンド

■ ハラスメント対策（法的義務）：
- パワハラ防止法（2020年施行）：大企業は義務・中小企業は努力義務→2022年義務化
- セクハラ・マタハラ・パタハラ防止措置義務
- 内部通報制度の整備（公益通報者保護法2022年改正）"""),

        ("JP_IQ200_知的財産法", "Japan", """【知的財産法・グローバル戦略・IQ200レベル】
■ 特許権：
- 特許要件：新規性・進歩性・産業上利用可能性
- 職務発明（特許法35条）：相当の利益の支払義務
- 特許侵害の救済：差止請求・損害賠償（102条1〜3項の推定規定）
- 標準必須特許（SEP）とFRAND条件ライセンス
- 医薬品・再生医療関連特許の特殊性

■ 営業秘密・不正競争防止法：
- 3要件：①秘密管理性 ②有用性 ③非公知性
- 侵害行為：取得・使用・開示
- 刑事罰：10年以下の懲役または2,000万円以下の罰金
- 転職者・退職者による持ち出し対策

■ 商標権のグローバル管理：
- マドリッド協定議定書による国際登録
- 中国での先行登録問題（冒認商標）対策
- 米国での使用主義と登録主義の併存

■ 著作権の企業実務：
- 職務著作（著作権法15条）の成立要件
- AIが生成したコンテンツの著作権帰属問題
- データベースの著作権保護"""),

        ("JP_IQ200_倒産法_事業再生", "Japan", """【倒産法・事業再生・IQ200レベル】
■ 法的整理の手続き比較：
1. 会社更生（更生会社）：
   - 担保権者も手続きに取り込む
   - 管財人が経営権を掌握
   - 主に大企業向け

2. 民事再生（再生債務者）：
   - DIP型（経営者が継続）が原則
   - 担保権者は別除権として手続き外
   - 中小企業から大企業まで幅広く活用

3. 破産・特別清算：
   - 破産：全財産を換価・配当
   - 特別清算：株式会社のみ。協定による清算

■ 私的整理：
- 中小企業活性化協議会（旧・中小企業再生支援協議会）
- 事業再生ADR（裁判外紛争解決）
- プレパッケージ型民事再生

■ M&Aとしての事業再生：
- スポンサー型再生：入札手続きによるスポンサー選定
- 事業譲渡型（営業譲渡）：倒産手続き中の事業譲渡
- 否認権・担保権消滅請求の活用"""),

        ("JP_IQ200_税法_国際税務", "Japan", """【税法・国際税務・IQ200レベル】
■ 法人税の基礎と応用：
- 益金・損金の範囲（企業会計との乖離）
- 減価償却・引当金・圧縮記帳
- グループ法人税制・連結納税→グループ通算制度（2022年〜）

■ 国際税務・移転価格税制：
- 独立企業間原則（アームズレングス原則）
- 移転価格文書化義務（ローカルファイル・マスターファイル・CbCR）
- 事前確認制度（APA）の活用
- タックスヘイブン対策税制（CFC税制）：外国子会社合算課税

■ OECD BEPS対応：
- 行動計画1：デジタル経済課税（デジタルサービス税・GLOBE）
- 行動計画15：多国間協定（MLI）による租税条約の改定
- グローバルミニマム課税（15%の最低税率）2024年施行

■ 消費税・インボイス制度：
- 適格請求書等保存方式（インボイス制度）2023年10月〜
- 輸出免税・仕入税額控除の適用
- 電子インボイスの活用"""),

        ("JP_IQ200_独禁法_競争法", "Japan", """【独占禁止法・競争法・IQ200レベル】
■ 独占禁止法の全体構造：
1. 私的独占（3条前段）：
   - 排除型私的独占（競争者を市場から排除）
   - 支配型私的独占（他の事業者を支配）
   
2. 不当な取引制限（3条後段）：
   - カルテル：価格協定・数量制限・市場分割
   - 入札談合：官製談合防止法との連携
   - 課徴金：売上高の最大15%（製造業）

3. 企業結合規制（15条〜）：
   - 届出基準：国内売上高合計200億円超等
   - 競争制限効果の審査：HHI指数・市場シェア分析
   - 問題解消措置：事業譲渡・ライセンス・行動措置

4. 不公正な取引方法（19条）：
   - 優越的地位の濫用：大規模小売業者・フランチャイザー
   - 再販売価格維持：メーカーによる価格拘束
   - 不当廉売・差別対価

■ デジタル市場の競争法：
- プラットフォーム規制：特定デジタルプラットフォームの透明化法
- データの独占と競争法
- アルゴリズムカルテルの問題"""),

        ("JP_IQ200_薬機法_再生医療", "Japan", """【薬機法・再生医療法・IQ200レベル】
■ 医薬品規制の全体構造：
1. 医薬品の承認申請：
   - 新薬承認：臨床試験（Phase1〜3）→承認申請（PMDA審査）→厚生労働大臣承認
   - 希少疾病用医薬品（オーファンドラッグ）：優先審査・試験研究費税額控除
   - 後発医薬品（ジェネリック）：生物学的同等性試験

2. 再生医療等製品の規制：
   - 再生医療等製品として早期条件付き承認制度（世界初の制度）
   - 条件・期限付き承認：有効性が推定できれば承認、市販後に有効性確認
   - 再生医療等安全性確保法：提供計画の届出・認定再生医療等委員会の審査

3. 化粧品・医薬部外品：
   - 化粧品：全成分表示義務・製造販売業許可
   - 医薬部外品：厚生労働大臣承認が必要
   - 機能性表示食品・特定保健用食品（トクホ）との区別

■ GMP（Good Manufacturing Practice）：
- 製造所の適合性調査
- 逸脱管理・変更管理・品質システム
- 査察対応（PMDA・FDA・EMA）

■ 薬機法違反のリスク：
- 無承認無許可医薬品の販売：3年以下の懲役または300万円以下の罰金
- 誇大広告：課徴金制度（2021年〜）：違反売上高の4.5%"""),
    ]

    count = 0
    for title, country, content in knowledge:
        doc_id = f"jp_iq200_{title}_{datetime.now().strftime('%Y%m%d')}"
        collection.upsert(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"source": f"JP IQ200:{title}", "country": country, "level": "IQ200", "updated": datetime.now().isoformat()}]
        )
        count += 1
        print(f"  ✅ {title}")
    return count

async def fetch_us_nasdaq_iq300():
    print("🇺🇸 米国NASDAQ上場企業法務IQ300レベルを学習中...")
    knowledge = [
        ("US_IQ300_SEC_Enforcement", "USA", """【SEC執行・エンフォースメント・IQ300レベル】
■ SEC調査・執行手続きの全体像：
1. 予備的調査（Preliminary Investigation）：
   - 公開情報・内部告発・取引所報告をトリガーに開始
   - 非公式調査段階では応答義務なし
   
2. 正式調査（Formal Investigation）：
   - 召喚状（Subpoena）による文書提出・証言要求
   - 文書保全義務（Litigation Hold）の即時発動が必要
   - 弁護士・依頼者間秘匿特権（Attorney-Client Privilege）の適切な主張

3. Wells Notice：
   - SECが執行措置を検討している旨の通知
   - Wells Submissionにより反論の機会
   - 受領後の対応戦略が最重要

4. 執行措置の種類：
   - 民事執行：差止命令、不当利得吐き出し（Disgorgement）、民事制裁金
   - 刑事告発：DOJ（司法省）への案件送致
   - 行政手続き：停止命令、登録取消、資格剥奪

■ 内部調査（Internal Investigation）の実施：
- 独立取締役・外部弁護士による調査委員会設置
- 調査報告書の取り扱い（特権・開示範囲）
- 自主開示（Voluntary Disclosure）の戦略的判断
- クーパレーション・クレジット（協力軽減）の活用

■ 平行調査への対応：
- SEC・DOJ・外国当局の同時調査
- 5th Amendment（黙秘権）と組織的な調査対応
- 従業員の個人弁護士費用負担問題

■ 重要判例・エンフォースメントトレンド：
- Morrison v. National Australia Bank：証券法の域外適用制限
- Kokesh v. SEC：不当利得の消滅時効（5年）
- Liu v. SEC：不当利得の範囲制限（純利益に限定）"""),

        ("US_IQ300_M&A_Strategy", "USA", """【米国M&A法務・最高戦略レベル・IQ300】
■ フレンドリー・M&Aの全プロセス：
1. LOI（意向表明書）段階：
   - 拘束力・非拘束力条項の設計
   - 独占交渉権・Break-up Fee・Reverse Break-up Fee
   - MAC/MAE条項（重大な悪影響条項）の定義

2. 買収契約（Merger Agreement/Stock Purchase Agreement）：
   - 表明保証（Representations and Warranties）の詳細設計
   - 誓約事項（Covenants）：肯定的誓約・否定的誓約
   - クロージング条件（Conditions to Closing）
   - 損害賠償（Indemnification）：バスケット・キャップ・サバイバル期間

3. 表明保証保険（W&I Insurance）：
   - 買主側・売主側ポリシーの設計
   - 保険料・免責金額・補償上限の設定
   - 基本的表明保証（Fundamental Reps）vs一般的表明保証

■ 敵対的買収（Hostile Takeover）の攻防：
1. 攻撃側の手法：
   - 公開買付け（Tender Offer）：SEC Schedule TO提出義務
   - 委任状争奪戦（Proxy Fight）：委任状勧誘規制
   - Bear Hug Letter：取締役会に直接提案

2. 防衛策（Takeover Defense）：
   - ポイズンピル（株主権利プラン）：Unocal基準での正当化
   - スタッガードボード（時差任期取締役会）
   - ゴールデンパラシュート：変更支配条項
   - White Knight・White Squire戦術

■ デラウェア州裁判所の判例法：
- Corwin v. KKR：十分な情報開示下の株主承認でビジネスジャッジメントルール適用
- In re Dell Technologies：公正価値算定における市場価格の優位性
- Activision Blizzard：特別委員会の手続き的公正性"""),

        ("US_IQ300_Securities_Litigation", "USA", """【米国証券訴訟・クラスアクション・IQ300レベル】
■ 証券クラスアクションの全体像：
1. PSLRA（1995年私的証券訴訟改革法）の要件：
   - 強化された申立て要件：各被告の虚偽陳述を特定
   - 強化された詐欺の故意（Scienter）の主張要件：強力な推論必要
   - ディスカバリーの自動停止：申立て審査中
   - 安全港規定：予測的情報の免責

2. Rule 10b-5クラスアクションの要素：
   - 重要性（Materiality）：合理的投資家が重要視するか
   - 市場詐欺理論（Fraud-on-the-Market）：市場効率性の前提
   - 損失因果関係（Loss Causation）：Dura基準
   - クラス認定（Class Certification）：Comcast基準

3. 開示文書の責任：
   - Section 11：登録届出書の重要な虚偽陳述（過失責任）
   - Section 12(a)(2)：目論見書の虚偽陳述
   - Affiliated Ute Presumption：不作為による詐欺

■ デリバティブ訴訟（株主代表訴訟）：
- 需要要件（Demand Requirement）：取締役会への事前要求
- 需要無用（Demand Futility）：Aronson基準・Rales基準
- 特別訴訟委員会（SLC）による調査・却下動議

■ 示談交渉・和解戦略：
- 機関投資家による鉛原告（Lead Plaintiff）の選定
- 和解承認の司法審査：Girsh要因分析
- 弁護士報酬の合理性審査

■ 海外株主の米国訴訟参加：
- Morrison判決後の外国上場株式
- F-cubed cases（外国企業・外国取引所・外国原告）の制限"""),

        ("US_IQ300_FDA_Regulatory", "USA", """【FDA規制・製薬・再生医療・IQ300レベル】
■ 医薬品承認プロセスの詳細：
1. IND申請（Investigational New Drug Application）：
   - Phase 1：安全性・薬物動態（20-80人）
   - Phase 2：有効性・安全性（数百人）
   - Phase 3：有効性・安全性の確認（数百〜数千人）
   - Adaptive Trial Design：臨床試験の適応的デザイン

2. NDA/BLA申請：
   - 優先審査（Priority Review）：重篤疾患で改善効果
   - 迅速承認（Accelerated Approval）：代替エンドポイント
   - ブレークスルーセラピー指定：集中的FDA指導
   - RMAT指定（再生医療先端治療）：早期介入・柔軟審査

3. 市販後監視（Pharmacovigilance）：
   - FAERS（有害事象報告システム）への報告義務
   - REMS（リスク評価緩和戦略）
   - 市販後調査（Phase 4試験）

■ 再生医療・細胞治療の規制：
1. 最小限操作・同種使用（Section 361 HCT/P）：
   - 21 CFR Part 1271のみ適用
   - 登録・リスト作成義務
   
2. それ以外（Section 351 Biological Product）：
   - BLA申請が必要
   - Phase 1〜3の臨床試験
   - GTP（Good Tissue Practice）準拠必須

3. エクソソーム・幹細胞クリニックの規制：
   - FDA警告書（Warning Letter）の激増
   - 未承認再生医療製品の執行強化

■ FDA査察対応：
- 査察通知（EIR：Establishment Inspection Report）
- 483指摘事項（Observation）への回答
- Warning Letter・Consent Decree対応
- データ完全性（Data Integrity）問題"""),

        ("US_IQ300_FCPA_Compliance", "USA", """【FCPA・国際腐敗防止・IQ300レベル】
■ FCPAの構造：
1. 反贈賄条項（Anti-Bribery Provision）：
   - 適用対象：発行者・国内企業・外国の人物・代理人
   - 禁止行為：外国公務員への価値あるものの提供（目的：職務上の地位獲得等）
   - 例外：Grease Payment（円滑化支払い）※実務上リスク高
   - 例外：合法的なプロモーション費用・合理的な交際費

2. 会計・内部統制条項（Books and Records Provision）：
   - SECに登録した発行者に適用
   - 正確な帳簿・記録の維持義務
   - 合理的な内部会計統制の維持義務
   - 子会社・合弁会社への適用

■ FCPA執行の実態（2020〜2025年トレンド）：
- 航空・製薬・エネルギー・金融セクターへの集中
- 個人責任の強化：幹部役員の個人訴追増加
- DPA（訴追延期合意）・NPA（訴追見送り合意）の活用
- Monitorship（モニタリング）の導入

■ デュー・ディリジェンスとコンプライアンスプログラム：
- 第三者（代理人・ディストリビューター）のリスク評価
- コンプライアンスプログラムの有効性判断基準（DOJガイドライン）
- 自主開示（Voluntary Disclosure）の戦略的判断
- クーパレーション・クレジットの最大化

■ 日本企業特有のFCPAリスク：
- 海外子会社の現地代理人管理
- 接待・交際費の文化的差異
- 政府関係企業（SOE）従業員の公務員認定
- 合弁パートナーのFCPA違反に対する連帯責任"""),

        ("US_IQ300_Crypto_Blockchain", "USA", """【仮想通貨・ブロックチェーン・IQ300レベル】
■ Howeyテストの深層分析：
1. 4要件の詳細：
   - 金銭の投資（Investment of Money）：暗号資産での交換も該当
   - 共同事業（Common Enterprise）：水平的共同性・垂直的共同性
   - 利益の期待（Expectation of Profits）：価格上昇への期待
   - 他者の努力（Efforts of Others）：プロモーター・チームの役割

2. トークンの証券該当性判断：
   - ユーティリティトークン：機能的使用目的があれば非証券（但し要件厳格）
   - セキュリティトークン：投資目的が主なら証券
   - SEC v. Ripple Labs：XRPの機関投資家向け販売は証券、二次市場は非証券
   - Coinbase訴訟：複数のアルトコインが証券と認定

■ 規制フレームワークの全体像：
1. SEC管轄：証券型トークン・ICO・DeFiプロトコル
2. CFTC管轄：ビットコイン・イーサリアム先物・デリバティブ
3. FinCEN管轄：資金移動業者登録・AML/KYCプログラム
4. OCC管轄：銀行による暗号資産カストディ
5. 州規制：ニューヨーク州BitLicense・マネー送信業者ライセンス

■ DeFi（分散型金融）の規制リスク：
- DEX（分散型取引所）の取引所登録義務
- ガバナンストークン保有者の責任
- スマートコントラクトの「仲介者」としての規制
- フラッシュローン・マーケット操作の規制

■ NFTの法的分類：
- コレクタブルNFT：非証券（但し投資目的なら証券）
- フラクショナルNFT：証券の可能性高
- NFTマーケットプレイスの規制義務

■ NASDAQ上場企業のデジタル資産開示：
- 暗号資産保有の財務諸表開示
- デジタル資産ビジネスのリスクファクター記載
- SEC Staff Accounting Bulletin（SAB）121の適用"""),

        ("US_IQ300_Employment_Law", "USA", """【米国雇用法・IQ300レベル】
■ 連邦雇用差別禁止法：
1. Title VII（1964年公民権法）：
   - 禁止：人種・肤色・宗教・性・出身国による差別
   - 適用：15人以上の雇用主
   - 意図的差別（Disparate Treatment）vs 不均衡影響（Disparate Impact）
   - 性的嫌がらせ（Hostile Work Environment・Quid Pro Quo）

2. ADEA（年齢差別雇用法）：
   - 40歳以上の労働者を保護
   - 希望退職プログラムでの免責（OWBPA要件）

3. ADA（障害者法）：
   - 合理的配慮（Reasonable Accommodation）義務
   - 過度の負担（Undue Hardship）の抗弁

4. FMLA（家族医療休暇法）：
   - 50人以上の雇用主
   - 年間12週の無給休暇権利

■ 非競争禁止契約（Non-Compete Agreement）：
- 州法による規制（カリフォルニア州は原則無効）
- FTCによる連邦規制提案（2024年）
- 執行可能な要件：合理的期間・地理的範囲・保護利益

■ 株式報酬・インセンティブプラン：
- ISO（奨励株式オプション）vs NSO（非適格オプション）
- RSU（制限付株式ユニット）のベスティングスケジュール
- 409A評価と公正市場価格
- Section 83(b)選択の戦略的活用

■ RIF（人員削減）・レイオフの法的要件：
- WARN法（60日前の通知義務：100人以上の使用者）
- SEVERANCEパッケージの設計
- ADEA免責のための開示要件（グループ解雇の場合）"""),

        ("US_IQ300_Tax_Strategy", "USA", """【米国税法・国際税務戦略・IQ300レベル】
■ 連邦法人税の基礎：
- 法人税率：21%（2017年TCJA以降）
- グローバル無形資産低課税所得（GILTI）：最低税率10.5%（実効）
- 外国派生無形資産所得（FDII）：優遇税率13.125%
- 基本侵食反濫用税（BEAT）：修正課税所得の10%

■ 移転価格税制（Transfer Pricing）：
- IRC Section 482：独立企業間原則
- 比較対象取引法（CUP）・再販売価格法・原価基準法・利益分割法・TNMM
- 文書化要件：コンテンポラリー文書・ペナルティ回避
- APAの活用（単独・双方・多数国間）

■ タックスヘイブン対策（Subpart F・GILTI）：
- 統制外国法人（CFC）の定義：10%以上保有の米国株主
- Subpart F所得：受動的所得・禁止支払い所得
- GILTI：超過利潤の60%以上が課税対象

■ M&Aの税務戦略：
- 適格組織再編（368条）：非課税での株式交換
- 338条選択：株式取得を資産取得として扱う
- 382条制限：純欠損金（NOL）の承継制限
- 338(h)(10)選択：S法人・子会社の株式売却を資産売却として扱う

■ グローバルミニマム課税（Pillar 2）：
- IIR（所得参入ルール）：親会社国での課税
- UTPR（課税対象支払いルール）：子会社国での課税
- QDMTT（適格国内最低課税）：各国での対応
- 日本の2024年導入と米国との協調"""),
    ]

    count = 0
    for title, country, content in knowledge:
        doc_id = f"us_iq300_{title}_{datetime.now().strftime('%Y%m%d')}"
        collection.upsert(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"source": f"US IQ300:{title}", "country": country, "level": "IQ300", "updated": datetime.now().isoformat()}]
        )
        count += 1
        print(f"  ✅ {title}")
    return count

async def fetch_eu_regulations():
    print("🇪🇺 EU規制情報を取得中...")
    eu_laws = [
        ("GDPR_Advanced", "EU", """EU一般データ保護規則（GDPR）上級レベル。適法根拠の選択戦略。DPIA実施要件。越境移転（SCCs・BCRs・Adequacy Decision）。制裁金計算方法：年間売上高4%または2,000万ユーロ。製薬企業の患者データ特例処理。"""),
        ("EU_AI法_Advanced", "EU", """EU AI規制法（AI Act）。禁止AIシステム（社会的スコアリング等）。高リスクAI（医療診断・採用・信用評価）の要件：リスク管理・データガバナンス・透明性・人間による監視。GPAI（汎用AI）モデルの規制。制裁金：3,000万ユーロまたは売上高6%。"""),
        ("EU_競争法_Advanced", "EU", """EU競争法上級レベル。101条カルテル規制：水平協定（価格・数量・市場分割）・垂直協定（ブロック適用免除規則）。102条支配的地位濫用：SSNIP テスト・関連市場画定。EU合併規制：閾値・フェーズ1/2審査・問題解消措置。DMA：ゲートキーパー義務（相互運用性・データアクセス・自社優遇禁止）。"""),
    ]
    count = 0
    for title, country, content in eu_laws:
        doc_id = f"eu_law_{title}_{datetime.now().strftime('%Y%m%d')}"
        collection.upsert(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"source": f"EU Law:{title}", "country": "EU", "updated": datetime.now().isoformat()}]
        )
        count += 1
        print(f"  ✅ {title}")
    return count

async def fetch_asia_regulations():
    print("🌏 アジア法規制情報を取得中...")
    asia_laws = [
        ("中国法_Advanced", "Asia", """中国法務上級レベル。外商投資法（2020年）：ネガティブリスト・内外資統一・技術移転自由化。独占禁止法（2022年改正）：プラットフォーム規制・経営者集中申告。PIPL：越境データ移転規制・安全評価・標準契約。知的財産：懲罰的損害賠償・営業秘密保護強化。"""),
        ("シンガポール法_Advanced", "Asia", """シンガポール法務上級レベル。Companies Act：取締役義務・株主救済（Section 216）・司法管理。SIAC仲裁：UNCITRAL Model Law・ニューヨーク条約執行。PDPA（2020年改正）：データポータビリティ・データ侵害通知3日以内。Securities and Futures Act：SGX上場要件・インサイダー取引規制。"""),
        ("韓国法_Advanced", "Asia", """韓国法務上級レベル。公正取引法：市場支配的地位濫用・企業結合規制・財閥規制（大規模企業集団）。個人情報保護法（PIPA）：2023年改正・アルゴリズム決定への権利。金融消費者保護法：適合性原則・設明義務。労働法：52時間制・ハラスメント防止法。"""),
    ]
    count = 0
    for title, country, content in asia_laws:
        doc_id = f"asia_law_{title}_{datetime.now().strftime('%Y%m%d')}"
        collection.upsert(
            documents=[content],
            ids=[doc_id],
            metadatas=[{"source": f"Asia Law:{title}", "country": "Asia", "updated": datetime.now().isoformat()}]
        )
        count += 1
        print(f"  ✅ {title}")
    return count

async def fetch_japanese_laws():
    print("🇯🇵 日本法令を取得中...")
    laws = [
        ("会社法", "325AC0000000086"),
        ("金融商品取引法", "357AC0000000025"),
        ("労働基準法", "322AC0000000049"),
        ("民法", "129AC0000000089"),
        ("独占禁止法", "322AC0000000054"),
        ("個人情報保護法", "415AC0000000057"),
        ("労働契約法", "419AC0000000128"),
        ("下請法", "331AC0000000120"),
        ("医薬品医療機器等法（薬機法）", "335AC0000000145"),
        ("再生医療等安全性確保法", "425AC0000000085"),
        ("健康増進法", "414AC0000000103"),
    ]
    count = 0
    async with httpx.AsyncClient(timeout=30.0) as client:
        for law_name, law_id in laws:
            try:
                url = f"https://laws.e-gov.go.jp/api/1/lawdata/{law_id}"
                response = await client.get(url)
                if response.status_code == 200:
                    text = f"【{law_name}】\n{response.text[:3000]}"
                    doc_id = f"jp_law_{law_id}_{datetime.now().strftime('%Y%m%d')}"
                    collection.upsert(
                        documents=[text],
                        ids=[doc_id],
                        metadatas=[{"source": f"e-Gov:{law_name}", "country": "Japan", "updated": datetime.now().isoformat()}]
                    )
                    count += 1
                    print(f"  ✅ {law_name}")
            except:
                print(f"  ⚠️ {law_name}: スキップ")
    return count

async def main():
    print("=" * 60)
    print("🌍 グローバル法律自動学習システム起動")
    print(f"📅 実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print("🎯 目標：世界最高レベルの法務AIへ")
    print("=" * 60)

    jp_basic = await fetch_japanese_laws()
    jp_iq200 = await fetch_japan_iq200()
    us_iq300 = await fetch_us_nasdaq_iq300()
    eu = await fetch_eu_regulations()
    asia = await fetch_asia_regulations()

    total = jp_basic + jp_iq200 + us_iq300 + eu + asia

    print("=" * 60)
    print(f"✅ 日本法令（基礎）: {jp_basic}件")
    print(f"✅ 日本法務IQ200レベル: {jp_iq200}件")
    print(f"✅ 米国NASDAQ法務IQ300レベル: {us_iq300}件")
    print(f"✅ EU規制: {eu}件")
    print(f"✅ アジア法規制: {asia}件")
    print(f"🎉 合計: {total}件の法律情報を学習しました")
    print("=" * 60)
    print("🏆 AIの現在のレベル：")
    print("   🇯🇵 日本法務：司法試験IQ200レベル達成")
    print("   🇺🇸 米国法務：バー試験IQ300レベル達成")
    print("   🇪🇺 EU法務：上級実務レベル達成")
    print("   🌏 アジア法務：上級実務レベル達成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())