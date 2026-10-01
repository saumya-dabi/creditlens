"""Chunking + hybrid retrieval (BM25 + Gemini embeddings, fused with RRF) with company filter."""
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from . import llm

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "docs"
CACHE = ROOT / "data" / "index.json"

COMPANIES = {
    "sgp": "Shree Ganesh Polymers Pvt Ltd",
    "nlx": "Nimbus Logistics LLP",
    "afp": "Aarohi Foods Pvt Ltd",
    "lending": "Credit policy",
}
DOC_TYPES = {"financials": "Financials", "gst": "GST returns", "bank": "Bank statements",
             "bureau": "Bureau report", "request": "Loan request", "policy": "Credit policy"}


@dataclass
class Chunk:
    id: str
    company: str
    doc: str
    section: str
    text: str


def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9.]+", s.lower())


def load_chunks() -> list[Chunk]:
    chunks = []
    for path in sorted(DOCS.glob("*.md")):
        company, doctype = path.stem.split("_", 1)
        raw = path.read_text()
        title = raw.splitlines()[0].lstrip("# ").strip()
        header = raw.split("\n## ")[0]
        for i, sec in enumerate(raw.split("\n## ")):
            name = "Overview" if i == 0 else sec.splitlines()[0].strip()
            body = sec if i == 0 else f"## {sec}"
            # every chunk carries the doc title so it is self-describing
            text = body if i == 0 else f"{title}\n{body}"
            chunks.append(Chunk(id=f"{path.stem}#{i}", company=company, doc=DOC_TYPES.get(doctype, doctype),
                                section=name, text=text.strip()))
        del header
    return chunks


class Index:
    def __init__(self, use_dense: bool | None = None):
        self.chunks = load_chunks()
        self.bm25 = BM25Okapi([_tok(c.text) for c in self.chunks])
        self.dense = None
        if use_dense is None:
            use_dense = llm.available()
        if use_dense:
            self.dense = self._load_or_embed()

    def _load_or_embed(self) -> np.ndarray:
        sig = [c.id + str(len(c.text)) for c in self.chunks]
        if CACHE.exists():
            data = json.loads(CACHE.read_text())
            if data.get("sig") == sig:
                return np.array(data["vecs"], dtype=np.float32)
        vecs = llm.embed([c.text for c in self.chunks])
        CACHE.write_text(json.dumps({"sig": sig, "vecs": vecs}))
        return np.array(vecs, dtype=np.float32)

    def search(self, query: str, k: int = 6, company: str | None = None, mode: str = "hybrid") -> list[tuple[Chunk, float]]:
        allowed = [i for i, c in enumerate(self.chunks) if company is None or c.company in (company, "lending")]
        rankings = []
        if mode in ("hybrid", "bm25"):
            s = self.bm25.get_scores(_tok(query))
            rankings.append(sorted(allowed, key=lambda i: -s[i]))
        if mode in ("hybrid", "dense") and self.dense is not None:
            q = np.array(llm.embed([query], task="RETRIEVAL_QUERY")[0], dtype=np.float32)
            d = self.dense @ q / (np.linalg.norm(self.dense, axis=1) * np.linalg.norm(q) + 1e-9)
            rankings.append(sorted(allowed, key=lambda i: -d[i]))
        fused: dict[int, float] = {}
        for r in rankings:  # reciprocal rank fusion
            for rank, i in enumerate(r):
                fused[i] = fused.get(i, 0) + 1 / (60 + rank)
        top = sorted(fused, key=lambda i: -fused[i])[:k]
        return [(self.chunks[i], fused[i]) for i in top]


def chunk_dict(c: Chunk) -> dict:
    return asdict(c)
