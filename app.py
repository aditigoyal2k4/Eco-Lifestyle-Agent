import os
import json
import threading
import requests
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from rag.vectorstore import retrieve, format_context, build_index, index_status

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "eco_secret_default")
CORS(app)

IBM_API_KEY = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "")

# Auto-correct the common wrong domain (dai.cloud.ibm.com → ml.cloud.ibm.com)
_raw_url = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")
IBM_WATSONX_URL = _raw_url.replace(".dai.cloud.ibm.com", ".ml.cloud.ibm.com")

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

_PLACEHOLDERS = {"", "your_ibm_cloud_api_key_here", "your_watsonx_project_id_here"}

# Ordered preference list — first model found available in the region wins.
# granite-3-3-8b-instruct is preferred when available (us-south, eu-gb, eu-de, jp-tok).
# llama-3-3-70b-instruct is the best available model in au-syd.
_MODEL_PREFERENCE = [
    "ibm/granite-3-3-8b-instruct",
    "meta-llama/llama-3-3-70b-instruct",
    "meta-llama/llama-3-2-11b-vision-instruct",
    "ibm/granite-8b-code-instruct",
]

# Resolved at first chat request; cached for the process lifetime.
_resolved_model: str | None = None


def _is_configured() -> bool:
    """Return True only when both credentials look like real values."""
    key_ok = IBM_API_KEY not in _PLACEHOLDERS and "_here" not in IBM_API_KEY
    pid_ok = IBM_PROJECT_ID not in _PLACEHOLDERS and "_here" not in IBM_PROJECT_ID
    return key_ok and pid_ok


def _resolve_model(token: str) -> str:
    """Query the region's model catalogue and return the first available preferred model."""
    global _resolved_model
    if _resolved_model:
        return _resolved_model
    try:
        url = f"{IBM_WATSONX_URL}/ml/v1/foundation_model_specs?version=2024-05-31&limit=200"
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
        if r.status_code == 200:
            available = {m["model_id"] for m in r.json().get("resources", [])}
            for candidate in _MODEL_PREFERENCE:
                if candidate in available:
                    _resolved_model = candidate
                    print(f"[EcoGuide] Using model: {_resolved_model} (region: {IBM_WATSONX_URL})")
                    return _resolved_model
    except Exception:
        pass
    # Fallback — try preferred list blind; first successful call will stick
    _resolved_model = _MODEL_PREFERENCE[0]
    return _resolved_model

ECO_TIPS = [
    {"icon": "🌱", "title": "Start Composting", "tip": "Compost food scraps to reduce landfill waste by up to 30% and enrich your garden soil naturally."},
    {"icon": "💧", "title": "Save Water Daily", "tip": "Fix leaky taps, take shorter showers, and collect rainwater. A 5-min shower saves 50 litres vs a bath."},
    {"icon": "♻️", "title": "Reduce Single-Use Plastic", "tip": "Switch to reusable bags, bottles, and containers. Refuse straws and single-use cutlery."},
    {"icon": "⚡", "title": "Switch to Renewable Energy", "tip": "Install solar panels or choose a green energy supplier to cut your carbon footprint by up to 1.5 tonnes/year."},
    {"icon": "🚲", "title": "Sustainable Transport", "tip": "Walk, cycle, or use public transport. Cycling instead of driving for short trips saves ~150g CO₂ per km."},
    {"icon": "🥦", "title": "Eat Plant-Based Meals", "tip": "Replacing one beef meal per week with plant-based food saves ~52kg CO₂ annually per person."},
    {"icon": "🛍️", "title": "Buy Second-Hand", "tip": "Thrift shopping extends product life and saves ~82% of the energy vs buying new clothing."},
    {"icon": "💡", "title": "LED Lighting", "tip": "Switch to LED bulbs. They use 75% less energy and last 25x longer than traditional incandescent bulbs."},
]

ECO_PRODUCTS = [
    {"name": "Bamboo Toothbrush", "category": "Personal Care", "impact": "Saves 1 plastic toothbrush every 3 months from landfill", "rating": 4.8},
    {"name": "Stainless Steel Water Bottle", "category": "Hydration", "impact": "Eliminates ~156 plastic bottles per year per person", "rating": 4.9},
    {"name": "Beeswax Food Wraps", "category": "Kitchen", "impact": "Replaces plastic wrap — biodegradable and reusable for 1 year", "rating": 4.7},
    {"name": "Solar Charger", "category": "Electronics", "impact": "Charges devices using 100% renewable energy anywhere", "rating": 4.6},
    {"name": "Compost Bin", "category": "Garden", "impact": "Diverts organic waste from landfill; produces rich compost", "rating": 4.8},
    {"name": "Reusable Produce Bags", "category": "Shopping", "impact": "Eliminates hundreds of plastic bags per year", "rating": 4.7},
    {"name": "Natural Bar Soap", "category": "Personal Care", "impact": "Zero plastic packaging; biodegradable formula", "rating": 4.5},
    {"name": "Cloth Napkins Set", "category": "Kitchen", "impact": "Replaces ~2,000 paper napkins/year for a family of 4", "rating": 4.6},
]

