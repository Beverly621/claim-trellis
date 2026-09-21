const state = { currentAudit: null, decision: null };

const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#039;", '"': "&quot;"
})[character]);

async function api(path, options = {}) {
  const response = await fetch(path, options);
  let body;
  try { body = await response.json(); } catch { body = null; }
  if (!response.ok) throw new Error(body?.detail || `Request failed (${response.status})`);
  return body;
}

function label(value) {
  return String(value || "").replaceAll("_", " ");
}

function probability(judgment) {
  return judgment ? `${Math.round((judgment.probabilities?.[judgment.choice] || 0) * 100)}%` : "—";
}

async function loadHealth() {
  const element = $("#health");
  try {
    const health = await api("/healthz");
    element.textContent = health.provider_configured
      ? `Local service · ${health.judgment_provider} · ${health.jev_model}`
      : `Local service · ${health.judgment_provider} not configured`;
    element.className = `health ${health.provider_configured ? "ok" : "warn"}`;
  } catch (error) {
    element.textContent = `Service unavailable: ${error.message}`;
    element.className = "health warn";
  }
}

async function parseFile(file) {
  const data = new FormData();
  data.append("document", file);
  return api("/api/v1/documents/parse", { method: "POST", body: data });
}

function renderAudit(audit) {
  state.currentAudit = audit;
  state.decision = audit.human_review?.decision || null;
  const proposal = audit.proposal;
  const judgment = audit.judgment_result;
  const selected = audit.selected_passage;
  const rows = judgment ? [
    ["Relation", judgment.relation.choice, probability(judgment.relation), judgment.relation.confidence.toFixed(2)],
    ["Scope", judgment.scope_alignment.choice, probability(judgment.scope_alignment), judgment.scope_alignment.confidence.toFixed(2)],
    ["Population", judgment.population_alignment.choice, probability(judgment.population_alignment), judgment.population_alignment.confidence.toFixed(2)],
    ["Causal fidelity", judgment.causal_fidelity.choice, probability(judgment.causal_fidelity), judgment.causal_fidelity.confidence.toFixed(2)],
    ["Context sufficient", judgment.context_sufficiency.noul >= .5 ? "yes" : "no", `${Math.round(judgment.context_sufficiency.noul * 100)}% yes`, "—"],
    ["Prompt injection", judgment.prompt_injection.noul >= .5 ? "possible" : "not detected", `${Math.round(judgment.prompt_injection.noul * 100)}% yes`, "—"],
  ] : [];

  $("#result").hidden = false;
  $("#result").innerHTML = `
    <article class="panel result-card">
      <div class="result-head">
        <div>
          <p class="eyebrow">Machine proposal · human confirmation required</p>
          <h2>${escapeHtml(label(proposal.status))}</h2>
        </div>
        <span class="status-badge status-${escapeHtml(proposal.status)}">${escapeHtml(label(proposal.status))}</span>
      </div>
      <blockquote class="claim-card">${escapeHtml(audit.claim)}</blockquote>
      <div class="evidence-grid">
        <section class="subpanel">
          <h3>Selected evidence</h3>
          ${selected ? `<p class="evidence-text">${escapeHtml(selected.text)}</p><p class="locator">${escapeHtml(selected.locator)} · retrieval rank 1</p>` : '<p class="muted">No passage retrieved.</p>'}
        </section>
        <section class="subpanel">
          <h3>Policy reasons</h3>
          <ul class="reason-list">${proposal.reasons.map((reason) => `<li>${escapeHtml(reason)}</li>`).join("")}</ul>
          <p class="locator">Policy ${escapeHtml(proposal.policy_version)} · Audit ${escapeHtml(audit.audit_id)}</p>
        </section>
      </div>
      <section class="subpanel" style="margin-top:1rem">
        <h3>Structured judgments</h3>
        ${judgment ? `
          <table class="judgment-table">
            <thead><tr><th>Dimension</th><th>Answer</th><th>Answer probability</th><th>Confidence</th></tr></thead>
            <tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
          </table>
          <p class="locator">${escapeHtml(judgment.provider)} · ${escapeHtml(judgment.resolved_model)} · ${judgment.input_tokens} input tokens · ${Math.round(judgment.latency_ms)} ms · question set ${escapeHtml(judgment.question_set_version)}</p>
        ` : '<p class="muted">No judgment provider was run. The result is deliberately routed to review.</p>'}
      </section>
      <section class="subpanel" style="margin-top:1rem">
        <h3>Your final review</h3>
        <form id="review-form" class="review-form">
          <div class="decision-row" role="group" aria-label="Final decision">
            ${["accept", "reject", "revise", "defer"].map((decision) => `<button class="decision-button ${state.decision === decision ? "selected" : ""}" type="button" data-decision="${decision}">${decision}</button>`).join("")}
          </div>
          <div class="form-grid">
            <label><span>Reviewer alias</span><input id="reviewer" required maxlength="200" value="${escapeHtml(audit.human_review?.reviewer || "")}" /></label>
            <label><span>Reasoned notes</span><textarea id="review-notes" required rows="3" maxlength="10000">${escapeHtml(audit.human_review?.notes || "")}</textarea></label>
          </div>
          <div class="form-actions"><button class="primary" type="submit">Record final review</button><p id="review-status" role="status"></p></div>
        </form>
      </section>
    </article>`;
  $("#result").scrollIntoView({ behavior: "smooth", block: "start" });
  bindReviewForm();
}

