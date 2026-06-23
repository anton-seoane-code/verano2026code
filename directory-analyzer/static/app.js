(() => {
  const pathInput = document.getElementById('path-input');
  const browseBtn = document.getElementById('browse-btn');
  const treeBrowser = document.getElementById('tree-browser');
  const recursiveCheck = document.getElementById('recursive');
  const detectDupsCheck = document.getElementById('detect-dups');
  const actionRadios = document.querySelectorAll('input[name="action"]');
  const analyzeBtn = document.getElementById('analyze-btn');
  const organizeBtn = document.getElementById('organize-btn');
  const clearBtn = document.getElementById('clear-btn');
  const resultsContent = document.getElementById('results-content');
  const reportContent = document.getElementById('report-content');
  const reportSection = document.getElementById('report-section');
  const loader = document.getElementById('loader');
  const loaderText = document.getElementById('loader-text');

  let selectedDirectory = '';
  let lastAnalyzeResult = null;

  function getAction() {
    for (const r of actionRadios) {
      if (r.checked) return r.value;
    }
    return 'move';
  }

  function showLoader(text) {
    loaderText.textContent = text;
    loader.classList.remove('hidden');
  }

  function hideLoader() {
    loader.classList.add('hidden');
  }

  async function apiPost(endpoint, data) {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  }

  async function browseTree(path) {
    try {
      const data = await apiPost('/api/browse', { path });
      if (!data.success) return [];
      return data;
    } catch {
      return null;
    }
  }

  async function buildTree(rootPath) {
    treeBrowser.innerHTML = '';
    treeBrowser.classList.add('visible');

    const data = await browseTree(rootPath);
    if (!data) {
      treeBrowser.innerHTML = '<div class="tree-item" style="color:#999">Error loading directory</div>';
      return;
    }

    const rootItem = createTreeItem(data.path, data.path, true);
    treeBrowser.appendChild(rootItem);

    const children = createChildrenContainer(data.directories, data.parent);
    rootItem.appendChild(children);

    if (data.parent) {
      const upItem = document.createElement('div');
      upItem.className = 'tree-item';
      upItem.innerHTML = '<span class="arrow">↩</span><span class="icon">📂</span><span class="label">..</span>';
      upItem.dataset.path = data.parent;
      upItem.addEventListener('click', (e) => {
        e.stopPropagation();
        buildTree(data.parent);
      });
      treeBrowser.insertBefore(upItem, treeBrowser.firstChild);
    }
  }

  function createTreeItem(path, label, expanded) {
    const item = document.createElement('div');
    item.className = 'tree-item' + (path === selectedDirectory ? ' selected' : '');
    item.dataset.path = path;

    const arrow = document.createElement('span');
    arrow.className = 'arrow';
    arrow.textContent = expanded ? '▼' : '▶';
    item.appendChild(arrow);

    const icon = document.createElement('span');
    icon.className = 'icon';
    icon.textContent = '📁';
    item.appendChild(icon);

    const labelSpan = document.createElement('span');
    labelSpan.className = 'label';
    labelSpan.textContent = label.split('/').pop() || label;
    item.appendChild(labelSpan);

    item.addEventListener('click', async (e) => {
      e.stopPropagation();
      const childrenContainer = item.nextElementSibling;

      if (childrenContainer && childrenContainer.classList.contains('tree-children')) {
        if (childrenContainer.style.display === 'none') {
          childrenContainer.style.display = '';
          item.querySelector('.arrow').textContent = '▼';
          if (childrenContainer.children.length === 0) {
            await loadChildren(childrenContainer, path, item);
          }
        } else {
          childrenContainer.style.display = 'none';
          item.querySelector('.arrow').textContent = '▶';
        }
      }

      document.querySelectorAll('.tree-item.selected').forEach(el => el.classList.remove('selected'));
      item.classList.add('selected');
      selectedDirectory = path;
      pathInput.value = path;
    });

    return item;
  }

  async function loadChildren(container, path, parentItem) {
    parentItem.classList.add('loading');
    const data = await browseTree(path);
    parentItem.classList.remove('loading');

    if (!data) return;

    for (const dirPath of data.directories) {
      const childItem = createTreeItem(dirPath, dirPath, false);
      container.appendChild(childItem);

      const childContainer = createChildrenContainer([], null);
      container.appendChild(childContainer);
    }
  }

  function createChildrenContainer(dirs) {
    const container = document.createElement('div');
    container.className = 'tree-children';

    for (const dirPath of dirs) {
      const item = createTreeItem(dirPath, dirPath, false);
      container.appendChild(item);

      const childContainer = document.createElement('div');
      childContainer.className = 'tree-children';
      childContainer.style.display = 'none';
      container.appendChild(childContainer);
    }

    return container;
  }

  browseBtn.addEventListener('click', () => {
    const path = pathInput.value.trim() || '/';
    buildTree(path);
  });

  pathInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      selectedDirectory = pathInput.value.trim();
      buildTree(selectedDirectory);
    }
  });

  analyzeBtn.addEventListener('click', async () => {
    const dir = pathInput.value.trim();
    if (!dir) return;

    selectedDirectory = dir;
    showLoader('Scanning directory...');

    try {
      const result = await apiPost('/api/analyze', {
        directory: dir,
        recursive: recursiveCheck.checked,
        detect_duplicates: detectDupsCheck.checked,
      });

      if (!result.success) {
        hideLoader();
        showError(result.error || 'Analysis failed');
        return;
      }

      lastAnalyzeResult = result;
      displayResults(result);
      reportContent.textContent = result.report;
      reportSection.style.display = '';
      organizeBtn.disabled = false;
      clearBtn.disabled = false;
    } catch (err) {
      hideLoader();
      showError('Network error: ' + err.message);
    }

    hideLoader();
  });

  organizeBtn.addEventListener('click', async () => {
    const dir = selectedDirectory || pathInput.value.trim();
    if (!dir) return;

    const action = getAction();
    showLoader(action === 'copy' ? 'Copying files...' : 'Moving files...');

    try {
      const result = await apiPost('/api/organize', {
        directory: dir,
        recursive: recursiveCheck.checked,
        copy: action === 'copy',
      });

      if (!result.success) {
        hideLoader();
        showError(result.error || 'Organization failed');
        return;
      }

      reportContent.textContent = result.report;
      reportSection.style.display = '';

      const totalMoved = Object.values(result.stats).reduce((sum, s) => sum + (s.moved || 0), 0);
      const totalSkipped = Object.values(result.stats).reduce((sum, s) => sum + (s.skipped || 0), 0);
      const actionLabel = action === 'copy' ? 'copied' : 'moved';
      showSuccess(`${totalMoved} files ${actionLabel}, ${totalSkipped} skipped`);
    } catch (err) {
      hideLoader();
      showError('Network error: ' + err.message);
    }

    hideLoader();
  });

  clearBtn.addEventListener('click', () => {
    resultsContent.innerHTML = '<p class="placeholder">Run an analysis to see results here.</p>';
    reportContent.textContent = '';
    reportSection.style.display = 'none';
    organizeBtn.disabled = true;
    clearBtn.disabled = true;
    lastAnalyzeResult = null;
  });

  function displayResults(result) {
    let html = '<table class="results-table">';
    html += '<thead><tr><th>Category</th><th class="count">Count</th></tr></thead><tbody>';

    const categories = result.categories || {};
    for (const cat of ['images', 'videos', 'documents']) {
      const count = (categories[cat] || []).length;
      if (count > 0 || cat === 'documents') {
        html += `<tr><td>${cat.charAt(0).toUpperCase() + cat.slice(1)}</td><td class="count">${count}</td></tr>`;
      }
    }

    if (result.unrecognized && result.unrecognized.length > 0) {
      html += `<tr><td>Unrecognized</td><td class="count">${result.unrecognized.length}</td></tr>`;
    }

    html += `<tr class="total"><td>Total</td><td class="count">${result.total_files}</td></tr>`;
    html += '</tbody></table>';

    if (result.duplicates && Object.keys(result.duplicates).length > 0) {
      html += '<div class="duplicates-section"><h4>Duplicate Groups</h4>';
      for (const [hash, files] of Object.entries(result.duplicates)) {
        html += '<div class="dup-group">';
        html += `<div class="dup-hash">${hash.substring(0, 12)}...</div>`;
        html += '<ul class="dup-files">';
        for (const f of files) {
          html += `<li>${f}</li>`;
        }
        html += '</ul></div>';
      }
      html += '</div>';
    }

    resultsContent.innerHTML = html;
  }

  function showError(msg) {
    resultsContent.innerHTML = `<p class="status-error">${msg}</p>`;
  }

  function showSuccess(msg) {
    resultsContent.innerHTML = `<p class="status-ok">${msg}</p>`;
  }

  reportSection.style.display = 'none';
})();
