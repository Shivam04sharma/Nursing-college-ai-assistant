class ChatBot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.quickOptions = document.getElementById('quickOptions');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.backBtn = document.getElementById('backBtn');
        this.restartBtn = document.getElementById('restartBtn');
        
        this.isTyping = false;
        this.currentOptions = [];
        
        this.initializeEventListeners();
        this.loadInitialMessage();
    }
    
    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        this.backBtn.addEventListener('click', () => this.goBack());
        this.restartBtn.addEventListener('click', () => this.restartChat());
    }
    
    async loadInitialMessage() {
        try {
            const response = await fetch('/get_initial_message');
            const data = await response.json();
            
            if (data.messages && data.messages.length > 0) {
                // Load existing messages
                data.messages.forEach(message => {
                    this.addMessage(message.text, message.sender, message.timestamp);
                });
            } else {
                // Show initial bot message
                this.showTypingIndicator();
                setTimeout(() => {
                    this.hideTypingIndicator();
                    this.addMessage(data.bot_response, 'bot');
                    this.updateQuickOptions(data.options);
                    this.enableInput();
                }, 1500);
            }
        } catch (error) {
            console.error('Error loading initial message:', error);
        }
    }
    
    async sendMessage(message = null) {
        const messageText = message || this.messageInput.value.trim();
        if (!messageText || this.isTyping) return;
        
        this.addMessage(messageText, 'user');
        this.messageInput.value = '';
        this.disableInput();
        this.clearQuickOptions();
        
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText })
            });
            
            const data = await response.json();
            
            setTimeout(() => {
                this.hideTypingIndicator();
                this.addMessage(data.bot_response, 'bot');
                
                if (!data.is_completed) {
                    this.updateQuickOptions(data.options);
                    this.enableInput();
                }
                
                this.updateControlButtons(data.can_go_back);
            }, 1000);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Maaf kijiye, koi technical samasya hai. Kripya phir se koshish karen.', 'bot');
            this.enableInput();
        }
    }
    
    addMessage(text, sender, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = timestamp || new Date().toLocaleTimeString('hi-IN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const avatarIcon = sender === 'bot' ? 'fas fa-robot' : 'fas fa-user';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${avatarIcon}"></i>
            </div>
            <div class="message-bubble">
                ${text}
                <div class="message-time">${time}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    updateQuickOptions(options) {
        this.currentOptions = options;
        this.quickOptions.innerHTML = '';
        
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'quick-option';
            button.textContent = option;
            button.addEventListener('click', () => this.sendMessage(option));
            this.quickOptions.appendChild(button);
        });
    }
    
    clearQuickOptions() {
        this.quickOptions.innerHTML = '';
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.classList.remove('d-none');
        this.chatMessages.appendChild(this.typingIndicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.classList.add('d-none');
        if (this.typingIndicator.parentNode) {
            this.typingIndicator.parentNode.removeChild(this.typingIndicator);
        }
    }
    
    enableInput() {
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
    }
    
    disableInput() {
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
    }
    
    updateControlButtons(canGoBack) {
        this.backBtn.style.display = canGoBack ? 'inline-block' : 'none';
    }
    
    async goBack() {
        try {
            const response = await fetch('/go_back', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Remove last two messages
                const messages = this.chatMessages.querySelectorAll('.message:not(#typingIndicator)');
                if (messages.length >= 2) {
                    messages[messages.length - 1].remove();
                    messages[messages.length - 2].remove();
                }
                
                this.updateQuickOptions(data.options);
                this.enableInput();
            }
        } catch (error) {
            console.error('Error going back:', error);
        }
    }
    
    async restartChat() {
        try {
            const response = await fetch('/restart_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Clear all messages
                this.chatMessages.innerHTML = '';
                
                // Show initial message
                this.showTypingIndicator();
                setTimeout(() => {
                    this.hideTypingIndicator();
                    this.addMessage(data.bot_response, 'bot');
                    this.updateQuickOptions(data.options);
                    this.enableInput();
                    this.updateControlButtons(false);
                }, 1000);
            }
        } catch (error) {
            console.error('Error restarting chat:', error);
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Initialize chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});