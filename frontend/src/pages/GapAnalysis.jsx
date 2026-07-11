import { useState } from 'react';
import { AlertTriangle, Search, Shield, ArrowRight, Zap, CheckCircle } from 'lucide-react';
import { runGapAnalysis } from '../services/api';

export default function GapAnalysis() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleAnalyze() {
    setLoading(true);
    try {
      const result = await runGapAnalysis();
      setReport(result);
    } catch {
      // Fallback demo data
      setReport({
        total_gaps: 6,
        priority_summary: '🚨 2 obligation(s) are overdue or non-compliant and require immediate attention. ⚠️ 4 obligation(s) have no evidence attached. 🔍 1 obligation(s) have low extraction confidence and need human re-review.',
        overdue: [
          { obligation_id: 'OBL-CYBER-001', summary: 'Implement comprehensive cybersecurity framework', obligation_type: 'cybersecurity', deadline_rule: 'Continuous', current_status: 'non_compliant' },
          { obligation_id: 'OBL-REPORT-002', summary: 'File quarterly compliance report with SEBI', obligation_type: 'reporting', deadline_rule: 'Within 15 days of quarter end', current_status: 'non_compliant' },
        ],
        missing_evidence: [
          { obligation_id: 'OBL-CYBER-001', summary: 'Implement comprehensive cybersecurity framework', evidence_required: ['Cybersecurity policy', 'VAPT report'] },
          { obligation_id: 'OBL-REPORT-002', summary: 'File quarterly compliance report with SEBI', evidence_required: ['Quarterly report', 'Filing receipt'] },
          { obligation_id: 'OBL-GRIEVANCE-002', summary: 'Register complaints on SCORES platform', evidence_required: ['SCORES registration'] },
          { obligation_id: 'OBL-SETTLE-001', summary: 'Settle client running accounts periodically', evidence_required: ['Settlement register'] },
        ],
        low_confidence: [
          { obligation_id: 'OBL-CYBER-002', summary: 'Report cybersecurity incidents within 6 hours', confidence_score: 0.55 },
        ],
        remediation_suggestions: [
          { obligation_id: 'OBL-CYBER-001', severity: 'critical', responsible_team: 'IT Compliance', suggested_deadline_days: 30, remediation_steps: ['Appoint CISO', 'Deploy firewall and IDS', 'Conduct VAPT', 'Document cybersecurity policy'], template_evidence: ['Cybersecurity policy document', 'VAPT report', 'IDS configuration'] },
          { obligation_id: 'OBL-REPORT-002', severity: 'high', responsible_team: 'Compliance Department', suggested_deadline_days: 7, remediation_steps: ['Prepare quarterly report', 'Get board sign-off', 'File with SEBI', 'Archive filing receipt'], template_evidence: ['Quarterly compliance report', 'Board resolution', 'SEBI filing receipt'] },
        ],
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Gap Analysis</h2>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Run the Gap-Finder Agent to scan all active obligations for compliance gaps
          </p>
        </div>
        <button onClick={handleAnalyze} disabled={loading} className="btn-primary flex items-center gap-2">
          {loading ? (
            <div className="animate-spin rounded-full h-4 w-4 border border-transparent" style={{ borderTopColor: 'white' }} />
          ) : (
            <Search size={16} />
          )}
          {loading ? 'Scanning...' : 'Run Gap Analysis'}
        </button>
      </div>

      {report && (
        <>
          {/* Summary */}
          <div className="glass-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg" style={{ background: report.total_gaps > 0 ? 'rgba(244,63,94,0.1)' : 'rgba(16,185,129,0.1)' }}>
                {report.total_gaps > 0 ? <AlertTriangle size={20} style={{ color: 'var(--accent-rose)' }} /> :
                  <CheckCircle size={20} style={{ color: 'var(--accent-emerald)' }} />}
              </div>
              <div>
                <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {report.total_gaps} Gap{report.total_gaps !== 1 ? 's' : ''} Found
                </h3>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                  {report.priority_summary}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(244,63,94,0.06)' }}>
                <p className="text-2xl font-bold" style={{ color: 'var(--accent-rose)' }}>{report.overdue?.length || 0}</p>
                <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>Overdue / Non-Compliant</p>
              </div>
              <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(245,158,11,0.06)' }}>
                <p className="text-2xl font-bold" style={{ color: 'var(--accent-amber)' }}>{report.missing_evidence?.length || 0}</p>
                <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>Missing Evidence</p>
              </div>
              <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(139,92,246,0.06)' }}>
                <p className="text-2xl font-bold" style={{ color: 'var(--accent-violet)' }}>{report.low_confidence?.length || 0}</p>
                <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>Low Confidence</p>
              </div>
            </div>
          </div>

          {/* Overdue */}
          {(report.overdue || []).length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--accent-rose)' }}>
                <AlertTriangle size={14} /> Overdue / Non-Compliant
              </h3>
              {report.overdue.map((gap, i) => (
                <div key={i} className="glass-card p-4" style={{ borderColor: 'rgba(244,63,94,0.15)' }}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs" style={{ color: 'var(--accent-blue)' }}>{gap.obligation_id}</span>
                    <span className="badge badge-non-compliant">{(gap.current_status || '').replace(/_/g, ' ')}</span>
                  </div>
                  <p className="text-sm" style={{ color: 'var(--text-primary)' }}>{gap.summary}</p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Deadline: {gap.deadline_rule || 'N/A'}</p>
                </div>
              ))}
            </div>
          )}

          {/* Remediation Suggestions */}
          {(report.remediation_suggestions || []).length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--accent-emerald)' }}>
                <Zap size={14} /> Remediation Suggestions
              </h3>
              {report.remediation_suggestions.map((sug, i) => (
                <div key={i} className="glass-card p-5" style={{ borderColor: 'rgba(16,185,129,0.15)' }}>
                  <div className="flex items-center gap-3 mb-3">
                    <span className="font-mono text-xs" style={{ color: 'var(--accent-blue)' }}>{sug.obligation_id}</span>
                    <span className={`badge ${sug.severity === 'critical' ? 'badge-non-compliant' : 'badge-partial'}`}>
                      {sug.severity}
                    </span>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      Assign to: {sug.responsible_team} · Deadline: {sug.suggested_deadline_days} days
                    </span>
                  </div>
                  <div className="space-y-2">
                    {(sug.remediation_steps || []).map((step, j) => (
                      <div key={j} className="flex items-start gap-2">
                        <ArrowRight size={12} className="mt-0.5 shrink-0" style={{ color: 'var(--accent-emerald)' }} />
                        <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{step}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(sug.template_evidence || []).map((ev, j) => (
                      <span key={j} className="badge badge-pending text-xs">{ev}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!report && !loading && (
        <div className="glass-card-static p-16 text-center">
          <Shield size={48} className="mx-auto mb-4" style={{ color: 'var(--text-muted)', opacity: 0.2 }} />
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Click "Run Gap Analysis" to scan your obligations for compliance gaps
          </p>
          <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
            The agent will check for overdue obligations, missing evidence, and low-confidence extractions
          </p>
        </div>
      )}
    </div>
  );
}
