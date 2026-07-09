/* ══════════════════════════════════════════════
   EcoGuide AI — Frontend Application
   ══════════════════════════════════════════════ */
'use strict';

// ── DOM references ──────────────────────────────
const chatForm        = document.getElementById('chatForm');
const userInput       = document.getElementById('userInput');
const chatMessages    = document.getElementById('chatMessages');
const sendBtn         = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const clearChatBtn    = document.getElementById('clearChatBtn');
const charCounter     = document.getElementById('charCounter');
const chatStatus      = document.getElementById('chatStatus');
const darkModeToggle  = document.getElementById('darkModeToggle');
const backToTop       = document.getElementById('backToTop');
const htmlEl          = document.documentElement;

// ── Dark Mode ────────────────────────────────────
const savedTheme = localStorage.getItem('eco-theme') || 'light';
htmlEl.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

darkModeToggle.addEventListener('click', () => {
  const current = htmlEl.getAttribute('data-theme');
  const next    = current === 'dark' ? 'light' : 'dark';
  htmlEl.setAttribute('data-theme', next);
  localStorage.setItem('eco-theme', next);
  updateThemeIcon(next);
});

function updateThemeIcon(theme) {
  darkModeToggle.innerHTML = theme === 'dark'
    ? '<i class="bi bi-sun-fill"></i>'
    : '<i class="bi bi-moon-stars-fill"></i>';
}

// ── Back to Top ──────────────────────────────────
window.addEventListener('scroll', () => {
  backToTop.classList.toggle('visible', window.scrollY > 400);
});
backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ── Hero Particles ───────────────────────────────
(function initParticles() {
  const container = document.getElementById('heroParticles');
  if (!container) return;
  const emojis = ['🌿', '🍃', '♻️', '🌱', '🌍', '💧', '☀️', '🌳'];
  for (let i = 0; i < 18; i++) {
    const p = document.createElement('span');
    p.className = 'particle';
    p.textContent = emojis[i % emojis.length];
    p.style.cssText = `
      left: ${Math.random() * 100}%;
      top: ${Math.random() * -50}px;
      animation-duration: ${5 + Math.random() * 8}s;
      animation-delay: ${Math.random() * 6}s;
      font-size: ${0.8 + Math.random() * 1.2}rem;
      opacity: ${0.3 + Math.random() * 0.4};
    `;
    container.appendChild(p);
  }
})();

// ── Impact Counter Animation ─────────────────────
(function initCounters() {
  const counters = document.querySelectorAll('.impact-num[data-target]');
  if (!counters.length) return;

  const animateCounter = (el) => {
    const target = parseInt(el.dataset.target, 10);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = Math.floor(current).toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 16);
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.4 });

  counters.forEach(el => observer.observe(el));
})();

// ── Textarea Auto-Resize & Send Button State ─────
userInput.addEventListener('input', () => {
  userInput.style.height = 'auto';
  userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
  const len = userInput.value.trim().length;
  sendBtn.disabled = len === 0;
  charCounter.textContent = `${userInput.value.length}/1000`;
  charCounter.style.color = userInput.value.length > 900 ? '#e74c3c' : '';
});

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) chatForm.dispatchEvent(new Event('submit'));
  }
});

// ── Quick Prompt Buttons ─────────────────────────
document.querySelectorAll('.btn-quick-prompt').forEach(btn => {
  btn.addEventListener('click', () => {
    const prompt = btn.dataset.prompt;
    document.getElementById('chat-section').scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => {
      userInput.value = prompt;
      userInput.dispatchEvent(new Event('input'));
      userInput.focus();
    }, 500);
  });
});

