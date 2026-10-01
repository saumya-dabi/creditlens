const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const icon = (n, cls = "i") => `<svg class="${cls}"><use href="#i-${n}"/></svg>`;
const NUM = /\d+(?:[.,]\d+)?/g;
const SKIP = /(FY\s?\d{4}(?:-\d{2,4})?|\b(?:19|20)\d{2}\b|\bQ[1-4]\b|\bS\d+\b|CMR-\d+|GSTR-\d[A-Z]?)/g;
// apply fn to every number that is not part of a fiscal-year, year, quarter, citation or form label
const mapNums = (str, fn) => str.split(SKIP).map((part, i) => i % 2 ? part : part.replace(NUM, fn)).join("");
const norm = n => { n = n.replace(/,/g, ""); return n.includes(".") ? n.replace(/0+$/, "").replace(/\.$/, "") : n; };

const state = { meta: null, co: "nlx", hits: [], tab: "ask", busy: false };
const BADGE = {
  supported: `<span class="badge pass">${icon("check")}verified</span>`,
  unsupported_number: `<span class="badge watch">${icon("alert")}unverified</span>`,
  uncited: `<span class="badge fail">${icon("x")}uncited</span>`,
};

async function api(path, body) {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
  const j = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
  return j;
}

/* ---------- boot ---------- */
async function boot() {
  try {
    state.meta = await api("/api/meta");
  } catch (e) {
    $("#bname").textContent = "Couldn't reach the server";
    $("#status").className = "status off"; $("#status span").textContent = "offline";
    return;
  }
  const st = $("#status");
  st.className = "status " + (state.meta.llm ? "on" : "off");
  $("span", st).textContent = state.meta.llm ? "model online" : "model offline";
  const p = new URLSearchParams(location.search).get("b");
  if (p && state.meta.companies[p]) state.co = p;
  renderBorrowers(); selectBorrower(state.co, false); renderEvals();
}

function renderBorrowers() {
  const tone = { "CMR-3": "pass", "CMR-4": "watch", "CMR-7": "fail" };
  $("#borrowers").innerHTML = Object.entries(state.meta.companies).map(([k, c]) => `
    <button class="bw" role="radio" aria-checked="${k === state.co}" data-co="${k}">
      <b>${esc(c.name)}</b><span>${esc(c.sector)} · ${esc(c.city)}</span>
      <em class="badge ${tone[c.bureau] || "dim"}">${esc(c.bureau)}</em></button>`).join("");
  $$(".bw").forEach(b => b.onclick = () => selectBorrower(b.dataset.co));
}

const DOCNAME = { financials: "Audited financials", gst: "GST return analysis", bank: "Bank statement analysis", bureau: "Commercial bureau report", request: "Loan request note", policy: "Credit policy extract" };

function selectBorrower(co, push = true) {
  state.co = co;
  const c = state.meta.companies[co];
  $$(".bw").forEach(b => b.setAttribute("aria-checked", b.dataset.co === co));
  $("#bname").textContent = c.name;
  $("#bmeta").innerHTML = `<span>${esc(c.sector)}, ${esc(c.city)}</span><span>Request <b>${esc(c.ask)}</b></span><span>Bureau <b class="num">${esc(c.bureau)}</b></span>`;
  $("#manifest").innerHTML = [...c.docs, ...state.meta.policy_docs].map(d => `<li><button data-doc="${d}">${icon("doc")}${DOCNAME[d.split("_")[1]] || d}</button></li>`).join("");
  $$("#manifest button").forEach(b => b.onclick = () => openDoc(b.dataset.doc));
  $("#samples").innerHTML = c.samples.map(s => `<button class="chip" type="button">${esc(s)}</button>`).join("");
  $$("#samples .chip").forEach(b => b.onclick = () => { $("#q").value = b.textContent; ask(); });
  resetAnswer(); $("#memo").innerHTML = ""; setEvidence([]);
  if (push) history.replaceState(null, "", `?b=${co}`);
}

function resetAnswer() {
  $("#pipe").hidden = true;
  $("#answer").innerHTML = $("#answer").dataset.empty ||= $("#answer").innerHTML;
}

/* ---------- tabs ---------- */
$$(".tabs button").forEach(b => b.onclick = () => {
  state.tab = b.dataset.tab;
  $$(".tabs button").forEach(x => x.setAttribute("aria-selected", x === b));
  $$(".tab").forEach(t => t.hidden = t.id !== `tab-${state.tab}`);
});

