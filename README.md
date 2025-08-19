**Oxylabs RAG QA System**

A fast, containerized Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, ChromaDB, and OpenAI. It ingests Oxylabs developer documentation (.txt files), creates semantic embeddings, and answers user queries by retrieving relevant document chunks and generating concise responses.

---

## 🚀 Features

- **Markdown-aware chunking**: Splits documents using `MarkdownTextSplitter` for logical chunk boundaries.
- **Configurable settings**: Centralized with Pydantic `BaseSettings` and `.env` support.
- **ChromaDB vector store**: Persists embeddings for fast startup.
- **MMR-based retrieval**: Maximal Marginal Relevance balances relevance and diversity.
- **GPT-4o generation**: High-fidelity, concise answers with token limits.
- **FastAPI endpoints**: `GET /health` and `POST /query` with Pydantic validation.
- **Containerized**: Dockerfile and docker-compose for quick deployment.

---

## 📦 Repository Structure

```text
├── data/                # Input .txt documentation files
├── chroma_db/           # Persisted vector database
├── env.                 # Environment variable definitions
├── docker-compose.yml   # Service orchestration
├── Dockerfile           # Container image definition
├── example_prompts.txt  # Sample queries for testing
├── main.py              # API entrypoint and RAG setup
├── requirements.txt     # Python dependencies
└── README.md            # Project overview and instructions
```

---

## 🔧 Prerequisites

- Docker & Docker Compose
- OpenAI API key with sufficient quota
- Python 3.13 (for local dev if not using Docker)

---

## ⚙️ Configuration

Create a `.env` file in the project root with an OPENAI_API_KEY:


> **Note**: `DATA_DIR` should contain your Oxylabs documentation `.txt` files.

---

## 🛠️ Installation & Running

### Local without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using Docker

1. Build the image:
   ```bash
   docker build -t oxylabs-rag .
   ```
2. Start services:
   ```bash
   docker-compose up -d
   ```
3. Check logs:
   ```bash
   docker-compose logs -f rag_app
   ```

---

## 🎯 API Usage

### Health Check

```bash
curl http://localhost:8000/health
# Response: { "status": "ok" }
```

### Query Endpoint

```bash
curl -X 'POST' \
  'http://localhost:8000/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "How do I authenticate with the Web Scraper API?"
}'
```

**Sample Response:**

```json
{
  "answer": "To authenticate with the Web Scraper API, you need to create your API user credentials by signing up for a free trial or purchasing the product in the Oxylabs dashboard. This will provide you with a `USERNAME` and `PASSWORD` that you can use for authentication.",
  "sources": [
    "./data/getting_started.txt",
    "./data/LangChain.txt",
    "./data/cloud_storage.txt"
  ]
}
```



---

## 📝 Example Prompts

See `example_prompts.txt` for a curated list of test questions covering authentication, pricing, proxy usage, and more.

---

## 📈 Monitoring & Logging

- Logs are output to the console and can be routed to a file or centralized logger.
- Customize `logging.basicConfig` in `main.py` to integrate with external monitoring tools.

---

## 🔒 Security & Authentication

For production, protect the `/query` endpoint with API keys or JWTs. FastAPI’s `fastapi.security` module can be used to implement this.

---

## 🔄 Data Freshness

To refresh the vector store without restarting, consider adding an admin endpoint (`POST /reload_docs`) that calls:

```python
vectordb = Chroma.from_documents(...)
vectordb.persist()
```

---

## 💡 Future Improvements

- **Authentication**: API key or OAuth on `/query`.
- **Observability**: Prometheus metrics and Grafana dashboards.
- **Scalability**: Deploy vector store as a separate service, cache frequent queries.
- **Cost Optimization**: Use smaller embedding models for non-critical chunks.
- **Testing**: Add unit tests for chunking and end-to-end tests for the API.

---

## 🏁 Credits

Built with ❤️ using FastAPI, LangChain, ChromaDB, and OpenAI APIs.

