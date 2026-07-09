"""
RAG Engine for EcoGuide AI
===========================
Splits eco knowledge documents into chunks, embeds them via IBM Watsonx
Slate embeddings, stores them in a local ChromaDB vector store, and
retrieves the top-k most relevant chunks for any user query.

Flow:
  build_index()  →  reads eco_knowledge/*.md
                 →  chunks each document
                 →  embeds chunks via IBM Slate 125M (au-syd)
                 →  persists to .chroma_db/ on disk

  retrieve(query, k=3)  →  embeds query
                        →  cosine similarity search in ChromaDB
                        →  returns list of {text, source, url, topic, score}
"""

import os
import re
import math
import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────

IBM_API_KEY    = os.getenv("IBM_API_KEY", "")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "")
_raw_url       = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")
IBM_WATSONX_URL = _raw_url.replace(".dai.cloud.ibm.com", ".ml.cloud.ibm.com")
IAM_TOKEN_URL  = "https://iam.cloud.ibm.com/identity/token"

EMBED_MODEL      = "ibm/slate-125m-english-rtrvr-v2"   # 768-dim, available in au-syd
EMBED_BATCH_SIZE = 16       # max texts per embedding API call
CHUNK_SIZE       = 400      # target tokens (~words) per chunk
CHUNK_OVERLAP    = 60       # overlap between consecutive chunks
TOP_K            = 3        # chunks returned per query

KNOWLEDGE_DIR = Path(__file__).parent.parent / "eco_knowledge"
CHROMA_DIR    = Path(__file__).parent.parent / ".chroma_db"

# ── IAM Token (cached) ──────────────────────────────────────────────────────

_token_cache: dict = {"token": None, "expires_at": 0}

def _get_token() -> str:
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]
    r = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": IBM_API_KEY},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    _token_cache["token"]      = data["access_token"]
    _token_cache["expires_at"] = now + data.get("expires_in", 3600)
    return _token_cache["token"]


# ── Embedding ───────────────────────────────────────────────────────────────

def _embed_batch(texts: list[str]) -> list[list[float]]:
    """Call IBM Watsonx text/embeddings for a batch of texts."""
    token = _get_token()
    url   = f"{IBM_WATSONX_URL}/ml/v1/text/embeddings?version=2024-05-31"
    payload = {
        "model_id":   EMBED_MODEL,
        "project_id": IBM_PROJECT_ID,
        "inputs":     texts,
    }
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return [item["embedding"] for item in r.json()["results"]]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts in batches, respecting EMBED_BATCH_SIZE."""
    all_embeddings = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i : i + EMBED_BATCH_SIZE]
        all_embeddings.extend(_embed_batch(batch))
    return all_embeddings


# ── Document Loading & Chunking ─────────────────────────────────────────────

def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML-style frontmatter from markdown content."""
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip()
            body = parts[2].strip()
    return meta, body


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping word-based chunks.
    Splits on paragraphs first, then merges/splits to hit chunk_size.
    """
    # Split into paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks: list[str] = []
    current_words: list[str] = []

    for para in paragraphs:
        words = para.split()
        if len(current_words) + len(words) <= chunk_size:
            current_words.extend(words)
        else:
            if current_words:
                chunks.append(" ".join(current_words))
            # If para itself is too long, split it
            if len(words) > chunk_size:
                for start in range(0, len(words), chunk_size - overlap):
                    chunk = words[start : start + chunk_size]
                    chunks.append(" ".join(chunk))
                current_words = words[-(overlap):]
            else:
                current_words = words

    if current_words:
        chunks.append(" ".join(current_words))

    return [c for c in chunks if len(c.split()) > 10]  # drop tiny fragments


def load_documents() -> list[dict]:
    """Load all markdown files from eco_knowledge/, return list of chunk dicts."""
    docs = []
    for md_file in sorted(KNOWLEDGE_DIR.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw)
        chunks = _chunk_text(body)
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{md_file.stem}:{i}:{chunk[:40]}".encode()).hexdigest()
            docs.append({
                "id":     chunk_id,
                "text":   chunk,
                "source": meta.get("source", md_file.stem),
                "url":    meta.get("url", ""),
                "topic":  meta.get("topic", md_file.stem),
                "file":   md_file.stem,
                "chunk":  i,
            })
    return docs


# ── ChromaDB Vector Store ───────────────────────────────────────────────────

def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name="eco_knowledge",
        metadata={"hnsw:space": "cosine"},
    )


def build_index(force: bool = False) -> int:
    """
    Build (or rebuild) the ChromaDB index from eco_knowledge/*.md.
    Returns the total number of chunks indexed.
    Skips re-indexing if the collection already has documents (unless force=True).
    """
    collection = _get_collection()

    if not force and collection.count() > 0:
        print(f"[RAG] Index already contains {collection.count()} chunks. Skipping rebuild.")
        return collection.count()

    print("[RAG] Loading documents...")
    docs = load_documents()
    print(f"[RAG] Loaded {len(docs)} chunks from {KNOWLEDGE_DIR}")

    # Embed in batches
    print("[RAG] Embedding chunks via IBM Slate 125M...")
    texts = [d["text"] for d in docs]
    embeddings = embed_texts(texts)
    print(f"[RAG] Embedded {len(embeddings)} chunks (dim={len(embeddings[0])})")

    # Upsert into ChromaDB
    collection.upsert(
        ids        = [d["id"]   for d in docs],
        embeddings = embeddings,
        documents  = [d["text"] for d in docs],
        metadatas  = [{"source": d["source"], "url": d["url"],
                       "topic": d["topic"],   "file": d["file"],
                       "chunk": d["chunk"]}   for d in docs],
    )
    print(f"[RAG] Index built: {collection.count()} chunks stored in {CHROMA_DIR}")
    return collection.count()


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Embed the query and return the top-k most relevant chunks.
    Returns list of dicts: {text, source, url, topic, score}
    """
    collection = _get_collection()
    if collection.count() == 0:
        return []

    q_embedding = embed_texts([query])[0]

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine distance → similarity score (1 = identical, 0 = orthogonal)
        score = round(1 - dist, 4)
        chunks.append({
            "text":   text,
            "source": meta.get("source", ""),
            "url":    meta.get("url", ""),
            "topic":  meta.get("topic", ""),
            "score":  score,
        })
    return chunks


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context block for the LLM prompt."""
    if not chunks:
        return ""
    parts = ["### Relevant Knowledge (retrieved from trusted eco sources)\n"]
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"**[Source {i}] {c['source']}** (relevance: {c['score']:.0%})\n"
            f"{c['text']}\n"
        )
    parts.append("### End of Retrieved Context\n")
    return "\n".join(parts)


def index_status() -> dict:
    """Return current index stats."""
    try:
        collection = _get_collection()
        return {"indexed": True, "chunk_count": collection.count(), "embed_model": EMBED_MODEL}
    except Exception as e:
        return {"indexed": False, "error": str(e)}
