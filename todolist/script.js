const STORAGE_KEY = 'todolist-tasks';
const SWIPE_THRESHOLD = 40;

let tasks = [];
let currentFilter = 'all';

const taskList = document.getElementById('taskList');
const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const emptyState = document.getElementById('emptyState');
const taskCount = document.getElementById('taskCount');
const emptyTitle = document.getElementById('emptyTitle');
const emptySubtitle = document.querySelector('.empty-subtitle');
const segments = document.querySelectorAll('.segment');
const dateEl = document.getElementById('currentDate');

const swipeState = new WeakMap();

function loadTasks() {
  try {
    tasks = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    tasks = [];
  }
}

function saveTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

function getFilteredTasks() {
  switch (currentFilter) {
    case 'active': return tasks.filter(t => !t.completed);
    case 'completed': return tasks.filter(t => t.completed);
    default: return tasks.slice();
  }
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function render() {
  const filtered = getFilteredTasks();
  const activeCount = tasks.filter(t => !t.completed).length;

  taskCount.textContent = activeCount;

  if (filtered.length === 0) {
    emptyState.classList.remove('hidden');
    taskList.innerHTML = '';
    switch (currentFilter) {
      case 'active':
        emptyTitle.textContent = 'All done!';
        emptySubtitle.textContent = 'No active tasks';
        break;
      case 'completed':
        emptyTitle.textContent = 'No completed tasks';
        emptySubtitle.textContent = 'Complete a task to see it here';
        break;
      default:
        emptyTitle.textContent = 'No tasks yet';
        emptySubtitle.textContent = 'Add one above to get started';
    }
    return;
  }

  emptyState.classList.add('hidden');
  taskList.innerHTML = filtered.map(task => {
    const c = task.completed ? 'completed' : '';
    return `<li class="task-item" data-id="${task.id}">
      <div class="task-content">
        <button class="check-btn ${c}">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </button>
        <span class="task-text ${c}">${escapeHtml(task.text)}</span>
      </div>
      <button class="delete-btn">Delete</button>
    </li>`;
  }).join('');
}

function addTask() {
  const text = taskInput.value.trim();
  if (!text) return;

  navigator.vibrate?.(10);

  const task = {
    id: generateId(),
    text,
    createdAt: Date.now(),
    completed: false
  };

  tasks.unshift(task);
  saveTasks();
  taskInput.value = '';
  taskInput.focus();
  render();

  const newItem = taskList.querySelector(`[data-id="${task.id}"]`);
  if (newItem) {
    newItem.classList.add('entering');
    requestAnimationFrame(() => newItem.classList.remove('entering'));
  }
}

function toggleTask(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;
  task.completed = !task.completed;
  saveTasks();
  render();
}

function deleteTask(id) {
  tasks = tasks.filter(t => t.id !== id);
  saveTasks();
  render();
}

/* Touch swipe */
function closeOtherSwipes(content) {
  document.querySelectorAll('.task-content.swiped').forEach(el => {
    if (el !== content) el.classList.remove('swiped');
  });
}

function handleTouchStart(e) {
  const content = e.target.closest('.task-content');
  if (!content || e.target.closest('.check-btn')) return;

  closeOtherSwipes(content);

  const t = e.touches[0];
  swipeState.set(content, {
    startX: t.clientX,
    startY: t.clientY,
    currentX: t.clientX,
    isSwiping: false
  });
}

function handleTouchMove(e) {
  const content = e.target.closest('.task-content');
  if (!content) return;

  const state = swipeState.get(content);
  if (!state) return;

  const t = e.touches[0];
  state.currentX = t.clientX;

  const deltaX = state.currentX - state.startX;
  const deltaY = Math.abs(t.clientY - state.startY);

  if (deltaY > 20 && Math.abs(deltaX) < 10) {
    swipeState.delete(content);
    return;
  }

  if (deltaX < 0) {
    state.isSwiping = true;
    const translate = Math.max(deltaX, -80);
    content.style.transform = `translateX(${translate}px)`;
    content.style.transition = 'none';
  }
}

function handleTouchEnd(e) {
  const content = e.target.closest('.task-content');
  if (!content) return;

  const state = swipeState.get(content);
  if (!state) return;

  content.style.transition = '';

  if (state.isSwiping) {
    const deltaX = state.currentX - state.startX;
    if (deltaX < -SWIPE_THRESHOLD) {
      content.classList.add('swiped');
    }
    content.style.transform = '';
  }

  swipeState.delete(content);
}

/* Click handlers */
function handleTaskClick(e) {
  const content = e.target.closest('.task-content');
  if (!content) return;

  const id = content.closest('.task-item').dataset.id;

  if (e.target.closest('.check-btn')) {
    navigator.vibrate?.(10);
    if (content.classList.contains('swiped')) content.classList.remove('swiped');
    toggleTask(id);
    return;
  }

  if (content.classList.contains('swiped')) {
    content.classList.remove('swiped');
    return;
  }

  navigator.vibrate?.(10);
  toggleTask(id);
}

function handleDeleteClick(e) {
  const delBtn = e.target.closest('.delete-btn');
  if (!delBtn) return;

  navigator.vibrate?.(15);
  const item = delBtn.closest('.task-item');
  const id = item.dataset.id;

  item.classList.add('exiting');
  item.addEventListener('animationend', () => deleteTask(id), { once: true });
}

/* Init */
function updateDate() {
  if (!dateEl) return;
  const now = new Date();
  dateEl.textContent = now.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  });
}

function init() {
  loadTasks();
  updateDate();
  render();

  addBtn.addEventListener('click', addTask);
  taskInput.addEventListener('keydown', e => { if (e.key === 'Enter') addTask(); });

  segments.forEach(seg => {
    seg.addEventListener('click', () => {
      navigator.vibrate?.(10);
      segments.forEach(s => s.classList.remove('active'));
      seg.classList.add('active');
      currentFilter = seg.dataset.filter;
      render();
    });
  });

  taskList.addEventListener('touchstart', handleTouchStart, { passive: true });
  taskList.addEventListener('touchmove', handleTouchMove, { passive: true });
  taskList.addEventListener('touchend', handleTouchEnd);
  taskList.addEventListener('touchcancel', handleTouchEnd);
  taskList.addEventListener('click', handleTaskClick);
  taskList.addEventListener('click', handleDeleteClick);
}

document.addEventListener('DOMContentLoaded', init);
