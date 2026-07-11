import { useState } from 'react';
import { Send, MessageSquare, FileText, Scale, Sparkles } from 'lucide-react';
import { queryAgent } from '../services/api';

const SUGGESTED_QUESTIONS = [
  "What are our cybersecurity reporting obligations?",
  "What's our new grievance SLA and are we compliant?",
  "Which obligations are overdue?",
  "What evidence do I need for margin compliance?",
  "Summarize our KYC obligations",
  "What are the penalties for non-compliance with SEBI reporting requirements?",
];

export default function QueryChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSend(question) {
    const q = question || input.trim();
    if (!q) return;

    setMessages(prev => [...prev, { role: 'user', text: q }]);
    setInput('');
    setLoading(true);

    try {
      const result = await queryAgent(q);
      setMessages(prev => [...prev, {
        role: 'agent',
        text: result.answer,
        citations: result.citations,
        related_obligations: result.related_obligations,
        confidence: result.confidence,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'agent',
        text: 'Unable to connect to the Query Agent. Please ensure the backend server is running on port 8000.',
      }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] animate-fade-in">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
          <Sparkles size={20} style={{ color: 'var(--accent-violet)' }} />
          Compliance Query Agent
        </h2>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
          Ask natural-language questions about your compliance obligations. Answers are cited from SEBI regulatory text.
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.length === 0 && (
          <div className="text-center py-16">
            <div className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, rgba(139,92,246,0.15), rgba(59,130,246,0.15))' }}>
              <Scale size={28} style={{ color: 'var(--accent-violet)' }} />
            </div>
            <p className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
              How can I help with compliance?
            </p>
            <p className="text-xs mb-6" style={{ color: 'var(--text-muted)' }}>
              I can answer questions about SEBI regulations, check your compliance status, and cite specific clauses.
            </p>

            <div className="grid grid-cols-2 gap-3 max-w-lg mx-auto">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button key={i} onClick={() => handleSend(q)}
                  className="p-3 rounded-xl text-left text-xs transition-all"
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', color: 'var(--text-secondary)' }}
                  onMouseEnter={e => { e.target.style.borderColor = 'var(--border-hover)'; e.target.style.background = 'rgba(255,255,255,0.05)'; }}
                  onMouseLeave={e => { e.target.style.borderColor = 'var(--border-glass)'; e.target.style.background = 'rgba(255,255,255,0.03)'; }}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i}>
            <div className={`chat-message ${msg.role}`}>
              <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
            </div>

            {/* Citations */}
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-2 ml-4 space-y-1">
                <p className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>📎 Citations:</p>
                {msg.citations.map((c, j) => (
                  <div key={j} className="flex items-start gap-2 p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
                    <FileText size={12} className="mt-0.5 shrink-0" style={{ color: 'var(--accent-blue)' }} />
                    <div>
                      <p className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>
                        {c.chapter} — Section {c.section_id}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        {c.text_preview}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Related obligations */}
            {msg.related_obligations && msg.related_obligations.length > 0 && (
              <div className="mt-2 ml-4 space-y-1">
                <p className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>📋 Related Obligations:</p>
                {msg.related_obligations.slice(0, 3).map((obl, j) => (
                  <div key={j} className="flex items-center gap-2 p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
                    <span className="font-mono text-xs" style={{ color: 'var(--accent-blue)' }}>{obl.obligation_id}</span>
                    <span className={`badge ${obl.current_status === 'compliant' ? 'badge-compliant' : obl.current_status === 'non_compliant' ? 'badge-non-compliant' : 'badge-partial'}`}
                      style={{ fontSize: '0.65rem' }}>
                      {(obl.current_status || 'unknown').replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{obl.summary}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-message agent flex items-center gap-3">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-blue)', animationDelay: '0ms' }} />
              <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-violet)', animationDelay: '150ms' }} />
              <div className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--accent-cyan)', animationDelay: '300ms' }} />
            </div>
            <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Analyzing regulatory text...</span>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={e => { e.preventDefault(); handleSend(); }} className="flex gap-3">
        <input type="text" value={input} onChange={e => setInput(e.target.value)}
          placeholder="Ask a compliance question..."
          className="input-field flex-1" disabled={loading} />
        <button type="submit" className="btn-primary flex items-center gap-2" disabled={loading || !input.trim()}>
          <Send size={16} /> Ask
        </button>
      </form>
    </div>
  );
}
