# 个人笔记 RAG 智能问答系统

一个完全本地化的个人笔记问答系统：用本地 embedding 模型把笔记向量化，存进本地 Chroma 向量库，再用检索增强生成（RAG）结合智谱 GLM-4-Flash 大模型回答你的问题。

- 检索在**本地**完成，不联网也能搜；
- 大模型调用走智谱开放平台（需自备 API Key）；
- 提供 Web API（FastAPI）与命令行两种使用方式。

## 目录结构

```
.
├── build_db.py        # 把 notes.json 向量化并写入本地 Chroma 库
├── main.py            # FastAPI 服务：POST /ask 问答接口
├── query.py           # 命令行版：直接检索 + 问答
├── requirements.txt   # Python 依赖
├── Dockerfile         # 容器化部署
├── notes.example.json # 笔记示例（真实笔记请放 notes.json，已被 .gitignore 忽略）
├── local_model/       # 本地 embedding 模型（需自行下载，见下）
└── chroma_db/         # 向量库（构建后生成，已忽略）
```

## 环境要求

- Python 3.11+
- 一个本地 sentence-transformers embedding 模型（例如 `BAAI/bge-small-zh-v1.5`）
- 智谱开放平台 API Key（https://open.bigmodel.cn）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备本地 embedding 模型

把模型下载到项目下的 `local_model/` 目录（需包含 `model.safetensors`、`config.json`、`tokenizer.json` 等）：

```bash
# 任选其一：
# 方式 A：用 huggingface
hf download BAAI/bge-small-zh-v1.5 --local-dir local_model
# 方式 B：或用 transformers / modelscope 下载后放到 local_model/
```

### 3. 准备笔记

复制示例并填入你的笔记：

```bash
cp notes.example.json notes.json
# 然后编辑 notes.json，格式：
# [{"id": 1, "title": "标题", "content": "正文..."}, ...]
```

### 4. 构建向量库

```bash
python build_db.py
```

### 5. 配置 API Key

不要把 Key 写进代码。用环境变量：

```bash
export ZHIPU_API_KEY="你的智谱APIKey"
```

### 6. 启动问答

**Web API 方式：**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

```bash
curl -X POST http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question": "你的笔记里提到客户会议了吗？"}'
```

**命令行方式：**

```bash
python query.py "你的笔记里提到客户会议了吗？"
```

## Docker 部署

```bash
docker build -t notes-rag .
docker run -p 8000:8000 -e ZHIPU_API_KEY=你的Key notes-rag
```

## 工作原理

1. `build_db.py` 加载本地 embedding 模型，把 `notes.json` 每条笔记编码成向量，存入本地 Chroma（`chroma_db/`）。
2. 提问时，先用语义检索从向量库取回最相关的 3 条笔记作为上下文。
3. 把上下文 + 问题发给智谱 GLM-4-Flash，由大模型基于**你的笔记内容**作答，并回传来源标题。

## 隐私说明

- 笔记原文与向量库全部保存在**本机**，检索过程不联网、不上传。
- 只有「问题 + 命中的笔记片段」会发送给智谱 API 用于生成答案。
- 请勿将 `notes.json`、`local_model/` 提交到公开仓库（已在 `.gitignore` 中忽略）。

## License

MIT
