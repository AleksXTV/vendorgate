const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const pct = x => x == null ? "–" : Math.round(100 * x) + "%";
const LABEL = {approve:"Approve", approve_with_conditions:"Approve with conditions", escalate:"Escalate to Security / Legal",
  reject:"Reject", human_review:"Human review required"};
const DOCS = [["sales_email","Sales email"],["contract","Contract"],["questionnaire","Questionnaire"],["install_script","install.sh"],["vendor","Vendor profile"]];
let samples = [], cur = null, curDoc = "sales_email", live = false, timer = null;

async function boot() {
  live = (await (await fetch("/api/config")).json()).live;
  $("#mode").textContent = live ? "● live: Clocked API key loaded" : "○ no API key: recorded runs only";
  $("#runLive").disabled = !live;
  samples = await (await fetch("/api/samples")).json();
  $("#sampleTabs").innerHTML = samples.map(s => `<button data-id="${s.id}">${esc(s.vendor.name)}</button>`).join("");
  $("#sampleTabs").onclick = e => e.target.dataset.id && pick(e.target.dataset.id);
  $("#docTabs").innerHTML = DOCS.map(([k, l]) => `<button data-k="${k}">${l}</button>`).join("");
  $("#docTabs").onclick = e => e.target.dataset.k && showDoc(e.target.dataset.k);
  $("#docEditor").oninput = () => { if (curDoc === "vendor") { try { cur.vendor = JSON.parse($("#docEditor").value) } catch (_) {} } else cur[curDoc] = $("#docEditor").value; };
  $("#runLive").onclick = runLive;
  $("#openRecorded").onclick = openRecorded;
  const q = new URLSearchParams(location.search);
  pick(q.get("sample") || samples[0].id);
  if (q.get("recorded")) openRecorded();
}
function pick(id) {
  cur = structuredClone(samples.find(s => s.id === id));
  document.querySelectorAll("#sampleTabs button").forEach(b => b.classList.toggle("on", b.dataset.id === id));
  const v = cur.vendor;
  $("#vendorCard").innerHTML = `<b>${esc(v.name)}</b> · ${esc(v.service)}<div class="row">Data: ${esc((v.data||[]).join("; "))}</div><div class="row">Deployment: ${esc(v.deployment)} · ~$${esc(v.annual_value_usd)}/yr</div>`;
  $("#openRecorded").disabled = !cur.recorded;
  showDoc("sales_email");
}
function showDoc(k) {
  curDoc = k;
  document.querySelectorAll("#docTabs button").forEach(b => b.classList.toggle("on", b.dataset.k === k));
  $("#docEditor").value = k === "vendor" ? JSON.stringify(cur.vendor, null, 2) : (cur[k] || "");
}
async function runLive() {
  $("#runLive").disabled = true;
  const r = await fetch("/api/reviews", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({vendor: cur.vendor, sales_email: cur.sales_email, contract: cur.contract, questionnaire: cur.questionnaire, install_script: cur.install_script})});
  if (!r.ok) { alert((await r.json()).detail); $("#runLive").disabled = false; return; }
  const {id} = await r.json();
  clearInterval(timer);
  timer = setInterval(async () => {
    const s = await (await fetch(`/api/reviews/${id}`)).json();
    render(s);
    if (!s.running) { clearInterval(timer); $("#runLive").disabled = false; }
  }, 700);
}
async function openRecorded() { render(await (await fetch(`/api/recorded/${cur.id}`)).json(), true); }

