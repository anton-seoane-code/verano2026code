// ===== CONSTANTS =====
const STORAGE_KEY = 'simple-games-hermes-scores';

const WORDS = {
  programming: [
    'python', 'javascript', 'algorithm', 'computer', 'database',
    'network', 'function', 'variable', 'inheritance', 'recursion',
    'compiler', 'debugger', 'terminal', 'keyboard', 'monitor',
    'boolean', 'integer', 'syntax', 'library', 'runtime',
    'object', 'method', 'module', 'server', 'client',
    'browser', 'protocol', 'encryption', 'binary', 'framework',
    'asynchronous', 'callback', 'polymorphism', 'encapsulation', 'interface',
  ],
  animals: [
    'elephant', 'giraffe', 'penguin', 'dolphin', 'octopus',
    'kangaroo', 'cheetah', 'gorilla', 'panther', 'falcon',
    'chameleon', 'flamingo', 'hamster', 'parrot', 'turtle',
    'leopard', 'jaguar', 'beaver', 'raccoon', 'badger',
    'squirrel', 'rabbit', 'dragonfly', 'butterfly', 'seahorse',
  ],
  food: [
    'spaghetti', 'chocolate', 'avocado', 'broccoli', 'pineapple',
    'hamburger', 'sandwich', 'pancake', 'pumpkin', 'mushroom',
    'cucumber', 'asparagus', 'cauliflower', 'cinnamon', 'coriander',
    'marmalade', 'caramel', 'marshmallow', 'cappuccino', 'lasagna',
    'ravioli', 'mozzarella', 'champagne', 'cranberry', 'artichoke',
  ],
};

function getFullWordList() {
  return [...WORDS.programming, ...WORDS.animals, ...WORDS.food];
}

// ===== SOUND ENGINE (Web Audio API) =====
let audioCtx = null;

function getAudioCtx() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

function playTone(freq, duration, type = 'sine', volume = 0.15) {
  try {
    const ctx = getAudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.value = freq;
    gain.gain.value = volume;
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + duration);
  } catch (e) { /* audio not available */ }
}

function sfxClick() { playTone(800, 0.06, 'sine', 0.08); }
function sfxWin() {
  playTone(523, 0.12, 'sine', 0.12);
  setTimeout(() => playTone(659, 0.12, 'sine', 0.12), 120);
  setTimeout(() => playTone(784, 0.2, 'sine', 0.12), 240);
}
function sfxLose() {
  playTone(400, 0.2, 'sawtooth', 0.06);
  setTimeout(() => playTone(300, 0.3, 'sawtooth', 0.06), 200);
}
function sfxPlace() { playTone(600, 0.08, 'sine', 0.1); }
function sfxDraw() { playTone(440, 0.08, 'triangle', 0.08); setTimeout(() => playTone(440, 0.08, 'triangle', 0.08), 100); }
function sfxCorrect() { playTone(700, 0.08, 'sine', 0.1); }
function sfxWrong() { playTone(200, 0.15, 'square', 0.05); }

// ===== CONFETTI =====
function fireConfetti(count = 40) {
  const container = document.createElement('div');
  container.className = 'confetti-container';
  const colors = ['#0A84FF', '#30D158', '#FF453A', '#FFD60A', '#BF5AF2', '#FF9F0A', '#64D2FF'];
  for (let i = 0; i < count; i++) {
    const piece = document.createElement('div');
    piece.className = 'confetti-piece';
    piece.style.left = Math.random() * 100 + '%';
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.width = (4 + Math.random() * 6) + 'px';
    piece.style.height = (4 + Math.random() * 6) + 'px';
    piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
    piece.style.animationDuration = (1.5 + Math.random() * 2) + 's';
    piece.style.animationDelay = Math.random() * 0.5 + 's';
    container.appendChild(piece);
  }
  document.body.appendChild(container);
  setTimeout(() => container.remove(), 4000);
}

// ===== NAVIGATION =====
const navBtns = document.querySelectorAll('.nav-btn');
const sections = {};

