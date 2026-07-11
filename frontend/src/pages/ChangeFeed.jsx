import { useState, useEffect } from 'react';
import { Activity, ArrowRight, FileText, AlertCircle, CheckCircle2, Minus } from 'lucide-react';
import { getCirculars, runChangeDetection } from '../services/api';

export default function ChangeFeed() {
  const [circulars, setCirculars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [changeReport, setChangeReport] = useState(null);
  const [detecting, setDetecting] = useState(false);

  useEffect(() => { loadCirculars(); }, []);

  async function loadCirculars() {
    try {
      const data = await getCirculars();
      setCirculars(data);
    } catch {
      setCirculars([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDetectChanges(circularId) {
    setDetecting(true);
    try {
      const result = await runChangeDetection(circularId);
      setChangeReport(result);
    } catch (err) {
      console.error(err);
    } finally {
      setDetecting(false);
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Regulatory Change Feed</h2>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
          Track ingested circulars and run the Change Detection Agent to identify regulatory changes
        </p>
      </div>

      {/* Change Report */}
      {changeReport && (
        <div className="glass-card p-6 space-y-4" style={{ borderColor: 'rgba(59,130,246,0.2)' }}>
          <h3 className="text-sm font-semibold flex items-center gap-2" style={{ color: 'var(--accent-blue)' }}>
            <Activity size={16} /> Change Detection Report
          </h3>
          <p className="text-sm" style={{ color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
            {changeReport.summary}
          </p>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(16,185,129,0.08)' }}>
              <p className="text-2xl font-bold" style={{ color: 'var(--accent-emerald)' }}>
                {changeReport.new_obligations?.length || 0}
              </p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>New Obligations</p>
            </div>
            <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(245,158,11,0.08)' }}>
              <p className="text-2xl font-bold" style={{ color: 'var(--accent-amber)' }}>
                {changeReport.modified_obligations?.length || 0}
              </p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>Modified Obligations</p>
            </div>
            <div className="p-4 rounded-xl text-center" style={{ background: 'rgba(100,116,139,0.08)' }}>
              <p className="text-2xl font-bold" style={{ color: 'var(--text-secondary)' }}>
                {changeReport.superseded_obligations?.length || 0}
              </p>
              <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>Superseded</p>
            </div>
          </div>

          {(changeReport.modified_obligations || []).map((mod, i) => (
            <div key={i} className="p-4 rounded-xl" style={{ background: 'rgba(245,158,11,0.05)', border: '1px solid rgba(245,158,11,0.15)' }}>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle size={14} style={{ color: 'var(--accent-amber)' }} />
                <span className="text-xs font-semibold" style={{ color: 'var(--accent-amber)' }}>MODIFIED</span>
                <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                  {mod.existing_obligation?.obligation_id}
                </span>
              </div>
              <p className="text-sm mb-2" style={{ color: 'var(--text-primary)' }}>{mod.what_changed}</p>
              <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                <strong>Impact:</strong> {mod.operational_impact}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Circular List */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-transparent"
              style={{ borderTopColor: 'var(--accent-blue)' }} />
          </div>
        ) : circulars.length === 0 ? (
          <div className="glass-card-static p-12 text-center">
            <FileText size={40} className="mx-auto mb-3" style={{ color: 'var(--text-muted)', opacity: 0.3 }} />
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>No circulars ingested yet.</p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
              Go to "Ingest Circular" to upload a SEBI circular PDF.
            </p>
          </div>
        ) : (
          circulars.map((c) => (
            <div key={c.id} className="glass-card p-5 flex items-center justify-between">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl" style={{ background: 'rgba(59,130,246,0.08)' }}>
                  <FileText size={20} style={{ color: 'var(--accent-blue)' }} />
                </div>
                <div>
                  <h4 className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{c.title}</h4>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    {c.circular_number || 'No number'} · Effective: {c.effective_date || 'N/A'}
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      {c.chunk_count || 0} chunks · {c.obligation_count || 0} obligations
                    </span>
                    <span className={`badge ${c.status === 'extracted' ? 'badge-compliant' : 'badge-pending'}`}>
                      {c.status}
                    </span>
                  </div>
                  {c.summary && (
                    <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>{c.summary}</p>
                  )}
                </div>
              </div>

              {c.circular_type === 'amendment' && (
                <button onClick={() => handleDetectChanges(c.id)} disabled={detecting}
                  className="btn-primary flex items-center gap-2" style={{ whiteSpace: 'nowrap' }}>
                  {detecting ? (
                    <div className="animate-spin rounded-full h-4 w-4 border border-transparent" style={{ borderTopColor: 'white' }} />
                  ) : (
                    <Activity size={14} />
                  )}
                  Detect Changes
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
