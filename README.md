# 🌿 EcoGuide AI — Sustainable Living Assistant

An AI-powered eco lifestyle agent built with **Python Flask** and **IBM Watsonx.ai**.  
Uses **RAG (Retrieval-Augmented Generation)** — every response is grounded in verified knowledge  
from UNEP, IPCC, IEA, EPA, FAO, and government sources, retrieved via **IBM Slate embeddings** and **ChromaDB**.

> **AI model auto-selects per region** — uses `ibm/granite-3-3-8b-instruct` where available,  
> falls back to `meta-llama/llama-3-3-70b-instruct` (e.g. `au-syd`).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Chat | Natural language Q&A — ask anything about sustainable living |
| 🧠 RAG Pipeline | Responses grounded in 10 trusted eco knowledge documents |
| 🔍 Source Citations | Every AI answer shows clickable sources with relevance % |
| 🌱 Eco Tips | 8 actionable daily sustainability habits |
| 🛍️ Eco Products | Curated sustainable product swaps with impact data |
| ♻️ Recycling Guide | Material-by-material recycling and disposal guide |
| 🏛️ Gov Schemes | India, USA & UK government green subsidies & incentives |
| 🌙 Dark Mode | Full dark/light theme with localStorage persistence |
| 📱 Mobile Ready | Fully responsive Bootstrap 5 design |
| ⚡ Animations | Particle effects, scroll reveal, counter animations |

---

## 📂 Project Structure

```text
eco-lifestyle-agent/
│
├── app.py                          # Flask backend — routes, Watsonx chat, RAG integration
├── requirements.txt                # Python dependencies (6 packages)
├── .env                            # API credentials — NEVER commit this file
├── README.md                       # This file
│
├── eco_knowledge/                  # RAG knowledge base — 10 markdown documents
│   ├── plastic_reduction.md        # Source: UN Environment Programme (UNEP)
│   ├── energy_saving.md            # Source: International Energy Agency (IEA)
│   ├── sustainable_food.md         # Source: EAT-Lancet Commission / FAO
│   ├── composting_waste.md         # Source: EPA / WRAP
│   ├── sustainable_transport.md    # Source: Our World in Data / IPCC
│   ├── water_conservation.md       # Source: UN Water / Environment Agency
│   ├── sustainable_fashion.md      # Source: Ellen MacArthur Foundation
│   ├── renewable_energy_schemes.md # Source: India MNRE / US IRS / UK DESNZ
│   ├── recycling_guide.md          # Source: EPA / WRAP
│   └── climate_change_facts.md     # Source: IPCC AR6 / NASA
│
├── rag/                            # RAG engine package
│   ├── __init__.py
│   └── vectorstore.py              # Chunking, IBM Slate embeddings, ChromaDB store & retrieval
│
├── templates/
│   └── index.html                  # Single-page frontend (Bootstrap 5, dark mode)
│
├── static/
│   ├── css/
│   │   └── style.css               # All styles — dark/light theme, animations, RAG source cards
│   └── js/
│       └── app.js                  # Chat logic, markdown renderer, data loaders, source rendering
│
└── .chroma_db/                     # ChromaDB persistent vector index (auto-generated at startup)
```

---

## 🧠 RAG Architecture

EcoGuide AI uses **Retrieval-Augmented Generation** to ground every AI response in verified  
knowledge from trusted environmental sources — not just the model's training data.

```
User Question
     │
     ▼  embed via IBM Slate 125M (768-dim)
     │
     ▼
ChromaDB (local, persistent)
  cosine similarity search → Top-3 most relevant chunks
     │
     ▼
Retrieved chunks  ← from UNEP, IEA, IPCC, EPA, FAO, WRAP, govt sources
     │
     ▼
Augmented prompt:
  [System prompt]  +  [Retrieved context with source names]  +  [User question]
     │
     ▼
IBM Watsonx LLM  (Granite 3.3 8B or Llama 3.3 70B — auto-selected per region)
  generates answer grounded in retrieved facts, cites specific statistics
     │
     ▼
Response + Source cards shown in chat UI  (clickable links + relevance %)
```

### Knowledge Base