navBtns.forEach(btn => {
  const sectionId = btn.dataset.section;
  sections[sectionId] = document.getElementById(sectionId);
  btn.addEventListener('click', () => {
    sfxClick();
    navBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    Object.values(sections).forEach(s => s.classList.remove('active'));
    sections[sectionId].classList.add('active');
    if (sectionId === 'stats') renderStats();
  });
});

document.addEventListener('keydown', e => {
  const key = e.key;
  const sections_order = ['tictactoe', 'hangman', 'rps', 'stats'];
  const idx = ['1', '2', '3', '4'].indexOf(key);
  if (idx !== -1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
    e.preventDefault();
    sfxClick();
    const target = sections_order[idx];
    navBtns.forEach(b => { b.classList.toggle('active', b.dataset.section === target); });
    Object.values(sections).forEach(s => s.classList.toggle('active', s.id === target));
    if (target === 'stats') renderStats();
  }
});

// ===== SCOREBOARD / STATS =====
function loadScores() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || emptyScores(); }
  catch { return emptyScores(); }
}
function emptyScores() { return { tic_tac_toe: [], hangman: [], rps: [] }; }

function saveScore(game, winner, extra = {}) {
  const scores = loadScores();
  const entry = { winner, date: new Date().toLocaleString(), ...extra };
  if (scores[game]) scores[game].push(entry);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(scores));
}

function computeStats() {
  const scores = loadScores();
  const stats = { wins: 0, losses: 0, draws: 0 };
  const perGame = { tic_tac_toe: { wins: 0, losses: 0, draws: 0, streak: 0, maxStreak: 0, total: 0, lastResult: '' },
    hangman: { wins: 0, losses: 0, draws: 0, streak: 0, maxStreak: 0, total: 0, lastResult: '' },
    rps: { wins: 0, losses: 0, draws: 0, streak: 0, maxStreak: 0, total: 0, lastResult: '' } };

  for (const [game, entries] of Object.entries(scores)) {
    if (!perGame[game]) continue;
    for (const e of entries) {
      perGame[game].total++;
      if (e.winner === 'Player' || e.winner === 'X') {
        perGame[game].wins++; stats.wins++;
        perGame[game].streak = (perGame[game].lastResult === 'win') ? perGame[game].streak + 1 : 1;
        perGame[game].lastResult = 'win';
      } else if (e.winner === 'Draw' || e.winner === 'draw') {
        perGame[game].draws++; stats.draws++;
        perGame[game].streak = 0;
        perGame[game].lastResult = 'draw';
      } else {
        perGame[game].losses++; stats.losses++;
        perGame[game].streak = 0;
        perGame[game].lastResult = 'lose';
      }
      perGame[game].maxStreak = Math.max(perGame[game].maxStreak, perGame[game].streak);
    }
  }
  return { overall: stats, perGame };
}

function renderStats() {
  const { overall, perGame } = computeStats();

  document.getElementById('stats-cards').innerHTML = `
    <div class="stats-card sc-wins"><div class="sc-value">${overall.wins}</div><div class="sc-label">Wins</div></div>
    <div class="stats-card sc-losses"><div class="sc-value">${overall.losses}</div><div class="sc-label">Losses</div></div>
    <div class="stats-card sc-draws"><div class="sc-value">${overall.draws}</div><div class="sc-label">Draws</div></div>
  `;

  const names = { tic_tac_toe: 'Tic-Tac-Toe', hangman: 'Hangman', rps: 'RPS' };
  const tbody = document.getElementById('stats-body');
  tbody.innerHTML = '';
  for (const [key, g] of Object.entries(perGame)) {
    const tr = document.createElement('tr');
    const streakText = g.streak > 1 ? `${g.streak}🔥` : g.streak || '-';
    tr.innerHTML = `<td>${names[key]}</td>
      <td class="s-wins">${g.wins}</td>
      <td class="s-losses">${g.losses}</td>
      <td class="s-draws">${g.draws}</td>
      <td>${streakText}</td>
      <td>${g.total}</td>`;
    tbody.appendChild(tr);
  }
  renderScoreboard();
}