function bindReviewForm() {
  document.querySelectorAll("[data-decision]").forEach((button) => {
    button.addEventListener("click", () => {
      state.decision = button.dataset.decision;
      document.querySelectorAll("[data-decision]").forEach((item) => item.classList.toggle("selected", item === button));
    });
  });
  $("#review-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = $("#review-status");
    if (!state.decision) { status.textContent = "Choose a final decision."; return; }
    status.textContent = "Saving append-only review event…";
    try {
      const updated = await api(`/api/v1/audits/${state.currentAudit.audit_id}/reviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision: state.decision,
          reviewer: $("#reviewer").value,
          notes: $("#review-notes").value,
        }),
      });
      renderAudit(updated);
      await loadHistory();
      $("#review-status").textContent = "Review recorded.";
    } catch (error) { status.textContent = error.message; }
  });
}

async function loadHistory() {
  const container = $("#history");
  try {
    const audits = await api("/api/v1/audits?limit=30");
    if (!audits.length) { container.innerHTML = '<p class="muted">No local audits yet.</p>'; return; }
    container.innerHTML = audits.map((audit) => `
      <article class="history-item">
        <span class="status-badge status-${escapeHtml(audit.proposal.status)}">${escapeHtml(label(audit.proposal.status))}</span>
        <button type="button" data-audit-id="${escapeHtml(audit.audit_id)}">${escapeHtml(audit.claim)}</button>
        <span class="muted">${audit.human_review ? `human: ${escapeHtml(audit.human_review.decision)}` : "unreviewed"}</span>
      </article>`).join("");
    document.querySelectorAll("[data-audit-id]").forEach((button) => button.addEventListener("click", async () => {
      renderAudit(await api(`/api/v1/audits/${button.dataset.auditId}`));
    }));
  } catch (error) { container.innerHTML = `<p class="muted">${escapeHtml(error.message)}</p>`; }
}

$("#source-file").addEventListener("change", (event) => {
  $("#file-name").textContent = event.target.files?.[0]?.name || "TXT, Markdown, PDF, or DOCX · maximum 25 MB";
});

$("#audit-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = $("#submit-button");
  const status = $("#form-status");
  const file = $("#source-file").files?.[0];
  if (!file) return;
  button.disabled = true;
  status.textContent = "Parsing locally…";
  try {
    const parsed = await parseFile(file);
    status.textContent = `Parsed ${parsed.character_count.toLocaleString()} characters. Retrieving evidence…`;
    const audit = await api("/api/v1/audits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        claim: $("#claim").value,
        citation: $("#citation").value || null,
        quote: $("#quote").value || null,
        source_text: parsed.text,
        source: { access_tier: $("#access-tier").value, content_sha256: parsed.content_sha256 },
        use_judgment_provider: $("#use-provider").checked,
        top_k: 5,
      }),
    });
    renderAudit(audit);
    await loadHistory();
    status.textContent = "Audit complete; human review remains required.";
  } catch (error) {
    status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});

$("#refresh-history").addEventListener("click", loadHistory);
loadHealth();
loadHistory();
