const sourceInput = document.querySelector("#sourceInput");
const optimizedOutput = document.querySelector("#optimizedOutput");
const suggestionList = document.querySelector("#suggestionList");
const optimizeBtn = document.querySelector("#optimizeBtn");
const scoreBadge = document.querySelector("#scoreBadge");
const countBadge = document.querySelector("#countBadge");
const analysisGrid = document.querySelector("#analysisGrid");
const passList = document.querySelector("#passList");
const complexityBadge = document.querySelector("#complexityBadge");
const passBadge = document.querySelector("#passBadge");

sourceInput.value = "";
optimizedOutput.textContent = "";
suggestionList.innerHTML = `<div class="suggestion-item">Feed source code into the optimizer to start the analysis.</div>`;
renderAnalysis(null);
renderPasses([]);

optimizeBtn.addEventListener("click", async () => {
  const source = sourceInput.value.trim();

  if (!source) {
    optimizedOutput.textContent = "";
    suggestionList.innerHTML = `<div class="suggestion-item">Add source code before launching the optimizer.</div>`;
    scoreBadge.textContent = "Score 0";
    countBadge.textContent = "0 found";
    renderAnalysis(null);
    renderPasses([]);
    sourceInput.focus();
    return;
  }

  optimizeBtn.disabled = true;
  optimizeBtn.textContent = "Scanning...";

  try {
    const response = await fetch("/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source })
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "Optimization failed");
    }

    renderResult(result);
  } catch (error) {
    optimizedOutput.textContent = error.message;
    suggestionList.innerHTML = "";
    scoreBadge.textContent = "Score 0";
    countBadge.textContent = "0 found";
    renderAnalysis(null);
    renderPasses([]);
  } finally {
    optimizeBtn.disabled = false;
    optimizeBtn.textContent = "Optimize";
  }
});

function renderResult(result) {
  const suggestions = Array.isArray(result.suggestions) ? result.suggestions : [];
  const passes = Array.isArray(result.passes) ? result.passes : [];

  optimizedOutput.textContent = result.optimized_code || "";
  scoreBadge.textContent = `Score ${result.score ?? 0}`;
  countBadge.textContent = `${suggestions.length} found`;
  renderAnalysis(result.analysis, result.optimized_analysis);
  renderPasses(passes);

  if (suggestions.length === 0) {
    suggestionList.innerHTML = `<div class="suggestion-item">No optimization opportunities found. The current code is already clean.</div>`;
    return;
  }

  suggestionList.innerHTML = suggestions.map((item) => {
    const confidence = Math.round(item.confidence * 100);
    return `
      <article class="suggestion-item">
        <div class="suggestion-title">
          <span>${escapeHtml(item.title)}</span>
          <span class="confidence">line ${item.line || "-"} | ${confidence}%</span>
        </div>
        <p>${escapeHtml(item.explanation)}</p>
        <div class="diff">
          <code>${escapeHtml(item.before)}</code>
          <code>${escapeHtml(item.after)}</code>
        </div>
      </article>
    `;
  }).join("");
}

function renderAnalysis(analysis, optimizedAnalysis = null) {
  if (!analysis) {
    analysisGrid.innerHTML = `<div class="metric wide muted-card">
      <span>Static scan</span>
      <strong>Awaiting source signal</strong>
    </div>`;
    complexityBadge.textContent = "O(?)";
    return;
  }

  complexityBadge.textContent = analysis.estimated_complexity || "O(?)";
  const metrics = [
    ["Source statements", analysis.statement_count],
    ["Source assignments", analysis.assignment_count],
    ["Source loops", analysis.loop_count],
    ["Identifiers", analysis.unique_identifier_count]
  ];

  analysisGrid.innerHTML = metrics.map(([label, value]) => `
    <div class="metric">
      <span>${label}</span>
      <strong>${formatMetric(value)}</strong>
    </div>
  `).join("") + `
    <div class="metric wide">
      <span>Hot identifiers</span>
      <strong>${escapeHtml(formatIdentifiers(analysis.hot_identifiers))}</strong>
    </div>
    ${renderOptimizedAnalysis(analysis, optimizedAnalysis)}
  `;
}

function renderPasses(passes) {
  if (!Array.isArray(passes) || passes.length === 0) {
    passBadge.textContent = "0 active";
    passList.innerHTML = `<div class="pass-item disabled">
      <div>
        <strong>No pipeline data</strong>
        <span>The optimizer response did not include pass reports.</span>
      </div>
      <b>0</b>
    </div>`;
    return;
  }

  const active = passes.filter((item) => item.enabled).length;
  const totalChanges = passes.reduce((total, item) => total + Number(item.changes || 0), 0);
  passBadge.textContent = `${active} active | ${totalChanges} changes`;
  passList.innerHTML = passes.map((item) => `
    <div class="pass-item ${item.enabled ? "" : "disabled"}">
      <div>
        <strong>${escapeHtml(item.name)}</strong>
        <span>${escapeHtml(item.description)}</span>
      </div>
      <b title="${item.enabled ? "Changes made by this pass" : "Pass disabled"}">${formatMetric(item.changes)}</b>
    </div>
  `).join("");
}

function renderOptimizedAnalysis(sourceAnalysis, optimizedAnalysis) {
  if (!optimizedAnalysis) {
    return `<div class="metric wide muted-card">
      <span>Optimized scan</span>
      <strong>Not returned by backend</strong>
    </div>`;
  }

  const loopDelta = Number(sourceAnalysis.loop_count || 0) - Number(optimizedAnalysis.loop_count || 0);
  const statementDelta = Number(sourceAnalysis.statement_count || 0) - Number(optimizedAnalysis.statement_count || 0);

  return `
    <div class="metric">
      <span>Optimized loops</span>
      <strong>${formatMetric(optimizedAnalysis.loop_count)}</strong>
    </div>
    <div class="metric">
      <span>Reduced statements</span>
      <strong>${formatSignedMetric(statementDelta)}</strong>
    </div>
    <div class="metric wide improvement-card">
      <span>Pipeline effect</span>
      <strong>${escapeHtml(formatPipelineEffect(loopDelta, optimizedAnalysis.estimated_complexity))}</strong>
    </div>
  `;
}

function formatPipelineEffect(loopDelta, optimizedComplexity) {
  if (loopDelta > 0) {
    return `${loopDelta} loop removed; optimized scan is ${optimizedComplexity || "available"}`;
  }
  return `Optimized scan is ${optimizedComplexity || "available"}`;
}

function formatMetric(value) {
  return value ?? 0;
}

function formatSignedMetric(value) {
  if (value > 0) {
    return `-${value}`;
  }
  if (value < 0) {
    return `+${Math.abs(value)}`;
  }
  return "0";
}

function formatIdentifiers(items) {
  if (!items || items.length === 0) {
    return "None";
  }
  return items.map(([name, count]) => `${name} (${count})`).join(", ");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
