import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Edit3, Eye, ChevronDown } from 'lucide-react';
import { getObligations, reviewObligation } from '../services/api';

export default function ReviewPanel() {
  const [obligations, setObligations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => { loadPending(); }, []);

  async function loadPending() {
    setLoading(true);
    try {
      const data = await getObligations({ review_status: 'pending_review' });
      setObligations(data);
    } catch {
      setObligations([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleReview(id, status) {
    try {
      await reviewObligation(id, {
        review_status: status,
        reviewed_by: 'Priya Sharma',
        review_notes: status === 'approved' ? 'Verified and approved' : 'Rejected — needs re-extraction',
      });
      loadPending();
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Human Review Queue</h2>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Review and approve/reject AI-extracted obligations before they become active rules
          </p>
        </div>
        <span className="badge badge-pending">{obligations.length} pending</span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-6 w-6 border-2 border-transparent"
            style={{ borderTopColor: 'var(--accent-blue)' }} />
        </div>
      ) : obligations.length === 0 ? (
        <div className="glass-card-static p-12 text-center">
          <CheckCircle size={40} className="mx-auto mb-3" style={{ color: 'var(--accent-emerald)', opacity: 0.5 }} />
          <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
            All obligations have been reviewed!
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            Upload a new circular to generate more obligations for review.
          </p>
        </div>
      ) : (
        <div className="space-y-4 stagger-children">
          {obligations.map((obl) => (
            <div key={obl.id} className="glass-card p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-mono text-xs" style={{ color: 'var(--accent-blue)' }}>
                      {obl.obligation_id}
                    </span>
                    <span className="badge badge-pending text-xs">
                      {(obl.obligation_type || '').replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      Confidence: {Math.round((obl.confidence_score || 0) * 100)}%
                    </span>
                  </div>
                  <p className="text-sm" style={{ color: 'var(--text-primary)' }}>
                    {obl.obligation_text_summary}
                  </p>

                  {expanded === obl.id && (
                    <div className="mt-4 space-y-3 p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)' }}>
                      <div><span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>Trigger: </span>
                        <span className="text-xs" style={{ color: 'var(--text-primary)' }}>{obl.trigger_condition || 'N/A'}</span></div>
                      <div><span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>Frequency: </span>
                        <span className="text-xs" style={{ color: 'var(--text-primary)' }}>{obl.frequency}</span></div>
                      <div><span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>Deadline: </span>
                        <span className="text-xs" style={{ color: 'var(--text-primary)' }}>{obl.deadline_rule || 'N/A'}</span></div>
                      <div><span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>Source: </span>
                        <span className="text-xs" style={{ color: 'var(--text-primary)' }}>{obl.source_clause_ref || 'N/A'}</span></div>
                      <div><span className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>Evidence Required: </span>
                        <span className="text-xs" style={{ color: 'var(--text-primary)' }}>
                          {(obl.evidence_required || []).join(', ') || 'N/A'}
                        </span></div>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button onClick={() => setExpanded(expanded === obl.id ? null : obl.id)}
                    className="btn-secondary p-2" title="View details">
                    <Eye size={16} />
                  </button>
                  <button onClick={() => handleReview(obl.id, 'approved')}
                    className="btn-success flex items-center gap-1" title="Approve">
                    <CheckCircle size={14} /> Approve
                  </button>
                  <button onClick={() => handleReview(obl.id, 'rejected')}
                    className="btn-danger flex items-center gap-1" title="Reject">
                    <XCircle size={14} /> Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
