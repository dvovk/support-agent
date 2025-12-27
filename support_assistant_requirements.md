# Project: Support Knowledge Assistant for Discord + Codebase

## 1) Overview
Build a support assistant that answers user questions and suggests fixes by grounding responses in:
- Historical Discord Q&A (initially provided as a static export).
- Public GitHub repository code and docs.
Later, it should automatically ingest new Discord messages and repo changes to stay current.

The assistant should recommend practical steps (e.g., restart service, clear cache, update config) based on known resolutions and code behavior. The system should be cost‑effective and start with a free‑tier model to validate accuracy before moving to a paid tier.

## 2) Goals
- Provide accurate support answers grounded in Discord discussions and code.
- Surface known fixes/solutions with concrete steps.
- Stay up to date as Discord and GitHub content changes.
- Support a free/low‑cost MVP and scale later.

## 3) Non‑Goals (initially)
- Fully automated code changes and deployments.
- Writing to Discord or committing to GitHub automatically.
- Training a custom LLM from scratch.

## 4) Users
- End users asking support questions.
- Maintainers needing quick diagnosis and consistent responses.

## 5) Core Use Cases
- “How do I fix X error?” → cite Discord resolution steps.
- “Why is feature Y failing?” → reference relevant code path and known issues.
- “What changed recently?” → use latest repo updates.

## 6) Data Sources
- Discord history (initial export).
- Public GitHub repo (code + docs + issues if desired).
- Later: live Discord via bot/API + GitHub webhook/polling.

## 7) System Approach (Recommended MVP)
Use Retrieval‑Augmented Generation (RAG) instead of fine‑tuning:
- Cheaper and faster to validate.
- Always up‑to‑date if the index is refreshed.
- Easier to inspect and debug.

## 8) Functional Requirements
- Ingest and normalize Discord history (messages, threads, timestamps, author, channel).
- Ingest GitHub repo content (README, docs, code files).
- Chunk content with context (channel, thread, file path).
- Create embeddings and store in a vector database.
- At query time:
  - Retrieve top relevant chunks.
  - Generate an answer grounded in those chunks.
  - Include references (Discord message links or file paths).
- Support update pipeline for new Discord and repo changes.
- Provide a “suggested fix steps” section when applicable.

## 9) Non‑Functional Requirements
- Cost: free tier model for MVP, low recurring costs.
- Latency: reasonable response time (<5–10s for MVP).
- Reliability: high confidence for known issues; decline when evidence is weak.
- Explainability: cite sources in each response.

## 10) Model Strategy
MVP (free/low‑cost options):
- Open‑source local models (Llama 3 8B, Mistral 7B) if you can run on GPU.
- Free API tiers (Groq/Together/Fireworks can be used for prototyping).
Production:
- Paid APIs (OpenAI/Anthropic) or larger hosted open‑source models.

## 11) Architecture (MVP)
- Ingestion: Discord export + GitHub clone.
- Processing: clean, dedupe, chunk.
- Embedding: open‑source embedding model or hosted embedding API.
- Vector store: local (Chroma, FAISS) or hosted (Pinecone).
- Retriever + Reranker (optional).
- LLM response layer with citation‑based answers.

## 12) Update Strategy
Phase 1: manual re‑index on new data drops.
Phase 2: automated:
- Discord bot pulls new messages periodically.
- GitHub webhook or scheduled repo pull and re‑index.

## 13) Security & Privacy
- Only public data is used.
- Store data locally or in controlled storage.

## 14) Acceptance Criteria (MVP)
- Answers reference relevant Discord or code sources.
- On known issues, fix suggestions match historical resolutions.
- Index refresh can be done in a single command.

## 15) Future Enhancements
- Fine‑tune on high‑quality Q&A pairs to improve tone and specificity.
- Add classifier to detect “known issue vs novel issue.”
- Admin UI for feedback and answer rating.
- Auto‑generate draft replies for Discord.
