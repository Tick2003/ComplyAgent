import { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import {
  Shield, AlertTriangle, CheckCircle2, Clock, FileWarning,
  TrendingUp, ArrowUpRight, Activity
} from 'lucide-react';
import { getDashboardStats } from '../services/api';

const STATUS_COLORS = {
  compliant: '#10b981',
  partially_compliant: '#f59e0b',
  non_compliant: '#f43f5e',
  not_yet_due: '#64748b',
};

const RADIAN = Math.PI / 180;

function HealthScoreRing({ score }) {
  const circumference = 2 * Math.PI * 56;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#f43f5e';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="140" height="140" className="health-score-ring">
        <circle cx="70" cy="70" r="56" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
        <circle
          cx="70" cy="70" r="56" fill="none"
          stroke={color} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="progress"
          style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold" style={{ color }}>{Math.round(score)}</span>
        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>/ 100</span>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color, subtext }) {
  return (
    <div className={`glass-card stat-card ${color} p-5`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium mb-1" style={{ color: 'var(--text-secondary)' }}>{label}</p>
          <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{value}</p>
          {subtext && <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{subtext}</p>}
        </div>
        <div className="p-2 rounded-lg" style={{ background: `var(--accent-${color}-glow, rgba(255,255,255,0.05))` }}>
          <Icon size={20} style={{ color: `var(--accent-${color})` }} />
        </div>
      </div>
    </div>
  );
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card-static p-3 text-sm" style={{ minWidth: '120px' }}>
        <p style={{ color: payload[0].payload.fill || 'var(--text-primary)' }} className="font-semibold">
          {payload[0].name}: {payload[0].value}
        </p>
      </div>
    );
  }
  return null;
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      // Use fallback demo data if API is unavailable
      setStats({
        health_score: 71.9,
        total_obligations: 16,
        compliant: 9,
        partially_compliant: 3,
        non_compliant: 2,
        not_yet_due: 2,
        pending_review: 0,
        overdue_count: 2,
        missing_evidence_count: 4,
        obligations_by_type: {
          kyc_onboarding: 2, risk_management: 3, grievance_redressal: 2,
          cybersecurity: 2, reporting: 2, record_keeping: 1,
          advertising: 1, systems_process: 2, disclosure: 1,
        },
        obligations_by_process: {
          'Client Onboarding (KYC/AML)': 2, 'Margin & Risk Management': 3,
          'Investor Grievance Redressal': 2, 'Cybersecurity & IT Infrastructure': 2,
          'Reporting to Exchange/SEBI': 2, 'Record-Keeping & Documentation': 1,
          'Advertising & Marketing': 1, 'Settlement & Accounts': 1,
          'Audit & Supervision': 1, 'Trading & Order Management': 1,
        },
        upcoming_deadlines: [],
        recent_changes: [],
      });
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-transparent"
          style={{ borderTopColor: 'var(--accent-blue)' }} />
      </div>
    );
  }

  const pieData = [
    { name: 'Compliant', value: stats.compliant, fill: STATUS_COLORS.compliant },
    { name: 'Partially Compliant', value: stats.partially_compliant, fill: STATUS_COLORS.partially_compliant },
    { name: 'Non-Compliant', value: stats.non_compliant, fill: STATUS_COLORS.non_compliant },
    { name: 'Not Yet Due', value: stats.not_yet_due, fill: STATUS_COLORS.not_yet_due },
  ].filter(d => d.value > 0);

  const typeData = Object.entries(stats.obligations_by_type || {}).map(([name, count]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    count,
    fill: '#3b82f6',
  }));

  const processData = Object.entries(stats.obligations_by_process || {}).map(([name, count]) => ({
    name: name.length > 25 ? name.slice(0, 25) + '…' : name,
    count,
  }));

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Health Score + Stats Row */}
      <div className="grid grid-cols-12 gap-6">
        {/* Health Score */}
        <div className="col-span-3 glass-card p-6 flex flex-col items-center justify-center text-center">
          <p className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: 'var(--text-secondary)' }}>
            Compliance Health Score
          </p>
          <HealthScoreRing score={stats.health_score} />
          <p className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
            Based on {stats.total_obligations} active obligations
          </p>
        </div>

        {/* Stat Cards */}
        <div className="col-span-9 grid grid-cols-3 gap-4 stagger-children">
          <StatCard icon={CheckCircle2} label="Compliant" value={stats.compliant} color="emerald"
            subtext={`${Math.round((stats.compliant / Math.max(stats.total_obligations, 1)) * 100)}% of total`} />
          <StatCard icon={AlertTriangle} label="Partially Compliant" value={stats.partially_compliant} color="amber"
            subtext="Needs attention" />
          <StatCard icon={FileWarning} label="Non-Compliant" value={stats.non_compliant} color="rose"
            subtext="Immediate action required" />
          <StatCard icon={Clock} label="Not Yet Due" value={stats.not_yet_due} color="blue"
            subtext="Upcoming obligations" />
          <StatCard icon={Shield} label="Pending Review" value={stats.pending_review} color="violet"
            subtext="Awaiting human approval" />
          <StatCard icon={Activity} label="Total Obligations" value={stats.total_obligations} color="blue"
            subtext={`${stats.missing_evidence_count} missing evidence`} />
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6">
        {/* Status Distribution Pie */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-secondary)' }}>
            Obligation Status Distribution
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={95}
                paddingAngle={4} dataKey="value" animationDuration={1200}>
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} stroke="transparent" />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: '12px', color: 'var(--text-secondary)' }}
                formatter={(value) => <span style={{ color: 'var(--text-secondary)' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Obligations by Type Bar Chart */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-secondary)' }}>
            Obligations by Type
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={typeData} layout="vertical" margin={{ left: 20, right: 20 }}>
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" width={120}
                tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={18}>
                {typeData.map((_, i) => (
                  <Cell key={i} fill={`hsl(${220 + i * 15}, 70%, 55%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Process Coverage + Recent Changes */}
      <div className="grid grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-secondary)' }}>
            Obligations by Process Area
          </h3>
          <div className="space-y-3">
            {processData.map((proc, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-xs w-32 shrink-0 truncate" style={{ color: 'var(--text-secondary)' }}>
                  {proc.name}
                </span>
                <div className="flex-1 h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full transition-all duration-1000"
                    style={{
                      width: `${(proc.count / Math.max(...processData.map(p => p.count))) * 100}%`,
                      background: `hsl(${200 + i * 18}, 70%, 55%)`,
                      animationDelay: `${i * 0.1}s`,
                    }} />
                </div>
                <span className="text-sm font-semibold w-6 text-right" style={{ color: 'var(--text-primary)' }}>
                  {proc.count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
            <Activity size={16} /> Recent Activity
          </h3>
          <div className="space-y-3">
            {(stats.recent_changes || []).length > 0 ? (
              stats.recent_changes.slice(0, 6).map((change, i) => (
                <div key={i} className="flex items-start gap-3 p-2 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)' }}>
                  <div className="w-2 h-2 mt-1.5 rounded-full shrink-0" style={{ background: 'var(--accent-blue)' }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                      {change.action} — {change.entity_type} {change.entity_id}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                      {change.user} · {new Date(change.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Activity size={32} style={{ color: 'var(--text-muted)' }} className="mx-auto mb-2 opacity-30" />
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Activity will appear here once the backend is running
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
