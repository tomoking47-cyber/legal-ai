# -*- coding: utf-8 -*-
"""カテゴリー別の話題リストと質問フレーム。ここを増やせば出力件数が増える。"""

# ---------------------------------------------------------------- 日本語カテゴリー

BEAUTY_TOPICS = [
    "化粧水","乳液","美容液","クリーム","日焼け止め","クレンジング","洗顔料","洗顔の回数",
    "パック","シートマスク","角質ケア","毛穴ケア","スクラブ","ふきとり化粧水","導入美容液","スキンケアの順番",
    "朝のスキンケア","夜のスキンケア","化粧下地","ファンデーション","コンシーラー","フェイスパウダー","チーク","アイシャドウ",
    "アイライナー","マスカラ","リップ","リップクリーム","眉の描き方","メイク直し","メイク落とし","二重洗顔",
    "シャンプー","コンディショナー","トリートメント","ヘアオイル","ドライヤーの使い方","頭皮ケア","ヘアブラシ","ネイルケア",
    "ハンドクリーム","ボディクリーム","ボディソープ","入浴剤","制汗剤","香水のつけ方","フレグランスの保管","化粧品の保管",
    "化粧品の使用期限","化粧筆の洗い方","メイクスポンジ","鏡の選び方","肌質の見分け方","乾燥肌のケア","脂性肌のケア","混合肌のケア",
    "敏感肌のケア","季節の変わり目の肌","マスクによる肌荒れ",
]

FASHION_TOPICS = [
    "衣類の毛玉","ニットの洗濯","シルクの手入れ","デニムの洗い方","白いシャツの管理","革靴の手入れ","スニーカーの洗い方","バッグの保管",
    "アクセサリーの手入れ","時計の手入れ","洗濯表示の読み方","柔軟剤の使い方","部屋干しの工夫","アイロンのかけ方","衣替えの手順","防虫剤の使い方",
    "クローゼットの湿気","静電気対策","毛布の洗濯","羽毛布団の手入れ","コートの手入れ","スーツの手入れ","ジャケットのしわ","ダウンの洗い方",
    "レインコートの手入れ","スニーカーの保管","ブーツの保管","革バッグの雨対策","帽子の手入れ","マフラーの洗い方","手袋の手入れ","水着の洗い方",
    "靴下の寿命","下着の買い替え時期","色移りの防ぎ方","縮んだニット","黄ばみの落とし方","毛玉取り器の使い方","衣類の畳み方","ハンガーの選び方",
    "スカーフの結び方","ベルトの手入れ","傘の手入れ","メガネの手入れ","サングラスの保管","着物の保管",
]

HEALTH_TOPICS = [
    "睡眠時間","寝る時刻","起きる時刻","昼寝","二度寝","寝返り","枕の高さ","マットレスの硬さ",
    "寝室の温度","寝室の明るさ","寝る前のスマホ","寝る前の食事","寝る前の入浴","寝つきの悪さ",
    "中途覚醒","朝の光","体内時計","時差ぼけ","休日の寝だめ","いびき",
    "水分補給","朝の一杯の水","カフェイン","アルコール","炭酸水","スポーツドリンク","経口補水液",
    "白湯","お茶","ハーブティー",
    "ウォーキング","ストレッチ","ラジオ体操","階段の上り下り","デスクワークの姿勢","立ち仕事",
    "肩こり","腰の張り","首の疲れ","目の疲れ","スマホ首",
    "入浴の温度","入浴の時間","湯船とシャワー","半身浴","サウナ","足湯","冷え","むくみ",
    "深呼吸","瞑想","休憩の取り方","気分転換","季節の変わり目の体調","梅雨の不調","夏バテ",
    "冬の乾燥","花粉の季節","紫外線と体調","日照時間と気分","在宅勤務の運動不足",
    "サプリメントの選び方","ビタミン","鉄分","たんぱく質","食物繊維","発酵食品","腸内環境",
    "朝食を抜くこと","間食","夜食","食べる順番","よく噛むこと","塩分","糖分","脂質",
    "体重の測り方","体温の測り方","血圧の測り方","健康診断の受け方","医療機関の選び方",
]

TREND_TOPICS = [
    "米の保存","パンの保存","野菜の保存","果物の保存","肉の保存","魚の保存","卵の保存",
    "冷凍のコツ","解凍のコツ","作り置き","下ごしらえ","下味","冷蔵庫の使い方","野菜室",
    "チルド室","保存容器","ラップの使い方","アルミホイルの使い方","キッチンペーパー",
    "だしの取り方","味噌","しょうゆ","みりん","酒","酢","塩","砂糖","油の選び方",
    "オリーブオイル","ごま油","スパイス","ハーブ","にんにく","しょうが","梅干し","漬物",
    "発酵食品","納豆","ヨーグルト","チーズ","豆腐","納豆の食べ方",
    "包丁の研ぎ方","まな板の手入れ","フライパンの手入れ","鍋の選び方","土鍋","鉄鍋",
    "炊飯","味噌汁","煮物","焼き物","蒸し物","揚げ物","炒め物","電子レンジ活用",
    "オーブンの使い方","トースターの使い方","炊飯器の活用","保温調理",
    "賞味期限","消費期限","食品ロス","買い物の頻度","献立の立て方","一人分の調理",
    "お弁当","水筒","キャンプ飯","旬の食材","地域の特産品","郷土料理","行事食","おせち",
    "コーヒーの淹れ方","紅茶の淹れ方","緑茶の淹れ方","水出し","氷の作り方",
]

