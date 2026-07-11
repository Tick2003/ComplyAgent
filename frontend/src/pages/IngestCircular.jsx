import { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadCircular } from '../services/api';

export default function IngestCircular() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [circularNumber, setCircularNumber] = useState('');
  const [effectiveDate, setEffectiveDate] = useState('');
  const [circularType, setCircularType] = useState('amendment');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file || !title) return;

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('circular_number', circularNumber);
    formData.append('effective_date', effectiveDate);
    formData.append('circular_type', circularType);

    try {
      const data = await uploadCircular(formData);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div>
        <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Ingest SEBI Circular</h2>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
          Upload a SEBI circular PDF to parse, extract obligations, and map to processes
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card-static p-6 space-y-5">
        {/* File Upload */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider mb-2 block" style={{ color: 'var(--text-secondary)' }}>
            Circular PDF
          </label>
          <div className="border-2 border-dashed rounded-xl p-8 text-center transition-all"
            style={{ borderColor: file ? 'var(--accent-emerald)' : 'var(--border-glass)', background: 'rgba(255,255,255,0.02)' }}>
            <input type="file" accept=".pdf" onChange={e => setFile(e.target.files[0])} className="hidden" id="pdf-upload" />
            <label htmlFor="pdf-upload" className="cursor-pointer">
              {file ? (
                <div className="flex items-center justify-center gap-2">
                  <FileText size={20} style={{ color: 'var(--accent-emerald)' }} />
                  <span className="text-sm font-medium" style={{ color: 'var(--accent-emerald)' }}>{file.name}</span>
                </div>
              ) : (
                <>
                  <Upload size={28} className="mx-auto mb-2" style={{ color: 'var(--text-muted)' }} />
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Click to upload PDF</p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>or drag and drop</p>
                </>
              )}
            </label>
          </div>
        </div>

        {/* Title */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider mb-2 block" style={{ color: 'var(--text-secondary)' }}>
            Circular Title
          </label>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)}
            placeholder="e.g., Amendment to Investor Grievance Redressal SLA"
            className="input-field" required />
        </div>

        {/* Number + Date */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider mb-2 block" style={{ color: 'var(--text-secondary)' }}>
              Circular Number
            </label>
            <input type="text" value={circularNumber} onChange={e => setCircularNumber(e.target.value)}
              placeholder="SEBI/HO/..." className="input-field" />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider mb-2 block" style={{ color: 'var(--text-secondary)' }}>
              Effective Date
            </label>
            <input type="date" value={effectiveDate} onChange={e => setEffectiveDate(e.target.value)}
              className="input-field" />
          </div>
        </div>

        {/* Type */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider mb-2 block" style={{ color: 'var(--text-secondary)' }}>
            Circular Type
          </label>
          <select value={circularType} onChange={e => setCircularType(e.target.value)} className="input-field">
            <option value="master_circular">Master Circular</option>
            <option value="amendment">Amendment Circular</option>
          </select>
        </div>

        <button type="submit" disabled={uploading || !file || !title}
          className="btn-primary w-full flex items-center justify-center gap-2"
          style={{ opacity: (uploading || !file || !title) ? 0.5 : 1 }}>
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border border-transparent" style={{ borderTopColor: 'white' }} />
              Processing...
            </>
          ) : (
            <>
              <Upload size={16} /> Upload & Process
            </>
          )}
        </button>
      </form>

      {/* Result */}
      {result && (
        <div className="glass-card p-5" style={{ borderColor: 'rgba(16,185,129,0.2)' }}>
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={18} style={{ color: 'var(--accent-emerald)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--accent-emerald)' }}>Successfully Processed</span>
          </div>
          <p className="text-sm" style={{ color: 'var(--text-primary)' }}>{result.title}</p>
          <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
            {result.chunk_count} chunks parsed · {result.obligation_count} obligations extracted · Status: {result.status}
          </p>
          {result.summary && (
            <p className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>{result.summary}</p>
          )}
        </div>
      )}

      {error && (
        <div className="glass-card p-5" style={{ borderColor: 'rgba(244,63,94,0.2)' }}>
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle size={18} style={{ color: 'var(--accent-rose)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--accent-rose)' }}>Processing Failed</span>
          </div>
          <p className="text-sm" style={{ color: 'var(--text-primary)' }}>{error}</p>
        </div>
      )}
    </div>
  );
}
