/**
 * API client for ComplyAgent backend.
 */
const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };

  // Remove Content-Type for FormData
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }
  return response.json();
}

// ── Dashboard ────────────────────────────────────────────────────────
export const getDashboardStats = () => request('/dashboard/stats');

// ── Circulars / Ingestion ────────────────────────────────────────────
export const getCirculars = () => request('/ingest/circulars');
export const getCircular = (id) => request(`/ingest/circulars/${id}`);
export const getCircularChunks = (id) => request(`/ingest/circulars/${id}/chunks`);
export const uploadCircular = (formData) =>
  request('/ingest/upload', { method: 'POST', body: formData });

// ── Obligations ──────────────────────────────────────────────────────
export const getObligations = (params = {}) => {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v))
  ).toString();
  return request(`/obligations/${qs ? `?${qs}` : ''}`);
};
export const getObligation = (id) => request(`/obligations/${id}`);
export const reviewObligation = (id, data) =>
  request(`/obligations/${id}/review`, { method: 'PUT', body: JSON.stringify(data) });
export const updateObligation = (id, data) =>
  request(`/obligations/${id}`, { method: 'PUT', body: JSON.stringify(data) });
export const getObligationProcesses = (id) => request(`/obligations/${id}/processes`);
export const addProcessMapping = (id, data) =>
  request(`/obligations/${id}/processes`, { method: 'POST', body: JSON.stringify(data) });
export const getObligationAuditTrail = (id) => request(`/obligations/${id}/audit-trail`);

// ── Evidence ─────────────────────────────────────────────────────────
export const getEvidence = (obligationId) => request(`/evidence/${obligationId}`);
export const attachEvidence = (obligationId, data) =>
  request(`/evidence/${obligationId}/attach`, { method: 'POST', body: JSON.stringify(data) });
export const setComplianceStatus = (obligationId, data) =>
  request(`/evidence/${obligationId}/status`, { method: 'POST', body: JSON.stringify(data) });
export const getStatusHistory = (obligationId) =>
  request(`/evidence/${obligationId}/status-history`);

// ── Agents ───────────────────────────────────────────────────────────
export const queryAgent = (question) =>
  request('/agents/query', { method: 'POST', body: JSON.stringify({ question }) });
export const runGapAnalysis = () =>
  request('/agents/gap-analysis', { method: 'POST' });
export const runChangeDetection = (circularId) =>
  request(`/agents/change-detection/${circularId}`, { method: 'POST' });

// ── Platform (Enhancement APIs) ──────────────────────────────────────
// Hash Chain / Blockchain Audit
export const verifyAuditChain = () => request('/platform/audit/verify-integrity');
export const getChainStats = () => request('/platform/audit/chain-stats');

// Impact Metrics
export const getImpactMetrics = () => request('/platform/metrics/impact');

// SCORES
export const getScoresComplaints = () => request('/platform/scores/complaints');
export const getScoresSLA = () => request('/platform/scores/sla-metrics');

// NLP Pipeline
export const analyzeObligationNLP = (id) => request(`/platform/nlp/analyze-obligation/${id}`);

// DPI
export const getDPICapabilities = () => request('/platform/dpi/capabilities');

// Profiles
export const getProfiles = () => request('/platform/profiles');
export const getProfile = (key) => request(`/platform/profiles/${key}`);

// Regulatory Coverage
export const getRegulatoryCoverage = () => request('/platform/regulatory-coverage');

// Supervision
export const getSupervisionOverview = () => request('/platform/supervision/overview');

// Alerts
export const getAlerts = () => request('/platform/alerts');

