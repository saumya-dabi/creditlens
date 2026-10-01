"""CreditLens HTTP API + static UI.  Run: uvicorn server:app --port 8601"""
import hashlib
import json
import re
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from creditlens import llm, qa  # noqa: E402
from creditlens.retrieval import COMPANIES, Index  # noqa: E402

app = FastAPI(title="CreditLens", docs_url=None, redoc_url=None)
INDEX = Index()
CACHE = ROOT / "data" / "answer_cache.json"
_cache: dict = json.loads(CACHE.read_text()) if CACHE.exists() else {}
_hits: dict[str, deque] = defaultdict(deque)
LIMIT_PER_HOUR = 40

SAMPLES = {
    "sgp": ["Does the collateral cover the proposed term loan as per policy?", "How big is the GSTR-1 vs GSTR-3B gap, and how much is unexplained?", "Is customer concentration a concern?", "What is the promoter's personal net worth?"],
    "nlx": ["Does Nimbus pass the minimum DSCR rule?", "Any outward cheque bounces for insufficient funds?", "What is the worst DPD in the last year?", "What interest rate is the overdraft priced at?"],
    "afp": ["How large are related-party sales?", "How fast did unsecured NBFC borrowing grow?", "Is debt to equity within policy?", "What was revenue in FY2022-23?"],
}
PROFILE = {
    "sgp": {"sector": "Automotive plastics", "city": "Pune", "ask": "₹4.5 cr term loan", "bureau": "CMR-3"},
    "nlx": {"sector": "B2B road freight", "city": "Bhiwandi", "ask": "₹1.5 cr WCTL + OD to ₹5.0 cr", "bureau": "CMR-7"},
    "afp": {"sector": "Packaged snacks", "city": "Indore", "ask": "₹6.0 cr term loan + CC to ₹6.0 cr", "bureau": "CMR-4"},
}


def _limit(req: Request):
    ip = req.headers.get("cf-connecting-ip") or (req.client.host if req.client else "?")
    q, now = _hits[ip], time.time()
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= LIMIT_PER_HOUR:
        raise HTTPException(429, "Hourly demo limit reached. This runs on a free model tier, so please try again later.")
    q.append(now)


def _save():
    CACHE.write_text(json.dumps(_cache))


def _hit(c, score):
    return {"id": c.id, "company": COMPANIES.get(c.company, c.company), "doc": c.doc, "section": c.section,
            "text": c.text, "score": round(score, 4)}


def _eval_summary():
    p = ROOT / "evals" / "results.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text())
    a = r.get("answers", {}).get("summary", {})
    return {"retrieval": r.get("retrieval"), "answers": a,
            "memos": {k: {kk: v.get(kk) for kk in ("recommendation", "rec_ok", "flags_found")} for k, v in r.get("memos", {}).items()},
            "ts": r.get("ts")}


@app.get("/api/meta")
def meta():
    docs = sorted(p.stem for p in (ROOT / "data" / "docs").glob("*.md"))
    return {"companies": {k: {"name": v, **PROFILE[k], "samples": SAMPLES[k],
                              "docs": [d for d in docs if d.startswith(k + "_")]} for k, v in COMPANIES.items() if k in PROFILE},
            "policy_docs": [d for d in docs if d.startswith("lending")],
            "chunks": len(INDEX.chunks), "retrieval": "BM25 + Gemini embeddings, RRF" if INDEX.dense is not None else "BM25",
            "llm": llm.available(), "evals": _eval_summary()}


@app.get("/api/doc/{name}")
def doc(name: str):
    if not re.fullmatch(r"[a-z]+_[a-z]+", name):
        raise HTTPException(404)
    p = ROOT / "data" / "docs" / f"{name}.md"
    if not p.exists():
        raise HTTPException(404)
    return {"name": name, "text": p.read_text()}


class Ask(BaseModel):
    q: str = Field(min_length=3, max_length=400)
    company: str


@app.post("/api/ask")
def ask(body: Ask, req: Request):
    if body.company not in PROFILE:
        raise HTTPException(400, "unknown borrower")
    key = hashlib.sha1(f"{body.company}|{body.q.strip().lower()}".encode()).hexdigest()
    if key in _cache:
        return {**_cache[key], "cached": True}
    _limit(req)
    t0 = time.time()
    try:
        hits = INDEX.search(body.q, k=6, company=body.company)
        t1 = time.time()
        r = qa.answer(INDEX, body.q, company=body.company)
    except RuntimeError as e:
        raise HTTPException(503, f"The model is unavailable right now ({str(e)[:120]}). Please retry in a minute.")
    t2 = time.time()
    out = {"question": body.q, "answerable": r["answerable"], "verdict": r["verdict"], "claims": r["claims"],
           "hits": [_hit(c, s) for c, s in r["hits"]], "model": llm.generate.last_model,
           "timing_ms": {"retrieve": int((t1 - t0) * 1000), "answer_verify": int((t2 - t1) * 1000)}}
    del hits
    _cache[key] = out
    _save()
    return {**out, "cached": False}


class Memo(BaseModel):
    company: str
    refresh: bool = False


@app.post("/api/memo")
def memo(body: Memo, req: Request):
    if body.company not in PROFILE:
        raise HTTPException(400, "unknown borrower")
    key = f"memo|{body.company}"
    if key in _cache and not body.refresh:
        return {**_cache[key], "cached": True}
    _limit(req)
    try:
        m = qa.credit_memo(INDEX, body.company)
    except RuntimeError as e:
        raise HTTPException(503, f"The model is unavailable right now ({str(e)[:120]}).")
    out = {k: m[k] for k in ("summary", "flags", "recommendation", "conditions_or_questions")}
    out["hits"] = [_hit(c, s) for c, s in m["hits"]]
    out["model"] = llm.generate.last_model
    _cache[key] = out
    _save()
    return {**out, "cached": False}


@app.exception_handler(HTTPException)
def http_err(_, e: HTTPException):
    return JSONResponse({"error": e.detail}, status_code=e.status_code)


app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html", headers={"Cache-Control": "no-cache"})
