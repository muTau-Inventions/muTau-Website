document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('aiChatToggle');
    const overlay = document.getElementById('aiChatOverlay');
    const close = document.getElementById('aiChatClose');
    const input = document.getElementById('aiChatInput');
    const send = document.getElementById('aiChatSend');
    const messages = document.getElementById('aiChatMessages');
    const status = document.getElementById('aiChatStatus');

    // Toggle Chat
    toggle.addEventListener('click', () => {
        overlay.classList.toggle('active');
        if (overlay.classList.contains('active')) {
            input.focus();
        }
    });

    close.addEventListener('click', () => {
        overlay.classList.remove('active');
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
        }
    });

    // Send Message
    function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // User message
        appendMessage(message, 'user');
        input.value = '';
        send.disabled = true;
        status.textContent = 'AI denkt...';

        // API Call
        fetch('/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                appendMessage('❌ ' + data.error, 'ai');
                status.textContent = 'Fehler bei der Anfrage';
            } else {
                appendMessage(data.response, 'ai');
                status.textContent = '';
            }
        })
        .catch(error => {
            appendMessage('❌ Verbindungsfehler: ' + error.message, 'ai');
            status.textContent = 'Verbindung verloren';
        })
        .finally(() => {
            send.disabled = false;
            input.focus();
        });
    }

    function appendMessage(text, type) {
        const div = document.createElement('div');
        div.className = `message ${type}-message`;
        div.innerHTML = `<div>${text.replace(/\n/g, '<br>')}</div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    send.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
