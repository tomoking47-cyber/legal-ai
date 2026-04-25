from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
import httpx
import chromadb
from dotenv import load_dotenv
from typing import List, Dict, Optional
from pypdf import PdfReader
from docx import Document
import io

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

chroma_client = chromadb.PersistentClient(path="./chroma_db")
try:
    collection = chroma_client.get_collection("legal_docs")
    print(f"✅ 自社文書データベース接続成功")
except:
    collection = None
    print("⚠️ 自社文書データベースなし")

SYSTEM_PROMPT = """あなたはグローバル上場企業の会長CEOの専任法務戦略パートナーです。
あなたの役割は法律を「守るためのルール」ではなく「勝つための武器」として使うことです。

【あなたの人格・思考スタイル】
- 元NYの大手法律事務所パートナー弁護士（M&A・訴訟・規制対応専門）
- 元東京の渉外法律事務所パートナー弁護士（金融・製薬・上場企業専門）
- 30年以上の実務経験を持つ交渉のプロ
- 常にBOSSの利益を最大化するために考える
- 「できない理由」を言わず「どうすれば勝てるか」を考える

【対応専門分野】
■ 米国法務
- NASDAQ上場・SEC規制・SOX法・FCPA
- デラウェア州会社法・UCC
- FDA規制（医薬品・再生医療・化粧品・健康食品）
- 米国訴訟戦略・クラスアクション対応

■ 日本法務
- 薬機法・再生医療等安全性確保法・医療機器法
- 金融商品取引法・会社法・独占禁止法
- 労働法・知的財産法・個人情報保護法

■ クロスボーダー法務
- 日米欧アジアにまたがる契約・M&A・規制対応
- GDPR・中国PIPL・アジア各国規制
- 国際仲裁（ICC・AAA・JAMS）戦略

■ ブロックチェーン・デジタル資産法務
- SEC規制・Howeyテスト・CFTC規制
- 日本資金決済法・暗号資産交換業者規制
- EU MiCA規制・NFT・DeFi・DAO法的地位

【文書分析時の回答フォーマット】

## 📄 文書の概要
（提出された文書の種類・当事者・目的を簡潔に整理）

## 🔍 発見された法的問題点
（問題点を重大度順に詳しく説明）

## ⚠️ リスク評価
（高・中・低に分類して詳しく説明）

## ⚔️ 攻めの戦略
（有利な立場を取るための具体的手法）

## 💬 反論・交渉フレーズ
（実際に使える言葉を日本語と英語で）

## ⚡ ベストシナリオ / ワーストシナリオ

## 🔥 私の戦略的意見
（BOSSにとって最善の選択肢を明言）

## 📋 即座のアクションプラン

【通常相談時の回答フォーマット】

## 🎯 状況の本質
## ⚔️ 攻めの戦略
## 🛡️ 守りの戦略
## 💬 具体的な反論・交渉フレーズ
## ⚡ ベストシナリオ / ワーストシナリオ
## 🔥 私の戦略的意見
## 📋 即座のアクションプラン
## ❓ 確認したい点

【回答の詳しさについて】
- 各項目は必ず3〜5文以上で詳しく説明する
- 法律用語を使った後は必ず「つまり〜」と噛み砕いて説明する
- 「なぜそうなのか」という理由を必ず説明する
- 具体的な事例・数字・金額を使って説明する
- 箇条書きだけで終わらず、必ず文章で補足説明を加える
- BOSSが交渉の場でそのまま使えるレベルの詳しさで説明する
- 回答は最低でも1000文字以上を目安にする

⚖️ 免責事項：本回答は戦略的法務アドバイスの提供を目的とした一般的情報です。
最終的な法的判断は必ず各国の資格を持つ弁護士にご確認ください。"""

sessions: Dict[str, List[dict]] = {}

def extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def search_company_docs(query: str) -> str:
    if collection is None:
        return ""
    try:
        results = collection.query(query_texts=[query], n_results=3)
        docs = results["documents"][0]
        sources = [m["source"] for m in results["metadatas"][0]]
        context = ""
        for doc, source in zip(docs, sources):
            context += f"【自社文書: {source}】\n{doc}\n\n"
        return context
    except:
        return ""

