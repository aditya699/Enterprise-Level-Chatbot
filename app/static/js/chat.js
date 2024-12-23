const messagesDiv = document.getElementById('messages');
const userInput = document.getElementById('userInput');

if (!messagesDiv || !userInput) {
    console.error('Required DOM elements not found');
}

function addMessage(content, isUser) {
    if (!messagesDiv) return;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addLoadingIndicator() {
    if (!messagesDiv) return;
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

// Make sendMessage globally available
window.sendMessage = async function() {
    if (!userInput) return;
    
    const message = userInput.value.trim();
    if (!message) return;

    // Clear input and disable it
    userInput.value = '';
    userInput.disabled = true;
    const button = document.querySelector('button');
    if (button) button.disabled = true;

    // Add user message
    addMessage(message, true);

    // Add loading indicator
    const loadingDiv = addLoadingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_message: message }),
            credentials: 'include'  // Added this
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Remove loading indicator
        if (loadingDiv) loadingDiv.remove();

        // Add bot response
        if (data && data.response) {
            addMessage(data.response, false);
        } else {
            throw new Error('Invalid response format');
        }
    } catch (error) {
        console.error('Error:', error);
        if (loadingDiv) loadingDiv.remove();
        addMessage('Sorry, I encountered an error. Please try again.', false);
    } finally {
        // Re-enable input
        if (userInput) userInput.disabled = false;
        const button = document.querySelector('button');
        if (button) button.disabled = false;
    }
}

// Allow sending message with Enter key
if (userInput) {
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Add initial message
document.addEventListener('DOMContentLoaded', () => {
    addMessage('Hello! How can I help you today?', false);
});