| File | Source | Topic |
|------|--------|-------|
| `plastic_reduction.md` | UN Environment Programme (UNEP) | Plastic-free living |
| `energy_saving.md` | International Energy Agency (IEA) | Home energy efficiency |
| `sustainable_food.md` | EAT-Lancet Commission / FAO | Plant-based diet, food waste |
| `composting_waste.md` | EPA / WRAP | Composting & zero waste |
| `sustainable_transport.md` | Our World in Data / IPCC | Low-carbon travel |
| `water_conservation.md` | UN Water / Environment Agency | Water saving |
| `sustainable_fashion.md` | Ellen MacArthur Foundation | Circular fashion |
| `renewable_energy_schemes.md` | India MNRE / US IRS / UK DESNZ | Govt subsidies & incentives |
| `recycling_guide.md` | EPA / WRAP | Material-by-material recycling |
| `climate_change_facts.md` | IPCC Sixth Assessment Report / NASA | Climate science & actions |

### RAG Configuration

| Parameter | Value | Notes |
|-----------|-------|-------|
| Embedding model | `ibm/slate-125m-english-rtrvr-v2` | 768-dim vectors, available in all regions |
| Vector store | ChromaDB (persistent) | Stored in `.chroma_db/`, cosine similarity |
| Chunk size | 300 words (480-token cap) | Respects Slate 125M's 512-token limit |
| Chunks indexed | 21 (from 10 documents) | Auto-rebuilt at server startup |
| Retrieval | Top-3 chunks per query | Scores displayed in UI |
| Index rebuild | `POST /api/rag/rebuild` | Or restart server |

### Adding New Knowledge Documents

1. Create a `.md` file in `eco_knowledge/` with frontmatter:

   ```markdown
   ---
   source: Your Source Name
   url: https://source-url.example
   topic: your_topic_slug
   ---

   # Document Title

   Your content here...
   ```

2. Rebuild the index:

   ```bash
   curl -X POST http://localhost:5000/api/rag/rebuild
   # or simply restart the server — index rebuilds automatically
   ```

---

## 🚀 Local Setup

### 1. Prerequisites