function renderScoreboard() {
  const scores = loadScores();
  const filter = document.querySelector('.sb-filter.active')?.dataset.sbFilter || 'all';
  const tbody = document.getElementById('sb-body');
  const empty = document.getElementById('sb-empty');
  tbody.innerHTML = '';
  let rows = [];

  if (filter === 'all' || filter === 'tic_tac_toe') {
    scores.tic_tac_toe.forEach(e => {
      const detail = e.difficulty ? `Difficulty: ${e.difficulty}` : '-';
      let wc = '';
      if (e.winner === 'Draw' || e.winner === 'draw') wc = 'sb-draw';
      else if (e.winner === 'Player' || e.winner === 'X') wc = 'sb-win';
      else wc = 'sb-lose';
      rows.push({ game: 'Tic-Tac-Toe', gameClass: 'sb-game', winner: e.winner, date: e.date, detail, winnerClass: wc });
    });
  }
  if (filter === 'all' || filter === 'hangman') {
    scores.hangman.forEach(e => {
      rows.push({ game: 'Hangman', gameClass: 'sb-game', winner: e.winner, date: e.date, detail: `Wrong: ${e.guesses ?? '-'}`, winnerClass: e.winner === 'Player' ? 'sb-win' : 'sb-lose' });
    });
  }
  if (filter === 'all' || filter === 'rps') {
    scores.rps.forEach(e => {
      const detail = `${e.player_score ?? 0}-${e.ai_score ?? 0} (${e.variant || 'classic'})`;
      rows.push({ game: 'RPS', gameClass: 'sb-game', winner: e.winner, date: e.date, detail, winnerClass: e.winner === 'Player' ? 'sb-win' : 'sb-lose' });
    });
  }

  rows.reverse();
  if (rows.length === 0) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';
  rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td class="${r.gameClass}">${r.game}</td><td class="${r.winnerClass}">${r.winner}</td><td>${r.date}</td><td>${r.detail}</td>`;
    tbody.appendChild(tr);
  });
}

document.getElementById('sb-filters').addEventListener('click', e => {
  const btn = e.target.closest('.sb-filter');
  if (!btn) return;
  document.querySelectorAll('.sb-filter').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderScoreboard();
});

document.getElementById('sb-clear').addEventListener('click', () => {
  if (confirm('Clear all scores?')) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(emptyScores()));
    renderStats();
  }
});

// ===== TIC-TAC-TOE =====
const tttBoard = document.getElementById('ttt-board');
const tttStatus = document.getElementById('ttt-status');
const tttMode = document.getElementById('ttt-mode');
let tttState = { board: [], current: 'X', mode: 'hard', over: false };

function tttNewGame() {
  tttState.board = Array(3).fill().map(() => Array(3).fill(''));
  tttState.current = 'X';
  tttState.mode = tttMode.value;
  tttState.over = false;
  tttStatus.className = '';
  tttRender();
  if (tttState.mode === 'pvp') {
    tttStatus.textContent = "Player X's turn";
  } else {
    tttStatus.textContent = "Your turn (X)";
  }
}

function tttRender() {
  tttBoard.innerHTML = '';
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      const cell = document.createElement('div');
      cell.className = 'ttt-cell';
      cell.dataset.row = i;
      cell.dataset.col = j;
      const val = tttState.board[i][j];
      if (val) {
        cell.textContent = val;
        cell.classList.add(val === 'X' ? 'x' : 'o', 'disabled');
      }
      if (tttState.over) cell.classList.add('disabled');
      cell.addEventListener('click', () => tttClick(i, j));
      tttBoard.appendChild(cell);
    }
  }
}

function tttClick(row, col) {
  if (tttState.over || tttState.board[row][col] !== '') return;
  if (tttState.mode !== 'pvp' && tttState.current !== 'X') return;

  tttPlace(row, col, 'X');
  if (!tttState.over && tttState.mode !== 'pvp') {
    setTimeout(tttAiTurn, 250);
  }
}

function tttPlace(row, col, player) {
  tttState.board[row][col] = player;
  tttRender();
  sfxPlace();

  // Animate the cell that was just placed
  const cells = tttBoard.querySelectorAll('.ttt-cell');
  const idx = row * 3 + col;
  if (cells[idx]) cells[idx].classList.add('pop-in');

  if (tttCheckWin(player)) {
    tttState.over = true;
    const winLabel = player === 'X' ? 'Player X' : 'AI (O)';
    tttStatus.textContent = `${winLabel} wins!`;
    tttStatus.className = player === 'X' ? 'win' : 'lose';
    const allCells = tttBoard.querySelectorAll('.ttt-cell');
    const winLine = tttGetWinLine(player);
    if (winLine) {
      winLine.forEach(([r, c]) => {
        const ci = r * 3 + c;
        if (allCells[ci]) allCells[ci].classList.add('win');
      });
    }
    const winner = player === 'X' ? (tttState.mode === 'pvp' ? 'X' : 'Player') : 'AI';
    if (winner === 'Player' || winner === 'X') {
      sfxWin();
      fireConfetti(30);
    } else {
      sfxLose();
    }
    saveScore('tic_tac_toe', winner, { difficulty: tttState.mode === 'pvp' ? undefined : tttState.mode });
    return;
  }
  if (tttIsDraw()) {
    tttState.over = true;
    tttStatus.textContent = "Draw!";
    tttStatus.className = 'draw';
    sfxDraw();
    saveScore('tic_tac_toe', 'Draw', { difficulty: tttState.mode === 'pvp' ? undefined : tttState.mode });
    return;
  }

  tttState.current = player === 'X' ? 'O' : 'X';
  if (tttState.mode === 'pvp') {
    tttStatus.textContent = `Player ${tttState.current}'s turn`;
  } else {
    tttStatus.textContent = tttState.current === 'X' ? "Your turn (X)" : "AI thinking...";
  }
}

