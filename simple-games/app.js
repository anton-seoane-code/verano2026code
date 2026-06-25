// ===== CONSTANTS =====
const STORAGE_KEY = 'simple-games-scores';
const WORDS = [
  'python', 'programming', 'algorithm', 'computer', 'database',
  'network', 'javascript', 'developer', 'function', 'variable',
  'loop', 'condition', 'exception', 'inheritance', 'recursion',
  'compiler', 'debugger', 'terminal', 'keyboard', 'monitor',
  'graphics', 'library', 'framework', 'runtime', 'syntax',
  'boolean', 'integer', 'string', 'array', 'object',
  'class', 'method', 'module', 'package', 'server',
  'client', 'browser', 'protocol', 'encryption', 'binary',
];

// ===== NAVIGATION =====
const navBtns = document.querySelectorAll('.nav-btn');
const sections = {};

navBtns.forEach(btn => {
  const sectionId = btn.dataset.section;
  sections[sectionId] = document.getElementById(sectionId);
  btn.addEventListener('click', () => {
    navBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    Object.values(sections).forEach(s => s.classList.remove('active'));
    sections[sectionId].classList.add('active');
    if (sectionId === 'scoreboard') renderScoreboard();
  });
});

// ===== SCOREBOARD =====
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
      rows.push({ game: 'Tic-Tac-Toe', gameClass: 'sb-game', winner: e.winner, date: e.date, detail, winnerClass: e.winner === 'Draw' ? '' : e.winner === 'Player' || e.winner === 'X' ? 'sb-win' : 'sb-lose' });
    });
  }
  if (filter === 'all' || filter === 'hangman') {
    scores.hangman.forEach(e => {
      rows.push({ game: 'Hangman', gameClass: 'sb-game', winner: e.winner, date: e.date, detail: `Wrong: ${e.guesses ?? '-'}`, winnerClass: e.winner === 'Player' ? 'sb-win' : 'sb-lose' });
    });
  }
  if (filter === 'all' || filter === 'rps') {
    scores.rps.forEach(e => {
      rows.push({ game: 'RPS', gameClass: 'sb-game', winner: e.winner, date: e.date, detail: `${e.player_score ?? 0}-${e.ai_score ?? 0}`, winnerClass: e.winner === 'Player' ? 'sb-win' : 'sb-lose' });
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
    renderScoreboard();
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

  if (tttCheckWin(player)) {
    tttState.over = true;
    tttStatus.textContent = `${player === 'X' ? 'Player X' : 'AI (O)'} wins!`;
    document.querySelectorAll('.ttt-cell.x, .ttt-cell.o').forEach(c => c.classList.add('win'));
    const winner = player === 'X' ? (tttState.mode === 'pvp' ? 'X' : 'Player') : 'AI';
    saveScore('tic_tac_toe', winner, { difficulty: tttState.mode === 'pvp' ? undefined : tttState.mode });
    return;
  }
  if (tttIsDraw()) {
    tttState.over = true;
    tttStatus.textContent = "Draw!";
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
const hangmanStatus = document.getElementById('hangman-status');
const keyboard = document.getElementById('keyboard');
const ctx = hangmanCanvas.getContext('2d');
let hmState = { word: '', guessed: new Set(), wrong: 0, over: false };
const MAX_WRONG = 6;

function hmNewGame() {
  hmState.word = WORDS[Math.floor(Math.random() * WORDS.length)];
  hmState.guessed = new Set();
  hmState.wrong = 0;
  hmState.over = false;
  hmDrawGallow();
  hmUpdateDisplay();
  hmStatus();
  hmRenderKeyboard();
}

function hmDrawGallow() {
  const w = 300, h = 240;
  ctx.clearRect(0, 0, w, h);
  ctx.strokeStyle = '#ffffff';
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

  ctx.lineWidth = 2.5;
  if (hmState.wrong > 0) {
    ctx.beginPath();
    ctx.arc(w - 70, 72, 17, 0, Math.PI * 2);
    ctx.stroke();
  }
  if (hmState.wrong > 1) {
    ctx.beginPath();
    ctx.moveTo(w - 70, 89);
    ctx.lineTo(w - 70, 140);
    ctx.stroke();
  }
  if (hmState.wrong > 2) {
    ctx.beginPath();
    ctx.moveTo(w - 70, 98);
    ctx.lineTo(w - 100, 120);
    ctx.stroke();
  }
  if (hmState.wrong > 3) {
    ctx.beginPath();
    ctx.moveTo(w - 70, 98);
    ctx.lineTo(w - 40, 120);
    ctx.stroke();
  }
  if (hmState.wrong > 4) {
    ctx.beginPath();
    ctx.moveTo(w - 70, 140);
    ctx.lineTo(w - 95, 175);
    ctx.stroke();
  }
  if (hmState.wrong > 5) {
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
  const rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'];
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
    hmUpdateDisplay();
    if (hmState.word.split('').every(c => hmState.guessed.has(c))) {
      hmState.over = true;
      hangmanStatus.textContent = `You win! The word was "${hmState.word}"`;
      saveScore('hangman', 'Player', { guesses: hmState.wrong });
    }
  } else {
    hmState.wrong++;
    hmDrawGallow();
    hmStatus();
    if (hmState.wrong >= MAX_WRONG) {
      hmState.over = true;
      hangmanWord.textContent = hmState.word.split('').join(' ');
      hangmanStatus.textContent = `You lose! The word was "${hmState.word}"`;
      saveScore('hangman', 'AI', { guesses: hmState.wrong });
    }
  }
  hmRenderKeyboard();
}

document.getElementById('hangman-new').addEventListener('click', hmNewGame);

// ===== ROCK PAPER SCISSORS =====
const rpsScore = document.getElementById('rps-score');
const rpsRound = document.getElementById('rps-round');
const rpsResult = document.getElementById('rps-result');
const rpsChoices = document.getElementById('rps-choices');
let rpsState = { p: 0, a: 0, round: 1, over: false, max: 2 };
const RPS_NAMES = { r: 'Rock', p: 'Paper', s: 'Scissors' };
const RPS_BEATS = { r: 's', s: 'p', p: 'r' };

function rpsNewGame() {
  rpsState = { p: 0, a: 0, round: 1, over: false, max: 2 };
  rpsUpdateDisplay();
  rpsResult.textContent = 'Choose your move!';
  rpsChoices.querySelectorAll('.rps-btn').forEach(b => b.disabled = false);
}

function rpsUpdateDisplay() {
  rpsScore.textContent = `You ${rpsState.p}  —  ${rpsState.a} AI`;
  rpsRound.textContent = `Best of 3`;
}

function rpsPlay(player) {
  if (rpsState.over) return;
  const ai = ['r', 'p', 's'][Math.floor(Math.random() * 3)];
  let msg = `You chose ${RPS_NAMES[player]}  ·  AI chose ${RPS_NAMES[ai]}`;

  if (player === ai) {
    msg += '\nDraw!';
  } else if (RPS_BEATS[player] === ai) {
    msg += '\nYou win this round!';
    rpsState.p++;
  } else {
    msg += '\nAI wins this round!';
    rpsState.a++;
  }
  rpsState.round++;
  rpsUpdateDisplay();
  rpsResult.textContent = msg;

  if (rpsState.p >= rpsState.max || rpsState.a >= rpsState.max) {
    rpsState.over = true;
    rpsChoices.querySelectorAll('.rps-btn').forEach(b => b.disabled = true);
    const winner = rpsState.p > rpsState.a ? 'Player' : 'AI';
    const msg2 = winner === 'Player' ? 'You win the game!' : 'AI wins the game!';
    rpsResult.textContent = msg + '\n\n' + msg2;
    saveScore('rps', winner, { player_score: rpsState.p, ai_score: rpsState.a });
  }
}

rpsChoices.addEventListener('click', e => {
  const btn = e.target.closest('.rps-btn');
  if (btn) rpsPlay(btn.dataset.choice);
});

document.getElementById('rps-new').addEventListener('click', rpsNewGame);

// ===== INIT =====
tttNewGame();
hmNewGame();
rpsNewGame();
