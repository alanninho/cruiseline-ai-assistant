# Cruise Assistant

An end-to-end RAG chatbot for a cruise line's customer support use case - built to demonstrate RAG/GenAI, ML engineering, and MLOps/full-stack skills using real, messy, industry-sourced data.

**Status:** Working demo - retrieval, generation, and a chat UI run end-to-end locally. 
See [Architecture](#architecture) for what's built vs. designed.


## What it does

Ask questions about cabin types, booking policies, onboard venues, and shore excursions across five real ship documents - the assistant retrieves relevant passages from a vector database and generates a grounded answer, citing its sources. It won't answer questions outside its knowledge base.


## Architecture

![Architecture diagram](docs/cruise_assistant_architecture_diagram.png)

Frontend (Next.js) → FastAPI → pgvector (dense retrieval) → Ollama (local LLM) → answer + sources

**What's built and running:**
- Ingestion pipeline for 11 real source documents (legal T&Cs, FAQs, excursions, ship technical sheets), each with a custom chunking strategy suited to its structure
- Embeddings (`sentence-transformers`) stored in Postgres/pgvector, with a flexible JSONB metadata column for heterogeneous chunk types
- FastAPI `/query` endpoint: vector search → LLM generation via Ollama, running entirely locally
- Two-layer guardrail against hallucination: a distance-threshold cutoff, and prompt-level grounding instructing the model to answer only from retrieved context
- Next.js chat frontend, connected end-to-end

**Designed, not yet implemented** (see [Roadmap](#roadmap)):
- Hybrid search (Elasticsearch sparse + pgvector dense)
- Reranking
- Knowledge graph (Neo4j) - containerized and running, not yet populated
- Multi-agent orchestration via LangGraph, MCP tool exposure
- Model routing (local vs. hosted LLM)
- RAGAS evaluation suite
- Kubernetes deployment, CI/CD, Langfuse/Prometheus observability


## Data sources

This project uses publicly available documents from a major cruise line's website and third-party travel-agent mirrors (booking terms, FAQs, ship technical sheets, excursion listings) as realistic source material for the RAG pipeline. 
This is a non-commercial portfolio project; the cruise line's name has been kept out of the project's branding intentionally. 
No scraped PDFs, logos, or raw source documents are committed to this repository - only the processed, chunked corpus derived from them.


## Known limitations

- One ship's technical sheet (of five) uses a different page layout and isn't parsed by the current venue extractor — documented, not fixed
- The similarity-threshold guardrail is loosely tuned; the primary defense against hallucination is prompt-level grounding, not the distance cutoff
- Retrieval is dense-only (pgvector); hybrid sparse+dense search was designed but not implemented
- No automated evaluation suite yet (RAGAS) — quality has been checked manually against known-good queries during development
- **Cross-encoder reranking was implemented but didn't clearly improve answer quality in testing** — on broad policy questions, it sometimes demoted the most complete clause in favor of a more narrowly relevant but less useful one. Likely cause: reranking scores query-chunk relevance in isolation, with no notion of which chunk is the *most complete* answer to a broad question. Left in the codebase (togglable in principle) as a documented, tested finding rather than a proven improvement — a good example of why reranking effectiveness is corpus and query-dependent, not a guaranteed win.

## Running locally

**Prerequisites:** Docker Desktop, `uv`, Node.js, [Ollama](https://ollama.com/download)

**1. Clone and set up environment variables**
```bash
git clone https://github.com/<your-username>/cruiseline-ai-assistant.git
cd cruiseline-ai-assistant
cp .env.example .env
```

**2. Start the backend services**
```bash
cd infra/docker
docker compose up -d
```

**3. Pull the local LLM**
```bash
ollama pull llama3.2:3b
```

**4. Set up Python and load the pre-built corpus** (from the project root)
```bash
uv sync
uv run python -m ingestion.load_vectors
```
This embeds and loads `data/processed/corpus.json` - the already-chunked corpus committed to this repo - into pgvector. (Raw scraped source documents aren't included; see `ingestion/scrapers/` and `ingestion/build_corpus.py` for how the corpus was originally generated.)

**5. Start the API**
```bash
uv run uvicorn api.main:app --reload
```

**6. Start the frontend** (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
```

**7. Open the app**
Visit `http://localhost:3000` and start asking questions.

> Note: Postgres runs on port `5433` (not the default `5432`) to avoid 
> conflicts with local Postgres installs - see `docker-compose.yml`.


## Tech stack

**Backend & retrieval**
- Python, FastAPI
- pgvector (Postgres extension) - vector similarity search
- `sentence-transformers` (all-MiniLM-L6-v2) - embeddings
- Ollama (Llama 3.2 3B) - local LLM inference

**Frontend**
- Next.js, React, TypeScript, Tailwind CSS

**Infrastructure**
- Docker, Docker Compose

**Data pipeline**
- `pypdf` - PDF text extraction
- `pdfplumber` - table extraction (technical sheets)
- Custom regex-based chunking strategies per document type (legal clauses, FAQ pairs, excursion records, venue tables)