function render(rep, recorded) {
  const d = rep.decision || {};
  const v = $("#verdict");
  if (rep.error) { v.className = "verdict human_review"; v.innerHTML = `<h2>Run failed</h2><div class="sub">${esc(rep.error)}</div>`; }
  else if (rep.running || !d.final) { v.className = "verdict empty"; v.innerHTML = `Reviewing <b>${esc(rep.vendor?.name)}</b>… ${rep.stages?.filter(s => s.status !== "running").length || 0} of 9 stages done`; }
  else {
    v.className = "verdict " + d.final;
    v.innerHTML = `<h2>${LABEL[d.final] || d.final}</h2>
      <div class="sub">${esc(rep.vendor.name)} · risk <b>${esc(d.risk_tier)}</b> · model recommendation <b>${esc(LABEL[d.model_choice] || d.model_choice)}</b> at ${pct(d.model_confidence)}${d.needs_human_signoff ? " · <b>human sign-off required</b>" : ""}</div>
      ${rep.memo?.headline ? `<p>${esc(rep.memo.headline)}</p>` : ""}
      ${(d.guardrails || []).length ? `<div class="guard"><b>Guardrails applied (code, not model):</b><br>${d.guardrails.map(esc).join("<br>")}</div>` : ""}
      <div class="sub" style="margin-top:6px">${rep.usage?.requests} Clocked requests · ${rep.usage?.credits ?? "–"} credits · ${rep.usage?.wall_seconds}s${recorded ? ` · recorded run (${esc(rep.recorded_at)})` : ""}</div>`;
  }
  $("#stages").innerHTML = (rep.stages || []).map(s => `<details class="stage" ${s.status === "warn" || s.status === "failed" ? "open" : ""}>
    <summary><span class="dot ${s.status}"></span><div><div class="t">${esc(s.title)}</div><div class="s">${esc(s.summary)}</div></div>
    <div class="eps">${s.endpoints.map(e => `<span class="ep">/${e}</span>`).join("")}</div></summary>
    <div class="body">${s.status === "running" ? "…" : detail(s, rep)}</div></details>`).join("");
  $("#trace").innerHTML = (rep.trace || []).map(c => `<div class="call">${c.ok ? "✓" : "✗"} <b>${esc(c.label)}</b> POST /clocked/${c.endpoint} · ${c.ms} ms · ${c.credits ?? "–"} credits
    <details><summary>request / response JSON</summary><pre class="code">${esc(JSON.stringify(c.request, null, 1))}</pre><pre class="code">${esc(JSON.stringify(c.response ?? c.error, null, 1))}</pre></details></div>`).join("");
}

function highlight(text, spans, cls) {
  spans = (spans || []).filter(s => s && s.start != null && s.end != null).sort((a, b) => a.start - b.start);
  let out = "", i = 0; const chars = Array.from(text || "");
  for (const s of spans) { if (s.start < i) continue; out += esc(chars.slice(i, s.start).join("")) + `<mark class="${cls || ""}" title="${esc(s.title || "")}">` + esc(chars.slice(s.start, s.end).join("")) + "</mark>"; i = s.end; }
  out += esc(chars.slice(i).join(""));
  return out.replace(/&lt;(PERSON|EMAIL|PHONE)&gt;/g, '<span class="ph">&lt;$1&gt;</span>').replace(/\[QUARANTINED BY VENDORGATE: suspected prompt injection\]/g, '<mark class="bad">[QUARANTINED: suspected prompt injection]</mark>');
}
const chip = (txt, kind) => `<span class="chip c-${kind}">${esc(txt)}</span>`;
const vchip = v => chip(String(v).replace(/_/g, " "), {supported:"ok", meets:"ok", benign:"ok", use:"ok", contradicted:"bad", violates:"bad", malicious:"bad", injection:"bad", not_stated:"warn", not_established:"warn", suspicious:"warn", expand:"warn", skip:"mut"}[v] || "mut");

