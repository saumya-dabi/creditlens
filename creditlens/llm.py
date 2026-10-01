"""Minimal Gemini REST client (free tier friendly): retries on 429/5xx, model fallback, JSON mode."""
import json
import os
import re
import time
from pathlib import Path

import requests

BASE = "https://generativelanguage.googleapis.com/v1beta"
CHAT_MODELS = [m.strip() for m in os.getenv("GEMINI_MODELS", "gemini-2.5-flash,gemini-2.5-flash-lite,gemini-2.0-flash").split(",") if m.strip()]
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")


def _key() -> str:
    k = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not k:
        env = Path.home() / ".hermes" / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("GEMINI_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"')
    if not k:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return k


def available() -> bool:
    try:
        _key()
        return True
    except RuntimeError:
        return False


def _post(path: str, body: dict, tries: int = 6) -> dict:
    url = f"{BASE}/{path}"
    delay = 4.0
    for attempt in range(tries):
        r = requests.post(url, json=body, headers={"x-goog-api-key": _key()}, timeout=120)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504) and attempt < tries - 1:
            m = re.search(r'"retryDelay":\s*"(\d+)', r.text)
            time.sleep(float(m.group(1)) + 1 if m else delay)
            delay = min(delay * 2, 60)
            continue
        raise RuntimeError(f"Gemini {r.status_code}: {r.text[:300]}")
    raise RuntimeError("Gemini: retries exhausted")


def generate(prompt: str, system: str = "", json_schema: dict | None = None, temperature: float = 0.1) -> str:
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if json_schema:
        body["generationConfig"]["responseMimeType"] = "application/json"
        body["generationConfig"]["responseSchema"] = json_schema
    last = None
    for model in CHAT_MODELS:
        try:
            data = _post(f"models/{model}:generateContent", body, tries=4)
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts if not p.get("thought"))
        except (RuntimeError, KeyError, IndexError) as e:  # fall through to next model
            last = e
    raise RuntimeError(f"all models failed: {last}")


def generate_json(prompt: str, schema: dict, system: str = "") -> dict:
    text = generate(prompt, system=system, json_schema=schema)
    text = re.sub(r"^```(json)?|```$", "", text.strip()).strip()
    return json.loads(text)


def embed(texts: list[str], task: str = "RETRIEVAL_DOCUMENT", dim: int = 768) -> list[list[float]]:
    out = []
    for i in range(0, len(texts), 50):
        batch = texts[i:i + 50]
        body = {"requests": [{"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": t}]},
                              "taskType": task, "outputDimensionality": dim} for t in batch]}
        data = _post(f"models/{EMBED_MODEL}:batchEmbedContents", body)
        out.extend(e["values"] for e in data["embeddings"])
    return out