// ── Simple Markdown Renderer ─────────────────────
function renderMarkdown(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // H3
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    // H2
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    // H1
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Unordered lists
    .replace(/^\s*[-*•] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    // Ordered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Blockquote
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr>')
    // Paragraphs (double newline)
    .replace(/\n\n/g, '</p><p>')
    // Single newlines
    .replace(/\n/g, '<br>')
    // Wrap in paragraph
    .replace(/^(.+)/, '<p>$1</p>');
}

// ── Chat ─────────────────────────────────────────
function getTimeString() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function buildSourcesHtml(sources) {
  if (!sources || sources.length === 0) return '';
  const items = sources.map(s => {
    const pct  = Math.round(s.score * 100);
    const link = s.url
      ? `<a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">${escapeHtml(s.source)}</a>`
      : `<span>${escapeHtml(s.source)}</span>`;
    return `<li class="rag-source-item">${link}<span class="rag-score">${pct}% match</span></li>`;
  }).join('');
  return `
    <div class="rag-sources">
      <div class="rag-sources-label"><i class="bi bi-journal-bookmark-fill me-1"></i>Sources</div>
      <ul class="rag-source-list">${items}</ul>
    </div>`;
}

function appendMessage(role, content, sources = []) {
  const isUser = role === 'user';
  const div = document.createElement('div');
  div.className = `message message-${isUser ? 'user' : 'bot'} animate-slide-in`;

  const avatarContent = isUser
    ? '<i class="bi bi-person-fill"></i>'
    : '🌿';

  div.innerHTML = `
    <div class="message-avatar">${avatarContent}</div>
    <div class="message-content">
      <div class="message-bubble">
        ${isUser ? escapeHtml(content) : renderMarkdown(content)}
      </div>
      ${!isUser ? buildSourcesHtml(sources) : ''}
      <div class="message-time">${getTimeString()}${!isUser && sources.length ? ' · RAG' : ''}</div>
    </div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function escapeHtml(text) {
  const el = document.createElement('div');
  el.appendChild(document.createTextNode(text));
  return el.innerHTML;
}

function setTyping(show) {
  typingIndicator.classList.toggle('d-none', !show);
  typingIndicator.classList.toggle('d-flex', show);
  if (show) chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setInputLocked(locked) {
  userInput.disabled  = locked;
  sendBtn.disabled    = locked;
  if (!locked) {
    userInput.focus();
    sendBtn.disabled = userInput.value.trim().length === 0;
  }
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  // Reset input
  userInput.value = '';
  userInput.style.height = 'auto';
  charCounter.textContent = '0/1000';
  setInputLocked(true);
  setTyping(true);
  chatStatus.textContent = 'Thinking...';

  // Show user message
  appendMessage('user', message);

  try {
    const res = await fetch('/api/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message }),
    });

    const data = await res.json();
    setTyping(false);

    if (data.response) {
      appendMessage('assistant', data.response, data.sources || []);
    } else if (data.error) {
      appendMessage('assistant', `⚠️ ${data.error}`);
    }
  } catch (err) {
    setTyping(false);
    appendMessage('assistant', '⚠️ Connection error. Please check your server is running and try again.');
  } finally {
    setInputLocked(false);
    chatStatus.textContent = 'Online • Powered by IBM Watsonx + RAG';
  }
});

// Clear Chat
clearChatBtn.addEventListener('click', async () => {
  try {
    await fetch('/api/clear', { method: 'POST' });
  } catch (_) {}
  chatMessages.innerHTML = '';
  appendMessage('assistant', '🌿 Conversation cleared! How can I help you live more sustainably today?');
  showToast('Conversation cleared successfully.');
});

// ── Data Loading ─────────────────────────────────
async function loadSection(url, render, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  try {
    const res  = await fetch(url);
    const data = await res.json();
    container.innerHTML = data.map(render).join('');
  } catch (_) {
    if (container) container.innerHTML = `
      <div class="col-12 text-center py-4 text-muted">
        <i class="bi bi-wifi-off fs-2 d-block mb-2"></i>Failed to load data.
      </div>`;
  }
}

function renderTip(tip) {
  return `
    <div class="col-sm-6 col-lg-3">
      <div class="tip-card">
        <span class="tip-icon">${tip.icon}</span>
        <div class="tip-title">${tip.title}</div>
        <p class="tip-text">${tip.tip}</p>
      </div>
    </div>`;
}

function renderProduct(p) {
  const stars = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));
  return `
    <div class="col-sm-6 col-lg-3">
      <div class="product-card">
        <span class="product-category">${p.category}</span>
        <div class="product-name">${p.name}</div>
        <p class="product-impact">${p.impact}</p>
        <div class="product-rating">
          <span class="stars">${stars}</span>
          <span class="rating-num">${p.rating}</span>
        </div>
      </div>
    </div>`;
}

function renderRecycling(r) {
  const iconMap = {
    'Plastic Bottles (PET #1)': '🧴',
    'Glass Jars & Bottles':     '🍾',
    'Cardboard & Paper':        '📦',
    'Aluminium Cans':           '🥫',
    'Electronic Waste (E-Waste)':'💻',
    'Batteries':                '🔋',
    'Food Waste':               '🍂',
    'Textiles & Clothing':      '👕',
  };
  const icon      = iconMap[r.material] || '♻️';
  const badgeHtml = r.accepted
    ? '<span class="accepted-badge">✓ Bin Collection</span>'
    : '<span class="special-badge">⚠ Special Drop-Off</span>';
  return `
    <div class="col-md-6">
      <div class="recycling-card">
        <div class="recycle-icon-wrap ${r.accepted ? 'accepted' : 'special'}">${icon}</div>
        <div class="flex-grow-1">
          <div class="d-flex align-items-start justify-content-between gap-2 mb-1">
            <div class="recycle-material">${r.material}</div>
            ${badgeHtml}
          </div>
          <div class="recycle-bin"><i class="bi bi-trash3 me-1"></i>${r.bin}</div>
          <p class="recycle-tips">${r.tips}</p>
        </div>
      </div>
    </div>`;
}

function renderScheme(s) {
  return `
    <div class="col-md-6 col-lg-4">
      <div class="scheme-card">
        <div class="scheme-top">
          <span class="scheme-category">${s.category}</span>
          <span class="scheme-country">${s.country}</span>
        </div>
        <div class="scheme-name">${s.name}</div>
        <p class="scheme-desc">${s.description}</p>
        <a href="${s.link}" target="_blank" rel="noopener" class="scheme-link">
          <i class="bi bi-box-arrow-up-right"></i> Learn More
        </a>
      </div>
    </div>`;
}

// ── Toast Notification ───────────────────────────
function showToast(msg) {
  const toastEl   = document.getElementById('ecoToast');
  const toastBody = document.getElementById('toastBody');
  if (!toastEl) return;
  toastBody.textContent = msg;
  const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
  toast.show();
}

// ── Scroll Reveal ────────────────────────────────
(function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fade-up');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.tip-card, .product-card, .recycling-card, .scheme-card').forEach(el => {
    observer.observe(el);
  });
})();

// ── Init ─────────────────────────────────────────
(async function init() {
  await Promise.all([
    loadSection('/api/tips',      renderTip,       'tipsGrid'),
    loadSection('/api/products',  renderProduct,   'productsGrid'),
    loadSection('/api/recycling', renderRecycling, 'recyclingGrid'),
    loadSection('/api/schemes',   renderScheme,    'schemesGrid'),
  ]);
  // Trigger scroll reveal on newly loaded cards
  document.querySelectorAll('.tip-card, .product-card, .recycling-card, .scheme-card').forEach(el => {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('animate-fade-up'); io.unobserve(e.target); } });
    }, { threshold: 0.08 });
    io.observe(el);
  });
})();
