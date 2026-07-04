
# CampusBot: DTU Hybrid-Search RAG Engine

CampusBot is a rate-limit-proof Retrieval-Augmented Generation (RAG) assistant designed for Delhi Technological University (DTU). It uses pre-computed local indices for both dense semantic matching and sparse keyword search. Since the indices are generated before deployment and tracked inside the repository, the system loads instantly and avoids runtime embedding generation and API bottlenecks.

---

## Project Context & Problem Statement

Navigating the DTU web infrastructure can be time-consuming because important information is scattered across multiple locations.

### Problems Addressed

- **Information Fragmentation**
  - Updates, evaluation metrics, notices, and policies are distributed across multiple pages and PDFs.

- **Lack of Dynamic Discovery**
  - Students must manually scan large files to locate specific rules or regulations.

- **Search Failure Problem**
  - Traditional keyword search fails when users do not know the exact wording used in official documents.

CampusBot solves these issues by transforming documents into a semantic search space where users can ask questions naturally.

---

## Practical Applications

### 1. Automated Policy Auditing for Placement Coordinators

**Manual Process**
- Download T&P policy documents.
- Search through multiple amendments.
- Read large sections manually.

**Using CampusBot**
Query:

> "What is the attendance policy for placement coordinators?"

CampusBot retrieves and combines information across multiple documents and returns a summarized answer instantly.

---

### 2. Examination Registration Assistance

**Manual Process**
- Navigate through examination notices.
- Find relevant PDF archives.
- Search manually for deadlines and criteria.

**Using CampusBot**
Queries:

> "Show examination registration guidelines"

> "What happens if I miss the registration deadline?"

CampusBot instantly retrieves the relevant information and returns a concise response.

---

## Core Features

### 1. Hybrid Retrieval Architecture

#### Dense Semantic Matching
Uses **FAISS (`faiss-cpu`)** to capture query intent even when exact words differ.

#### Sparse Lexical Matching
Uses **BM25 (`rank_bm25`)** to locate technical terms, rules, and keywords.

#### Reciprocal Rank Fusion (RRF)
Combines dense and sparse retrieval scores to improve context quality.

---

### 2. Performance & Stability

#### Zero Runtime Embedding Overhead
- Documents are embedded before deployment.
- Active containers load indices directly from disk.

#### Rate-Limit Resilience
- Eliminates dependency on live embedding requests.
- Avoids `429 RESOURCE_EXHAUSTED` issues.

#### OpenMP Runtime Guard
Prevents library conflicts such as:

```text
libomp.dylib aborts
```

Supports macOS (Apple Silicon) and Linux environments.

---

### 3. Unified User Interface

#### Dynamic Routing

Frontend scripts automatically switch between:

- Local:
```text
localhost:5001
```

- Production deployment endpoints

#### Structured Response Enforcement

The LLM layer returns sanitized JSON responses to maintain a clean UI.

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend | HTML5, CSS3 |
| Backend | Flask + CORS |
| Vector Database | FAISS |
| Keyword Search | BM25 |
| LLM | Google Gemini (`gemini-2.5-flash`) |
| SDK | `google-genai` |

---

## Evaluation & Performance Metrics

To ensure high reliability, accuracy, and rapid response times for Delhi Technological University (DTU) students and faculty, CampusBot has been benchmarked using industry-standard RAG evaluation frameworks and latency testing.

### 1. RAGAS Quality Evaluation
We evaluated CampusBot using the **RAGAS (Retrieval Augmented Generation Assessment)** framework with Vertex AI and local embeddings. The system achieves exceptional performance across all primary metrics:

| Metric | Score | Description |
| :--- | :---: | :--- |
| **Faithfulness** | **0.9400** | Measures how factually accurate the generated answer is grounded in the retrieved DTU context without hallucinations. |
| **Context Recall** | **0.9200** | Measures the retriever's ability to fetch all necessary institutional rules, policies, and circulars needed to answer the query. |
| **Context Precision** | **0.9000** | Evaluates whether the most relevant document chunks are ranked at the very top of the retrieval results. |
| **Answer Correctness** | **0.8920** | Assesses the overall accuracy and semantic alignment of the answer against ground-truth institutional facts. |
| **Answer Relevancy** | **0.8893** | Measures how directly and concisely the answer addresses the user's specific prompt without redundancy. |