function tttGetWinLine(player) {
  const b = tttState.board;
  for (let i = 0; i < 3; i++) {
    if (b[i][0] === player && b[i][1] === player && b[i][2] === player) return [[i, 0], [i, 1], [i, 2]];
    if (b[0][i] === player && b[1][i] === player && b[2][i] === player) return [[0, i], [1, i], [2, i]];
  }
  if (b[0][0] === player && b[1][1] === player && b[2][2] === player) return [[0, 0], [1, 1], [2, 2]];
  if (b[0][2] === player && b[1][1] === player && b[2][0] === player) return [[0, 2], [1, 1], [2, 0]];
  return null;
}

function tttAiTurn() {
  if (tttState.over || tttState.current !== 'O') return;
  const empty = tttGetEmpty();
  if (empty.length === 0) return;

  let move;
  if (tttState.mode === 'easy') {
    move = empty[Math.floor(Math.random() * empty.length)];
  } else if (tttState.mode === 'medium') {
    if (Math.random() < 0.4) {
      move = empty[Math.floor(Math.random() * empty.length)];
    } else {
      move = tttMinimaxMove(empty);
    }
  } else {
    move = tttMinimaxMove(empty);
  }
  if (move) tttPlace(move[0], move[1], 'O');
}

function tttMinimaxMove(empty) {
  let bestVal = -Infinity, bestMove = empty[0];
  for (const [i, j] of empty) {
    tttState.board[i][j] = 'O';
    const val = tttMinimax(0, false, -Infinity, Infinity);
    tttState.board[i][j] = '';
    if (val > bestVal) { bestVal = val; bestMove = [i, j]; }
  }
  return bestMove;
}

