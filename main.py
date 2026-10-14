import os
import chromadb
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="个人笔记 RAG 助手")

# 加载本地模型
model = SentenceTransformer(os.path.join(BASE_DIR, 'local_model'))

# 连接向量库
client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, 'chroma_db'))
collection = client.get_collection("notes")

# 智谱 API Key —— 从环境变量读取，切勿硬编码写死
API_KEY = os.getenv("ZHIPU_API_KEY")
if not API_KEY:
    raise RuntimeError("缺少环境变量 ZHIPU_API_KEY，请先 export ZHIPU_API_KEY=你的智谱APIKey")

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(query: Query):
    # 1. 检索
    q_vector = model.encode(query.question).tolist()
    results = collection.query(query_embeddings=[q_vector], n_results=3)
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    # 2. 拼上下文
    context = "\n".join([f"[{m['title']}] {d}" for d, m in zip(docs, metas)])

    # 3. 调用智谱 GLM-4-Flash
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "glm-4-flash",
        "messages": [
            {"role": "system", "content": "你是一个个人笔记助手，根据提供的笔记内容回答问题。"},
            {"role": "user", "content": f"笔记内容：\n{context}\n\n问题：{query.question}"}
        ]
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)

    # 调试输出
    print("=" * 50)
    print("智谱状态码:", resp.status_code)
    print("智谱返回内容:", resp.text)
    print("=" * 50)

    if resp.status_code != 200:
        return {
            "error": "智谱API调用失败",
            "status_code": resp.status_code,
            "raw_response": resp.text
        }

    data = resp.json()
    answer = data["choices"][0]["message"]["content"]

    return {
        "question": query.question,
        "answer": answer,
        "sources": [m["title"] for m in metas]
    }

@app.get("/")
def root():
    return {"status": "ok", "message": "RAG 服务运行中"}