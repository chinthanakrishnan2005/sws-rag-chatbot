document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const loadingTemplate = document.getElementById('loading-template');

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Add message to UI
    const addMessage = (content, type, sources = []) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Handle paragraphs for better readability
        const paragraphs = content.split('\n\n');
        paragraphs.forEach(p => {
            if (p.trim()) {
                const pTag = document.createElement('p');
                pTag.textContent = p;
                contentDiv.appendChild(pTag);
            }
        });

        messageDiv.appendChild(contentDiv);

        // Add sources if present and it's a bot message
        if (type === 'bot' && sources.length > 0) {
            const sourcesContainer = document.createElement('div');
            sourcesContainer.className = 'sources-container';
            
            sources.forEach(source => {
                const sourceTag = document.createElement('div');
                sourceTag.className = 'source-tag';
                sourceTag.innerHTML = `
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    ${source}
                `;
                sourcesContainer.appendChild(sourceTag);
            });
            
            messageDiv.appendChild(sourcesContainer);
        }

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    };

    const showLoading = () => {
        const clone = loadingTemplate.content.cloneNode(true);
        chatMessages.appendChild(clone);
        scrollToBottom();
    };

    const hideLoading = () => {
        const loading = document.getElementById('loading-indicator');
        if (loading) {
            loading.remove();
        }
    };

    const handleSend = async () => {
        const text = userInput.value.trim();
        if (!text) return;

        // Disable input while processing
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Add user message
        addMessage(text, 'user');
        
        // Show loading indicator
        showLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: text })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            hideLoading();
            addMessage(data.answer, 'bot', data.sources);

        } catch (error) {
            console.error('Error:', error);
            hideLoading();
            addMessage("Sorry, I encountered an error communicating with the server. Please check if the API is running.", 'bot');
        } finally {
            // Re-enable input
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', handleSend);
    
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
});
