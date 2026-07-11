import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ChevronDown, FileText, ArrowUpDown } from 'lucide-react';
import { getObligations } from '../services/api';

const TYPE_LABELS = {
  kyc_onboarding: 'KYC / Onboarding',
  reporting: 'Reporting',
  disclosure: 'Disclosure',
  systems_process: 'Systems / Process',
  timeline: 'Timeline',
  risk_management: 'Risk Management',
  grievance_redressal: 'Grievance Redressal',
  cybersecurity: 'Cybersecurity',
  advertising: 'Advertising',
  record_keeping: 'Record-Keeping',
};

const STATUS_BADGE = {
  compliant: 'badge-compliant',
  partially_compliant: 'badge-partial',
  non_compliant: 'badge-non-compliant',
  not_yet_due: 'badge-not-due',
};

export default function ObligationExplorer() {
  const navigate = useNavigate();
  const [obligations, setObligations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => { loadObligations(); }, [typeFilter, statusFilter, search]);

  async function loadObligations() {
    setLoading(true);
    try {
      const data = await getObligations({
        obligation_type: typeFilter,
        search: search || undefined,
      });
      let filtered = data;
      if (statusFilter) {
        filtered = data.filter(o => o.current_compliance_status === statusFilter);
      }
      setObligations(filtered);
    } catch {
      // Fallback demo data
      setObligations(DEMO_OBLIGATIONS);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-64">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search obligations..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input-field pl-11"
          />
        </div>

        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)} className="input-field w-48">
          <option value="">All Types</option>
          {Object.entries(TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>

        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="input-field w-48">
          <option value="">All Statuses</option>
          <option value="compliant">Compliant</option>
          <option value="partially_compliant">Partially Compliant</option>
          <option value="non_compliant">Non-Compliant</option>
          <option value="not_yet_due">Not Yet Due</option>
        </select>

        <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
          {obligations.length} obligation{obligations.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Table */}
      <div className="glass-card-static overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-transparent"
              style={{ borderTopColor: 'var(--accent-blue)' }} />
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Summary</th>
                <th>Type</th>
                <th>Process Area</th>
                <th>Frequency</th>
                <th>Status</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {obligations.map((obl) => (
                <tr key={obl.id || obl.obligation_id} onClick={() => navigate(`/obligations/${obl.id}`)}>
                  <td>
                    <span className="font-mono text-xs" style={{ color: 'var(--accent-blue)' }}>
                      {obl.obligation_id}
                    </span>
                  </td>
                  <td style={{ maxWidth: '300px' }}>
                    <p className="truncate text-sm">{obl.obligation_text_summary}</p>
                  </td>
                  <td>
                    <span className="badge badge-pending" style={{ fontSize: '0.7rem' }}>
                      {TYPE_LABELS[obl.obligation_type] || obl.obligation_type}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                      {(obl.process_areas || [])[0] || '—'}
                    </span>
                  </td>
                  <td className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    {obl.frequency}
                  </td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[obl.current_compliance_status] || 'badge-not-due'}`}>
                      {(obl.current_compliance_status || 'unknown').replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-12 h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
                        <div className="h-full rounded-full" style={{
                          width: `${(obl.confidence_score || 0) * 100}%`,
                          background: (obl.confidence_score || 0) > 0.8 ? 'var(--accent-emerald)' : 'var(--accent-amber)',
                        }} />
                      </div>
                      <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                        {Math.round((obl.confidence_score || 0) * 100)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// Fallback demo data
const DEMO_OBLIGATIONS = [
  { id: 1, obligation_id: 'OBL-KYC-001', obligation_text_summary: 'Complete KYC verification for all new clients before allowing trading', obligation_type: 'kyc_onboarding', process_areas: ['Client Onboarding (KYC/AML)'], frequency: 'event-based', current_compliance_status: 'compliant', confidence_score: 0.95 },
  { id: 2, obligation_id: 'OBL-KYC-002', obligation_text_summary: 'Perform periodic KYC re-verification for existing clients', obligation_type: 'kyc_onboarding', process_areas: ['Client Onboarding (KYC/AML)'], frequency: 'annual', current_compliance_status: 'partially_compliant', confidence_score: 0.88 },
  { id: 3, obligation_id: 'OBL-MARGIN-001', obligation_text_summary: 'Collect upfront margins from clients before trade execution', obligation_type: 'risk_management', process_areas: ['Margin & Risk Management'], frequency: 'daily', current_compliance_status: 'compliant', confidence_score: 0.92 },
  { id: 5, obligation_id: 'OBL-GRIEVANCE-001', obligation_text_summary: 'Resolve all investor grievances within 21 calendar days from receipt', obligation_type: 'grievance_redressal', process_areas: ['Investor Grievance Redressal'], frequency: 'event-based', current_compliance_status: 'compliant', confidence_score: 0.93 },
  { id: 7, obligation_id: 'OBL-CYBER-001', obligation_text_summary: 'Implement comprehensive cybersecurity framework including firewalls and IDS', obligation_type: 'cybersecurity', process_areas: ['Cybersecurity & IT Infrastructure'], frequency: 'one-time', current_compliance_status: 'non_compliant', confidence_score: 0.87 },
  { id: 10, obligation_id: 'OBL-REPORT-002', obligation_text_summary: 'File quarterly compliance report with SEBI', obligation_type: 'reporting', process_areas: ['Reporting to Exchange/SEBI'], frequency: 'quarterly', current_compliance_status: 'non_compliant', confidence_score: 0.89 },
];
