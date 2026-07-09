# 🌿 EcoGuide AI — Sustainable Living Assistant

An AI-powered eco lifestyle agent built with **Python Flask** and **IBM Watsonx.ai (Granite 3.3 8B Instruct)**.  
Ask any sustainability question and get instant, actionable guidance to reduce your environmental impact.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Chat | Natural language Q&A powered by IBM Granite model |
| 🧠 RAG Pipeline | Grounded responses using ChromaDB and IBM Watsonx embeddings |
| 🌱 Eco Tips | 8+ actionable daily sustainability habits |
| 🛍️ Eco Products | Curated sustainable product swaps with impact data |
| ♻️ Recycling Guide | Material-by-material recycling and disposal guide |
| 🏛️ Gov Schemes | India, USA & UK government green subsidies & incentives |
| 🌙 Dark Mode | Full dark/light theme with localStorage persistence |
| 📱 Mobile Ready | Fully responsive Bootstrap 5 design |
| ⚡ Animations | Particle effects, scroll reveal, counter animations |

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

## 🚀 Local Setup & Deployment

### 1. Prerequisites

- Python 3.10 or higher
- An [IBM Cloud account](https://cloud.ibm.com/registration) (free tier works)
- IBM Watsonx.ai project created

### 2. Clone / Download the Project

```bash
git clone <repo-url>
cd eco-lifestyle-agent
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=change_this_to_a_random_secret
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Where to get your IBM credentials:

| Credential | Where to find |
|------------|---------------|
| `IBM_API_KEY` | IBM Cloud → Manage → Access (IAM) → API Keys → **Create** |
| `IBM_PROJECT_ID` | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → Your Watsonx project → Manage → General → **Project ID** |
| `IBM_WATSONX_URL` | Keep default for US South; change region prefix if needed (`eu-gb`, `eu-de`, `jp-tok`, `au-syd`) |

### 6. Run the Application

```bash
python app.py
```

Open your browser: **http://localhost:5000**

---

## 🤖 IBM Watsonx.ai Setup Guide

1. **Create an IBM Cloud account** at [cloud.ibm.com](https://cloud.ibm.com)
2. **Provision Watson Studio** (Lite plan is free)
3. **Create a new project** in [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
4. **Associate a Watsonx.ai runtime** to your project
5. **Generate an API Key** from IBM Cloud IAM
6. Copy your **Project ID** from project settings → Manage → General

The app uses the `ibm/granite-3-3-8b-instruct` model via the `/ml/v1/text/chat` endpoint.

---

## 🌐 Production Deployment

### Option A — Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Option B — Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_ENV=production
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t ecoguide-ai .
docker run -p 5000:5000 --env-file .env ecoguide-ai
```

### Option C — IBM Code Engine (Serverless)

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
2. Connect repository to Railway/Render
3. Set environment variables in dashboard:
   - `IBM_API_KEY`
   - `IBM_PROJECT_ID`
   - `IBM_WATSONX_URL`
   - `FLASK_SECRET_KEY`
   - `FLASK_ENV=production`

---

## 🔒 Security Notes

- **Never commit `.env`** to version control — it is already in `.gitignore`
- Use a strong random `FLASK_SECRET_KEY` in production
- Set `FLASK_DEBUG=False` in production
- Rate-limit the `/api/chat` endpoint in production deployments

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Main application page |
| `POST` | `/api/chat` | Send message, get AI response |
| `GET`  | `/api/tips` | Eco living tips |
| `GET`  | `/api/products` | Eco product recommendations |
| `GET`  | `/api/recycling` | Recycling guidelines |
| `GET`  | `/api/schemes` | Government eco schemes |
| `POST` | `/api/clear` | Clear conversation session |
| `GET`  | `/api/health` | Health check + API config status |

### Chat API Example

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I reduce plastic use at home?"}'
```

**Response:**
```json
{
  "response": "Great question! Here are practical ways to reduce plastic...",
  "message_count": 2
}
```

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
