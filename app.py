"""CreditLens — Streamlit UI."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from creditlens import llm, qa  # noqa: E402
from creditlens.retrieval import COMPANIES, Index  # noqa: E402

st.set_page_config(page_title="CreditLens — SME credit copilot", page_icon="🔎", layout="wide")


@st.cache_resource
def get_index():
    return Index()


SAMPLES = {
    "sgp": ["Does the collateral cover the proposed term loan as per policy?", "How big is the GSTR-1 vs GSTR-3B gap?", "Is customer concentration a concern?"],
    "nlx": ["Does Nimbus pass the minimum DSCR rule?", "Any outward cheque bounces for insufficient funds?", "What is the worst DPD in the last year?"],
    "afp": ["How large are related-party sales?", "How fast did unsecured borrowing grow?", "What was revenue in FY2022-23?"],
}
BADGE = {"supported": "✅ verified", "unsupported_number": "⚠️ number not found in cited source", "uncited": "❌ no citation"}
SEV = {"hard_fail": "🔴 Hard fail", "watch": "🟠 Watch", "positive": "🟢 Strength"}

st.title("🔎 CreditLens")
st.caption("A credit-analyst copilot for SME lending. It answers from the borrower's file with citations, refuses when the file is silent, "
           "and checks every number it quotes against the cited source. All borrowers and figures are fictional.")

if not llm.available():
    st.error("LLM key not configured on this server: retrieval works, answers are disabled.")

idx = get_index()
with st.sidebar:
    co = st.radio("Borrower file", list(SAMPLES), format_func=lambda c: COMPANIES[c])
    st.markdown("**In the file:** financials · GST returns · bank statements · bureau report · loan request, plus the lender's credit policy.")
    st.markdown(f"Retrieval: {'BM25 + Gemini embeddings (RRF)' if idx.dense is not None else 'BM25'}")
    st.markdown("[Eval report](https://github.com/saumya-dabi/creditlens/blob/main/evals/REPORT.md) · [Code](https://github.com/saumya-dabi/creditlens)")

tab_qa, tab_memo, tab_docs = st.tabs(["Ask the file", "Pre-screen memo", "Source documents"])

with tab_qa:
    cols = st.columns(3)
    for col, s in zip(cols, SAMPLES[co]):
        if col.button(s, use_container_width=True):
            st.session_state.q = s
    q = st.text_input("Question", key="q", placeholder="e.g. Does the DSCR meet policy?")
    if q and llm.available():
        with st.spinner("Retrieving and answering..."):
            try:
                r = qa.answer(idx, q, company=co)
            except Exception as e:
                st.error(f"Model call failed (free-tier limits?): {e}")
                st.stop()
        if not r["answerable"]:
            st.warning("**Not in the file.** " + r["verdict"])
        else:
            st.success(r["verdict"])
        for c in r["claims"]:
            refs = " ".join(f"`S{i}`" for i in c["sources"])
            st.markdown(f"- {c['text']} {refs} — {BADGE[c['check']['status']]}"
                        + (f" (missing: {', '.join(c['check']['missing'])})" if c["check"]["missing"] else ""))
        with st.expander(f"Retrieved sources ({len(r['hits'])})"):
            for i, (c, s) in enumerate(r["hits"], 1):
                st.markdown(f"**S{i}** · {COMPANIES.get(c.company, c.company)} · {c.doc} · {c.section}")
                st.code(c.text, language="markdown")

with tab_memo:
    st.write("Runs every document in the file against the credit policy and drafts a pre-screen memo with cited risk flags.")
    if st.button(f"Generate memo for {COMPANIES[co]}", type="primary", disabled=not llm.available()):
        with st.spinner("Reading the full file..."):
            try:
                st.session_state[f"memo_{co}"] = qa.credit_memo(idx, co)
            except Exception as e:
                st.error(f"Model call failed: {e}")
    m = st.session_state.get(f"memo_{co}")
    if m:
        st.subheader(f"Recommendation: {m['recommendation']}")
        st.write(m["summary"])
        for sev in ("hard_fail", "watch", "positive"):
            for f in [f for f in m["flags"] if f["severity"] == sev]:
                st.markdown(f"**{SEV[sev]} — {f['title']}**  \n{f['evidence']} "
                            + " ".join(f"`S{i}`" for i in f["sources"]) + f" — {BADGE[f['check']['status']]}")
        if m["conditions_or_questions"]:
            st.markdown("**Conditions / questions for the borrower**")
            for x in m["conditions_or_questions"]:
                st.markdown(f"- {x}")

with tab_docs:
    for path in sorted((Path(__file__).parent / "data" / "docs").glob("*.md")):
        if path.stem.startswith(co) or path.stem.startswith("lending"):
            with st.expander(path.stem):
                st.markdown(path.read_text())
