"""Run the CreditLens eval suite.
  python -m evals.run --retrieval-only   # no LLM calls (BM25 only unless embeddings cached)
  python -m evals.run                    # full: retrieval (3 modes) + answers + memos
Writes evals/results.json and evals/REPORT.md
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from creditlens import llm, qa  # noqa: E402
from creditlens.retrieval import Index  # noqa: E402
from evals.golden import MEMO, QA  # noqa: E402

OUT = Path(__file__).parent


def retrieval_eval(index: Index, modes: list[str], k: int = 6) -> dict:
    res = {}
    items = [x for x in QA if x["gold"]]
    for mode in modes:
        recall, full = 0.0, 0
        for x in items:
            got = {c.id.split("#")[0] for c, _ in index.search(x["q"], k=k, company=x["company"], mode=mode)}
            hit = len(set(x["gold"]) & got) / len(x["gold"])
            recall += hit
            full += hit == 1.0
        res[mode] = {"recall@%d" % k: round(recall / len(items), 3), "all_gold_found": f"{full}/{len(items)}"}
    return res


def answer_eval(index: Index) -> dict:
    rows = []
    for x in QA:
        t = time.time()
        try:
            r = qa.answer(index, x["q"], company=x["company"])
        except Exception as e:  # keep the run going; count as failure
            rows.append({"id": x["id"], "error": str(e)[:200]})
            continue
        text = " ".join(c["text"] for c in r["claims"]) + " " + r["verdict"]
        expect_ans = x.get("answerable", True)
        row = {"id": x["id"], "q": x["q"], "answerable_pred": r["answerable"], "answerable_gold": expect_ans,
               "answer": text.strip(), "latency_s": round(time.time() - t, 1),
               "claims": len(r["claims"]),
               "supported": sum(c["check"]["status"] == "supported" for c in r["claims"]),
               "uncited": sum(c["check"]["status"] == "uncited" for c in r["claims"])}
        if expect_ans:
            row["correct"] = r["answerable"] and all(m.lower() in text.lower() for m in x["must"])
        else:
            row["correct"] = not r["answerable"]
        rows.append(row)
        time.sleep(1)
    ok = [r for r in rows if "error" not in r]
    ans = [r for r in ok if r["answerable_gold"]]
    na = [r for r in ok if not r["answerable_gold"]]
    claims = sum(r["claims"] for r in ok) or 1
    return {
        "rows": rows,
        "summary": {
            "n": len(rows), "errors": len(rows) - len(ok),
            "answer_accuracy": f"{sum(r['correct'] for r in ans)}/{len(ans)}",
            "abstention_accuracy": f"{sum(r['correct'] for r in na)}/{len(na)}",
            "false_abstentions": sum(not r["answerable_pred"] for r in ans),
            "citation_support_rate": round(sum(r["supported"] for r in ok) / claims, 3),
            "uncited_claims": sum(r["uncited"] for r in ok),
            "median_latency_s": sorted(r["latency_s"] for r in ok)[len(ok) // 2] if ok else None,
        },
    }


def memo_eval(index: Index) -> dict:
    out = {}
    for co, exp in MEMO.items():
        try:
            m = qa.credit_memo(index, co)
        except Exception as e:
            out[co] = {"error": str(e)[:200]}
            continue
        blob = " ".join((f["title"] + " " + f["evidence"]).lower() for f in m["flags"] if f["severity"] != "positive")
        found = [k for k in exp["must_flag"] if k in blob]
        out[co] = {"recommendation": m["recommendation"], "rec_ok": m["recommendation"] in exp["recommendation"],
                   "flags_found": f"{len(found)}/{len(exp['must_flag'])}",
                   "missed": [k for k in exp["must_flag"] if k not in found],
                   "flag_citation_support": f"{sum(f['check']['status'] == 'supported' for f in m['flags'])}/{len(m['flags'])}",
                   "flags": [{k: f[k] for k in ("severity", "title", "evidence")} for f in m["flags"]]}
        time.sleep(2)
    return out


def report(res: dict) -> str:
    L = ["# CreditLens eval report", "", f"Run: {res['ts']} | models: {', '.join(llm.CHAT_MODELS)} | embed: {llm.EMBED_MODEL}", "",
         "## Retrieval (gold evidence docs in top 6)", "", "| Mode | Recall@6 | All gold found |", "|---|---|---|"]
    for m, v in res["retrieval"].items():
        L.append(f"| {m} | {v['recall@6']} | {v['all_gold_found']} |")
    if "answers" in res:
        s = res["answers"]["summary"]
        L += ["", "## Answers", "", *(f"- {k.replace('_', ' ')}: {v}" for k, v in s.items()), "",
              "| id | correct | abstained | claims supported | answer |", "|---|---|---|---|---|"]
        for r in res["answers"]["rows"]:
            if "error" in r:
                L.append(f"| {r['id']} | ERROR | | | {r['error'][:80]} |")
            else:
                L.append(f"| {r['id']} | {'✅' if r['correct'] else '❌'} | {not r['answerable_pred']} | {r['supported']}/{r['claims']} | {r['answer'][:140].replace('|', '/')} |")
    if "memos" in res:
        L += ["", "## Credit memos", "", "| Borrower | Recommendation | Rec OK | Risk flags found | Missed | Flag citations supported |", "|---|---|---|---|---|---|"]
        for co, v in res["memos"].items():
            if "error" in v:
                L.append(f"| {co} | ERROR {v['error'][:60]} | | | | |")
            else:
                L.append(f"| {co} | {v['recommendation']} | {'✅' if v['rec_ok'] else '❌'} | {v['flags_found']} | {', '.join(v['missed']) or '-'} | {v['flag_citation_support']} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrieval-only", action="store_true")
    a = ap.parse_args()
    idx = Index()
    modes = ["bm25"] + (["dense", "hybrid"] if idx.dense is not None else [])
    res = {"ts": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "retrieval": retrieval_eval(idx, modes)}
    if not a.retrieval_only:
        res["answers"] = answer_eval(idx)
        res["memos"] = memo_eval(idx)
    (OUT / "results.json").write_text(json.dumps(res, indent=2, default=str))
    (OUT / "REPORT.md").write_text(report(res))
    print(report(res))
