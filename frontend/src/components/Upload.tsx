import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { uploadFile, validateFile } from '../services/api';
import { ProcessingProgress } from '../types';

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [validation, setValidation] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState<ProcessingProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setValidation(null);
    setError(null);
    setIsValidating(true);

    try {
      const result = await validateFile(selectedFile);
      setValidation(result);
    } catch (e: any) {
      setError(e.message || 'Failed to validate file');
    } finally {
      setIsValidating(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setProgress(null);
    setError(null);

    try {
      await uploadFile(file, (data) => {
        setProgress(data);

        if (data.stage === 'complete') {
          setTimeout(() => {
            navigate(`/batches/${data.batch_id}`);
          }, 1500);
        }

        if (data.stage === 'error') {
          setError(data.message || 'Processing failed');
          setIsUploading(false);
        }
      });
    } catch (e: any) {
      setError(e.message || 'Upload failed');
      setIsUploading(false);
    }
  };

  const getProgressPercentage = () => {
    if (!progress) return 0;
    if (progress.percentage) return progress.percentage;
    if (progress.stage === 'complete') return 100;
    if (progress.stage === 'parsing') return 5;
    if (progress.stage === 'parsed') return 10;
    if (progress.stage === 'creating_records') return 15;
    if (progress.stage === 'generating_embeddings') return 25;
    if (progress.stage === 'embeddings_complete') return 40;
    if (progress.stage === 'matching') return 45;
    return 0;
  };

  return (
    <div>
      <div className="card">
        <h2 className="card-title">Upload Usage File</h2>
        <p style={{ color: 'var(--gray-600)', marginBottom: '1.5rem' }}>
          Upload a TXT or CSV file with pipe-delimited usage data to match against the works database.
        </p>

        {!isUploading && (
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''}`}
          >
            <input {...getInputProps()} />
            <UploadIcon className="dropzone-icon" />
            <p className="dropzone-text">
              {isDragActive
                ? 'Drop the file here...'
                : 'Drag & drop a file here, or click to select'}
            </p>
            <p className="dropzone-hint">Supports TXT and CSV files (pipe-delimited)</p>
          </div>
        )}

        {isValidating && (
          <div className="loading">
            <div className="spinner" />
          </div>
        )}

        {file && validation && !isUploading && (
          <div style={{ marginTop: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <FileText size={24} style={{ color: 'var(--primary)' }} />
              <div>
                <div style={{ fontWeight: 500 }}>{file.name}</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
                  {validation.total_records} records found
                </div>
              </div>
            </div>

            {validation.sample_records && validation.sample_records.length > 0 && (
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>
                  Sample records:
                </div>
                <div className="table-container">
                  <table style={{ fontSize: '0.875rem' }}>
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Work Title</th>
                        <th>Songwriter</th>
                        <th>Recording Title</th>
                        <th>Artist</th>
                      </tr>
                    </thead>
                    <tbody>
                      {validation.sample_records.map((record: any, idx: number) => (
                        <tr key={idx}>
                          <td>{record.row_number}</td>
                          <td>{record.work_title || '-'}</td>
                          <td>{record.songwriter || '-'}</td>
                          <td>{record.recording_title || '-'}</td>
                          <td>{record.recording_artist || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <button className="btn btn-primary" onClick={handleUpload}>
              <UploadIcon size={18} />
              Start Processing
            </button>
          </div>
        )}

        {isUploading && progress && (
          <div style={{ marginTop: '1.5rem' }}>
            <div className="progress-container">
              <div style={{ marginBottom: '0.5rem', fontWeight: 500 }}>
                {progress.stage === 'complete' ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)' }}>
                    <CheckCircle size={20} /> Processing Complete
                  </span>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Loader size={20} className="spinner" style={{ animation: 'spin 1s linear infinite' }} />
                    {progress.message || 'Processing...'}
                  </span>
                )}
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${getProgressPercentage()}%` }}
                />
              </div>
              {progress.total_records && (
                <div className="progress-stats">
                  <span>
                    {progress.processed || 0} / {progress.total_records} records
                  </span>
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    {progress.matched !== undefined && (
                      <span className="progress-stat">
                        <span className="stat-dot matched" />
                        {progress.matched} matched
                      </span>
                    )}
                    {progress.flagged !== undefined && (
                      <span className="progress-stat">
                        <span className="stat-dot flagged" />
                        {progress.flagged} flagged
                      </span>
                    )}
                    {progress.unmatched !== undefined && (
                      <span className="progress-stat">
                        <span className="stat-dot unmatched" />
                        {progress.unmatched} unmatched
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {error && (
          <div style={{
            marginTop: '1rem',
            padding: '1rem',
            background: '#fee2e2',
            borderRadius: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: '#991b1b'
          }}>
            <AlertCircle size={20} />
            {error}
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">Expected File Format</h3>
        <p style={{ color: 'var(--gray-600)', marginBottom: '1rem' }}>
          Files should be pipe-delimited (|) with the following columns:
        </p>
        <ul style={{ marginLeft: '1.5rem', color: 'var(--gray-600)' }}>
          <li><strong>Recording Title</strong> - The recorded song title</li>
          <li><strong>Recording Artist</strong> - The performing artist</li>
          <li><strong>Work Title</strong> - The composition title</li>
          <li><strong>Songwriter</strong> - The composer/lyricist</li>
        </ul>
        <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--gray-50)', borderRadius: '0.5rem', fontFamily: 'monospace', fontSize: '0.875rem' }}>
          Recording Title|Recording Artist|Work Title|Songwriter<br />
          Yesterday|The Beatles|Yesterday|McCartney, Paul
        </div>
      </div>
    </div>
  );
}