RECYCLING_GUIDELINES = [
    {"material": "Plastic Bottles (PET #1)", "bin": "Blue Recycling Bin", "tips": "Rinse clean, remove caps (recycle separately), crush to save space.", "accepted": True},
    {"material": "Glass Jars & Bottles", "bin": "Green Glass Bank", "tips": "Rinse clean. Remove lids. Do not include Pyrex or broken glass in standard bins.", "accepted": True},
    {"material": "Cardboard & Paper", "bin": "Blue Recycling Bin", "tips": "Flatten boxes. Keep dry. Remove tape and staples where possible.", "accepted": True},
    {"material": "Aluminium Cans", "bin": "Blue Recycling Bin", "tips": "Rinse cans. Crush to save space. Aluminium is infinitely recyclable.", "accepted": True},
    {"material": "Electronic Waste (E-Waste)", "bin": "E-Waste Drop-Off Centre", "tips": "Never put in regular bins. Take to certified e-waste recyclers or retailer take-back schemes.", "accepted": False},
    {"material": "Batteries", "bin": "Battery Collection Point", "tips": "Supermarkets and electronics stores have dedicated battery collection boxes.", "accepted": False},
    {"material": "Food Waste", "bin": "Brown Organic Bin / Compost", "tips": "Use a food caddy for kitchen scraps. Compost at home or use municipal collection.", "accepted": False},
    {"material": "Textiles & Clothing", "bin": "Charity Shop / Textile Bank", "tips": "Donate wearable items. Worn textiles go to fabric recycling bins at clothing stores.", "accepted": False},
]

GOVT_SCHEMES = [
    {
        "name": "PM Surya Ghar Muft Bijli Yojana",
        "country": "India 🇮🇳",
        "description": "300 units of free solar electricity per month for households. Subsidies up to ₹78,000 for rooftop solar installations.",
        "link": "https://pmsuryaghar.gov.in",
        "category": "Solar Energy"
    },
    {
        "name": "National Electric Mobility Mission Plan",
        "country": "India 🇮🇳",
        "description": "FAME scheme provides subsidies up to ₹15,000 per kWh on EV batteries, promoting electric vehicle adoption.",
        "link": "https://heavyindustries.gov.in",
        "category": "Electric Vehicles"
    },
    {
        "name": "Swachh Bharat Mission",
        "country": "India 🇮🇳",
        "description": "National mission for waste management, sanitation and cleanliness. Supports community composting and waste segregation.",
        "link": "https://swachhbharat.mygov.in",
        "category": "Waste Management"
    },
    {
        "name": "Green Building Rating (GRIHA)",
        "country": "India 🇮🇳",
        "description": "National rating system for green buildings. Tax benefits and subsidized loans for GRIHA-certified constructions.",
        "link": "https://www.grihaindia.org",
        "category": "Green Buildings"
    },
    {
        "name": "IRA Clean Energy Tax Credits",
        "country": "USA 🇺🇸",
        "description": "Up to 30% tax credit on residential solar, EVs, heat pumps, and energy-efficient home improvements under the Inflation Reduction Act.",
        "link": "https://www.irs.gov/credits-deductions/credits-for-new-clean-vehicles-purchased-in-2023-or-after",
        "category": "Tax Credits"
    },
    {
        "name": "UK ECO4 Scheme",
        "country": "UK 🇬🇧",
        "description": "Government-funded scheme for free or heavily subsidised home insulation and low-carbon heating for eligible households.",
        "link": "https://www.gov.uk/improve-energy-efficiency",
        "category": "Home Energy"
    },
]

