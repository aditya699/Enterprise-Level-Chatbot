const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('userInput');

function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = `
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    `;
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return loadingDiv;
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    addMessage(message, true);
    const loadingDiv = addLoadingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_message: message })
        });

        const data = await response.json();
        loadingDiv.remove();
        addMessage(data.response, false);
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.remove();
        addMessage('Sorry, I encountered an error. Please try again.', false);
    }
}

userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});