let currentResults = {};
let currentFile = null;

document.getElementById("scanBtn").addEventListener("click", scanDirectory);
document.getElementById("dirInput").addEventListener("keydown", e => {
  if (e.key === "Enter") scanDirectory();
});
document.getElementById("selectAll").addEventListener("change", function() {
  document.querySelectorAll(".file-checkbox").forEach(cb => cb.checked = this.checked);
  updateFileCount();
});
document.getElementById("generateBtn").addEventListener("click", generate);
document.getElementById("clearHistoryBtn").addEventListener("click", clearHistory);

loadHistory();

async function scanDirectory() {
  const dir = document.getElementById("dirInput").value.trim();
  if (!dir) return;

  const res = await fetch("/api/scan", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({dir})
  });
  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  renderFileList(data.files);
  document.getElementById("filesSection").style.display = "block";
  document.getElementById("optionsSection").style.display = "block";
  document.getElementById("resultsSection").style.display = "none";
  currentResults = {};
  currentFile = null;
}

function renderFileList(files) {
  const list = document.getElementById("fileList");
  list.innerHTML = "";
  files.forEach(f => {
    const div = document.createElement("div");
    div.className = "file-item";
    div.innerHTML = `
      <input type="checkbox" class="file-checkbox" value="${f.name}" checked>
      <span class="file-name">${f.name}</span>
      <span class="file-size">${formatSize(f.size)}</span>
    `;
    div.querySelector(".file-checkbox").addEventListener("change", updateFileCount);
    list.appendChild(div);
  });
  updateFileCount();
}

function updateFileCount() {
  const checked = document.querySelectorAll(".file-checkbox:checked").length;
  const total = document.querySelectorAll(".file-checkbox").length;
  document.getElementById("fileCount").textContent = `${checked} / ${total} files`;
  const allChecked = checked === total && total > 0;
  document.getElementById("selectAll").checked = allChecked;
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

async function generate() {
  const dir = document.getElementById("dirInput").value.trim();
  const files = Array.from(document.querySelectorAll(".file-checkbox:checked")).map(cb => cb.value);
  if (files.length === 0) return alert("Select at least one file.");

  const options = {
    summaries: document.getElementById("genSummaries").checked,
    mindmaps: document.getElementById("genMindmaps").checked,
    quizzes: document.getElementById("genQuizzes").checked,
  };
  if (!options.summaries && !options.mindmaps && !options.quizzes) {
    return alert("Select at least one output type.");
  }

  const progress = document.getElementById("progress");
  progress.style.display = "flex";

  const res = await fetch("/api/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({dir, files, options})
  });
  const data = await res.json();

  progress.style.display = "none";
  currentResults = data.results || {};
  currentFile = Object.keys(currentResults)[0];
  showResults();
  loadHistory();
}

function showResults() {
  document.getElementById("resultsSection").style.display = "block";
  renderTabs();
  renderResultPanel();
}

function renderTabs() {
  const container = document.getElementById("fileTabs");
  container.innerHTML = "";
  Object.keys(currentResults).forEach((fname, i) => {
    const btn = document.createElement("button");
    btn.className = "tab-btn" + (i === 0 ? " active" : "");
    btn.textContent = fname;
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFile = fname;
      renderResultPanel();
    });
    container.appendChild(btn);
  });
}

function renderResultPanel() {
  const container = document.getElementById("resultContent");
  container.innerHTML = "";

  const res = currentResults[currentFile];
  if (!res) return;

  if (res.error) {
    container.innerHTML = `<div class="result-panel active"><p style="color:var(--danger)">Error: ${res.error}</p></div>`;
    return;
  }

  const panels = document.createElement("div");
  let first = true;

  if (res.summary) {
    const panel = createPanel("summary", "Summary", first);
    const text = document.createElement("div");
    text.className = "summary-text";
    text.innerHTML = markdownToHtml(res.summary.content);
    panel.appendChild(text);

    const pdfBtn = document.createElement("button");
    pdfBtn.className = "pdf-btn";
    pdfBtn.textContent = "Download PDF";
    pdfBtn.dataset.content = res.summary.content;
    pdfBtn.dataset.title = `Summary - ${currentFile}`;
    pdfBtn.addEventListener("click", downloadPdf);
    panel.appendChild(pdfBtn);

    panels.appendChild(panel);
    if (first) first = false;
  }

  if (res.mindmap) {
    const panel = createPanel("mindmap", "Mind Map", first);
    const mmContainer = document.createElement("div");
    mmContainer.className = "mindmap-container";
    const svg = document.createElement("div");
    svg.className = "markmap";
    svg.textContent = res.mindmap.content;
    mmContainer.appendChild(svg);
    panel.appendChild(mmContainer);
    panels.appendChild(panel);
    if (first) first = false;
  }

  if (res.quiz) {
    const panel = createPanel("quiz", "Quiz", first);
    renderQuiz(panel, res.quiz.questions);
    panels.appendChild(panel);
    if (first) first = false;
  }

  container.appendChild(panels);

  setTimeout(() => {
    if (window.markmap && document.querySelector(".markmap")) {
      markmap.autoLoader.renderAll();
    }
    document.querySelectorAll(".markmap").forEach(el => {
      if (el._rendered) return;
      el._rendered = true;
    });
  }, 100);
}