function detail(s, rep) {
  const f = rep.findings || {}, d = s.data || {};
  if (s.status === "failed") return `<div class="guard">${esc(d.error)}</div>`;
  switch (s.id) {
    case "intake": return Object.entries(d.documents || {}).map(([k, x]) => {
      const g = x.guard || {}, p = x.protect || {};
      return `<p><b>${esc(k)}</b> · guard ${vchip(g.verdict || "unknown")} ${g.verdict && g.verdict !== "benign" ? `${esc(g.category)}, severity ${esc(g.severity)}, p=${pct(g.injection)}` : ""} · ${(p.entities || []).length} personal-data values replaced</p>
        ${(g.evidence || []).map(e => `<div class="q bad">“${esc(e.quote)}”</div>`).join("")}
        <div class="doc">${highlight(rep.documents?.[k] || "")}</div>`; }).join("");
    case "script": {
      const lines = new Set((d.evidence || []).map(e => e.line?.trim()));
      const code = (rep.original_documents?.install_script || "").split("\n").map(l => lines.has(l.trim()) ? `<span class="hl">${esc(l)}</span>` : esc(l)).join("\n");
      return `<p>${vchip(d.verdict)} ${esc(d.category)} · severity ${esc(d.severity)} · malicious ${pct(d.malicious)} · suspicious ${pct(d.suspicious)}</p><pre class="code">${code}</pre>`; }
    case "terms": {
      const t = f.terms || {};
      const spans = Object.entries(t).filter(([, x]) => x.start != null).map(([k, x]) => ({start: x.start, end: x.end, title: k}));
      return `<table><tr><th>Term</th><th>Value (verbatim)</th><th>Normalized</th><th>Conf.</th></tr>${Object.entries(t).map(([k, x]) =>
        `<tr><td>${esc(k.replace(/_/g, " "))}</td><td>${x.value == null || (Array.isArray(x.value) && !x.value.length) ? chip("not stated", "warn") : esc(Array.isArray(x.value) ? x.value.map(v => typeof v === "object" ? JSON.stringify(v) : v).join(", ") : x.value)}</td><td>${esc(typeof x.normalized === "object" ? JSON.stringify(x.normalized) : x.normalized ?? "")}</td><td>${pct(x.confidence)}</td></tr>`).join("")}</table>
        <p class="s">Highlighted in the contract (masked copy):</p><div class="doc">${highlight(rep.documents?.contract, spans)}</div>`; }
    case "policy": return `<table><tr><th>Requirement</th><th>Action</th><th>Applies</th></tr>${(d.results || []).map(x =>
        `<tr><td>${esc(x.id)}</td><td>${vchip(x.action)} ${x.reason ? `<span class="s">${esc(x.reason.replace(/_/g, " "))}</span>` : ""}</td><td><div class="bar"><i style="width:${pct(x.relevance_score)}"></i></div>${pct(x.relevance_score)}</td></tr>`).join("")}</table>`;
    case "conflicts": return (f.conflicts || []).length ? f.conflicts.map(c => `<div class="pair"><div class="q bad"><b>${esc(c.a?.document)}</b><br>“${esc(c.a?.quote)}”</div><div class="q bad"><b>${esc(c.b?.document)}</b><br>“${esc(c.b?.quote)}”</div></div>`).join("")
        : `<p>No conflicts. Pair relations: ${(d.pairs || []).map(p => `${esc(p.a)}↔${esc(p.b)}: ${esc(p.relation)}`).join(", ")}</p>`;
    case "claims": return `<table><tr><th>Sales claim</th><th>Verdict</th><th>Evidence</th></tr>${(f.claims || []).map(c =>
        `<tr><td>${esc(c.claim)}</td><td>${vchip(c.verdict)}<br><span class="s">support ${pct(c.supported)}</span></td><td>${c.evidence ? `<div class="q">${esc(c.evidence.document)}: “${esc(c.evidence.quote)}”</div>` : ""}</td></tr>`).join("")}</table>`;
    case "compliance": return `<table><tr><th>Requirement</th><th>Result</th><th>Probabilities</th></tr>${Object.entries(f.compliance || {}).map(([k, c]) =>
        `<tr><td><b>${esc(k)}</b><br><span class="s">${esc(c.title)}</span></td><td>${vchip(c.choice)}</td><td>${Object.entries(c.probabilities || {}).map(([l, p]) => `${esc(l.replace(/_/g, " "))} ${pct(p)}`).join(" · ")}</td></tr>`).join("")}</table>`;
    case "decision": { const x = rep.decision || {};
      return `<table><tr><th>Option</th><th>Probability</th></tr>${Object.entries(x.probabilities || {}).map(([l, p]) => `<tr><td>${esc(LABEL[l] || l)}</td><td><div class="bar"><i style="width:${pct(p)}"></i></div>${pct(p)}</td></tr>`).join("")}</table>
        <p>Risk tier: <b>${esc(x.risk_tier)}</b> (expected level ${x.risk_score?.toFixed?.(2) ?? "–"} of 3) · fixable by negotiation: ${pct(x.fixable_by_negotiation)}</p>`; }
    case "memo": { const m = rep.memo || {}; const bad = m.unsupported_lines || [];
      let asks = esc(m.asks || ""); bad.forEach(b => { asks = asks.replace(esc(b), `<mark class="bad" title="not grounded in the findings">${esc(b)}</mark>`); });
      return `<p><b>Self-check (Verify):</b> ${pct(m.grounded)} grounded${bad.length ? `, ${bad.length} line(s) flagged` : ""} · Legal review needed: ${m.legal_review === true ? "yes" : m.legal_review === false ? "no" : "–"}</p>
        <p class="s">What to ask the vendor</p><div class="memo">${asks}</div>
        ${bad.length ? `<p class="s">Not grounded, check by hand:</p>${bad.map(b => `<div class="q bad">${esc(b)}</div>`).join("")}` : ""}
        <p class="s">Draft email to the vendor</p><div class="memo">${esc(m.vendor_email || "")}</div>`; }
  }
  return "";
}
boot();
