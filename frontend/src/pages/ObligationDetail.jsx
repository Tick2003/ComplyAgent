import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, FileText, Clock, AlertTriangle, CheckCircle2,
  Link2, Upload, MessageSquare, Send, History, Shield
} from 'lucide-react';
import {
  getObligation, getEvidence, getStatusHistory,
  getObligationAuditTrail, attachEvidence, setComplianceStatus,
  queryAgent
} from '../services/api';

const STATUS_BADGE = {
  compliant: 'badge-compliant',
  partially_compliant: 'badge-partial',
  non_compliant: 'badge-non-compliant',
  not_yet_due: 'badge-not-due',
};

export default function ObligationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [obligation, setObligation] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [statusHistory, setStatusHistory] = useState([]);
  const [auditTrail, setAuditTrail] = useState([]);
  const [activeTab, setActiveTab] = useState('details');
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [statusForm, setStatusForm] = useState({ status: '', notes: '' });
  const [evidenceForm, setEvidenceForm] = useState({ title: '', content: '', evidence_type: 'document' });

  useEffect(() => { loadData(); }, [id]);

  async function loadData() {
    try {
      const [obl, ev, hist, audit] = await Promise.all([
        getObligation(id),
        getEvidence(id),
        getStatusHistory(id),
        getObligationAuditTrail(id),
      ]);
      setObligation(obl);
      setEvidence(ev);
      setStatusHistory(hist);
      setAuditTrail(audit);
    } catch {
      // Fallback
    }
  }

  async function handleStatusChange(e) {
    e.preventDefault();
    if (!statusForm.status) return;
    try {
      await setComplianceStatus(id, { ...statusForm, changed_by: 'Priya Sharma' });
      setStatusForm({ status: '', notes: '' });
      loadData();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleAddEvidence(e) {
    e.preventDefault();
    if (!evidenceForm.title) return;
    try {
      await attachEvidence(id, { ...evidenceForm, uploaded_by: 'Priya Sharma' });
      setEvidenceForm({ title: '', content: '', evidence_type: 'document' });
      loadData();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleChat(e) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const question = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', text: question }]);
    setChatInput('');
    setChatLoading(true);
    try {
      const result = await queryAgent(question);
      setChatMessages(prev => [...prev, { role: 'agent', text: result.answer, citations: result.citations }]);
    } catch {
      setChatMessages(prev => [...prev, { role: 'agent', text: 'Unable to get a response. Ensure the backend is running.' }]);
    } finally {
      setChatLoading(false);
    }
  }

  if (!obligation) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-transparent"
          style={{ borderTopColor: 'var(--accent-blue)' }} />
      </div>
    );
  }

  const tabs = [
    { id: 'details', label: 'Details', icon: FileText },
    { id: 'evidence', label: `Evidence (${evidence.length})`, icon: Link2 },
    { id: 'audit', label: 'Audit Trail', icon: History },
    { id: 'chat', label: 'Ask Agent', icon: MessageSquare },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start gap-4">
        <button onClick={() => navigate('/obligations')} className="btn-secondary p-2 mt-1">
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-1">
            <span className="font-mono text-sm" style={{ color: 'var(--accent-blue)' }}>
              {obligation.obligation_id}
            </span>
            <span className={`badge ${STATUS_BADGE[obligation.current_compliance_status] || 'badge-not-due'}`}>
              {(obligation.current_compliance_status || 'unknown').replace(/_/g, ' ')}
            </span>
          </div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
            {obligation.obligation_text_summary}
          </h2>
        </div>
      </div>

      {/* Quick Info Cards */}
      <div className="grid grid-cols-5 gap-4">
        {[
          { label: 'Type', value: (obligation.obligation_type || '').replace(/_/g, ' ') },
          { label: 'Frequency', value: obligation.frequency },
          { label: 'Deadline', value: obligation.deadline_rule || 'N/A' },
          { label: 'Confidence', value: `${Math.round((obligation.confidence_score || 0) * 100)}%` },
          { label: 'Source', value: obligation.source_clause_ref || 'N/A' },
        ].map((item, i) => (
          <div key={i} className="glass-card p-4">
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{item.label}</p>
            <p className="text-sm font-medium mt-1 truncate" style={{ color: 'var(--text-primary)' }}>{item.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id ? 'text-white' : ''
            }`}
            style={{
              background: activeTab === tab.id ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
              color: activeTab === tab.id ? 'var(--accent-blue)' : 'var(--text-secondary)',
            }}
          >
            <tab.icon size={15} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="glass-card-static p-6">
        {activeTab === 'details' && (
          <div className="space-y-6">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-secondary)' }}>
                Trigger Condition
              </h4>
              <p className="text-sm" style={{ color: 'var(--text-primary)' }}>
                {obligation.trigger_condition || 'Not specified'}
              </p>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-secondary)' }}>
                Evidence Required
              </h4>
              <div className="flex flex-wrap gap-2">
                {(obligation.evidence_required || []).map((ev, i) => (
                  <span key={i} className="badge badge-pending">{ev}</span>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-secondary)' }}>
                Penalty / Risk if Non-Compliant
              </h4>
              <p className="text-sm" style={{ color: 'var(--accent-rose)' }}>
                {obligation.penalty_or_risk_if_noncompliant || 'Not specified'}
              </p>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-secondary)' }}>
                Process Areas
              </h4>
              <div className="flex flex-wrap gap-2">
                {(obligation.process_areas || []).map((p, i) => (
                  <span key={i} className="badge" style={{ background: 'rgba(59,130,246,0.1)', color: 'var(--accent-blue)', border: '1px solid rgba(59,130,246,0.2)' }}>
                    {p}
                  </span>
                ))}
              </div>
            </div>

            {/* Update Status Form */}
            <div className="pt-4" style={{ borderTop: '1px solid var(--border-glass)' }}>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-secondary)' }}>
                Update Compliance Status
              </h4>
              <form onSubmit={handleStatusChange} className="flex gap-3">
                <select value={statusForm.status} onChange={e => setStatusForm(s => ({ ...s, status: e.target.value }))}
                  className="input-field w-48">
                  <option value="">Select status...</option>
                  <option value="compliant">Compliant</option>
                  <option value="partially_compliant">Partially Compliant</option>
                  <option value="non_compliant">Non-Compliant</option>
                  <option value="not_yet_due">Not Yet Due</option>
                </select>
                <input type="text" placeholder="Notes (optional)" value={statusForm.notes}
                  onChange={e => setStatusForm(s => ({ ...s, notes: e.target.value }))}
                  className="input-field flex-1" />
                <button type="submit" className="btn-primary">Update</button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="space-y-4">
            {evidence.map((ev, i) => (
              <div key={i} className="flex items-start gap-3 p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)' }}>
                <div className="p-2 rounded-lg" style={{ background: 'rgba(16,185,129,0.1)' }}>
                  {ev.evidence_type === 'link' ? <Link2 size={16} style={{ color: 'var(--accent-emerald)' }} /> :
                    <FileText size={16} style={{ color: 'var(--accent-emerald)' }} />}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{ev.title}</p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{ev.content}</p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    {ev.uploaded_by} · {new Date(ev.uploaded_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}

            <div className="pt-4" style={{ borderTop: '1px solid var(--border-glass)' }}>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--text-secondary)' }}>
                Attach Evidence
              </h4>
              <form onSubmit={handleAddEvidence} className="space-y-3">
                <div className="flex gap-3">
                  <select value={evidenceForm.evidence_type}
                    onChange={e => setEvidenceForm(f => ({ ...f, evidence_type: e.target.value }))}
                    className="input-field w-36">
                    <option value="document">Document</option>
                    <option value="link">Link</option>
                    <option value="checkbox">Checkbox</option>
                  </select>
                  <input type="text" placeholder="Evidence title" value={evidenceForm.title}
                    onChange={e => setEvidenceForm(f => ({ ...f, title: e.target.value }))}
                    className="input-field flex-1" />
                </div>
                <div className="flex gap-3">
                  <input type="text" placeholder="Description or URL" value={evidenceForm.content}
                    onChange={e => setEvidenceForm(f => ({ ...f, content: e.target.value }))}
                    className="input-field flex-1" />
                  <button type="submit" className="btn-success flex items-center gap-2">
                    <Upload size={14} /> Attach
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="space-y-0">
            {(auditTrail.length > 0 ? auditTrail : statusHistory).map((entry, i) => (
              <div key={i} className="flex gap-4 pb-4 mb-4" style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <div className="flex flex-col items-center">
                  <div className="w-3 h-3 rounded-full shrink-0" style={{ background: 'var(--accent-blue)' }} />
                  {i < (auditTrail.length || statusHistory.length) - 1 && (
                    <div className="w-px flex-1 mt-1" style={{ background: 'rgba(255,255,255,0.08)' }} />
                  )}
                </div>
                <div className="flex-1 -mt-1">
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                    {entry.action || `Status → ${entry.status?.replace(/_/g, ' ')}`}
                  </p>
                  {entry.old_value && (
                    <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                      {entry.old_value} → {entry.new_value}
                    </p>
                  )}
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    {entry.user || entry.changed_by} · {new Date(entry.timestamp || entry.changed_at).toLocaleString()}
                  </p>
                  {(entry.details || entry.notes) && (
                    <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
                      {entry.details || entry.notes}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {auditTrail.length === 0 && statusHistory.length === 0 && (
              <p className="text-sm text-center py-8" style={{ color: 'var(--text-muted)' }}>No audit trail entries yet.</p>
            )}
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="flex flex-col h-96">
            <div className="flex-1 overflow-y-auto space-y-3 mb-4">
              {chatMessages.length === 0 && (
                <div className="text-center py-12">
                  <MessageSquare size={32} className="mx-auto mb-2 opacity-20" style={{ color: 'var(--text-muted)' }} />
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                    Ask the agent about this obligation
                  </p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    e.g., "What evidence do I need for this?" or "Am I compliant?"
                  </p>
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} className={`chat-message ${msg.role}`}>
                  <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                </div>
              ))}
              {chatLoading && (
                <div className="chat-message agent flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border border-transparent"
                    style={{ borderTopColor: 'var(--accent-blue)' }} />
                  <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Thinking...</span>
                </div>
              )}
            </div>
            <form onSubmit={handleChat} className="flex gap-3">
              <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)}
                placeholder="Ask about this obligation..." className="input-field flex-1" />
              <button type="submit" className="btn-primary flex items-center gap-2" disabled={chatLoading}>
                <Send size={14} /> Ask
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
