// chat.js — AI Chat window logic

const chatMsgs = document.getElementById('chat-msgs');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');

function appendMessage(text, sender) {
  if (!chatMsgs) return;
  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-msg ${sender}`;

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';
  bubble.textContent = text;

  const time = document.createElement('div');
  time.className = 'chat-time';
  time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  msgDiv.appendChild(bubble);
  msgDiv.appendChild(time);
  chatMsgs.appendChild(msgDiv);
  chatMsgs.scrollTop = chatMsgs.scrollHeight;
}

function showTyping() {
  if (!chatMsgs) return;
  const typingDiv = document.createElement('div');
  typingDiv.className = 'chat-msg ai';
  typingDiv.id = 'typing-indicator';
  typingDiv.innerHTML = `
    <div class="chat-bubble chat-typing">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>`;
  chatMsgs.appendChild(typingDiv);
  chatMsgs.scrollTop = chatMsgs.scrollHeight;
}

function removeTyping() {
  document.getElementById('typing-indicator')?.remove();
}

async function sendChatMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage(message, 'user');
  chatInput.value = '';
  chatInput.disabled = true;
  showTyping();

  try {
    const res = await fetch('/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    removeTyping();
    appendMessage(data.reply || 'Sorry, something went wrong.', 'ai');
  } catch (err) {
    removeTyping();
    appendMessage('Connection error. Please try again.', 'ai');
  } finally {
    chatInput.disabled = false;
    chatInput.focus();
  }
}

if (chatSendBtn) {
  chatSendBtn.addEventListener('click', sendChatMessage);
}

if (chatInput) {
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });
}

// Suggested question chips
document.querySelectorAll('.chat-suggestion').forEach(chip => {
  chip.addEventListener('click', () => {
    chatInput.value = chip.textContent.trim();
    sendChatMessage();
  });
});