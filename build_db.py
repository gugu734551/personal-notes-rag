import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

# 动态获取当前脚本所在目录，无论从哪里启动都不会迷路
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 加载本地模型
model = SentenceTransformer(os.path.join(BASE_DIR, 'local_model'))

# 2. 读取笔记
with open(os.path.join(BASE_DIR, 'notes.json'), 'r', encoding='utf-8') as f:
    notes = json.load(f)

# 3. 初始化本地 Chroma
client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, 'chroma_db'))

try:
    client.delete_collection("notes")
except Exception:
    pass

collection = client.get_or_create_collection("notes")

# 4. 写入向量
for note in notes:
    vector = model.encode(note["content"]).tolist()
    collection.upsert(
        embeddings=[vector],
        documents=[note["content"]],
        metadatas=[{"title": note["title"]}],
        ids=[str(note["id"])]
    )

print(f"向量库构建完成！共写入 {len(notes)} 条笔记。")