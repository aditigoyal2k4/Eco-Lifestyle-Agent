# 🌿 EcoGuide AI — Sustainable Living Assistant

An AI-powered sustainable lifestyle assistant built with **Python Flask** and **IBM Watsonx.ai (Granite 3.3 8B Instruct)**.

Ask any sustainability-related question and receive instant, practical guidance to reduce your environmental impact. The application combines **Retrieval-Augmented Generation (RAG)** with IBM Granite to provide grounded, fact-based responses.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Chat | Natural language Q&A powered by IBM Granite 3.3 8B Instruct |
| 🧠 RAG Pipeline | Grounded responses using ChromaDB and IBM Watsonx embeddings |
| 🌱 Eco Tips | 8+ actionable daily sustainability habits |
| 🛍️ Eco Products | Curated sustainable product alternatives with environmental impact |
| ♻️ Recycling Guide | Material-specific recycling and disposal instructions |
| 🏛️ Government Schemes | Green incentives and sustainability schemes for India, USA, and UK |
| 🌙 Dark Mode | Dark/Light theme with localStorage persistence |
| 📱 Responsive Design | Mobile-friendly Bootstrap 5 interface |
| ⚡ Modern UI | Particle effects, scroll animations, and interactive counters |

---

# 🧠 Retrieval-Augmented Generation (RAG)

EcoGuide AI implements a robust **Retrieval-Augmented Generation (RAG)** pipeline to ensure responses are accurate, relevant, and supported by trusted sustainability knowledge.

## RAG Components

### 📚 Knowledge Base
- Stores sustainability documents inside `eco_knowledge/`
- Includes:
  - Eco lifestyle resources
  - Recycling information
  - Product sustainability data
  - Government policies
  - Climate guidance

### 📄 Document Processing
- Documents are automatically divided into semantic chunks.
- Overlapping chunking preserves context during retrieval.

### 🔍 Embedding Model
- IBM Watsonx Embeddings convert text into high-dimensional vectors.

### 🗄️ Vector Database
- Uses **ChromaDB** for fast local similarity search.
- Implemented in:

```
rag/vectorstore.py
```

### 🔎 Retrieval Engine
Integrated into the Flask backend.

For every user query:

1. Generate embedding
2. Search ChromaDB
3. Retrieve relevant document chunks
4. Inject retrieved context into Granite prompt
5. Generate grounded response

### 💬 Frontend Integration

Retrieved document sources are displayed alongside AI responses to improve transparency and trust.

---

# 🔄 End-to-End RAG Flow

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
ChromaDB Similarity Search
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build Prompt with Context
      │
      ▼
IBM Granite 3.3 8B Instruct
      │
      ▼
AI Response + Source References
```

---

# 📂 Project Structure

```text
eco-lifestyle-agent/
│
├── app.py                  # Flask backend + Watsonx.ai + RAG integration
├── requirements.txt        # Python dependencies
├── .env                    # API credentials (Never commit)
├── .env.example            # Environment template
│
├── eco_knowledge/          # Sustainability knowledge base
│
├── rag/
│   └── vectorstore.py      # ChromaDB setup & retrieval engine
│
├── templates/
│   └── index.html          # Frontend
│
└── static/
    ├── css/
    │   └── style.css       # Styling, dark mode, animations
    │
    └── js/
        └── app.js          # Chat logic, API calls, source rendering
```

---

# 🚀 Local Setup

## 1. Prerequisites

- Python 3.10+
- IBM Cloud Account (Lite plan works)
- IBM Watsonx.ai Project

---

## 2. Clone Repository

```bash
git clone <repo-url>
cd eco-lifestyle-agent
```

---

## 3. Create Virtual Environment

### Linux/macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Copy the template:

```bash
cp .env.example .env
```

Update `.env`

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com

FLASK_SECRET_KEY=change_this_to_a_random_secret

FLASK_ENV=development
FLASK_DEBUG=True
```

---

# 🔑 IBM Credentials

| Variable | Where to Find |
|-----------|---------------|
| IBM_API_KEY | IBM Cloud → Manage → Access (IAM) → API Keys |
| IBM_PROJECT_ID | Watsonx Project → Manage → General → Project ID |
| IBM_WATSONX_URL | Default US South endpoint (change if using another region) |

Supported regions include:

- us-south
- eu-gb
- eu-de
- jp-tok
- au-syd

---

# ▶️ Run the Application

```bash
python app.py
```

Visit:

```
http://localhost:5000
```

---

# 🤖 IBM Watsonx.ai Setup

1. Create an IBM Cloud account.
2. Provision Watson Studio (Lite plan).
3. Create a Watsonx.ai Project.
4. Associate a Watsonx Runtime.
5. Generate an IBM Cloud API Key.
6. Copy your Project ID.
7. Update your `.env` file.

The application uses:

**IBM Granite 3.3 8B Instruct**

through the REST endpoint:

```
/ml/v1/text/chat
```

---

## 🔒 Security Notes

- **Never commit `.env`** to version control — it is already in `.gitignore`
- Use a strong random `FLASK_SECRET_KEY` in production
- Set `FLASK_DEBUG=False` in production
- Rate-limit the `/api/chat` endpoint in production deployments

---

# 🧪 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Main application |
| POST | `/api/chat` | AI chat with RAG source retrieval |
| GET | `/api/tips` | Eco living tips |
| GET | `/api/products` | Sustainable product recommendations |
| GET | `/api/recycling` | Recycling guidelines |
| GET | `/api/schemes` | Government sustainability schemes |
| POST | `/api/clear` | Clear conversation history |
| GET | `/api/health` | Health & configuration status |

---

## 📦 Dependencies

```
flask==3.0.3            # Web framework
python-dotenv==1.0.1    # .env file loading
requests==2.32.3        # HTTP client for IBM API calls
ibm-watsonx-ai==1.1.2   # IBM Watsonx SDK (optional, uses REST directly)
gunicorn==22.0.0        # Production WSGI server
flask-cors==4.0.1       # CORS headers
chromadb
langchain
```

---

## 🌍 Sources & References

- [IBM Watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-api.html)
- [IBM Granite Models](https://www.ibm.com/granite)
- [UN Sustainable Development Goals](https://sdgs.un.org)
- [EPA Recycling Guidelines](https://www.epa.gov/recycle)
- [IPCC Climate Reports](https://www.ipcc.ch)
- [PM Surya Ghar Scheme](https://pmsuryaghar.gov.in)

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

> 🌱 **Every small action counts. Start your sustainable journey today.**