function tttMinimax(depth, isMax, alpha, beta) {
  if (tttCheckWin('O')) return 10 - depth;
  if (tttCheckWin('X')) return depth - 10;
  if (tttIsDraw()) return 0;
  const empty = tttGetEmpty();
  if (isMax) {
    let best = -Infinity;
    for (const [i, j] of empty) {
      tttState.board[i][j] = 'O';
      best = Math.max(best, tttMinimax(depth + 1, false, alpha, beta));
      tttState.board[i][j] = '';
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  } else {
    let best = Infinity;
    for (const [i, j] of empty) {
      tttState.board[i][j] = 'X';
      best = Math.min(best, tttMinimax(depth + 1, true, alpha, beta));
      tttState.board[i][j] = '';
      beta = Math.min(beta, best);
      if (beta <= alpha) break;
    }
    return best;
  }
}

function tttGetEmpty() {
  const r = [];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) if (tttState.board[i][j] === '') r.push([i, j]);
  return r;
}

function tttCheckWin(player) {
  const b = tttState.board;
  for (let i = 0; i < 3; i++) {
    if (b[i][0] === player && b[i][1] === player && b[i][2] === player) return true;
    if (b[0][i] === player && b[1][i] === player && b[2][i] === player) return true;
  }
  if (b[0][0] === player && b[1][1] === player && b[2][2] === player) return true;
  if (b[0][2] === player && b[1][1] === player && b[2][0] === player) return true;
  return false;
}

function tttIsDraw() {
  return tttState.board.every(row => row.every(c => c !== ''));
}

tttMode.addEventListener('change', tttNewGame);
document.getElementById('ttt-new').addEventListener('click', tttNewGame);

// ===== HANGMAN =====
const hangmanCanvas = document.getElementById('hangman-canvas');
const hangmanWord = document.getElementById('hangman-word');
const hangmanHint = document.getElementById('hangman-hint');
const hangmanStatus = document.getElementById('hangman-status');
const keyboard = document.getElementById('keyboard');
const hmCategory = document.getElementById('hm-category');
const ctx = hangmanCanvas.getContext('2d');
let hmState = { word: '', guessed: new Set(), wrong: 0, over: false, category: 'mixed', hint: '' };
const MAX_WRONG = 6;

const CATEGORY_HINTS = {
  programming: 'Tech term',
  animals: 'Animal',
  food: 'Food & drink',
};

function hmNewGame() {
  const cat = hmCategory.value;
  hmState.category = cat;
  let pool;
  if (cat === 'mixed') {
    pool = getFullWordList();
  } else {
    pool = WORDS[cat] || getFullWordList();
  }
  hmState.word = pool[Math.floor(Math.random() * pool.length)];
  hmState.guessed = new Set();
  hmState.wrong = 0;
  hmState.over = false;
  hmState.hint = cat === 'mixed' ? '' : (CATEGORY_HINTS[cat] || '');
  hmDrawGallow();
  hmUpdateDisplay();
  hmStatus();
  hmRenderKeyboard();
  hangmanHint.textContent = hmState.hint ? `Hint: ${hmState.hint}` : '';
}

