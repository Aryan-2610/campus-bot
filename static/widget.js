document.addEventListener("DOMContentLoaded", () => {
    // 1. Create and inject CSS for the widget
    const style = document.createElement('style');
    style.innerHTML = `
        #chat-widget { position: fixed; bottom: 20px; right: 20px; z-index: 10000; font-family: sans-serif; }
        #chat-button { 
            width: 60px; height: 60px; background: #EA9320; border-radius: 50%; 
            cursor: pointer; color: white; display: flex; align-items: center; 
            justify-content: center; font-size: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); 
        }
        #chat-window { 
            width: 350px; height: 450px; background: white; border: 1px solid #ddd; 
            display: none; flex-direction: column; border-radius: 15px; overflow: hidden; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.2); margin-bottom: 10px;
        }
        #chat-header { background: #EA9320; color: white; padding: 15px; font-weight: bold; }
        #chat-messages { flex: 1; padding: 15px; overflow-y: auto; background: #fdfdfd; display: flex; flex-direction: column; }
        .msg { margin-bottom: 10px; padding: 8px 12px; border-radius: 12px; max-width: 85%; font-size: 14px; }
        .user-msg { background: #f0f0f0; align-self: flex-end; }
        .bot-msg { background: #EA9320; color: white; align-self: flex-start; }
        .source-tag { font-size: 10px; color: #888; margin-top: -5px; margin-bottom: 10px; }
        #chat-input-area { display: flex; border-top: 1px solid #eee; padding: 10px; }
        #chat-input { flex: 1; border: 1px solid #ddd; padding: 8px; border-radius: 20px; outline: none; }
        #chat-send { background: #EA9320; color: white; border: none; padding: 5px 15px; margin-left: 5px; border-radius: 20px; cursor: pointer; }
    `;
    document.head.appendChild(style);

    // 2. Create HTML structure
    const widget = document.createElement('div');
    widget.id = 'chat-widget';
    widget.innerHTML = `
        <div id="chat-window">
            <div id="chat-header">DTU Assistant</div>
            <div id="chat-messages"></div>
            <div id="chat-input-area">
                <input type="text" id="chat-input" placeholder="Ask a question...">
                <button id="chat-send">Send</button>
            </div>
        </div>
        <div id="chat-button">💬</div>
    `;
    document.body.appendChild(widget);

    const btn = document.getElementById('chat-button');
    const win = document.getElementById('chat-window');
    const send = document.getElementById('chat-send');
    const input = document.getElementById('chat-input');
    const msgArea = document.getElementById('chat-messages');

    btn.onclick = () => win.style.display = win.style.display === 'none' ? 'flex' : 'none';

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        // User message
        msgArea.innerHTML += `<div class="msg user-msg">${text}</div>`;
        input.value = '';

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();

            // Handle Formatting
            let botText = data.inap ? "Inappropriate input detected." : data.answer;
            botText = botText.replace(/\n/g, '<br>');

            msgArea.innerHTML += `<div class="msg bot-msg">${botText}</div>`;
            if (data.source_file && data.source_file !== "N/A") {
                msgArea.innerHTML += `<div class="source-tag">Source: ${data.source_file}</div>`;
            }
        } catch (e) {
            msgArea.innerHTML += `<div class="msg bot-msg">Error connecting to server.</div>`;
        }
        msgArea.scrollTop = msgArea.scrollHeight;
    }

    send.onclick = sendMessage;
    input.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };
});