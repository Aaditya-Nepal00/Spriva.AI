import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useAppContext } from '../context/AppContext';

const AIAssistant = () => {
  const { setIsLoading, isLoading } = useAppContext();
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hello. I'm Spriva, your grant funding advisor. I can help you find grants, review eligibility, or strategize your applications. What are you working on?", timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { 
      role: 'user', 
      content: input, 
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await response.json();
      
      const fullContent = data.response;
      const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      // Simulate typing effect
      setMessages(prev => [...prev, { role: 'assistant', content: '', timestamp, isTyping: true }]);
      
      let currentContent = '';
      const words = fullContent.split(' ');
      
      for (let i = 0; i < words.length; i++) {
        currentContent += (i === 0 ? '' : ' ') + words[i];
        
        // Update the last message
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = { 
            role: 'assistant', 
            content: currentContent, 
            timestamp,
            isTyping: i < words.length - 1
          };
          return newMessages;
        });
        
        // Speed of typing (ms per word)
        await new Promise(resolve => setTimeout(resolve, 30 + Math.random() * 50));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestion = (text) => {
    setInput(text);
    // We could auto-send here too
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="ai-assistant">
      <div className="chat-viewport">
        <div className="messages-list">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-group ${msg.role}`}>
              {msg.role === 'assistant' && <div className="agent-label font-11">Spriva</div>}
              <div className={`message-bubble ${msg.isTyping ? 'is-typing' : ''}`}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
              <div className="timestamp font-11 text-muted">{msg.timestamp}</div>
            </div>
          ))}
          {isLoading && (
            <div className="message-group assistant">
              <div className="agent-label font-11">Spriva</div>
              <div className="message-bubble typing">
                <span>.</span><span>.</span><span>.</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="input-container">
        {messages.length === 1 && (
          <div className="suggestions">
            <button className="pill" onClick={() => handleSuggestion('What grants match my org?')}>What grants match my org?</button>
            <button className="pill" onClick={() => handleSuggestion('How can I improve my eligibility score?')}>How can I improve my eligibility score?</button>
            <button className="pill" onClick={() => handleSuggestion('Help me write a stronger executive summary')}>Help me write a stronger executive summary</button>
          </div>
        )}
        <form className="input-area" onSubmit={handleSend}>
          <textarea 
            rows="1"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Spriva anything about grant funding..."
          />
          <button type="submit" className="send-btn" disabled={isLoading || !input.trim()}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
      </div>

      <style jsx>{`
        .ai-assistant { height: 100%; display: flex; flex-direction: column; max-width: 800px; margin: 0 auto; position: relative; }
        
        .chat-viewport { flex: 1; overflow-y: auto; padding: 24px 0 140px 0; }
        .messages-list { display: flex; flex-direction: column; gap: 24px; }

        .message-group { display: flex; flex-direction: column; gap: 4px; max-width: 70%; }
        .message-group.user { align-self: flex-end; }
        .message-group.assistant { align-self: flex-start; }

        .agent-label { color: var(--text-muted); margin-bottom: 2px; }
        .timestamp { align-self: flex-end; margin-top: 4px; }
        .user .timestamp { align-self: flex-end; }
        .assistant .timestamp { align-self: flex-start; }

        .message-bubble { padding: 12px 16px; font-size: 14px; line-height: 1.6; }
        .user .message-bubble { 
          background: #1a1a1a; 
          color: var(--text-primary); 
          border-radius: 12px 12px 2px 12px; 
        }
        .assistant .message-bubble { 
          background: #111111; 
          border: 1px solid var(--border); 
          color: var(--text-primary); 
          border-radius: 12px 12px 12px 2px; 
        }

        .message-bubble a {
          color: var(--score-high);
          text-decoration: underline;
        }

        .message-bubble p {
          margin-bottom: 12px;
        }

        .message-bubble ul, .message-bubble ol {
          margin-bottom: 12px;
          padding-left: 20px;
        }

        .message-bubble li {
          margin-bottom: 8px;
        }

        .message-bubble p:last-child, .message-bubble ul:last-child, .message-bubble ol:last-child {
          margin-bottom: 0;
        }

        .assistant .message-bubble.is-typing::after {
          content: '|';
          display: inline-block;
          margin-left: 2px;
          animation: cursor-blink 0.8s infinite;
          color: var(--text-primary);
        }

        @keyframes cursor-blink { 0% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }

        .typing span { animation: blink 1.4s infinite both; font-size: 20px; line-height: 1; }
        .typing span:nth-child(2) { animation-delay: .2s; }
        .typing span:nth-child(3) { animation-delay: .4s; }
        @keyframes blink { 0% { opacity: .2; } 20% { opacity: 1; } 100% { opacity: .2; } }

        .input-container { 
          position: absolute; 
          bottom: 0; 
          left: 0; 
          right: 0; 
          background: var(--bg-primary); 
          padding-top: 20px;
          border-top: 1px solid var(--border);
        }
        .suggestions { display: flex; gap: 8px; margin-bottom: 12px; overflow-x: auto; padding-bottom: 4px; }
        .suggestions .pill { white-space: nowrap; cursor: pointer; color: var(--text-secondary); background: transparent; }
        .suggestions .pill:hover { border-color: var(--text-primary); color: var(--text-primary); }

        .input-area { display: flex; align-items: flex-end; gap: 12px; margin-bottom: 24px; }
        .input-area textarea { flex: 1; min-height: 40px; max-height: 120px; resize: none; background: #111; padding: 10px 16px; }
        .send-btn { width: 40px; height: 40px; background: transparent; color: var(--text-secondary); }
        .send-btn:hover:not(:disabled) { color: var(--text-primary); }

        /* ─── Mobile ─── */
        @media (max-width: 768px) {
          .ai-assistant { max-width: 100%; }
          .chat-viewport { padding: 16px 0 140px 0; }
          .message-group { max-width: 90%; }
          .input-container { 
            position: fixed;
            bottom: 56px;
            left: 0;
            right: 0;
            padding: 8px 16px;
            background: var(--bg-primary);
            border-top: 1px solid var(--border);
            z-index: 500;
          }
          .suggestions { 
            flex-wrap: nowrap; 
            overflow-x: auto; 
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            padding: 0 4px 4px 0;
          }
          .suggestions::-webkit-scrollbar { display: none; }
          .suggestions .pill { min-height: 36px; font-size: 11px; }
          .input-area { margin-bottom: 0; gap: 6px; }
          .input-area textarea { font-size: 16px; min-height: 40px; padding: 10px 12px; }
          .send-btn { width: 36px; height: 40px; min-height: 40px; flex-shrink: 0; }
        }
      `}</style>
    </div>
  );
};

export default AIAssistant;