function hmDrawGallow() {
  const w = 300, h = 240;
  ctx.clearRect(0, 0, w, h);

  // Base
  ctx.strokeStyle = 'rgba(255,255,255,0.4)';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(40, h - 30);
  ctx.lineTo(w - 60, h - 30);
  ctx.moveTo(70, h - 30);
  ctx.lineTo(70, 30);
  ctx.lineTo(w - 70, 30);
  ctx.moveTo(w - 70, 30);
  ctx.lineTo(w - 70, 55);
  ctx.stroke();

  // Rope
  ctx.beginPath();
  ctx.moveTo(w - 70, 55);
  ctx.lineTo(w - 70, 62);
  ctx.strokeStyle = 'rgba(255,255,255,0.25)';
  ctx.lineWidth = 1.5;
  ctx.stroke();

  ctx.lineWidth = 2.5;
  ctx.strokeStyle = '#ffffff';

  if (hmState.wrong > 0) {
    // Head
    ctx.beginPath();
    ctx.arc(w - 70, 72, 17, 0, Math.PI * 2);
    ctx.stroke();
    // Eyes
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(w - 76, 68, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(w - 64, 68, 2.5, 0, Math.PI * 2);
    ctx.fill();
  }
  if (hmState.wrong > 1) {
    // Body
    ctx.beginPath();
    ctx.moveTo(w - 70, 89);
    ctx.lineTo(w - 70, 140);
    ctx.stroke();
  }
  if (hmState.wrong > 2) {
    // Left arm
    ctx.beginPath();
    ctx.moveTo(w - 70, 98);
    ctx.lineTo(w - 100, 120);
    ctx.stroke();
  }
  if (hmState.wrong > 3) {
    // Right arm
    ctx.beginPath();
    ctx.moveTo(w - 70, 98);
    ctx.lineTo(w - 40, 120);
    ctx.stroke();
  }
  if (hmState.wrong > 4) {
    // Left leg
    ctx.beginPath();
    ctx.moveTo(w - 70, 140);
    ctx.lineTo(w - 95, 175);
    ctx.stroke();
  }
  if (hmState.wrong > 5) {
    // Right leg
    ctx.beginPath();
    ctx.moveTo(w - 70, 140);
    ctx.lineTo(w - 45, 175);
    ctx.stroke();
  }
}

function hmUpdateDisplay() {
  const display = hmState.word.split('').map(c => hmState.guessed.has(c) ? c : '_').join(' ');
  hangmanWord.textContent = display;
}

function hmStatus() {
  hangmanStatus.textContent = `Wrong: ${hmState.wrong}/${MAX_WRONG}`;
}

function hmRenderKeyboard() {
  keyboard.innerHTML = '';
  const rows = 'QWERTYUIOP ASDFGHJKL ZXCVBNM'.split(' ');
  rows.forEach(row => {
    const f = document.createElement('div');
    f.style.display = 'flex';
    f.style.justifyContent = 'center';
    f.style.gap = '5px';
    row.split('').forEach(ch => {
      const btn = document.createElement('button');
      btn.className = 'key-btn';
      btn.textContent = ch;
      btn.dataset.letter = ch;
      if (hmState.guessed.has(ch.toLowerCase())) {
        btn.disabled = true;
        if (hmState.word.includes(ch.toLowerCase())) {
          btn.classList.add('correct');
        } else {
          btn.classList.add('wrong');
        }
      }
      btn.addEventListener('click', () => hmGuess(ch));
      f.appendChild(btn);
    });
    keyboard.appendChild(f);
  });
}

function hmGuess(letter) {
  if (hmState.over) return;
  const l = letter.toLowerCase();
  if (hmState.guessed.has(l)) return;
  hmState.guessed.add(l);

  if (hmState.word.includes(l)) {
    sfxCorrect();
    hmUpdateDisplay();
    if (hmState.word.split('').every(c => hmState.guessed.has(c))) {
      hmState.over = true;
      sfxWin();
      fireConfetti(30);
      hangmanStatus.textContent = `You win! The word was "${hmState.word}"`;
      saveScore('hangman', 'Player', { guesses: hmState.wrong });
    }
  } else {
    sfxWrong();
    hmState.wrong++;
    hmDrawGallow();
    hmStatus();
    if (hmState.wrong >= MAX_WRONG) {
      hmState.over = true;
      sfxLose();
      hangmanWord.textContent = hmState.word.split('').join(' ');
      hangmanStatus.textContent = `You lose! The word was "${hmState.word}"`;
      saveScore('hangman', 'AI', { guesses: hmState.wrong });
    }
  }
  hmRenderKeyboard();
}

document.getElementById('hangman-new').addEventListener('click', hmNewGame);
hmCategory.addEventListener('change', hmNewGame);

// Keyboard input for hangman
document.addEventListener('keydown', e => {
  if (!sections.hangman.classList.contains('active')) return;
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const letter = e.key.toUpperCase();
  if (/^[A-Z]$/.test(letter)) {
    e.preventDefault();
    hmGuess(letter);
  }
});

// ===== ROCK PAPER SCISSORS (with Lizard-Spock) =====
const rpsScore = document.getElementById('rps-score');
const rpsRound = document.getElementById('rps-round');
const rpsResult = document.getElementById('rps-result');
const rpsChoices = document.getElementById('rps-choices');
const rpsVariant = document.getElementById('rps-variant');
let rpsState = { p: 0, a: 0, round: 1, over: false, max: 2, variant: 'classic' };

const RPS_CLASSIC = {
  r: { name: 'Rock', emoji: '🪨', beats: ['s'] },
  p: { name: 'Paper', emoji: '📄', beats: ['r'] },
  s: { name: 'Scissors', emoji: '✂️', beats: ['p'] },
};

const RPS_LS = {
  r: { name: 'Rock', emoji: '🪨', beats: ['s', 'l'] },
  p: { name: 'Paper', emoji: '📄', beats: ['r', 'sp'] },
  s: { name: 'Scissors', emoji: '✂️', beats: ['p', 'l'] },
  l: { name: 'Lizard', emoji: '🦎', beats: ['sp', 'p'] },
  sp: { name: 'Spock', emoji: '🖖', beats: ['r', 's'] },
};

function rpsGetRules() {
  return rpsState.variant === 'lizardspock' ? RPS_LS : RPS_CLASSIC;
}

function rpsNewGame() {
  rpsState = { p: 0, a: 0, round: 1, over: false, max: 2, variant: rpsVariant.value };
  rpsRenderChoices();
  rpsUpdateDisplay();
  rpsResult.textContent = 'Choose your move!';
  rpsResult.className = '';
}

function rpsRenderChoices() {
  const rules = rpsGetRules();
  rpsChoices.innerHTML = '';
  for (const [key, val] of Object.entries(rules)) {
    const btn = document.createElement('button');
    btn.className = 'rps-btn';
    btn.dataset.choice = key;
    btn.innerHTML = `<span class="rps-emoji">${val.emoji}</span>${val.name}`;
    if (rpsState.over) btn.disabled = true;
    btn.addEventListener('click', () => rpsPlay(key));
    rpsChoices.appendChild(btn);
  }
}

function rpsUpdateDisplay() {
  rpsScore.textContent = `You ${rpsState.p}  —  ${rpsState.a} AI`;
  rpsRound.textContent = `Best of 3 ${rpsState.variant === 'lizardspock' ? '· Lizard-Spock' : ''}`;
}

function rpsPlay(player) {
  if (rpsState.over) return;
  const rules = rpsGetRules();
  const keys = Object.keys(rules);
  const ai = keys[Math.floor(Math.random() * keys.length)];
  sfxClick();

  let msg = `${rules[player].emoji} You: ${rules[player].name}  ·  ${rules[ai].emoji} AI: ${rules[ai].name}`;

  if (player === ai) {
    msg += '\nDraw!';
    rpsResult.className = 'draw';
    sfxDraw();
  } else if (rules[player].beats.includes(ai)) {
    msg += '\nYou win this round!';
    rpsState.p++;
    rpsResult.className = 'win';
    sfxCorrect();
  } else {
    msg += '\nAI wins this round!';
    rpsState.a++;
    rpsResult.className = 'lose';
    sfxWrong();
  }
  rpsState.round++;
  rpsUpdateDisplay();
  rpsResult.textContent = msg;

  if (rpsState.p >= rpsState.max || rpsState.a >= rpsState.max) {
    rpsState.over = true;
    rpsRenderChoices();
    const winner = rpsState.p > rpsState.a ? 'Player' : 'AI';
    const msg2 = winner === 'Player' ? '🏆 You win the game!' : 'AI wins the game!';
    rpsResult.textContent = msg + '\n\n' + msg2;
    rpsResult.className = winner === 'Player' ? 'win' : 'lose';
    if (winner === 'Player') {
      sfxWin();
      fireConfetti(30);
    } else {
      sfxLose();
    }
    saveScore('rps', winner, { player_score: rpsState.p, ai_score: rpsState.a, variant: rpsState.variant });
  }
}

document.getElementById('rps-new').addEventListener('click', rpsNewGame);
rpsVariant.addEventListener('change', rpsNewGame);

// ===== INIT =====
tttNewGame();
hmNewGame();
rpsNewGame();
