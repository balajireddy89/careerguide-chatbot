const conversationHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    // Attach suggestion chip click listeners
    const chips = document.querySelectorAll('.chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            if (question) {
                document.getElementById('userInput').value = question;
                sendMessage();
            }
        });
    });

    // Modal listeners
    const infoBtn = document.getElementById('infoBtn');
    const closeModal = document.getElementById('closeModal');
    const aboutModal = document.getElementById('aboutModal');

    infoBtn.addEventListener('click', () => aboutModal.classList.add('open'));
    closeModal.addEventListener('click', () => aboutModal.classList.remove('open'));
    aboutModal.addEventListener('click', (e) => {
        if (e.target === aboutModal) aboutModal.classList.remove('open');
    });
});

async function sendMessage() {
    const inputElement = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const userMessage = inputElement.value.trim();

    if (!userMessage) return;

    // Clear input & disable UI during request
    inputElement.value = '';
    inputElement.disabled = true;
    sendBtn.disabled = true;

    // Render User Message Bubble
    appendUserBubble(userMessage);

    // Show Thinking Indicator
    showLoading(true);

    try {
        const response = await fetch('http://localhost:8080/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMessage,
                history: conversationHistory.slice(-8)
            })
        });

        const data = await response.json();

        showLoading(false);

        if (data && data.response) {
            appendBotBubble(data.response, data.model, data.fallbackUsed);
            
            // Update local memory
            conversationHistory.push({ role: 'user', content: userMessage });
            conversationHistory.push({ role: 'assistant', content: data.response });
        } else {
            appendBotBubble("Sorry, I received an invalid response. Please try again.", "error", false);
        }

    } catch (error) {
        console.error('Chat error:', error);
        showLoading(false);
        appendBotBubble("Sorry, I'm unable to connect to the AI service right now. Please check your backend connection.", "error", false);
    } finally {
        inputElement.disabled = false;
        sendBtn.disabled = false;
        inputElement.focus();
    }
}

function appendUserBubble(text) {
    const chatContainer = document.getElementById('chatContainer');

    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper user-wrapper';

    wrapper.innerHTML = `
        <div class="avatar">👤</div>
        <div class="message-content">
            <div class="sender-name">You</div>
            <div class="bubble user-bubble">${escapeHtml(text)}</div>
        </div>
    `;

    chatContainer.appendChild(wrapper);
    scrollToBottom();
}

function appendBotBubble(text, model, fallbackUsed) {
    const chatContainer = document.getElementById('chatContainer');

    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot-wrapper';

    let badgeHtml = '';
    if (model && model !== 'error' && model !== 'none' && model !== 'system') {
        if (fallbackUsed) {
            badgeHtml = `<div class="model-badge fallback-badge">🔄 Fallback Model: ${escapeHtml(model)}</div>`;
        } else {
            badgeHtml = `<div class="model-badge primary-badge">⚡ Primary Model: ${escapeHtml(model)}</div>`;
        }
    }

    wrapper.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="message-content">
            <div class="sender-name">CareerGuide AI</div>
            <div class="bubble bot-bubble">${formatMarkdown(text)}</div>
            ${badgeHtml}
        </div>
    `;

    chatContainer.appendChild(wrapper);
    scrollToBottom();
}

function showLoading(active) {
    const indicator = document.getElementById('loadingIndicator');
    if (active) {
        indicator.classList.add('active');
    } else {
        indicator.classList.remove('active');
    }
    scrollToBottom();
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function sanitizeHtml(htmlStr) {
    if (!htmlStr) return '';
    const temp = document.createElement('div');
    temp.innerHTML = htmlStr;

    // Remove dangerous executable tags
    const badTags = temp.querySelectorAll('script, iframe, object, embed, style, form, input, button');
    badTags.forEach(el => el.remove());

    // Remove inline event handlers (onerror, onload, etc.)
    const allElements = temp.querySelectorAll('*');
    allElements.forEach(el => {
        Array.from(el.attributes).forEach(attr => {
            if (attr.name.startsWith('on') || attr.value.trim().toLowerCase().startsWith('javascript:')) {
                el.removeAttribute(attr.name);
            }
        });
    });

    return temp.innerHTML;
}

function formatMarkdown(text) {
    if (!text) return '';

    // If marked library is available, use standard GitHub Flavored Markdown
    if (typeof marked !== 'undefined') {
        try {
            marked.setOptions({
                breaks: true,
                gfm: true
            });
            const parsed = marked.parse(text);
            return sanitizeHtml(parsed);
        } catch (e) {
            console.warn('Marked parse warning, using fallback parser:', e);
        }
    }

    return parseMarkdownFallback(text);
}

function parseMarkdownFallback(text) {
    if (!text) return '';
    let html = escapeHtml(text);

    // Unescape literal <br> tags returned in text
    html = html.replace(/&lt;br\s*\/?&gt;/gi, '<br>');

    // Code blocks ```code```
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headers ###
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italics *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Lists (- item or * item)
    html = html.replace(/^[\*\-]\s+(.*)$/gim, '<li>$1</li>');

    // Tables
    const lines = html.split('\n');
    let inTable = false;
    let tableHtml = '';
    let resultLines = [];

    for (let line of lines) {
        let trimmed = line.trim();
        if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
            if (/^\|[\s\-:|]+\|$/.test(trimmed)) continue;
            let cells = trimmed.split('|').slice(1, -1).map(c => c.trim());
            let cellTag = inTable ? 'td' : 'th';
            let rowHtml = '<tr>' + cells.map(c => `<${cellTag}>${c}</${cellTag}>`).join('') + '</tr>';
            
            if (!inTable) {
                inTable = true;
                tableHtml = '<div class="table-wrapper"><table>' + rowHtml;
            } else {
                tableHtml += rowHtml;
            }
        } else {
            if (inTable) {
                inTable = false;
                tableHtml += '</table></div>';
                resultLines.push(tableHtml);
                tableHtml = '';
            }
            resultLines.push(line);
        }
    }
    if (inTable) {
        tableHtml += '</table></div>';
        resultLines.push(tableHtml);
    }

    html = resultLines.join('<br>');
    return sanitizeHtml(html);
}
