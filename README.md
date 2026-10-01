# 🔎 CreditLens: a cited, self-checking credit copilot for SME lending

**Live demo:** see the link on [saumya-dabi-portfolio.vercel.app](https://saumya-dabi-portfolio.vercel.app) · **Eval report:** [evals/REPORT.md](evals/REPORT.md)

## The problem
A credit analyst at an Indian SME lender reads five or more documents per borrower: audited financials, GST returns, bank-statement analysis, bureau report and the loan request. They then check every figure against the credit policy. A generic chatbot doesn't help here. One wrong DSCR or a missed cheque bounce is a bad loan. The product bar is **every claim traceable, and silence when the file is silent**.

## What it does
- **Ask the file.** Ask questions in plain English, scoped to one borrower. Each claim carries `[S#]` citations to the source chunk.
- **Citation verifier.** Deterministic, no LLM. Every number in a claim must appear in the chunk it cites, otherwise the claim is flagged ⚠️. The model never grades itself.
- **Abstention.** If the file doesn't contain the answer (for example, the promoter's net worth), the copilot says so instead of guessing.
- **Pre-screen memo.** Reads the whole file against the credit policy and outputs hard-fail, watch-list and strength flags, a recommendation, and questions for the borrower.

## How it works
```
docs (md) ─► section chunks ─► BM25 ┐
                              Gemini embeddings ┘─► RRF fusion ─► top-6 (borrower + policy only)
                                                         │
                         Gemini 2.5 Flash, JSON schema: {answerable, claims[{text, sources}], verdict}
                                                         │
                                     number-level citation verifier ─► UI badges
```
Design choices and trade-offs:
| Decision | Why | Trade-off |
|---|---|---|
| Hybrid retrieval (BM25 + dense, RRF) | Credit questions are full of exact tokens (GSTR-3B, DPD, CMR-7) that dense embeddings blur | Two indexes to keep in sync |
| Hard company filter + always include policy | Cross-borrower leakage is the worst failure in lending | Can't answer comparison questions unless scope = all |
| Structured JSON output | Makes citations machine-checkable | Slightly stiffer prose |
| Rule-based verifier, not LLM-as-judge | Cheap, deterministic, explainable to a credit head | Checks numbers, not reasoning |
| Free-tier Gemini + model fallback | $0 to run | Rate limits under load |

## Evals
`python -m evals.run` runs 26 golden questions (22 answerable, 4 deliberately unanswerable) and 3 memo ground truths. It measures:
retrieval recall@6 (BM25 vs dense vs hybrid), answer accuracy, abstention accuracy, citation support rate, and memo flag recall. Results are in [evals/REPORT.md](evals/REPORT.md).

## Data
Three **fictional** borrowers, each with a different risk profile:
- a clean manufacturer with one GST gap
- a stressed logistics LLP: DSCR below 1, cheque bounces, 32 DPD, credit shopping
- a fast-growing food company with related-party and unsecured-debt risk

There is also a credit policy extract. Regenerate them with `python data/build_corpus.py`.

## Run
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...   # free key from aistudio.google.com
streamlit run app.py
```

## Next, if this were a product
PDF/bank-statement ingestion, analyst feedback loop on flags (precision by flag type), policy versioning, and an audit log per memo.

Built by [Saumya Dabi](https://saumya-dabi-portfolio.vercel.app). Started from patterns in [awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) (RAG with citations, RAG failure diagnostics), rebuilt for a lending workflow I worked on at CreditQ.
