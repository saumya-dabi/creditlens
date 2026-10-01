"""Minimal Gemini REST client for the free tier.
Free-tier quotas are per model per day (e.g. 20 requests/day on the top Flash model), so the client rotates
through a pool of models: a model that returns a daily-quota 429 is skipped for an hour, per-minute 429s are
retried with the server's suggested delay, and a malformed JSON answer falls through to the next model."""
import json
import os
import re
import time
from pathlib import Path

import requests

BASE = "https://generativelanguage.googleapis.com/v1beta"
CHAT_MODELS = [m.strip() for m in os.getenv(
    "GEMINI_MODELS",
    "gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-flash-lite-latest,gemma-4-31b-it,gemini-3.8-flash,gemini-flash-latest",
).split(",") if m.strip()]
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
_exhausted: dict[str, float] = {}


class DailyQuota(RuntimeError):
    pass


def _key() -> str:
    k = os.getenv("GEMINI_API_KEY")
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


def _post(path: str, body: dict, tries: int = 4) -> dict:
    delay = 4.0
    for attempt in range(tries):
        r = requests.post(f"{BASE}/{path}", json=body, headers={"x-goog-api-key": _key()}, timeout=180)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429 and "PerDay" in r.text:
            raise DailyQuota(r.text[:200])
        if r.status_code in (429, 500, 502, 503, 504) and attempt < tries - 1:
            m = re.search(r'"retryDelay":\s*"(\d+)', r.text)
            time.sleep(min(float(m.group(1)) + 1, 65) if m else delay)
            delay = min(delay * 2, 60)
            continue
        raise RuntimeError(f"Gemini {r.status_code}: {r.text[:300]}")
    raise RuntimeError("Gemini: retries exhausted")


def _strip(text: str) -> str:
    return re.sub(r"^```(json)?|```$", "", text.strip()).strip()


def generate(prompt: str, system: str = "", json_schema: dict | None = None, temperature: float = 0.1) -> str:
    last = None
    for model in CHAT_MODELS:
        if time.time() - _exhausted.get(model, 0) < 3600:
            continue
        gemma = model.startswith("gemma")  # Gemma on the Gemini API has no system instruction field
        body = {"contents": [{"role": "user", "parts": [{"text": f"{system}\n\n{prompt}" if gemma and system else prompt}]}],
                "generationConfig": {"temperature": temperature}}
        if system and not gemma:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_schema:
            body["generationConfig"]["responseMimeType"] = "application/json"
            body["generationConfig"]["responseSchema"] = json_schema
        try:
            data = _post(f"models/{model}:generateContent", body)
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
            if json_schema:
                json.loads(_strip(text))
            generate.last_model = model
            return text
        except DailyQuota as e:
            _exhausted[model] = time.time()
            last = e
        except (RuntimeError, KeyError, IndexError, ValueError) as e:
            last = e
    raise RuntimeError(f"all models failed or out of free quota: {str(last)[:200]}")


generate.last_model = None


def generate_json(prompt: str, schema: dict, system: str = "") -> dict:
    return json.loads(_strip(generate(prompt, system=system, json_schema=schema)))


def embed(texts: list[str], task: str = "RETRIEVAL_DOCUMENT", dim: int = 768) -> list[list[float]]:
    out = []
    for i in range(0, len(texts), 50):
        batch = texts[i:i + 50]
        body = {"requests": [{"model": f"models/{EMBED_MODEL}", "content": {"parts": [{"text": t}]},
                              "taskType": task, "outputDimensionality": dim} for t in batch]}
        data = _post(f"models/{EMBED_MODEL}:batchEmbedContents", body)
        out.extend(e["values"] for e in data["embeddings"])
    return out