# ---------------------------------------------------------------- 英語カテゴリー

INBOUND_TOPICS = [
    "drugstores","convenience stores","supermarkets","department stores","100-yen shops",
    "home centres","tax-free shopping","consumption tax","cash and cards","IC cards",
    "coin lockers","luggage forwarding","carry-on rules","customs on the way home",
    "bringing food home","bringing medicine","packing for summer","packing for winter",
    "packing for the rainy season","humidity","the heat in August","pollen season",
    "UV levels","sunscreen labels","SPF and PA","cosmetics labels","ingredient lists",
    "expiry dates on cosmetics","skincare product names","face masks","hand soap",
    "toiletries you can buy locally","laundry while travelling","coin laundries",
    "hotel amenities","slippers and shoes indoors","public baths","onsen etiquette",
    "tattoos and bathing","towels","tap water","vending machines","bottle recycling",
    "rubbish bins","sorting rubbish","eating while walking","convenience-store food",
    "onigiri","bento","instant noodles","matcha products","wagashi","seasonal sweets",
    "allergy labelling","vegetarian options","halal options","reading a menu",
    "restaurant etiquette","tipping","queueing","reservations","English-speaking staff",
    "translation apps","pharmacy staff","over-the-counter medicine","first aid supplies",
    "power plugs","SIM and eSIM","pocket wifi","postal services","souvenir choices",
    "gift wrapping","seasonal shopping","sales seasons","sizing differences","shoe sizes",
]

WISDOM_TOPICS = [
    "taking shoes off indoors","the genkan","tatami","futon airing","seasonal bedding",
    "sliding doors","small apartments","storage in narrow spaces","under-bed storage",
    "the gap beside the fridge","vertical storage","seasonal clothing rotation",
    "refill packs","reusable cloth","furoshiki","tenugui","bento boxes","chopstick rests",
    "single-purpose kitchen tools","drying racks","laundry poles","indoor drying",
    "dehumidifiers","the rainy season","mould prevention","ventilation habits",
    "cleaning order","cleaning cloths","newspaper for windows","baking soda","citric acid",
    "the year-end clean","daily tidying","the entrance mat","shoe cabinets","umbrella care",
    "seasonal food","the concept of shun","dashi","fermentation","pickling","rice storage",
    "tea culture","hot and cold drinks by season","hand towels","wet towels at restaurants",
    "gift-giving customs","packaging","seasonal greetings","the new year","festivals",
    "kotatsu","heated carpets","hot water bottles","layering clothes","cooling towels",
    "summer heat habits","insect prevention","plants indoors","balcony gardening",
    "waste separation","local rules","community boards","neighbourhood etiquette",
    "noise consideration","earthquake preparation","emergency bags","water storage",
    "torches and radios","first aid at home","stockpiling food","rotating supplies",
    "reading a Japanese label","product lot numbers","warranty culture","repair over replace",
]

# ---------------------------------------------------------------- 話題の種類

# 状態・現象（自分で「やる」ものではない）
STATE_TOPICS = {
    "冷え","むくみ","肩こり","腰の張り","首の疲れ","目の疲れ","スマホ首","いびき",
    "寝つきの悪さ","中途覚醒","夏バテ","梅雨の不調","冬の乾燥","花粉の季節",
    "季節の変わり目の体調","季節の変わり目の肌","マスクによる肌荒れ","静電気対策",
    "衣類の毛玉","クローゼットの湿気","在宅勤務の運動不足","日照時間と気分",
    "紫外線と体調","時差ぼけ","食品ロス","体内時計","腸内環境","肌質の見分け方",
}

# 行為・手順（「やる」もの）
ACTION_TOPICS = {
    "洗顔の回数","スキンケアの順番","朝のスキンケア","夜のスキンケア","メイク直し",
    "メイク落とし","二重洗顔","眉の描き方","ドライヤーの使い方","香水のつけ方",
    "化粧筆の洗い方","衣替えの手順","部屋干しの工夫","アイロンのかけ方",
    "昼寝","二度寝","寝返り","休日の寝だめ","半身浴","サウナ","足湯","深呼吸","瞑想",
    "水分補給","朝の一杯の水","朝食を抜くこと","間食","夜食","食べる順番","よく噛むこと",
    "休憩の取り方","気分転換","階段の上り下り","ウォーキング","ストレッチ","ラジオ体操",
    "体重の測り方","体温の測り方","血圧の測り方","健康診断の受け方","医療機関の選び方",
    "冷凍のコツ","解凍のコツ","作り置き","下ごしらえ","下味","炊飯","煮物","焼き物",
    "蒸し物","揚げ物","炒め物","電子レンジ活用","保温調理","献立の立て方","一人分の調理",
    "買い物の頻度","水出し","氷の作り方",
}

