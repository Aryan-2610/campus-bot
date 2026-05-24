(function() {
    // Self-executing function to avoid polluting the global namespace
    const API_URL = 'http://localhost:5001/api'; // Replace with your actual backend URL

    const sessionId = crypto.randomUUID();

    // --- Create and Inject CSS ---
    function injectCSS() {
        // Simple web fonts
        const fontLink = document.createElement('link');
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600&display=swap';
        fontLink.rel = 'stylesheet';
        document.head.appendChild(fontLink);

        const style = document.createElement('style');
        // Simple, clean college-appropriate design
        style.textContent = `
        :root {
            --chat-primary: #2c3e50;
            --chat-secondary: #34495e;
            --chat-accent: #3498db;
            --chat-bg: #ffffff;
            --chat-light-bg: #f8f9fa;
            --chat-border: #dee2e6;
            --chat-text: #333333;
            --chat-text-light: #666666;
            --chat-text-white: #ffffff;
        }

        #chat-widget-container { 
            position: fixed; 
            bottom: 20px; 
            right: 20px; 
            z-index: 9999;
            font-family: 'Open Sans', Arial, sans-serif;
        }

        #chat-toggle-button { 
            background-color: var(--chat-primary);
            color: var(--chat-text-white);
            border: none; 
            border-radius: 8px; 
            width: 60px; 
            height: 60px; 
            font-size: 16px; 
            cursor: pointer; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            display: flex; 
            flex-direction: column;
            justify-content: center; 
            align-items: center; 
            transition: background-color 0.2s ease;
            font-weight: 500;
        }

        #chat-toggle-button:hover { 
            background-color: var(--chat-secondary);
        }

        #chat-window { 
            position: absolute; 
            bottom: 70px; 
            right: 0; 
            width: 350px; 
            height: 500px; 
            background-color: var(--chat-bg);
            border-radius: 8px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            display: none; 
            flex-direction: column; 
            overflow: hidden; 
            border: 1px solid var(--chat-border);
            transform: translateY(10px);
            opacity: 0;
            transition: all 0.2s ease;
        }

        #chat-window.open { 
            display: flex; 
            transform: translateY(0);
            opacity: 1;
        }

        .chat-header { 
            background-color: var(--chat-primary);
            color: var(--chat-text-white); 
            padding: 16px 20px; 
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
            flex-shrink: 0;
        }

        .chat-header-icon {
            width: 32px;
            height: 32px;
            background-color: var(--chat-accent);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
        }

        .chat-header-info .title { 
            font-size: 16px; 
            font-weight: 600;
            margin: 0;
        }

        .chat-header-info .subtitle { 
            font-size: 13px; 
            opacity: 0.8;
            margin: 2px 0 0 0;
        }

        .chat-messages { 
            flex-grow: 1; 
            padding: 16px; 
            overflow-y: auto; 
            background-color: var(--chat-light-bg);
            display: flex; 
            flex-direction: column; 
            gap: 12px;
        }

        .chat-messages::-webkit-scrollbar {
            width: 6px;
        }

        .chat-messages::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        .chat-messages::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }

        .message { 
            padding: 10px 14px; 
            border-radius: 6px; 
            max-width: 80%; 
            line-height: 1.4; 
            font-size: 14px;
            animation: fadeIn 0.2s ease;
        }

        .user-message { 
            background-color: var(--chat-accent);
            color: var(--chat-text-white);
            align-self: flex-end; 
            margin-left: 20%;
        }

        .bot-message { 
            background-color: var(--chat-bg);
            color: var(--chat-text);
            align-self: flex-start; 
            border: 1px solid var(--chat-border);
            margin-right: 20%;
        }

        .chat-input-container { 
            display: flex; 
            padding: 16px; 
            border-top: 1px solid var(--chat-border); 
            background-color: var(--chat-bg);
            align-items: center;
            gap: 8px;
        }

        #chat-input { 
            flex-grow: 1; 
            border: 1px solid var(--chat-border); 
            border-radius: 6px; 
            padding: 10px 12px; 
            outline: none; 
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s ease;
        }

        #chat-input:focus { 
            border-color: var(--chat-accent);
        }

        #chat-input::placeholder {
            color: var(--chat-text-light);
        }

        #chat-send { 
            background-color: var(--chat-accent);
            color: var(--chat-text-white);
            border: none; 
            border-radius: 6px;
            width: 40px;
            height: 40px;
            font-size: 16px; 
            cursor: pointer; 
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s ease;
        }

        #chat-send:hover { 
            background-color: #2980b9;
        }

        /* Simple typing indicator */
        .typing-indicator { 
            display: flex; 
            align-items: center; 
            gap: 6px; 
            padding: 10px 14px;
            background-color: var(--chat-bg);
            border: 1px solid var(--chat-border);
            border-radius: 6px;
            align-self: flex-start;
            max-width: 80%;
            margin-right: 20%;
        }

        .typing-indicator span { 
            width: 6px; 
            height: 6px; 
            background-color: var(--chat-text-light);
            border-radius: 50%; 
            animation: typing 1.2s infinite ease-in-out; 
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.24s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.12s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0s; }
        
        @keyframes typing { 
            0%, 80%, 100% { 
                opacity: 0.4;
                transform: scale(1);
            } 
            40% { 
                opacity: 1;
                transform: scale(1.2);
            } 
        }

        @keyframes fadeIn { 
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Mobile responsive */
        @media (max-width: 480px) {
            #chat-window {
                width: 320px;
                height: 450px;
            }
        }
        `;
        document.head.appendChild(style);
    }

    // --- Create and Inject HTML ---
    function createWidgetHTML() {
        const container = document.createElement('div');
        container.id = 'chat-widget-container';
        // Simple, professional HTML structure
        container.innerHTML = `
        <div id="chat-window">
            <div class="chat-header">
                <div class="chat-header-icon">?</div>
                <div class="chat-header-info">
                    <div class="title">Campus Help</div>
                    <div class="subtitle">Ask us anything</div>
                </div>
            </div>
            <div class="chat-messages"></div>
            <div class="chat-input-container">
                <input type="text" id="chat-input" placeholder="Type your question..." autocomplete="off">
                <button id="chat-send" aria-label="Send Message">→</button>
            </div>
        </div>
        <button id="chat-toggle-button">
            <div>Help</div>
        </button>
        `;
        document.body.appendChild(container);
    }

    // --- Widget Logic (functionality unchanged) ---
    function initializeChat() {
        const toggleButton = document.getElementById('chat-toggle-button');
        const chatWindow = document.getElementById('chat-window');
        const messagesContainer = document.querySelector('.chat-messages');
        const input = document.getElementById('chat-input');
        const sendButton = document.getElementById('chat-send');
        const userLang = navigator.language || 'en-US';

        toggleButton.addEventListener('click', () => {
            chatWindow.classList.toggle('open');
            if (chatWindow.classList.contains('open')) {
                input.focus();
            }
        });

        const showTypingIndicator = () => {
            const indicator = document.createElement('div');
            indicator.className = 'message typing-indicator';
            indicator.innerHTML = '<span></span><span></span><span></span>';
            messagesContainer.appendChild(indicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        };

        const hideTypingIndicator = () => {
            const indicator = messagesContainer.querySelector('.typing-indicator');
            if (indicator) {
                indicator.remove();
            }
        };

        const sendMessage = async () => {
            const query = input.value.trim();
            if (!query) return;

            addMessage(query, 'user');
            input.value = '';
            input.focus();
            showTypingIndicator();

            try {
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query, sessionId, language: userLang }),
                });

                hideTypingIndicator();
                if (!response.ok) throw new Error(`Network response was not ok: ${response.statusText}`);
                const data = await response.json();
                addMessage(data.response, 'bot');

            } catch (error) {
                hideTypingIndicator();
                console.error("Chat Error:", error);
                addMessage("Sorry, I'm having trouble connecting. Please try again later.", 'bot');
            }
        };

        sendButton.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => { 
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Simple welcome message
        addMessage("Hi! How can I help you with campus information?", "bot");
    }

    // Initialize when ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            injectCSS();
            createWidgetHTML();
            initializeChat();
        });
    } else {
        injectCSS();
        createWidgetHTML();
        initializeChat();
    }
})();