async def fetch_law_content(keyword: str) -> str:
    law_map = {
        "労働": "労働基準法", "解雇": "労働契約法",
        "契約": "民法", "会社": "会社法",
        "株式": "金融商品取引法", "インサイダー": "金融商品取引法",
        "上場": "金融商品取引法", "刑事": "刑法",
        "税": "法人税法", "個人情報": "個人情報保護法",
        "薬": "薬機法", "医薬品": "薬機法",
        "再生医療": "再生医療等安全性確保法",
        "化粧品": "薬機法", "健康食品": "健康増進法",
        "トークン": "資金決済法", "仮想通貨": "資金決済法",
    }
    matched_laws = []
    for key, law_name in law_map.items():
        if key in keyword:
            matched_laws.append(law_name)
    if matched_laws:
        return f"参照法令: {', '.join(set(matched_laws))}"
    return ""

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    history_count: int
    referenced_laws: str
    company_docs_used: bool

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if req.session_id not in sessions:
        sessions[req.session_id] = []

    company_context = search_company_docs(req.message)
    law_info = await fetch_law_content(req.message)

    enhanced_message = req.message
    company_docs_used = False

    if company_context:
        enhanced_message += f"\n\n【自社文書より関連情報】\n{company_context}"
        company_docs_used = True

    if law_info:
        enhanced_message += f"\n\n【参照法令】\n{law_info}"

    sessions[req.session_id].append({"role": "user", "content": enhanced_message})

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=sessions[req.session_id]
    )

    answer = message.content[0].text
    sessions[req.session_id].append({"role": "assistant", "content": answer})

    return ChatResponse(
        answer=answer,
        history_count=len(sessions[req.session_id]),
        referenced_laws=law_info,
        company_docs_used=company_docs_used
    )

@app.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...),
    instruction: str = Form("この文書を法的に分析してください"),
    session_id: str = Form("default")
):
    file_bytes = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        text = extract_pdf(file_bytes)
        file_type = "PDF"
    elif filename.endswith(".docx"):
        text = extract_docx(file_bytes)
        file_type = "Word文書"
    else:
        return {"error": "PDF または Word(.docx) ファイルのみ対応しています"}

    if not text.strip():
        return {"error": "文書からテキストを読み取れませんでした"}

    document_message = f"""
{instruction}

【アップロードされた文書】
ファイル名: {file.filename}
ファイル形式: {file_type}

【文書の内容】
{text[:8000]}
"""

    if session_id not in sessions:
        sessions[session_id] = []

    law_info = await fetch_law_content(text[:500])
    company_context = search_company_docs(instruction)

    if company_context:
        document_message += f"\n\n【自社文書より関連情報】\n{company_context}"

    sessions[session_id].append({"role": "user", "content": document_message})

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=sessions[session_id]
    )

    answer = message.content[0].text
    sessions[session_id].append({"role": "assistant", "content": answer})

    return ChatResponse(
        answer=answer,
        history_count=len(sessions[session_id]),
        referenced_laws=law_info,
        company_docs_used=bool(company_context)
    )

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "会話履歴をリセットしました"}

app.mount("/images", StaticFiles(directory="images"), name="images")

@app.get("/")
async def root():
    return FileResponse("chat.html")

@app.get("/update")
async def update_page():
    return FileResponse("update.html")

@app.get("/api/update-status")
async def update_status():
    try:
        col = chroma_client.get_collection("legal_docs")
        count = col.count()
        all_data = col.get(include=["metadatas"])
        metadatas = all_data["metadatas"]
        
        countries = {}
        sources = {}
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = 0
        
        for meta in metadatas:
            country = meta.get("country", "自社文書")
            countries[country] = countries.get(country, 0) + 1
            source = meta.get("source", "不明")
            sources[source] = sources.get(source, 0) + 1
            if today in meta.get("updated", ""):
                today_count += 1
        
        return {
            "total": count,
            "today": today_count,
            "countries": countries,
            "sources": sources,
            "date": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
            "update_logs": []
        }
    except Exception as e:
        return {"error": str(e), "total": 0, "today": 0, "countries": {}, "sources": {}, "date": "", "update_logs": []}