# 手順が複数ステップある話題（「順番」を問えるもの）
SEQUENCE_TOPICS = {
    "スキンケアの順番","朝のスキンケア","夜のスキンケア","メイク落とし","二重洗顔",
    "衣替えの手順","下ごしらえ","献立の立て方","食べる順番","洗濯表示の読み方",
}

ACTION_SUFFIXES = ("の使い方","の取り方","の洗い方","の淹れ方","の研ぎ方","の手入れ",
                   "の選び方","の描き方","のかけ方","ケア","対策","補給","の保存","の管理")


def topic_type(topic: str) -> str:
    """話題を state（状態）/ act（行為）/ obj（モノ）に分ける"""
    if topic in STATE_TOPICS:
        return "state"
    if topic in ACTION_TOPICS or topic.endswith(ACTION_SUFFIXES):
        return "act"
    return "obj"


# ---------------------------------------------------------------- 質問フレーム
# (フレーム, 使ってよい話題の種類)

JA_FRAMES = [
    ("{t}について、よくある誤解は？",              {"act","obj","state"}),
    ("{t}は人によって違うの？",                    {"act","obj","state"}),
    ("{t}はなぜ必要なの？",                        {"act","obj"}),
    ("{t}の目安はどれくらい？",                    {"act","obj"}),
    ("{t}は季節で変えたほうがいいの？",            {"act","obj"}),
    ("{t}に決まりはあるの？",                      {"act","obj"}),
    ("{t}は毎日やったほうがいいの？",              {"act"}),
    ("{t}はいつやるのがいいの？",                  {"act"}),
    ("{t}はやりすぎるとどうなるの？",              {"act"}),
    ("{t}をやめるとどうなるの？",                  {"act"}),
    ("{t}はどこまでやればいいの？",                {"act"}),
    ("{t}は本当に意味があるの？",                  {"act"}),
    ("{t}を選ぶときは何を見ればいいの？",          {"obj"}),
    ("{t}の正しい使い方は？",                      {"obj"}),
    ("{t}はどう保管すればいいの？",                {"obj"}),
    ("{t}はどう見分ければいいの？",                {"obj"}),
    ("{t}はなぜ起こるの？",                        {"state"}),
    ("{t}が気になるときは、どうすればいいの？",    {"state"}),
    ("{t}は放っておいても大丈夫なの？",            {"state"}),
    ("{t}は何が原因で変わるの？",                  {"state"}),
]

# 順番を問えるのは SEQUENCE_TOPICS だけ
SEQ_FRAME = ("{t}は、どの順番でやればいいの？", {"act"})

# 英語フレーム。主語の単複で文法が崩れない形だけを使う
EN_FRAMES = [
    ("What should I know about {t} in Japan?",                 None),
    ("What do people get wrong about {t} in Japan?",            None),
    ("What surprises visitors about {t} in Japan?",             None),
    ("Why are things different in Japan when it comes to {t}?", None),
    ("What do people in Japan actually do about {t}?",          None),
    ("What is the etiquette around {t} in Japan?",              None),
    ("How do I deal with {t} in Japan?",                        None),
    ("What is the practical way to handle {t} in Japan?",       None),
    ("Do I need to think about {t} before visiting Japan?",     None),
    ("What is worth knowing about {t} before you go?",          None),
    ("What has changed about {t} in Japan?",                    None),
    ("Is {t} something visitors should plan for?",              None),
]

CATEGORIES = {
    "beauty":   {"label":"ビューティー・スキンケア・メイク・ヘア", "shelf":"beauty",  "topics":BEAUTY_TOPICS,   "frames":JA_FRAMES, "lang":"ja"},
    "fashion":  {"label":"衣類・靴・バッグ・洗濯とお手入れ",       "shelf":"fashion", "topics":FASHION_TOPICS,  "frames":JA_FRAMES, "lang":"ja"},
    "health":   {"label":"ウェルネス・健康",             "shelf":"health",  "topics":HEALTH_TOPICS,   "frames":JA_FRAMES, "lang":"ja"},
    "trend":    {"label":"フード・暮らし",               "shelf":"trend",   "topics":TREND_TOPICS,    "frames":JA_FRAMES, "lang":"ja"},
    "inbound":  {"label":"訪日外国人向け（英語）",       "shelf":"inbound", "topics":INBOUND_TOPICS,  "frames":EN_FRAMES, "lang":"en"},
    "wisdom":   {"label":"日本の暮らしの知恵（英語）",   "shelf":"wisdom",  "topics":WISDOM_TOPICS,   "frames":EN_FRAMES, "lang":"en"},
}
