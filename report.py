import chromadb
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

chroma_client = chromadb.PersistentClient(path="./chroma_db")

def get_report():
    try:
        collection = chroma_client.get_collection("legal_docs")
        count = collection.count()
        
        # 全データを取得
        all_data = collection.get(include=["metadatas"])
        metadatas = all_data["metadatas"]
        
        # 国別・カテゴリ別に集計
        countries = {}
        sources = {}
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = 0
        
        for meta in metadatas:
            # 国別集計
            country = meta.get("country", "自社文書")
            countries[country] = countries.get(country, 0) + 1
            
            # ソース別集計
            source = meta.get("source", "不明")
            sources[source] = sources.get(source, 0) + 1
            
            # 今日の学習数
            updated = meta.get("updated", "")
            if today in updated:
                today_count += 1
        
        return {
            "total": count,
            "today": today_count,
            "countries": countries,
            "sources": sources,
            "date": datetime.now().strftime("%Y年%m月%d日 %H:%M")
        }
    except Exception as e:
        return {"error": str(e)}

def generate_report_html(data):
    if "error" in data:
        return f"エラーが発生しました: {data['error']}"
    
    countries_html = ""
    for country, count in data["countries"].items():
        bar_width = min(100, int(count / data["total"] * 100))
        countries_html += f"""
        <tr>
            <td style="padding:8px; color:#c9a84c;">{country}</td>
            <td style="padding:8px; color:#e8e0d0;">{count}件</td>
            <td style="padding:8px;">
                <div style="background:#3a3020; border-radius:4px; height:8px; width:200px;">
                    <div style="background:#b8960c; border-radius:4px; height:8px; width:{bar_width}%;"></div>
                </div>
            </td>
        </tr>"""
    
    sources_html = ""
    for source, count in list(data["sources"].items())[:10]:
        sources_html += f"<li style='color:#e8e0d0; padding:4px 0;'>📚 {source}: {count}件</li>"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #0a0a0a; color: #e8e0d0; margin: 0; padding: 20px; }}
  .container {{ max-width: 800px; margin: 0 auto; }}
  .header {{ background: linear-gradient(135deg, #0d0d0d, #1a1400); border: 1px solid #b8960c; border-radius: 8px; padding: 30px; text-align: center; margin-bottom: 20px; }}
  .header h1 {{ color: #c9a84c; font-size: 28px; letter-spacing: 3px; margin: 0; }}
  .header p {{ color: #6a5a3a; font-size: 12px; letter-spacing: 2px; margin-top: 8px; }}
  .card {{ background: linear-gradient(135deg, #0f0f0f, #1a1a0f); border: 1px solid #2a2a1a; border-left: 3px solid #b8960c; border-radius: 4px; padding: 20px; margin-bottom: 15px; }}
  .card h2 {{ color: #c9a84c; font-size: 16px; letter-spacing: 2px; margin: 0 0 15px 0; }}
  .stat {{ display: inline-block; text-align: center; padding: 15px 25px; background: #1a1400; border: 1px solid #3a3020; border-radius: 4px; margin: 5px; }}
  .stat .number {{ color: #c9a84c; font-size: 36px; font-weight: bold; }}
  .stat .label {{ color: #6a5a3a; font-size: 11px; letter-spacing: 1px; margin-top: 5px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  .gold-line {{ height: 1px; background: linear-gradient(90deg, transparent, #b8960c, transparent); margin: 20px 0; }}
  .version {{ background: #1a1400; border: 1px solid #b8960c; border-radius: 20px; padding: 4px 12px; color: #c9a84c; font-size: 11px; display: inline-block; margin-top: 10px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>⚖️ LEGAL AI AGENT</h1>
    <p>DAILY LEARNING REPORT · 日次学習レポート</p>
    <p>{data['date']}</p>
    <div class="version">VERSION {datetime.now().strftime('%Y.%m.%d')}</div>
  </div>

  <div class="card">
    <h2>📊 学習データ統計</h2>
    <div style="text-align:center;">
      <div class="stat">
        <div class="number">{data['total']}</div>
        <div class="label">総学習件数</div>
      </div>
      <div class="stat">
        <div class="number">{data['today']}</div>
        <div class="label">本日の新規学習</div>
      </div>
      <div class="stat">
        <div class="number">{len(data['countries'])}</div>
        <div class="label">対応国数</div>
      </div>
    </div>
  </div>

  <div class="gold-line"></div>

  <div class="card">
    <h2>🌍 国別学習データ</h2>
    <table>{countries_html}</table>
  </div>

  <div class="card">
    <h2>📚 学習済み法律・文書（上位10件）</h2>
    <ul>{sources_html}</ul>
  </div>

  <div class="gold-line"></div>

  <div class="card">
    <h2>🎯 AIの現在のレベル</h2>
    <ul>
      <li style="color:#e8e0d0; padding:6px 0;">⚖️ 日本法務：司法試験レベル対応中</li>
      <li style="color:#e8e0d0; padding:6px 0;">🇺🇸 米国法務：バー試験レベル対応中</li>
      <li style="color:#e8e0d0; padding:6px 0;">🇪🇺 EU法務：GDPR・競争法・MiCA対応中</li>
      <li style="color:#e8e0d0; padding:6px 0;">🌏 アジア法務：中国・韓国・シンガポール対応中</li>
      <li style="color:#e8e0d0; padding:6px 0;">💊 薬機法・FDA：医薬品・再生医療・化粧品対応中</li>
      <li style="color:#e8e0d0; padding:6px 0;">🔗 ブロックチェーン：SEC・CFTC・MiCA対応中</li>
    </ul>
  </div>

  <div style="text-align:center; color:#3a3020; font-size:11px; margin-top:20px; letter-spacing:1px;">
    ⚖️ LEGAL AI AGENT · ISB BIOT · {data['date']}
  </div>
</div>
</body>
</html>"""
    
    return html

def send_email_report(to_email: str, smtp_user: str, smtp_password: str):
    data = get_report()
    html_content = generate_report_html(data)
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"⚖️ Legal AI 日次学習レポート {data['date']}"
    msg['From'] = smtp_user
    msg['To'] = to_email
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"✅ レポートを{to_email}に送信しました")
    except Exception as e:
        print(f"⚠️ メール送信エラー: {e}")

if __name__ == "__main__":
    data = get_report()
    html = generate_report_html(data)
    
    # HTMLファイルとして保存
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ レポートを生成しました")
    print(f"📊 総学習件数: {data.get('total', 0)}件")
    print(f"📅 本日の新規学習: {data.get('today', 0)}件")
    print(f"🌍 対応国数: {len(data.get('countries', {}))}国")
    print(f"\n📄 report.htmlを開いてレポートを確認してください")