// API configuration
const API_BASE_URL = '/v1';

// DOM elements
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const statusElement = document.getElementById('status');
const helpBtn = document.getElementById('helpBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Focus input on load
    messageInput.focus();
    
    // Add event listeners
    chatForm.addEventListener('submit', handleSubmit);
    helpBtn.addEventListener('click', showHelp);
    
    // Handle Enter key
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    });
});

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Disable input while processing
    setLoading(true);
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        // Send message to API
        console.log('Sending message:', message);
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Add bot response
        addMessage(data.message, 'bot', data.status);
        
        // Update status
        updateStatus('Ready', 'ready');
        
    } catch (error) {
        console.error('Error:', error);
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        // Show error message
        addMessage(
            '⚠️ Sorry, I encountered an error. Please make sure the server is running and try again.',
            'bot',
            'error'
        );
        
        updateStatus('Error connecting to server', 'error');
    } finally {
        setLoading(false);
        messageInput.focus();
    }
}

// Add message to chat
function addMessage(text, sender, status = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    
    // Convert markdown-style formatting
    const formattedText = formatMessage(text);
    textDiv.innerHTML = formattedText;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format message with markdown-like syntax
function formatMessage(text) {
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Keep lists intact
    text = text.replace(/<br>• /g, '<br>• ');
    text = text.replace(/<br>🔹 /g, '<br>🔹 ');
    
    return text;
}

// Add typing indicator
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🤖';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message-text';
    indicatorDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    contentDiv.appendChild(indicatorDiv);
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
    
    return 'typing-indicator';
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Show help
async function showHelp() {
    setLoading(true);
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat/help`);
        const data = await response.json();
        
        removeTypingIndicator(typingId);
        addMessage(data.message, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessage('Error loading help. Please try again.', 'bot', 'error');
    } finally {
        setLoading(false);
    }
}

// Set loading state
function setLoading(isLoading) {
    sendBtn.disabled = isLoading;
    messageInput.disabled = isLoading;
    
    if (isLoading) {
        updateStatus('Processing...', 'loading');
    }
}

// Update status
function updateStatus(text, state = 'ready') {
    statusElement.textContent = text;
    statusElement.className = state;
}

// Scroll to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Auto-reconnect on page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        updateStatus('Ready', 'ready');
    }
});
