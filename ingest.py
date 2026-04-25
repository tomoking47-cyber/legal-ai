import os
import chromadb
from pypdf import PdfReader
from docx import Document

docs_folder = "./docs"
chroma_client = chromadb.PersistentClient(path="./chroma_db")

try:
    chroma_client.delete_collection("legal_docs")
except:
    pass

collection = chroma_client.create_collection("legal_docs")

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def split_text(text, chunk_size=500):
    chunks = []
    words = text.split()
    current = []
    count = 0
    for word in words:
        current.append(word)
        count += len(word)
        if count >= chunk_size:
            chunks.append(" ".join(current))
            current = []
            count = 0
    if current:
        chunks.append(" ".join(current))
    return chunks

files = os.listdir(docs_folder)
total = 0

for filename in files:
    file_path = os.path.join(docs_folder, filename)
    text = ""
    
    if filename.endswith(".pdf"):
        print(f"📄 PDF読み込み中: {filename}")
        text = read_pdf(file_path)
    elif filename.endswith(".docx"):
        print(f"📝 Word読み込み中: {filename}")
        text = read_docx(file_path)
    else:
        continue
    
    if not text.strip():
        print(f"⚠️ テキストが読み取れませんでした: {filename}")
        continue
    
    chunks = split_text(text)
    
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            ids=[f"{filename}_{i}"],
            metadatas=[{"source": filename}]
        )
        total += 1
    
    print(f"✅ {filename}: {len(chunks)}件のデータを登録しました")

print(f"\n🎉 完了！合計{total}件のデータを学習しました")
