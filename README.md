# Oxylabs RAG QA System

A fast, containerized Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, ChromaDB, and OpenAI. It ingests Oxylabs developer documentation (.txt files), creates semantic embeddings, and answers user queries by retrieving relevant document chunks and generating concise responses.

---

## Table of Contents

- [Features](#features)  
- [Repository Structure](#repository-structure)  
- [Prerequisites](#prerequisites)  
- [Configuration](#configuration)  
- [Installation & Running](#installation--running)  
- [API Usage](#api-usage)  
- [Testing the LLM](#testing-the-llm)  
- [System Showcase](#system-showcase)
- [Example Prompts](#example-prompts)  
- [Current Limitations](#current-limitations)
- [Production-Ready Improvements](#production-ready-improvements)
- [Monitoring & Logging](#monitoring--logging)  
- [Security & Authentication](#security--authentication)  
- [Data Freshness](#data-freshness)  
- [Future Improvements](#future-improvements)  
- [Credits](#credits)  

---

## 🚀 Features

- **Markdown-aware chunking**: Splits documents using `MarkdownTextSplitter` for logical chunk boundaries.  
- **Configurable settings**: Centralized with Pydantic `BaseSettings` and `.env` support.  
- **ChromaDB vector store**: Persists embeddings for fast startup; the `chroma_db/` folder is generated automatically when building or running the Docker image.  
- **MMR-based retrieval**: Maximal Marginal Relevance balances relevance and diversity.  
- **GPT-4o generation**: High-fidelity, concise answers with token limits.  
- **FastAPI endpoints**: `GET /health` and `POST /query` with Pydantic validation.  
- **Containerized**: Dockerfile and docker-compose for quick deployment.

---

## 📦 Repository Structure

```text
├── data/                # Input .txt documentation files for chunking
├── chroma_db/           # Auto-generated vector database directory
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

Create a `.env` file in the project root with your OpenAI API key:

```dotenv
OPENAI_API_KEY=your_openai_api_key_here
```

> **Note:** The `data_dir` folder (as configured in `main.py`) must contain all your Oxylabs documentation `.txt` files for chunking.

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
curl -X POST \
  http://localhost:8000/query \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
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

## 🧪 Testing the LLM

Use the built-in Swagger UI to interactively test endpoints and your retrieval-augmented LLM:

**[http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)**

The Swagger interface provides:
- Interactive API documentation
- Request/response examples  
- Direct endpoint testing
- Parameter validation and error handling

---

## 🎪 System Showcase

### Running Locally

After starting the application locally, you can test the system with these Oxylabs-specific queries:

#### Authentication & Setup
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

## ⚠️ Current Limitations

### 1. **Vector Store Persistence**
- ChromaDB runs in-memory during development, losing data on container restarts
- No backup or replication mechanisms for the vector database
- Single-point-of-failure for the entire retrieval system

### 2. **Document Processing**
- Only supports `.txt` files; cannot process PDFs, HTML, or structured documentation
- No incremental document updates - requires full reprocessing for any changes
- Limited chunk size optimization for different document types

### 3. **Scalability Constraints**
- Single-threaded processing during document ingestion
- No horizontal scaling capabilities for concurrent queries
- Memory usage grows linearly with document corpus size

### 4. **Security Vulnerabilities**
- API endpoints lack authentication and rate limiting
- OpenAI API key stored in environment variables without encryption
- No audit logging for query access patterns

### 5. **Reliability Issues**
- No circuit breakers for OpenAI API failures
- Missing retry mechanisms for transient errors
- No graceful degradation when vector store is unavailable

### 6. **Performance Bottlenecks**
- Synchronous processing blocks concurrent requests
- No caching layer for frequently asked questions
- Embedding generation happens on every document update

### 7. **Monitoring Gaps**
- Basic console logging without structured formats
- No metrics collection for query latency or accuracy
- Missing alerting for system failures or performance degradation

---

## 🏗️ Production-Ready Improvements

### **Scalability & Performance**

#### **Horizontal Scaling**
- **Load Balancer**: Deploy behind nginx or AWS ALB to distribute traffic
- **Container Orchestration**: Use Kubernetes with auto-scaling based on CPU/memory
- **Microservices Architecture**: Separate retrieval, generation, and embedding services
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: rag-api
        image: oxylabs-rag:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### **Caching Strategy**
- **Redis Cache**: Store frequent query-response pairs with TTL
- **Embedding Cache**: Persist computed embeddings to avoid recomputation
- **Response Caching**: Cache similar questions using semantic similarity

#### **Async Processing**
- **Background Jobs**: Use Celery for document processing and embedding generation
- **Streaming Responses**: Implement Server-Sent Events for real-time answer generation
- **Connection Pooling**: Optimize database and API connections

### **Data Freshness & Update Mechanisms**

#### **Real-Time Updates**
```python
# Document Update Pipeline
@app.post("/admin/update-docs")
async def update_documents():
    """Hot-reload documents without downtime"""
    # 1. Download latest docs from source
    # 2. Process incrementally 
    # 3. Update vector store with new embeddings
    # 4. Swap old index with new (blue-green deployment)
    pass
```

#### **Change Detection**
- **File Monitoring**: Watch documentation repositories for changes
- **Webhook Integration**: Trigger updates when documentation is published
- **Version Control**: Track document versions and rollback capabilities

#### **Data Pipeline**
- **ETL Process**: Extract from multiple sources (Git, CMS, APIs)
- **Data Validation**: Ensure document quality before embedding
- **Incremental Processing**: Only update changed documents

### **Security & Authentication**

#### **API Security**
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/query")
async def query(request: QueryRequest, user=Depends(verify_token)):
    # Secure endpoint implementation
    pass
```

#### **Security Measures**
- **Rate Limiting**: Implement per-user/IP rate limits using Redis
- **Input Validation**: Sanitize queries to prevent injection attacks
- **Encryption**: Encrypt sensitive data at rest and in transit
- **RBAC**: Role-based access control for different user types

#### **Compliance**
- **Audit Logging**: Track all API calls with user context
- **GDPR Compliance**: Data retention policies and user data deletion
- **SOC 2**: Implement security controls for enterprise customers

### **Monitoring & Observability**

#### **Metrics Collection**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Custom metrics
query_counter = Counter('rag_queries_total', 'Total queries processed')
query_duration = Histogram('rag_query_duration_seconds', 'Query processing time')
embedding_cache_hits = Counter('embedding_cache_hits_total', 'Cache hits')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    query_duration.observe(time.time() - start_time)
    query_counter.inc()
    return response
```

#### **Observability Stack**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Dashboards for system health and performance
- **Jaeger**: Distributed tracing for request flows
- **ELK Stack**: Centralized logging with Elasticsearch, Logstash, Kibana

#### **Health Checks**
- **Deep Health Checks**: Verify database connectivity, API availability
- **Circuit Breakers**: Prevent cascade failures
- **SLA Monitoring**: Track uptime, response times, error rates

### **Cost Optimization**

#### **OpenAI API Optimization**
```python
# Cost-aware model selection
def select_model_by_complexity(query: str) -> str:
    if len(query) < 50 and is_simple_query(query):
        return "gpt-3.5-turbo"  # Cheaper for simple queries
    return "gpt-4o"  # Full capability for complex queries

# Token management
def optimize_context(chunks: List[str], max_tokens: int = 4000) -> List[str]:
    """Intelligently truncate context to stay within token limits"""
    return select_most_relevant_chunks(chunks, max_tokens)
```

#### **Infrastructure Optimization**
- **Spot Instances**: Use AWS Spot for non-critical workloads (70% cost savings)
- **Auto-scaling**: Scale down during low-traffic periods
- **Resource Right-sizing**: Monitor and optimize container resource allocation

#### **Embedding Optimization**
- **Model Selection**: Use lighter embedding models for development/testing
- **Batch Processing**: Process multiple documents simultaneously
- **Compression**: Compress vector embeddings to reduce storage costs

#### **Operational Efficiency**
- **Reserved Instances**: Long-term AWS commitments for predictable workloads
- **Multi-region Deployment**: Optimize costs based on geographic usage
- **Data Lifecycle**: Archive old embeddings and implement retention policies

---

## 📈 Monitoring & Logging

- Logs are output to the console and can be routed to a file or centralized logger.  
- Customize `logging.basicConfig` in `main.py` to integrate with external monitoring tools.  

---

## 🔒 Security & Authentication

For production, protect the `/query` endpoint with API keys or JWTs. FastAPI's `fastapi.security` module can be used to implement this.

---

## 🔄 Data Freshness

To refresh the vector store without restarting, consider adding an admin endpoint (`POST /reload_docs`) that calls:

```python
vectordb = Chroma.from_documents(...)
vectordb.persist()
```

---

## 💡 Future Improvements

- **Multi-language Support**: Support for documentation in multiple languages
- **Advanced RAG Techniques**: Implement RAG-Fusion, Self-RAG, or Corrective RAG
- **Knowledge Graph Integration**: Combine vector search with knowledge graphs
- **Fine-tuned Models**: Custom embedding models trained on Oxylabs documentation
- **Conversational Memory**: Maintain context across multiple queries in a session

---

## 🏁 Credits

Built with ❤️ using FastAPI, LangChain, ChromaDB, and OpenAI APIs.