SYSTEM_PROMPT = """You are EcoGuide, an expert AI assistant for sustainable living and environmental awareness. You are knowledgeable, friendly, and encouraging about eco-friendly practices.

Your expertise covers:
- Reducing carbon footprint in daily life
- Zero-waste and plastic-free living
- Sustainable food choices and plant-based diets
- Eco-friendly travel and transportation
- Renewable energy solutions
- Green home improvements
- Recycling, composting, and upcycling
- Sustainable fashion and consumption
- Water conservation
- Community environmental initiatives
- Government eco schemes and subsidies
- Climate change facts and solutions

Guidelines:
- When retrieved context is provided, use it as your PRIMARY knowledge source and cite specific statistics from it
- Provide actionable, practical advice tailored to everyday situations
- Include specific numbers and statistics when relevant (e.g., "saves X kg CO₂ per year")
- Suggest affordable and accessible options first
- Be encouraging, not preachy — celebrate small steps
- Mention local resources, certifications, or schemes where applicable
- Keep responses concise but comprehensive (200-350 words)
- Use bullet points or numbered lists for clarity
- Always end with one motivating "eco-action" the user can take today

Remember: You are helping people make sustainable choices that are easy, affordable, and impactful."""

# ── RAG index built once at startup in a background thread ─────────────────
_rag_ready = False
_rag_lock  = threading.Lock()

def _build_rag_index():
    global _rag_ready
    try:
        count = build_index()
        with _rag_lock:
            _rag_ready = True
        print(f"[RAG] Ready — {count} chunks indexed.")
    except Exception as e:
        print(f"[RAG] Index build failed: {e}. Continuing without RAG.")