- Python **3.10 or higher** (tested on 3.14)
- An [IBM Cloud account](https://cloud.ibm.com/registration) — free Lite plan works
- A Watsonx.ai project created at [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)

### 2. Get the Project

```bash
git clone <repo-url>
cd eco-lifestyle-agent
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Credentials


Edit `.env`:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=change_this_to_a_long_random_string
FLASK_ENV=development
FLASK_DEBUG=True
```

**How to get your credentials:**

| Credential | Where to find |
|------------|---------------|
| `IBM_API_KEY` | [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) → **Create an IBM Cloud API key** |
| `IBM_PROJECT_ID` | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → Your project → **Manage** → **General** → Project ID |
| `IBM_WATSONX_URL` | Use your region's URL (see table below) |

**Region URLs:**

| Region | URL |
|--------|-----|
| US South (Dallas) | `https://us-south.ml.cloud.ibm.com` |
| EU (London) | `https://eu-gb.ml.cloud.ibm.com` |
| EU (Frankfurt) | `https://eu-de.ml.cloud.ibm.com` |
| Asia Pacific (Tokyo) | `https://jp-tok.ml.cloud.ibm.com` |
| Asia Pacific (Sydney) | `https://au-syd.ml.cloud.ibm.com` |

### 6. Run the Application

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

On first startup the RAG index builds automatically in the background (takes ~30 seconds while it embeds 21 chunks via IBM Slate). The chat UI is available immediately; RAG kicks in once indexing completes.

---

## 🤖 IBM Watsonx Setup Guide

1. **Create a free IBM Cloud account** at [cloud.ibm.com/registration](https://cloud.ibm.com/registration)
2. **Create an API key** at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) — copy it immediately, shown only once
3. **Create a Watsonx project** at [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → New project → Empty project
4. **Associate Watson Machine Learning** — project → Manage → Services & integrations → Add Watson Machine Learning
5. **Copy your Project ID** — project → Manage → General → Project ID

**Model auto-selection** — the app queries your region's model catalogue at startup and picks the best available:

| Priority | Model | Available in |
|----------|-------|-------------|
| 1st | `ibm/granite-3-3-8b-instruct` | us-south, eu-gb, eu-de, jp-tok |
| 2nd | `meta-llama/llama-3-3-70b-instruct` | au-syd |
| 3rd | `meta-llama/llama-3-2-11b-vision-instruct` | fallback |
| 4th | `ibm/granite-8b-code-instruct` | fallback |

---

## 🌐 Production Deployment

### Option A — Gunicorn

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

> Use `-w 1` to avoid multiple processes each rebuilding the RAG index simultaneously.

### Option B — Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_ENV=production
EXPOSE 5000
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t ecoguide-ai .
docker run -p 5000:5000 --env-file .env ecoguide-ai
```

### Option C — IBM Code Engine

```bash
ibmcloud login
ibmcloud ce project create --name ecoguide
ibmcloud ce app create \
  --name ecoguide-ai \
  --image icr.io/your-namespace/ecoguide-ai \
  --env-from-secret ecoguide-secrets \
  --port 5000
```

### Option D — Railway / Render / Heroku

1. Push to GitHub
2. Connect repo to Railway / Render
3. Set environment variables in the dashboard: `IBM_API_KEY`, `IBM_PROJECT_ID`, `IBM_WATSONX_URL`, `FLASK_SECRET_KEY`, `FLASK_ENV=production`

---

## 🧪 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main application page |
| `POST` | `/api/chat` | Send message → AI response + RAG sources |
| `GET` | `/api/tips` | 8 eco living tips |
| `GET` | `/api/products` | 8 eco product recommendations |
| `GET` | `/api/recycling` | 8 recycling guidelines |
| `GET` | `/api/schemes` | 6 government eco schemes |
| `POST` | `/api/clear` | Clear conversation session |
| `GET` | `/api/health` | Health check — credentials, model, RAG status |
| `GET` | `/api/rag/status` | RAG index stats — chunk count, embed model |
| `POST` | `/api/rag/rebuild` | Force-rebuild the RAG index in background |

### Chat Request / Response

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I reduce plastic use at home?"}'
```

```json
{
  "response": "Reducing plastic use at home is a fantastic step... A single reusable bag can replace 500–700 plastic bags over its lifetime (UNEP)...",
  "rag_used": true,
  "sources": [
    { "source": "UN Environment Programme (UNEP)", "url": "https://www.unep.org/plastic-pollution", "topic": "plastic_reduction", "score": 0.86, "text": "..." },
    { "source": "UN Environment Programme (UNEP)", "url": "https://www.unep.org/plastic-pollution", "topic": "plastic_reduction", "score": 0.76, "text": "..." },
    { "source": "WRAP / EPA Recycling Guidelines",  "url": "https://www.epa.gov/recycle",           "topic": "recycling",          "score": 0.71, "text": "..." }
  ],
  "message_count": 2
}
```

### Health Check Response

```bash
curl http://localhost:5000/api/health
```

```json
{
  "status": "healthy",
  "configured": true,
  "api_key_set": true,
  "project_id_set": true,
  "active_model": "meta-llama/llama-3-3-70b-instruct",
  "region": "https://au-syd.ml.cloud.ibm.com",
  "rag_ready": true,
  "rag_chunks": 21,
  "embed_model": "ibm/slate-125m-english-rtrvr-v2"
}
```

---

## 📦 Dependencies

```
flask>=3.0.0         # Web framework
python-dotenv>=1.0.0 # .env file loading
requests>=2.31.0     # HTTP client for IBM Watsonx REST API calls
gunicorn>=21.2.0     # Production WSGI server
flask-cors>=4.0.0    # CORS headers
chromadb>=0.5.0      # Local vector store for RAG
```

---

## 🔒 Security Notes

- **Never commit `.env`** — it is already in `.gitignore`
- Use a strong random `FLASK_SECRET_KEY` in production (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`)
- Set `FLASK_DEBUG=False` in production
- The `.chroma_db/` directory contains your indexed embeddings — add it to `.gitignore` if preferred

---

## 🌍 Sources & References

- [IBM Watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-api.html)
- [IBM Slate Embedding Models](https://www.ibm.com/products/watsonx-ai/foundation-models)
- [UN Environment Programme](https://www.unep.org)
- [IPCC Sixth Assessment Report](https://www.ipcc.ch/assessment-report/ar6/)
- [International Energy Agency](https://www.iea.org)
- [EPA Recycling Guidelines](https://www.epa.gov/recycle)
- [PM Surya Ghar Muft Bijli Yojana](https://pmsuryaghar.gov.in)
- [FAO Food & Agriculture Data](https://www.fao.org)

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

> 🌱 **Every small action counts. Start your sustainable journey today.**