> [!NOTE]
> High scores across **Faithfulness (94%)** and **Context Recall (92%)** validate that the hybrid FAISS + BM25 retrieval architecture with Reciprocal Rank Fusion (RRF) effectively captures complex policy amendments and technical terms while minimizing hallucinations.

---

### 2. Latency Benchmark
System latency was benchmarked across end-to-end query execution (including hybrid retrieval, RRF fusion scoring, and Gemini LLM response generation):

- **Average Latency**: `2.687 seconds/query`
- **Fastest Query**: `2.456 seconds`
- **Slowest Query**: `3.074 seconds`
- **Total Execution Time**: `13.434 seconds` across 5 complex institutional queries.

By pre-computing local FAISS and BM25 indices on disk, CampusBot achieves sub-3-second average response times with zero runtime embedding generation overhead.

---

## Directory Structure

```text
campus-bot/
│
├── data/
│   └── Source material, PDFs, and circulars
│
├── db/
│   ├── index.faiss
│   ├── index.pkl
│   └── bm25.pkl
│
├── eval/
│   ├── generate_eval_dataset.py  # Script to generate evaluation datasets
│   ├── ragas_eval_hf.py          # RAGAS evaluation using HuggingFace embeddings
│   └── run_ragas_eval.py         # Main RAGAS evaluation pipeline
│
├── templates/
│   └── index.html
│
├── .env
├── .gitignore
├── app.py
├── ingest.py                     # Document indexing and embedding pipeline
├── latency_time.txt              # Latency benchmark results
├── rag_engine.py                 # Core RAG retrieval and fusion logic
├── ragas_detailed_results.csv    # Granular per-query RAGAS metrics
├── ragas_final_results.txt       # Summary RAGAS evaluation averages
├── requirements.txt
└── time-test.py                  # Automated latency benchmarking script
```

---

## Administrative Operations Manual

### Step 1: Update Local Data

Place updated documents inside:

```text
campus-bot/data/
```

Remove outdated documents to avoid retrieval conflicts.

---

### Step 2: Regenerate Search Indices

Activate the environment:

```bash
source .venv/bin/activate
python ingest.py
```

This process:

- Reads raw documents
- Chunks content
- Generates embeddings
- Updates:

```text
db/index.faiss
db/index.pkl
db/bm25.pkl
```

---

### Step 3: Verify Changes Locally

Run:

```bash
python app.py
```

Open:

```text
http://localhost:5001
```

Verify updated responses.

---

### Step 4: Push to Production

```bash
git add data/ db/
git commit -m "Admin: Re-indexed campus documentation database"
git push origin main
```

Deployment updates automatically after the push.

---

## Local Installation & Verification

### 1. Clone Repository

```bash
git clone https://github.com/your-username/campus-bot.git

cd campus-bot

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

### 2. Configure Environment Variables

Create:

```text
.env
```

Add:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

### 3. Start Development Server

```bash
python app.py
```

Open:

```text
http://localhost:5001
```

---

## Production Deployment (Render)

### Web Service Settings

| Setting | Value |
|-----------|--------|
| Runtime | Python 3 |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |

### Production Environment Variables

| Key | Purpose |
|------|----------|
| `GEMINI_API_KEY` | Authentication for Gemini |
| `KMP_DUPLICATE_LIB_OK=TRUE` | Prevent OpenMP runtime conflicts |

---

## Security Parameters

Recommended `.gitignore`:

```gitignore
.env
.env*

__pycache__/
*.pyc
.DS_Store
.vscode/
.idea/
tempCodeRunnerFile.py

# Keep db tracked
```

---

## Architecture Flow

```text
[User Query]
      │
      ▼
[Dynamic Routing]
      │
      ▼
[rag_engine.py]
      ├── Dense Search (FAISS)
      └── Sparse Search (BM25)
      │
      ▼
[Fused Context]
      │
      ▼
[Gemini API]
      │
      ▼
[JSON Response]
      │
      ▼
[Frontend UI]
```
