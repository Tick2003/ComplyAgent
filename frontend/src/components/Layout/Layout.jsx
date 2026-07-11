import { useState, useEffect } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, FileText, Shield, AlertTriangle,
  Upload, MessageSquare, Bell, ChevronRight, Scale, Activity,
  TrendingUp, Eye, ChevronDown
} from 'lucide-react';
import { getAlerts } from '../../services/api';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/impact', icon: TrendingUp, label: 'Impact Metrics' },
  { path: '/obligations', icon: FileText, label: 'Obligations' },
  { path: '/review', icon: Shield, label: 'Review Queue' },
  { path: '/gaps', icon: AlertTriangle, label: 'Gap Analysis' },
  { path: '/changes', icon: Activity, label: 'Change Feed' },
  { path: '/ingest', icon: Upload, label: 'Ingest Circular' },
  { path: '/chat', icon: MessageSquare, label: 'Ask Agent' },
  { path: '/supervisor', icon: Eye, label: 'Supervision Mode' },
];

export default function Layout() {
  const location = useLocation();
  const [alertCount, setAlertCount] = useState(0);
  const [showAlerts, setShowAlerts] = useState(false);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    loadAlerts();
  }, []);

  async function loadAlerts() {
    try {
      const data = await getAlerts();
      setAlerts(data.alerts || []);
      setAlertCount(data.total || 0);
    } catch {
      setAlertCount(3); // Fallback
      setAlerts([
        { id: 'ALERT-1', severity: 'critical', title: 'Non-Compliant: OBL-CYBER-001', message: 'Cybersecurity framework not implemented', type: 'non_compliant' },
        { id: 'ALERT-2', severity: 'high', title: 'SCORES SLA Below Target', message: 'Current SLA compliance: 80.85% (target: 90%)', type: 'sla_breach' },
        { id: 'ALERT-3', severity: 'warning', title: 'Missing Evidence: OBL-REPORT-002', message: 'No evidence for quarterly report', type: 'missing_evidence' },
      ]);
    }
  }

  const severityColor = { critical: 'var(--accent-rose)', high: 'var(--accent-amber)', warning: 'var(--accent-amber)' };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 bottom-0 w-64 glass-card-static"
        style={{ borderRadius: 0, borderRight: '1px solid var(--border-glass)' }}>
        {/* Logo */}
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-violet))' }}>
            <Scale size={22} color="white" />
          </div>
          <div>
            <h1 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>ComplyAgent</h1>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>SEBI RegTech Engine</p>
          </div>
        </div>

        {/* Firm Name */}
        <div className="mx-4 mb-4 p-3 rounded-xl" style={{ background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.1)' }}>
          <p className="text-xs font-semibold" style={{ color: 'var(--accent-blue)' }}>FIRM</p>
          <p className="text-sm font-medium mt-0.5" style={{ color: 'var(--text-primary)' }}>Horizon Securities Pvt. Ltd.</p>
        </div>

        {/* Navigation */}
        <nav className="px-3 space-y-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 260px)' }}>
          {navItems.map(({ path, icon: Icon, label }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{label}</span>
              {location.pathname === path && (
                <ChevronRight size={14} className="ml-auto" style={{ color: 'var(--accent-blue)' }} />
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4">
          <div className="p-3 rounded-xl" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)' }}>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                style={{ background: 'linear-gradient(135deg, var(--accent-emerald), #059669)', color: 'white' }}>
                PS
              </div>
              <div>
                <p className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>Priya Sharma</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Compliance Officer</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1 min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-10 px-8 py-4 flex items-center justify-between"
          style={{ background: 'rgba(5, 10, 24, 0.8)', backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--border-glass)' }}>
          <div>
            <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              {navItems.find(n => n.path === location.pathname)?.label || 'ComplyAgent'}
            </h2>
            <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
              Intermediary Category: Stockbroker · Corpus: SEBI Master Circular 2025
            </p>
          </div>
          <div className="flex items-center gap-3 relative">
            <button onClick={() => setShowAlerts(!showAlerts)}
              className="btn-secondary flex items-center gap-2 text-sm relative">
              <Bell size={16} />
              {alertCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{ background: 'var(--accent-rose)', color: 'white', fontSize: '0.65rem' }}>
                  {alertCount}
                </span>
              )}
            </button>

            {/* Alert Dropdown */}
            {showAlerts && (
              <div className="absolute top-12 right-0 w-96 glass-card-static p-0 overflow-hidden z-50"
                style={{ boxShadow: '0 20px 60px rgba(0,0,0,0.5)' }}>
                <div className="p-4" style={{ borderBottom: '1px solid var(--border-glass)' }}>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Alerts</span>
                    <span className="badge badge-non-compliant">{alertCount} active</span>
                  </div>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {alerts.map((alert, i) => (
                    <div key={i} className="p-3 flex items-start gap-3 transition-all"
                      style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                      <div className="w-2 h-2 mt-1.5 rounded-full shrink-0"
                        style={{ background: severityColor[alert.severity] }} />
                      <div className="min-w-0">
                        <p className="text-xs font-medium truncate" style={{ color: 'var(--text-primary)' }}>{alert.title}</p>
                        <p className="text-xs mt-0.5 truncate" style={{ color: 'var(--text-muted)' }}>{alert.message}</p>
                      </div>
                      <span className={`badge shrink-0 ${alert.severity === 'critical' ? 'badge-non-compliant' : 'badge-partial'}`}
                        style={{ fontSize: '0.6rem', padding: '2px 6px' }}>
                        {alert.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Page Content */}
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