def get_iam_token():
    """Fetch IAM access token from IBM Cloud."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": IBM_API_KEY,
    }
    response = requests.post(IAM_TOKEN_URL, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


def query_watsonx(user_message: str, conversation_history: list, context_block: str = "") -> str:
    """Send a message to the best available Watsonx model and return the response."""
    global _resolved_model
    try:
        token = get_iam_token()
        model_id = _resolve_model(token)
        url = f"{IBM_WATSONX_URL}/ml/v1/text/chat?version=2024-05-31"

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in conversation_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Prepend retrieved context to the user message when available
        if context_block:
            augmented_message = (
                f"{context_block}\n\n"
                f"**User question:** {user_message}\n\n"
                f"Using the retrieved context above, please provide a detailed, accurate answer "
                f"with specific statistics where available."
            )
        else:
            augmented_message = user_message
        messages.append({"role": "user", "content": augmented_message})

        payload = {
            "model_id": model_id,
            "project_id": IBM_PROJECT_ID,
            "messages": messages,
            "parameters": {
                "max_new_tokens": 600,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
            },
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        # If this specific model isn't supported, clear cache and retry once with next candidate
        if response.status_code == 404:
            body = response.json()
            codes = [e.get("code", "") for e in body.get("errors", [])]
            if "model_not_supported" in codes or "model_no_support_for_function" in codes:
                _resolved_model = None  # bust cache
                # Try next model in preference list
                available_idx = _MODEL_PREFERENCE.index(model_id) if model_id in _MODEL_PREFERENCE else -1
                for next_model in _MODEL_PREFERENCE[available_idx + 1:]:
                    payload["model_id"] = next_model
                    r2 = requests.post(url, headers=headers, json=payload, timeout=60)
                    if r2.status_code == 200:
                        _resolved_model = next_model
                        print(f"[EcoGuide] Switched to fallback model: {next_model}")
                        return r2.json()["choices"][0]["message"]["content"]
                return (
                    f"⚠️ **No compatible model found in region `{IBM_WATSONX_URL}`**\n\n"
                    f"Models tried: {', '.join(_MODEL_PREFERENCE)}\n\n"
                    f"Your Watsonx instance only has: `granite-3-1-8b-base`, `granite-8b-code-instruct`, etc.\n"
                    f"None of these support the chat interface. Try changing `IBM_WATSONX_URL` to "
                    f"`https://us-south.ml.cloud.ibm.com` in your `.env` and restart."
                )

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        tried_url = f"{IBM_WATSONX_URL}/ml/v1/text/chat?version=2024-05-31"
        if status == 401:
            return (
                "⚠️ **401 Unauthorized** — Your IBM API Key was rejected.\n\n"
                "- Make sure `IBM_API_KEY` in `.env` is correct and not expired\n"
                "- Regenerate at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)\n"
                "- Restart the server after updating `.env`"
            )
        if status == 403:
            return (
                "⚠️ **403 Forbidden** — Your account lacks access to this model or project.\n\n"
                "- Ensure your project has a **Watsonx.ai Runtime** service associated\n"
                "- Go to [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → "
                "your project → **Manage** → **Services & integrations**\n"
                "- Add **Watson Machine Learning** if not already present"
            )
        return f"⚠️ **HTTP {status} Error**: {str(e)}\n\nURL tried: `{tried_url}`"
    except requests.exceptions.Timeout:
        return "⚠️ The request timed out. Please try again in a moment."
    except KeyError:
        return "⚠️ Unexpected response format from Watsonx. Please try again."
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"


# ──────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────

@app.route("/")
def index():
    """Render main page."""
    session.setdefault("conversation", [])
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages from frontend."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if not _is_configured():
        return jsonify({
            "setup_required": True,
            "response": (
                "🔑 **IBM Credentials Not Configured**\n\n"
                "Follow these steps to enable the AI chat:\n\n"
                "**Step 1 — Create a free IBM Cloud account**\n"
                "Go to [cloud.ibm.com/registration](https://cloud.ibm.com/registration) and sign up (no credit card needed for the Lite plan).\n\n"
                "**Step 2 — Get your API Key**\n"
                "- Open [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)\n"
                "- Click **Create an IBM Cloud API key**\n"
                "- Copy the key value immediately (shown only once)\n\n"
                "**Step 3 — Create a Watsonx project**\n"
                "- Go to [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)\n"
                "- Click **New project → Create an empty project**\n"
                "- Open the project → **Manage** tab → **General** → copy the **Project ID**\n\n"
                "**Step 4 — Create your `.env` file**\n"
                "In the project folder run:\n"
                "`cp .env.example .env`\n\n"
                "Then edit `.env` and fill in:\n"
                "```\nIBM_API_KEY=<your key here>\n"
                "IBM_PROJECT_ID=<your project ID here>\n"
                "IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com\n```\n\n"
                "**Step 5 — Restart the server**\n"
                "Stop Flask with `Ctrl+C` then run `python app.py` again.\n\n"
                "> 💡 The correct URL prefix depends on your region: `us-south`, `eu-gb`, `eu-de`, `jp-tok`, or `au-syd`."
            ),
        }), 200

    conversation = session.get("conversation", [])

    # ── RAG retrieval ────────────────────────────────────────────────────────
    sources: list[dict] = []
    context_block = ""
    with _rag_lock:
        rag_ready = _rag_ready
    if rag_ready:
        try:
            sources = retrieve(user_message, k=3)
            if sources:
                context_block = format_context(sources)
        except Exception as e:
            print(f"[RAG] Retrieval error: {e}")

    ai_response = query_watsonx(user_message, conversation, context_block)

    conversation.append({"role": "user", "content": user_message})
    conversation.append({"role": "assistant", "content": ai_response})
    session["conversation"] = conversation[-20:]
    session.modified = True

    return jsonify({
        "response":      ai_response,
        "sources":       sources,
        "rag_used":      bool(sources),
        "message_count": len(conversation),
    })


@app.route("/api/tips", methods=["GET"])
def get_tips():
    """Return eco tips."""
    return jsonify(ECO_TIPS)


@app.route("/api/products", methods=["GET"])
def get_products():
    """Return eco-friendly product recommendations."""
    return jsonify(ECO_PRODUCTS)


@app.route("/api/recycling", methods=["GET"])
def get_recycling():
    """Return recycling guidelines."""
    return jsonify(RECYCLING_GUIDELINES)


@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    """Return government eco schemes."""
    return jsonify(GOVT_SCHEMES)


@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    """Clear the current conversation session."""
    session["conversation"] = []
    session.modified = True
    return jsonify({"message": "Conversation cleared."})


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    with _rag_lock:
        rag_ready = _rag_ready
    rag_info = index_status()
    return jsonify({
        "status":        "healthy",
        "configured":    _is_configured(),
        "api_key_set":   IBM_API_KEY not in _PLACEHOLDERS,
        "project_id_set":IBM_PROJECT_ID not in _PLACEHOLDERS,
        "active_model":  _resolved_model,
        "region":        IBM_WATSONX_URL,
        "rag_ready":     rag_ready,
        "rag_chunks":    rag_info.get("chunk_count", 0),
        "embed_model":   rag_info.get("embed_model", ""),
    })


@app.route("/api/rag/status", methods=["GET"])
def rag_status():
    """RAG index status endpoint."""
    with _rag_lock:
        ready = _rag_ready
    info = index_status()
    return jsonify({"ready": ready, **info})


@app.route("/api/rag/rebuild", methods=["POST"])
def rag_rebuild():
    """Force-rebuild the RAG index (admin use)."""
    global _rag_ready
    with _rag_lock:
        _rag_ready = False
    t = threading.Thread(target=_build_rag_index, daemon=True)
    t.start()
    return jsonify({"message": "Index rebuild started in background."})


if __name__ == "__main__":
    # Build RAG index in background so server starts immediately
    if _is_configured():
        threading.Thread(target=_build_rag_index, daemon=True).start()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
