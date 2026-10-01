"""Grounded answering with sentence-level citations, abstention, and a deterministic citation verifier."""
import re

from . import llm
from .retrieval import COMPANIES, Index

SYSTEM = """You are CreditLens, a credit-analyst copilot for an Indian SME lender.
Rules:
- Answer ONLY from the numbered sources. Never use outside knowledge for facts or numbers.
- Every factual claim must end with citations like [S2] or [S1][S4] pointing to the source that contains it.
- Copy numbers exactly as written in the sources (units included). Do not compute new figures unless asked; if you compute, show the inputs with their citations.
- When the question involves a policy threshold, compare the company figure with the policy and say clearly whether it passes, fails, or is a watch-list item.
- If the sources do not contain the answer, set answerable=false and say what is missing. Do not guess.
- Be concise: 2-6 short claims."""

SCHEMA = {
    "type": "object",
    "properties": {
        "answerable": {"type": "boolean"},
        "claims": {"type": "array", "items": {"type": "object", "properties": {
            "text": {"type": "string"},
            "sources": {"type": "array", "items": {"type": "integer"}}},
            "required": ["text", "sources"]}},
        "verdict": {"type": "string", "description": "One-line takeaway for the credit analyst"},
    },
    "required": ["answerable", "claims", "verdict"],
}

NUM = re.compile(r"\d+(?:\.\d+)?")


def _numbers(s: str) -> set[str]:
    out = set()
    for n in NUM.findall(s.replace(",", "")):
        out.add(n.rstrip("0").rstrip(".") if "." in n else n)
    return out


def verify_claim(claim: dict, sources: list) -> dict:
    """A claim is 'supported' if it cites >=1 valid source and every number in it appears in a cited source.
    Small integers (<=12: months, counts like 'Q4') are ignored to avoid noise; years are ignored too."""
    ids = [i for i in claim.get("sources", []) if 1 <= i <= len(sources)]
    if not ids:
        return {"status": "uncited", "missing": []}
    cited = " ".join(sources[i - 1][0].text for i in ids)
    have = _numbers(cited)
    need = {n for n in _numbers(claim["text"]) if not (n.isdigit() and (int(n) <= 12 or 1990 <= int(n) <= 2030))}
    missing = sorted(n for n in need if n not in have)
    return {"status": "supported" if not missing else "unsupported_number", "missing": missing}


def answer(index: Index, question: str, company: str | None = None, k: int = 6, mode: str = "hybrid") -> dict:
    hits = index.search(question, k=k, company=company, mode=mode)
    ctx = "\n\n".join(f"[S{i}] ({COMPANIES.get(c.company, c.company)} | {c.doc} | {c.section})\n{c.text}"
                      for i, (c, _) in enumerate(hits, 1))
    scope = f"The analyst is reviewing {COMPANIES[company]}." if company else ""
    prompt = f"{scope}\nQuestion: {question}\n\nSources:\n{ctx}"
    out = llm.generate_json(prompt, SCHEMA, system=SYSTEM)
    for c in out.get("claims", []):
        c["check"] = verify_claim(c, hits)
    return {"question": question, "company": company, "hits": hits, **out}


# ---------------------------------------------------------------- credit memo
MEMO_SYSTEM = """You are CreditLens. Produce a pre-screen credit memo for the analyst using ONLY the numbered sources.
For each risk flag, quote the company figure, the policy rule it is checked against, and cite both.
Severity: 'hard_fail' = breaches a hard eligibility rule; 'watch' = hits a watch-list trigger; 'positive' = a mitigating strength.
Recommendation must be one of: 'Proceed', 'Proceed with conditions', 'Refer to credit committee', 'Decline'. Never invent facts."""

MEMO_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "flags": {"type": "array", "items": {"type": "object", "properties": {
            "severity": {"type": "string", "enum": ["hard_fail", "watch", "positive"]},
            "title": {"type": "string"},
            "evidence": {"type": "string"},
            "sources": {"type": "array", "items": {"type": "integer"}}},
            "required": ["severity", "title", "evidence", "sources"]}},
        "recommendation": {"type": "string", "enum": ["Proceed", "Proceed with conditions", "Refer to credit committee", "Decline"]},
        "conditions_or_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "flags", "recommendation", "conditions_or_questions"],
}


def credit_memo(index: Index, company: str) -> dict:
    hits = [(c, 1.0) for c in index.chunks if c.company in (company, "lending")]
    ctx = "\n\n".join(f"[S{i}] ({COMPANIES.get(c.company, c.company)} | {c.doc} | {c.section})\n{c.text}"
                      for i, (c, _) in enumerate(hits, 1))
    out = llm.generate_json(f"Borrower: {COMPANIES[company]}\n\nSources:\n{ctx}", MEMO_SCHEMA, system=MEMO_SYSTEM)
    for f in out.get("flags", []):
        f["check"] = verify_claim({"text": f["evidence"], "sources": f["sources"]}, hits)
    out["hits"] = hits
    return out
