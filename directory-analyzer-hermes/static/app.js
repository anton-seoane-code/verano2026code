(function () {
  'use strict';

  // ── DOM refs ───────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const dirInput = $('#directory-input');
  const browseBtn = $('#browse-btn');
  const analyzeBtn = $('#analyze-btn');
  const organizeBtn = $('#organize-btn');
  const dryRunBtn = $('#dry-run-btn');
  const backBtn = $('#back-btn');
  const reportBackBtn = $('#report-back-btn');
  const browserUpBtn = $('#browser-up-btn');
  const browserHereBtn = $('#browser-here-btn');
  const recursiveToggle = $('#recursive-toggle');
  const duplicatesToggle = $('#duplicates-toggle');
  const copyToggle = $('#copy-toggle');

  const inputSection = $('#input-section');
  const resultsSection = $('#results-section');
  const reportSection = $('#report-section');
  const browserSection = $('#browser-section');

  const statsGrid = $('#stats-grid');
  const dirLabel = $('#directory-label');
  const dupSection = $('#duplicates-section');
  const dupList = $('#duplicates-list');
  const unrecSection = $('#unrecognized-section');
  const unrecList = $('#unrecognized-list');
  const reportOutput = $('#report-output');
  const browserPath = $('#browser-path');
  const browserContent = $('#browser-content');
  const toast = $('#toast');

  // ── State ──────────────────────────────────────
  let currentDir = '';
  let lastAnalysis = null;

  // ── Toast ──────────────────────────────────────
  let toastTimer = null;
  function showToast(msg, type) {
    toast.textContent = msg;
    toast.className = 'toast' + (type ? ' ' + type : '');
    clearTimeout(toastTimer);
    // Force reflow
    void toast.offsetWidth;
    toast.classList.add('show');
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
  }

  // ── API helper ─────────────────────────────────
  async function api(path, body) {
    const resp = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    if (!data.success) throw new Error(data.error || 'Unknown error');
    return data;
  }

  // ── Directory Browser ──────────────────────────
  async function openBrowser(path) {
    try {
      const data = await api('/api/browse', { path: path || '/' });
      browserPath.textContent = data.path;
      const parent = data.parent;
      browserUpBtn.style.display = parent ? 'inline-flex' : 'none';
      browserContent.innerHTML = '';

      if (data.directories.length === 0 && data.files.length === 0) {
        browserContent.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);">Empty directory</div>';
      }

      data.directories.forEach((d) => {
        const el = document.createElement('div');
        el.className = 'browser-dir';
        el.innerHTML = `📁 ${d.name}`;
        el.addEventListener('click', () => openBrowser(d.path));
        browserContent.appendChild(el);
      });

      data.files.forEach((f) => {
        const el = document.createElement('div');
        el.className = 'browser-file';
        el.textContent = `📄 ${f}`;
        browserContent.appendChild(el);
      });

      browserSection.style.display = 'block';
      browserHereBtn.dataset.path = data.path;
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  browseBtn.addEventListener('click', () => {
    const path = dirInput.value.trim() || '/home';
    openBrowser(path);
  });

  browserUpBtn.addEventListener('click', () => {
    const current = browserPath.textContent;
    const parent = current.split('/').slice(0, -1).join('/') || '/';
    openBrowser(parent);
  });

  browserHereBtn.addEventListener('click', () => {
    dirInput.value = browserHereBtn.dataset.path;
    browserSection.style.display = 'none';
  });

  // ── Analysis ───────────────────────────────────
  analyzeBtn.addEventListener('click', runAnalysis);
  dirInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') runAnalysis(); });

  async function runAnalysis() {
    const dir = dirInput.value.trim();
    if (!dir) { showToast('Enter a directory path', 'error'); return; }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing…';
    resultsSection.style.display = 'none';
    reportSection.style.display = 'none';

    try {
      const data = await api('/api/analyze', {
        directory: dir,
        recursive: recursiveToggle.checked,
        detect_duplicates: duplicatesToggle.checked,
      });

      currentDir = data.directory;
      lastAnalysis = data;
      renderResults(data);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = 'Analyze';
    }
  }

  // ── Render ─────────────────────────────────────
  function renderResults(data) {
    dirLabel.textContent = data.directory;

    // Stats cards
    const cats = data.category_counts || {};
    const total = data.total_files;
    const iconMap = { images: '📷', videos: '🎬', documents: '📄' };
    const labelMap = { images: 'Images', videos: 'Videos', documents: 'Documents' };

    statsGrid.innerHTML = '';
    ['images', 'videos', 'documents'].forEach((cat) => {
      const count = cats[cat] || 0;
      const card = document.createElement('div');
      card.className = 'stat-card';
      card.innerHTML = `
        <div class="stat-icon">${iconMap[cat] || '📁'}</div>
        <div class="stat-count">${count}</div>
        <div class="stat-label">${labelMap[cat] || cat}</div>
      `;
      statsGrid.appendChild(card);
    });

    // Total card
    const totalCard = document.createElement('div');
    totalCard.className = 'stat-card stat-total';
    totalCard.innerHTML = `
      <div class="stat-icon">📊</div>
      <div class="stat-count">${total}</div>
      <div class="stat-label">Total Files</div>
    `;
    statsGrid.appendChild(totalCard);

    // Unrecognized
    const unrec = data.unrecognized || [];
    if (unrec.length > 0) {
      unrecSection.style.display = 'block';
      unrecList.innerHTML = '';
      unrec.forEach((path) => {
        const el = document.createElement('div');
        el.className = 'unrec-item';
        // Show just the filename
        const parts = path.split('/');
        el.textContent = parts[parts.length - 1];
        el.title = path;
        unrecList.appendChild(el);
      });
    } else {
      unrecSection.style.display = 'none';
    }

    // Duplicates
    const dups = data.duplicates || {};
    const dupCount = data.duplicate_count || 0;
    if (dupCount > 0) {
      dupSection.style.display = 'block';
      dupList.innerHTML = '';
      Object.entries(dups).forEach(([hash, files]) => {
        const group = document.createElement('div');
        group.className = 'dup-group';
        group.innerHTML = `
          <div class="dup-hash">🔗 ${hash.slice(0, 12)}… (${files.length} files)</div>
          <ul>${files.map((f) => {
            const parts = f.split('/');
            return `<li>${parts[parts.length - 1]}</li>`;
          }).join('')}</ul>
        `;
        dupList.appendChild(group);
      });
    } else {
      dupSection.style.display = 'none';
    }

    resultsSection.style.display = 'block';
  }

  // ── Organize ───────────────────────────────────
  organizeBtn.addEventListener('click', () => doOrganize(false));
  dryRunBtn.addEventListener('click', () => doOrganize(true));

  async function doOrganize(dryRun) {
    if (!currentDir) { showToast('No directory analyzed', 'error'); return; }

    const dir = dryRun ? currentDir : currentDir;

    organizeBtn.disabled = true;
    dryRunBtn.disabled = true;

    try {
      const data = await api('/api/organize', {
        directory: dir,
        recursive: recursiveToggle.checked,
        copy: copyToggle.checked,
      });

      // Show report
      reportOutput.textContent = data.report;
      reportSection.style.display = 'block';

      if (dryRun) {
        showToast('Preview complete', 'success');
      } else {
        const moved = Object.values(data.stats).reduce((sum, s) => {
          if (typeof s === 'object' && s.moved !== undefined) return sum + s.moved;
          return sum;
        }, 0);
        showToast(`Organized ${moved} files into subdirectories`, 'success');
      }
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      organizeBtn.disabled = false;
      dryRunBtn.disabled = false;
    }
  }

  // ── Navigation ─────────────────────────────────
  backBtn.addEventListener('click', () => {
    resultsSection.style.display = 'none';
  });

  reportBackBtn.addEventListener('click', () => {
    reportSection.style.display = 'none';
  });

  // ── Init ───────────────────────────────────────
  // Pre-fill home directory
  dirInput.value = '/home/ars';
})();