/* ---------- evidence rail ---------- */
function setEvidence(hits, numsByIdx = {}) {
  state.hits = hits;
  $("#evcount").textContent = hits.length ? `${hits.length} passages` : "";
  if (!hits.length) { $("#ev").innerHTML = `<p class="ev-empty">Retrieved passages appear here, ranked by hybrid search (BM25 + embeddings, fused with RRF), always scoped to this borrower plus the credit policy.</p>`; return; }
  const max = Math.max(...hits.map(h => h.score || 1));
  $("#ev").innerHTML = hits.map((h, i) => {
    const want = new Set(numsByIdx[i + 1] || []);
    const body = mapNums(esc(h.text), m => want.has(norm(m)) ? `<mark class="hit">${m}</mark>` : m);
    return `<article class="src ${h.company === "Credit policy" ? "policy" : ""}" data-i="${i + 1}">
      <header><b>S${i + 1}</b><span title="${esc(h.doc + " · " + h.section)}">${esc(h.doc)} · ${esc(h.section)}</span>
      <span class="bar" title="retrieval score"><i style="width:${Math.round(100 * (h.score || 1) / max)}%"></i></span></header>
      <pre>${body}</pre></article>`;
  }).join("");
}

function focusSources(ids) {
  const list = $("#ev");
  list.classList.toggle("focus", ids.length > 0);
  $$(".src", list).forEach(s => s.classList.toggle("on", ids.includes(+s.dataset.i)));
  const first = ids.length && $(`.src[data-i="${ids[0]}"]`, list);
  if (first && window.matchMedia("(min-width:1241px)").matches) first.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

/* ---------- ask ---------- */
$("#askf").onsubmit = e => { e.preventDefault(); ask(); };

function stage(name, cls, t) {
  const s = $(`.stage[data-s="${name}"]`); s.className = "stage " + cls;
  if (t !== undefined) $("em", s).textContent = t;
}

async function ask() {
  const q = $("#q").value.trim();
  if (q.length < 3 || state.busy) return;
  state.busy = true; $("#askb").disabled = true;
  $("#pipe").hidden = false; ["retrieve", "answer", "verify"].forEach(s => stage(s, "", ""));
  stage("retrieve", "run");
  $("#answer").innerHTML = `<div class="verdict"><div class="vi"><span class="skel" style="width:18px"></span></div><div style="flex:1;display:grid;gap:9px"><span class="skel" style="width:70%"></span><span class="skel" style="width:45%"></span></div></div>
    <ul class="claims">${[88, 72, 80].map(w => `<li class="claim"><span class="skel" style="width:${w}%"></span></li>`).join("")}</ul>`;
  const tick = setTimeout(() => { stage("retrieve", "done"); stage("answer", "run"); }, 700);
  try {
    const r = await api("/api/ask", { q, company: state.co });
    clearTimeout(tick);
    stage("retrieve", "done", r.cached ? "cached" : `${r.timing_ms.retrieve} ms`);
    stage("answer", "done", r.cached ? "" : `${(r.timing_ms.answer_verify / 1000).toFixed(1)} s`);
    stage("verify", "run");
    await new Promise(res => setTimeout(res, 260));
    const n = r.claims.length, ok = r.claims.filter(c => c.check.status === "supported").length;
    stage("verify", "done", n ? `${ok}/${n} verified` : "abstained");
    renderAnswer(r);
  } catch (e) {
    clearTimeout(tick);
    ["retrieve", "answer", "verify"].forEach(s => stage(s, ""));
    $("#answer").innerHTML = `<div class="err">${icon("alert")}<div><b>That didn't go through.</b><br>${esc(e.message)}</div><button class="btn sec" id="retry">${icon("refresh")}Retry</button></div>`;
    $("#retry").onclick = ask;
  } finally { state.busy = false; $("#askb").disabled = false; }
}

function claimNums(c) {
  const out = []; mapNums(c.text, m => { out.push(norm(m)); return m; });
  return [...new Set(out)].filter(n => !(/^\d+$/.test(n) && +n <= 12));
}

function renderAnswer(r) {
  const numsByIdx = {};
  r.claims.forEach(c => { const ns = claimNums(c); c.sources.forEach(i => (numsByIdx[i] ||= []).push(...ns)); });
  setEvidence(r.hits, numsByIdx);
  const vcls = r.answerable ? "ok" : "na";
  const vlabel = r.answerable ? "Answer" : "Not in the file";
  $("#answer").innerHTML = `
    <div class="verdict ${vcls} rise"><div class="vi">${icon(r.answerable ? "shield" : "ban")}</div>
      <div><div class="label vl">${vlabel}</div><div class="vt">${esc(r.verdict)}</div></div></div>
    <ul class="claims">${r.claims.map((c, k) => {
      const missing = new Set(c.check.missing || []);
      const body = mapNums(esc(c.text).replace(/\s*\[S\d+\](\[S\d+\])*/g, ""), m => {
        const v = norm(m); const keep = claimNums({ text: m }).length;
        return keep ? `<mark class="${missing.has(v) ? "bad" : ""}">${m}</mark>` : m;
      });
      return `<li class="claim rise" style="animation-delay:${60 + k * 50}ms" data-src="${c.sources.join(",")}">
        <p>${body}</p><div class="meta">${c.sources.map(i => `<button class="cite" data-i="${i}" aria-label="Show source S${i}">S${i}</button>`).join("")}${BADGE[c.check.status] || ""}</div></li>`;
    }).join("")}</ul>
    <div class="runinfo"><span>${r.cached ? "served from cache" : "model " + esc(r.model || "")}</span><span>${r.hits.length} passages retrieved</span>${r.claims.length ? `<span>${r.claims.filter(c => c.check.status === "supported").length}/${r.claims.length} claims verified against source</span>` : ""}</div>`;
  $$(".claim").forEach(li => {
    const ids = li.dataset.src.split(",").filter(Boolean).map(Number);
    li.onmouseenter = () => { li.classList.add("hot"); focusSources(ids); };
    li.onmouseleave = () => { li.classList.remove("hot"); focusSources([]); };
    li.onfocusin = li.onmouseenter; li.onfocusout = li.onmouseleave;
  });
  $$(".cite").forEach(b => b.onclick = () => focusSources([+b.dataset.i]));
  $("#footmodel").textContent = r.model ? `last answer · ${r.model}` : "";
}

/* ---------- documents ---------- */
async function openDoc(name) {
  $$("#manifest button").forEach(b => b.classList.toggle("lit", b.dataset.doc === name));
  try {
    const d = await api(`/api/doc/${name}`);
    $("#evcount").textContent = "full document";
    $("#ev").classList.remove("focus");
    $("#ev").innerHTML = `<article class="src on"><header><b>DOC</b><span>${esc(DOCNAME[name.split("_")[1]] || name)}</span></header><pre style="max-height:none">${esc(d.text)}</pre></article>`;
  } catch (e) { /* ignore */ }
}

/* ---------- memo ---------- */
$("#memob").onclick = () => memo(false);
async function memo(refresh) {
  const b = $("#memob"); b.disabled = true;
  $("#memo").innerHTML = `<div class="rec"><span class="label">Reading all documents against policy</span><span class="skel" style="width:240px;height:22px"></span><p><span class="skel" style="width:90%"></span></p></div>
    <div class="flags">${[0, 1, 2].map(() => `<div class="flag"><span class="skel" style="width:60%"></span><span class="skel" style="width:85%;grid-column:1"></span></div>`).join("")}</div>`;
  try {
    const m = await api("/api/memo", { company: state.co, refresh });
    renderMemo(m);
  } catch (e) {
    $("#memo").innerHTML = `<div class="err" style="margin-top:22px">${icon("alert")}<div><b>Memo failed.</b><br>${esc(e.message)}</div><button class="btn sec" id="mretry">${icon("refresh")}Retry</button></div>`;
    $("#mretry").onclick = () => memo(refresh);
  } finally { b.disabled = false; }
}

function renderMemo(m) {
  const hitsShort = m.hits.map(h => ({ ...h }));
  const recCls = { "Decline": "decline", "Refer to credit committee": "refer", "Proceed with conditions": "refer", "Proceed": "proceed" }[m.recommendation] || "";
  const by = s => m.flags.filter(f => f.severity === s);
  const group = (s, title, color) => by(s).length ? `<div class="flaggroup"><h4><i style="background:${color}"></i>${title} · ${by(s).length}</h4>${by(s).map(f => `
    <div class="flag rise"><b>${esc(f.title)}</b><div class="meta">${f.sources.slice(0, 4).map(i => `<button class="cite" data-i="${i}">S${i}</button>`).join("")}${BADGE[f.check.status] || ""}</div><p>${esc(f.evidence.replace(/\s*\[S\d+\]/g, ""))}</p></div>`).join("")}</div>` : "";
  $("#memo").innerHTML = `
    <div class="rec ${recCls} rise" data-stamp="${esc({ "Decline": "Declined", "Refer to credit committee": "Referred", "Proceed with conditions": "Conditional", "Proceed": "Approved" }[m.recommendation] || "")}"><span class="label">Recommendation</span><h3>${esc(m.recommendation)}</h3>
      <div class="tally"><span class="badge fail">${by("hard_fail").length} hard fail</span><span class="badge watch">${by("watch").length} watch</span><span class="badge pass">${by("positive").length} strengths</span></div>
      <p>${esc(m.summary.replace(/\s*\[S\d+\]/g, ""))}</p></div>
    <div class="flags">${group("hard_fail", "Hard-rule breaches", "var(--fail)")}${group("watch", "Watch-list triggers", "var(--watch)")}${group("positive", "Mitigating strengths", "var(--pass)")}</div>
    ${m.conditions_or_questions.length ? `<div class="qs"><div class="label">Conditions and questions for the borrower</div><ol>${m.conditions_or_questions.map(q => `<li>${esc(q)}</li>`).join("")}</ol></div>` : ""}
    <div class="runinfo"><span>${m.cached ? "served from cache" : "model " + esc(m.model || "")}</span><span>${m.hits.length} passages read</span><button class="chip" id="regen">${icon("refresh")}Regenerate</button></div>`;
  setEvidence(hitsShort);
  $$("#memo .cite").forEach(b => b.onclick = () => focusSources([+b.dataset.i]));
  $$("#memo .flag").forEach(f => { const ids = $$(".cite", f).map(b => +b.dataset.i); f.onmouseenter = () => focusSources(ids); f.onmouseleave = () => focusSources([]); });
  $("#regen").onclick = () => memo(true);
}

/* ---------- evals ---------- */
function renderEvals() {
  const e = state.meta.evals;
  if (!e) { $("#evals").innerHTML = `<p class="prose">Eval results haven't been generated yet.</p>`; return; }
  const a = e.answers || {}, r = e.retrieval || {};
  const pct = v => typeof v === "number" ? `${Math.round(v * 100)}%` : v;
  $("#evals").innerHTML = `
    <div class="evgrid">
      <div class="metric"><div class="label">Answer accuracy</div><b>${esc(a.answer_accuracy)}</b><span>golden questions answered correctly</span></div>
      <div class="metric"><div class="label">Abstention</div><b>${esc(a.abstention_accuracy)}</b><span>unanswerable questions correctly refused</span></div>
      <div class="metric"><div class="label">Citation support</div><b>${pct(a.citation_support_rate)}</b><span>claims whose numbers appear in the cited source</span></div>
      <div class="metric"><div class="label">Retrieval recall@6</div><b>${pct((r.hybrid || r.bm25 || {})["recall@6"])}</b><span>gold evidence in the top six passages</span></div>
    </div>
    <table class="evtable"><thead><tr><th>Borrower</th><th>Memo recommendation</th><th>Matches analyst</th><th>Risk flags caught</th></tr></thead><tbody>
      ${Object.entries(e.memos || {}).map(([k, v]) => `<tr><td>${esc(state.meta.companies[k]?.name || k)}</td><td>${esc(v.recommendation)}</td><td>${v.rec_ok ? `<span class="badge pass">${icon("check")}yes</span>` : `<span class="badge fail">${icon("x")}no</span>`}</td><td class="num">${esc(v.flags_found)}</td></tr>`).join("")}
    </tbody></table>
    <div class="prose">
      <h3>What's measured</h3>
      <p>26 golden questions written against the three files: 22 with a known answer and 4 that the file can't answer, to test refusal. Retrieval is scored on whether the gold document lands in the top six. Answers are scored on required figures. Citation support is checked by code, not by the model: every number in a claim must exist in the passage it cites.</p>
      <h3>Known gaps</h3>
      <p>The verifier checks numbers, not reasoning, so a claim can quote the right figure and still draw the wrong conclusion. The memo misses collateral as a flag in two of the three files, and that's the next prompt fix. Run date ${esc(e.ts || "")}. Full report in <a href="https://github.com/saumya-dabi/creditlens/blob/main/evals/REPORT.md" target="_blank" rel="noopener">evals/REPORT.md</a>.</p>
    </div>`;
}

boot();