function createPanel(id, label, active) {
  const div = document.createElement("div");
  div.className = "result-panel" + (active ? " active" : "");
  div.dataset.panel = id;
  div.innerHTML = `<h3>${label}</h3>`;
  return div;
}

function renderQuiz(container, questions) {
  if (!questions || questions.length === 0) {
    container.innerHTML += "<p style='color:var(--text-secondary)'>No questions generated.</p>";
    return;
  }

  questions.forEach((q, idx) => {
    const qDiv = document.createElement("div");
    qDiv.className = "quiz-question";
    qDiv.innerHTML = `<div class="q-text">${idx + 1}. ${q.question}</div>`;

    Object.entries(q.options).forEach(([label, text]) => {
      const optDiv = document.createElement("div");
      optDiv.className = "quiz-option";
      optDiv.innerHTML = `
        <input type="radio" name="q${idx}" value="${label}">
        <span>${label}) ${text}</span>
      `;
      optDiv.querySelector("input").addEventListener("change", function() {
        const correct = q.answer;
        const parent = this.closest(".quiz-question");
        parent.querySelectorAll(".quiz-option").forEach(o => {
          o.classList.remove("correct", "wrong", "reveal-correct");
        });
        if (this.value === correct) {
          this.parentElement.classList.add("correct");
        } else {
          this.parentElement.classList.add("wrong");
          parent.querySelector(`.quiz-option input[value="${correct}"]`).parentElement.classList.add("reveal-correct");
        }
      });
      qDiv.appendChild(optDiv);
    });

    const revealBtn = document.createElement("button");
    revealBtn.className = "reveal-btn";
    revealBtn.textContent = "Reveal answer";
    revealBtn.addEventListener("click", function() {
      const parent = this.closest(".quiz-question");
      parent.querySelectorAll(".quiz-option").forEach(o => o.classList.remove("correct", "wrong"));
      parent.querySelector(`.quiz-option input[value="${q.answer}"]`).parentElement.classList.add("correct");
    });
    qDiv.appendChild(revealBtn);

    container.appendChild(qDiv);
  });
}

async function downloadPdf(e) {
  const btn = e.currentTarget;
  if (btn.classList.contains("loading")) return;
  btn.classList.add("loading");
  btn.textContent = "Generating PDF...";

  try {
    const res = await fetch("/api/export/pdf", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        content: btn.dataset.content,
        title: btn.dataset.title,
      })
    });
    if (!res.ok) throw new Error("Export failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = (btn.dataset.title || "summary") + ".pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    alert("PDF export failed: " + err.message);
  } finally {
    btn.classList.remove("loading");
    btn.textContent = "Download PDF";
  }
}

async function loadHistory() {
  const res = await fetch("/api/history");
  const data = await res.json();
  const entries = data.entries || [];

  const section = document.getElementById("historySection");
  const list = document.getElementById("historyList");

  if (entries.length === 0) {
    section.style.display = "none";
    return;
  }

  section.style.display = "block";
  list.innerHTML = "";

  entries.forEach(entry => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.dataset.id = entry.id;

    const time = new Date(entry.timestamp);
    const timeStr = time.toLocaleString(undefined, {
      month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit"
    });

    div.innerHTML = `
      <span class="history-item-time">${timeStr}</span>
      <span class="history-item-dir">${escapeHtml(entry.directory)}</span>
      <span class="history-item-files">${entry.files.length} file(s)</span>
    `;

    div.addEventListener("click", () => restoreHistory(entry.id));
    list.appendChild(div);
  });
}

async function restoreHistory(id) {
  const res = await fetch(`/api/history/${id}`);
  const entry = await res.json();
  if (!entry || entry.error) return;

  currentResults = entry.results || {};
  currentFile = Object.keys(currentResults)[0];
  showResults();
  document.getElementById("dirInput").value = entry.directory;

  const options = entry.options || {};
  document.getElementById("genSummaries").checked = !!options.summaries;
  document.getElementById("genMindmaps").checked = !!options.mindmaps;
  document.getElementById("genQuizzes").checked = !!options.quizzes;

  if (entry.files) {
    renderFileList(entry.files.map(f => typeof f === "string" ? {name: f, size: 0} : f));
    document.getElementById("filesSection").style.display = "block";
    document.getElementById("optionsSection").style.display = "block";
  }
}

async function clearHistory() {
  if (!confirm("Clear all history?")) return;
  await fetch("/api/history/clear", {method: "POST"});
  loadHistory();
}

function markdownToHtml(md) {
  const lines = md.split("\n");
  let html = "";
  let inList = false;
  lines.forEach(line => {
    if (line.startsWith("# ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h1>${escapeHtml(line.slice(2))}</h1>`;
    } else if (line.startsWith("## ")) {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<h2>${escapeHtml(line.slice(3))}</h2>`;
    } else if (line.startsWith("- ")) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += `<li>${escapeHtml(line.slice(2))}</li>`;
    } else if (line.startsWith("   ")) {
      if (inList) { html += "<ul>"; inList = true; }
      html += `<li>${escapeHtml(line.trim())}</li>`;
    } else if (line.trim() === "") {
      if (inList) { html += "</ul>"; inList = false; }
      html += "<br>";
    } else {
      if (inList) { html += "</ul>"; inList = false; }
      html += `<p>${escapeHtml(line)}</p>`;
    }
  });
  if (inList) html += "</ul>";
  return html;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
