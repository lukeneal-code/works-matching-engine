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
        <h2 className="card-title" style={{ marginBottom: '8px' }}>Upload Usage File</h2>
        <p style={{ color: 'var(--notion-text-secondary)', marginBottom: '24px', fontSize: '14px' }}>
          Upload a pipe-delimited file to match against the works database.
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
            <p className="dropzone-hint">Supports .txt and .csv files</p>
          </div>
        )}

        {isValidating && (
          <div className="loading">
            <div className="spinner" />
          </div>
        )}

        {file && validation && !isUploading && (
          <div style={{ marginTop: '24px' }}>
            <div className="file-info">
              <FileText size={20} className="file-info-icon" />
              <div>
                <div className="file-info-name">{file.name}</div>
                <div className="file-info-meta">{validation.total_records} records found</div>
              </div>
            </div>

            {validation.sample_records && validation.sample_records.length > 0 && (
              <div style={{ marginTop: '24px' }}>
                <div style={{ fontSize: '12px', fontWeight: '500', marginBottom: '8px', color: 'var(--notion-text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Preview
                </div>
                <div className="table-container">
                  <table>
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
                          <td style={{ color: 'var(--notion-text-secondary)' }}>{record.row_number}</td>
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

            <div style={{ marginTop: '24px' }}>
              <button className="btn btn-primary" onClick={handleUpload}>
                <UploadIcon size={16} />
                Start Processing
              </button>
            </div>
          </div>
        )}

        {isUploading && progress && (
          <div style={{ marginTop: '24px' }}>
            <div className="progress-container">
              <div style={{ marginBottom: '12px', fontWeight: '500', fontSize: '14px' }}>
                {progress.stage === 'complete' ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--notion-green)' }}>
                    <CheckCircle size={16} /> Processing Complete
                  </span>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--notion-text-secondary)' }}>
                    <Loader size={16} style={{ animation: 'spin 0.6s linear infinite' }} />
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
                  <div style={{ display: 'flex', gap: '16px' }}>
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
            marginTop: '16px',
            padding: '12px',
            background: 'var(--notion-red-bg)',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--notion-red)',
            fontSize: '14px'
          }}>
            <AlertCircle size={16} />
            {error}
          </div>
        )}
      </div>

      <div className="format-guide">
        <h3>Expected File Format</h3>
        <p>Files should be pipe-delimited (|) with the following columns:</p>
        <ul>
          <li><strong>Recording Title</strong> - The recorded song title</li>
          <li><strong>Recording Artist</strong> - The performing artist</li>
          <li><strong>Work Title</strong> - The composition title</li>
          <li><strong>Songwriter</strong> - The composer/lyricist</li>
        </ul>
        <div className="code-block">
          Recording Title|Recording Artist|Work Title|Songwriter<br />
          Yesterday|The Beatles|Yesterday|McCartney, Paul
        </div>
      </div>
    </div>
  );
}
