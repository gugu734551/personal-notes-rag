# personal-notes-rag
个人笔记 RAG 智能问答系统 | 独立开发 | Python + FastAPI + ChromaDB + Sentence-Transformers  设计并实现本地知识库 RAG 系统，使用 BAAI/bge-small-zh-v1.5 本地向量模型，零 API 成本完成文本向量化。  基于 ChromaDB 构建向量检索服务，实现笔记语义检索，支持跨端数据复用（从 Android SQLite 导出）。  使用 FastAPI 封装 /ask 问答接口，集成智谱 GLM-4-Flash 大模型 API，实现"检索 → 拼上下文 → LLM 生成 → 返回来源"完整 RAG 链路。  编写 Dockerfile 实现容器化部署，具备工程化交付能力。
