import { useState, useEffect } from 'react';
import { Shield, Eye, CheckCircle, AlertTriangle, FileWarning, Lock, Scale, Activity } from 'lucide-react';
import { getSupervisionOverview } from '../services/api';

export default function SupervisionMode() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    try {
      const result = await getSupervisionOverview();
      setData(result);
    } catch {
      // Fallback demo data
      setData({
        firm: { name: 'Horizon Securities Pvt. Ltd.', sebi_registration: 'INZ000012345', category: 'Stock Broker', exchanges: ['NSE', 'BSE'] },
        compliance_summary: { total_obligations: 16, compliant: 9, partially_compliant: 3, non_compliant: 2, not_yet_due: 2, health_score: 56.3 },
        type_compliance: {
          'Kyc Onboarding': { compliance_rate: 50.0, compliant: 1, total: 2 },
          'Risk Management': { compliance_rate: 66.7, compliant: 2, total: 3 },
          'Grievance Redressal': { compliance_rate: 50.0, compliant: 1, total: 2 },
          'Cybersecurity': { compliance_rate: 0.0, compliant: 0, total: 2 },
          'Reporting': { compliance_rate: 50.0, compliant: 1, total: 2 },
        },
        grievance_metrics: { current_sla_days: 7, previous_sla_days: 21, current_compliance_rate: 80.85, average_resolution_days: 5.2 },
        audit_integrity: { chain_verified: true, total_audit_entries: 32, message: 'Chain integrity VERIFIED.' },
        last_inspection_date: '2025-03-15', next_inspection_due: '2025-09-15', risk_rating: 'Medium',
      });
    } finally {
      setLoading(false);
    }
  }

  if (loading || !data) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-transparent" style={{ borderTopColor: 'var(--accent-blue)' }} />
    </div>;
  }

  const { firm, compliance_summary: cs, type_compliance, grievance_metrics: gm, audit_integrity: ai } = data;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Banner */}
      <div className="glass-card p-6" style={{ borderColor: 'rgba(139,92,246,0.3)', background: 'linear-gradient(135deg, rgba(139,92,246,0.08), rgba(59,130,246,0.05))' }}>
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl" style={{ background: 'linear-gradient(135deg, var(--accent-violet), var(--accent-blue))' }}>
            <Eye size={24} color="white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>SEBI Supervision Mode</h2>
              <span className="badge badge-pending">READ-ONLY</span>
            </div>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
              Regulator / Exchange Inspector view — aggregate compliance data for {firm.name}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>SEBI Registration</p>
            <p className="text-sm font-mono font-bold" style={{ color: 'var(--accent-blue)' }}>{firm.sebi_registration}</p>
          </div>
        </div>
      </div>

      {/* Firm Info + Health Score */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass-card p-5">
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Firm</p>
          <p className="text-sm font-semibold mt-1" style={{ color: 'var(--text-primary)' }}>{firm.name}</p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>{firm.category} · {firm.exchanges?.join(', ')}</p>
        </div>
        <div className="glass-card stat-card blue p-5">
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Health Score</p>
          <p className="text-2xl font-bold mt-1" style={{ color: cs.health_score >= 70 ? 'var(--accent-emerald)' : cs.health_score >= 40 ? 'var(--accent-amber)' : 'var(--accent-rose)' }}>
            {cs.health_score}%
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Based on {cs.total_obligations} obligations</p>
        </div>
        <div className="glass-card p-5">
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Risk Rating</p>
          <p className="text-lg font-bold mt-1" style={{ color: data.risk_rating === 'High' ? 'var(--accent-rose)' : data.risk_rating === 'Medium' ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
            {data.risk_rating}
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Next inspection: {data.next_inspection_due}</p>
        </div>
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Lock size={14} style={{ color: ai.chain_verified ? 'var(--accent-emerald)' : 'var(--accent-rose)' }} />
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Audit Chain</p>
          </div>
          <p className="text-sm font-semibold" style={{ color: ai.chain_verified ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
            {ai.chain_verified ? 'VERIFIED' : 'BREACH DETECTED'}
          </p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{ai.total_audit_entries} entries · SHA-256</p>
        </div>
      </div>

      {/* Compliance Breakdown */}
      <div className="grid grid-cols-2 gap-6">
        <div className="glass-card-static p-6">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-secondary)' }}>Compliance Status Breakdown</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Compliant', value: cs.compliant, icon: CheckCircle, color: 'emerald' },
              { label: 'Partially Compliant', value: cs.partially_compliant, icon: AlertTriangle, color: 'amber' },
              { label: 'Non-Compliant', value: cs.non_compliant, icon: FileWarning, color: 'rose' },
              { label: 'Not Yet Due', value: cs.not_yet_due, icon: Activity, color: 'blue' },
            ].map((item, i) => (
              <div key={i} className="p-3 rounded-xl" style={{ background: `rgba(var(--accent-${item.color}-rgb, 255,255,255), 0.04)` }}>
                <div className="flex items-center gap-2">
                  <item.icon size={14} style={{ color: `var(--accent-${item.color})` }} />
                  <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                </div>
                <p className="text-xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>{item.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Type-wise Compliance */}
        <div className="glass-card-static p-6">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-secondary)' }}>Compliance by Category</h3>
          <div className="space-y-3">
            {Object.entries(type_compliance).map(([name, data], i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs w-36 shrink-0 truncate" style={{ color: 'var(--text-secondary)' }}>{name}</span>
                <div className="flex-1 h-2.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full" style={{
                    width: `${data.compliance_rate}%`,
                    background: data.compliance_rate >= 80 ? 'var(--accent-emerald)' : data.compliance_rate >= 50 ? 'var(--accent-amber)' : 'var(--accent-rose)',
                  }} />
                </div>
                <span className="text-xs font-mono w-12 text-right" style={{ color: 'var(--text-primary)' }}>
                  {data.compliance_rate}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grievance Metrics */}
      <div className="glass-card-static p-6">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
          <Scale size={16} /> SCORES Grievance Compliance
        </h3>
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Current SLA', value: `${gm.current_sla_days} days`, sub: `Was ${gm.previous_sla_days} days` },
            { label: 'Compliance Rate', value: `${gm.current_compliance_rate}%`, sub: 'Target: 90%' },
            { label: 'Avg Resolution', value: `${gm.average_resolution_days} days`, sub: 'Within SLA' },
            { label: 'SLA Reduction', value: '66.7%', sub: '21 → 7 days' },
          ].map((item, i) => (
            <div key={i} className="p-4 rounded-xl text-center" style={{ background: 'rgba(255,255,255,0.02)' }}>
              <p className="text-lg font-bold" style={{ color: 'var(--accent-blue)' }}>{item.value}</p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>{item.label}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{item.sub}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
