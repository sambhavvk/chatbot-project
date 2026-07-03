/* ================================================================
   Customer Support Chatbot - Frontend JavaScript
   ================================================================ */

// Configuration - update API_ENDPOINT to your deployed API Gateway URL
const API_ENDPOINT = 'http://localhost:8080/chat';
const USER_ID = 'web-user-' + Math.random().toString(36).substring(2, 8);

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const escalationBanner = document.getElementById('escalationBanner');
const statusIndicator = document.getElementById('statusIndicator');

// State
let isProcessing = false;

// ---- Initialisation ----
document.addEventListener('DOMContentLoaded', () => {
    messageInput.addEventListener('keydown', onKeyDown);
    sendButton.addEventListener('click', onSendClick);
    messageInput.focus();
});

// ---- Event Handlers ----
function onKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function onSendClick() {
    sendMessage();
}

// ---- Send Message ----
async function sendMessage() {
    if (isProcessing) return;

    const message = messageInput.value.trim();
    if (!message) return;

    // Clear input immediately
    messageInput.value = '';
    isProcessing = true;
    setUIState('sending');

    // Display user message
    appendMessage('user', message);

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: USER_ID,
                message: message,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Remove typing indicator
        typingIndicator.remove();

        // Display bot response
        appendMessage('bot', data.response, {
            intent: data.intent,
            confidence: data.confidence,
            sentiment: data.sentiment,
        });

        // Handle escalation
        if (data.escalated) {
            showEscalationBanner();
        } else {
            hideEscalationBanner();
        }

    } catch (error) {
        typingIndicator.remove();
        appendMessage('bot', 'Sorry, I encountered an error. Please try again later.');
        console.error('API Error:', error);
    } finally {
        isProcessing = false;
        setUIState('ready');
    }
}

// ---- UI Helpers ----
function appendMessage(type, text, meta = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message`;

    const icon = document.createElement('div');
    icon.className = 'message-icon';
    icon.textContent = type === 'user' ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Convert newlines to <br> and handle simple formatting
    const formattedText = escapeHtml(text)
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    bubble.innerHTML = `<p>${formattedText}</p>`;

    msgDiv.appendChild(icon);
    msgDiv.appendChild(bubble);

    // Optional metadata
    if (meta && type === 'bot') {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.textContent = `intent: ${meta.intent} | confidence: ${(meta.confidence * 100).toFixed(0)}%`;
        msgDiv.appendChild(metaDiv);
    }

    chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message bot-message typing-indicator';
    div.innerHTML = `
        <div class="message-icon">🤖</div>
        <div class="message-bubble">
            <span class="typing-dot">●</span>
            <span class="typing-dot">●</span>
            <span class="typing-dot">●</span>
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
}

function showEscalationBanner() {
    escalationBanner.style.display = 'flex';
    // Auto-hide after 8 seconds
    clearTimeout(window._escalationTimeout);
    window._escalationTimeout = setTimeout(hideEscalationBanner, 8000);
}

function hideEscalationBanner() {
    escalationBanner.style.display = 'none';
}

function setUIState(state) {
    switch (state) {
        case 'sending':
            sendButton.disabled = true;
            messageInput.disabled = true;
            messageInput.placeholder = 'Sending...';
            statusIndicator.textContent = '● Typing...';
            break;
        case 'ready':
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.placeholder = 'Type your message here...';
            messageInput.focus();
            statusIndicator.textContent = '● Online';
            break;
        default:
            break;
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ---- Utilities ----
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add typing animation CSS dynamically
const style = document.createElement('style');
style.textContent = `
    .typing-dot {
        display: inline-block;
        animation: typingBounce 1.4s infinite;
        margin: 0 2px;
        color: #888;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.3; }
        30% { transform: translateY(-4px); opacity: 1; }
    }
`;
document.head.appendChild(style);