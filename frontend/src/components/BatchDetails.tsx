import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  Download,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileQuestion,
  Bot
} from 'lucide-react';
import {
  getBatch,
  getMatches,
  getUnmatched,
  reviewMatch,
  exportUnmatched,
  exportFlagged
} from '../services/api';
import { Match, UsageRecord } from '../types';

type TabType = 'matched' | 'flagged' | 'unmatched';

export default function BatchDetails() {
  const { batchId } = useParams<{ batchId: string }>();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('matched');
  const [page, setPage] = useState(1);

  const { data: batch, isLoading: batchLoading } = useQuery({
    queryKey: ['batch', batchId],
    queryFn: () => getBatch(batchId!),
    enabled: !!batchId,
  });

  const { data: matches, isLoading: matchesLoading } = useQuery({
    queryKey: ['matches', batchId, activeTab, page],
    queryFn: () => {
      if (activeTab === 'matched') {
        return getMatches(batchId!, page, 20, undefined, 0.85);
      } else if (activeTab === 'flagged') {
        return getMatches(batchId!, page, 20, undefined, 0.5, false);
      }
      return Promise.resolve({ matches: [], total: 0, page: 1, page_size: 20 });
    },
    enabled: !!batchId && activeTab !== 'unmatched',
  });

  const { data: unmatched, isLoading: unmatchedLoading } = useQuery({
    queryKey: ['unmatched', batchId, page],
    queryFn: () => getUnmatched(batchId!, page, 20),
    enabled: !!batchId && activeTab === 'unmatched',
  });

  const reviewMutation = useMutation({
    mutationFn: ({ matchId, action }: { matchId: number; action: 'confirm' | 'reject' }) =>
      reviewMatch(matchId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches', batchId] });
      queryClient.invalidateQueries({ queryKey: ['batch', batchId] });
    },
  });

  const getConfidenceColor = (score: number) => {
    if (score >= 0.85) return 'confidence-high';
    if (score >= 0.7) return 'confidence-medium';
    return 'confidence-low';
  };

  const getMatchTypeBadge = (type: string) => {
    switch (type) {
      case 'exact':
        return <span className="badge badge-success">Exact Match</span>;
      case 'high_confidence':
        return <span className="badge badge-success">High Confidence</span>;
      case 'ai_matched':
        return (
          <span className="badge badge-info">
            <Bot size={12} style={{ marginRight: '0.25rem' }} />
            AI Matched
          </span>
        );
      case 'medium_confidence':
        return <span className="badge badge-warning">Medium Confidence</span>;
      case 'low_confidence':
        return <span className="badge badge-danger">Low Confidence</span>;
      default:
        return <span className="badge">{type}</span>;
    }
  };

  if (batchLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
      </div>
    );
  }

  if (!batch) {
    return (
      <div className="card">
        <div className="empty-state">
          <p>Batch not found</p>
          <Link to="/batches" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Back to batches
          </Link>
        </div>
      </div>
    );
  }

  const isLoading = matchesLoading || unmatchedLoading;
  const currentData = activeTab === 'unmatched' ? unmatched : matches;
  const totalPages = currentData ? Math.ceil(currentData.total / currentData.page_size) : 0;

  return (
    <div>
      <Link
        to="/batches"
        style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: 'var(--gray-600)', textDecoration: 'none', marginBottom: '1rem' }}
      >
        <ArrowLeft size={18} />
        Back to batches
      </Link>

      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">{batch.filename}</h2>
            <p style={{ color: 'var(--gray-500)', fontSize: '0.875rem' }}>
              Processed {new Date(batch.created_at).toLocaleString()}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <a
              href={exportFlagged(batch.id)}
              className="btn btn-secondary"
              download
            >
              <Download size={16} />
              Export Flagged
            </a>
            <a
              href={exportUnmatched(batch.id)}
              className="btn btn-secondary"
              download
            >
              <Download size={16} />
              Export Unmatched
            </a>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ padding: '1rem', background: 'var(--gray-50)', borderRadius: '0.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 700 }}>{batch.total_records}</div>
            <div style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>Total Records</div>
          </div>
          <div style={{ padding: '1rem', background: '#d1fae5', borderRadius: '0.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--success)' }}>{batch.matched_records}</div>
            <div style={{ fontSize: '0.875rem', color: '#065f46' }}>Matched</div>
          </div>
          <div style={{ padding: '1rem', background: '#fef3c7', borderRadius: '0.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--warning)' }}>{batch.flagged_records}</div>
            <div style={{ fontSize: '0.875rem', color: '#92400e' }}>Flagged</div>
          </div>
          <div style={{ padding: '1rem', background: '#fee2e2', borderRadius: '0.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--danger)' }}>{batch.unmatched_records}</div>
            <div style={{ fontSize: '0.875rem', color: '#991b1b' }}>Unmatched</div>
          </div>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'matched' ? 'active' : ''}`}
            onClick={() => { setActiveTab('matched'); setPage(1); }}
          >
            <CheckCircle size={16} style={{ marginRight: '0.5rem' }} />
            Matched ({batch.matched_records})
          </button>
          <button
            className={`tab ${activeTab === 'flagged' ? 'active' : ''}`}
            onClick={() => { setActiveTab('flagged'); setPage(1); }}
          >
            <AlertTriangle size={16} style={{ marginRight: '0.5rem' }} />
            Flagged ({batch.flagged_records})
          </button>
          <button
            className={`tab ${activeTab === 'unmatched' ? 'active' : ''}`}
            onClick={() => { setActiveTab('unmatched'); setPage(1); }}
          >
            <FileQuestion size={16} style={{ marginRight: '0.5rem' }} />
            Unmatched ({batch.unmatched_records})
          </button>
        </div>

        {isLoading ? (
          <div className="loading">
            <div className="spinner" />
          </div>
        ) : activeTab === 'unmatched' ? (
          // Unmatched records view
          unmatched?.records?.length ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Row #</th>
                    <th>Work Title</th>
                    <th>Songwriter</th>
                    <th>Recording Title</th>
                    <th>Artist</th>
                  </tr>
                </thead>
                <tbody>
                  {unmatched.records.map((record: UsageRecord) => (
                    <tr key={record.id}>
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
          ) : (
            <div className="empty-state">
              <CheckCircle className="empty-state-icon" style={{ color: 'var(--success)' }} />
              <p>All records have been matched!</p>
            </div>
          )
        ) : (
          // Matches view
          matches?.matches?.length ? (
            <div>
              {matches.matches.map((match: Match) => (
                <div key={match.id} className="match-card">
                  <div className="match-header">
                    <div>
                      {getMatchTypeBadge(match.match_type)}
                      {match.is_confirmed && (
                        <span className="badge badge-success" style={{ marginLeft: '0.5rem' }}>
                          <CheckCircle size={12} /> Confirmed
                        </span>
                      )}
                      {match.is_rejected && (
                        <span className="badge badge-danger" style={{ marginLeft: '0.5rem' }}>
                          <XCircle size={12} /> Rejected
                        </span>
                      )}
                    </div>
                    <div className="match-score" style={{ color: `var(--${match.confidence_score >= 0.85 ? 'success' : match.confidence_score >= 0.7 ? 'warning' : 'danger'})` }}>
                      {(match.confidence_score * 100).toFixed(1)}%
                    </div>
                  </div>

                  <div className="match-details">
                    <div className="match-section">
                      <div className="match-section-title">Usage Record (Row {match.usage_record.row_number})</div>
                      <div><strong>Title:</strong> {match.usage_record.work_title || match.usage_record.recording_title}</div>
                      <div><strong>Songwriter:</strong> {match.usage_record.songwriter || '-'}</div>
                      {match.usage_record.recording_artist && (
                        <div><strong>Artist:</strong> {match.usage_record.recording_artist}</div>
                      )}
                    </div>
                    <div className="match-section">
                      <div className="match-section-title">Matched Work ({match.work.work_code})</div>
                      <div><strong>Title:</strong> {match.work.title}</div>
                      <div><strong>Songwriters:</strong> {match.work.songwriters.join(', ')}</div>
                      {match.work.iswc && (
                        <div><strong>ISWC:</strong> {match.work.iswc}</div>
                      )}
                    </div>
                  </div>

                  <div style={{ marginTop: '1rem' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--gray-500)', marginBottom: '0.5rem' }}>Similarity Scores:</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                      {match.title_similarity !== null && (
                        <div className="confidence-bar">
                          <span style={{ fontSize: '0.75rem', width: '60px' }}>Title</span>
                          <div className="confidence-meter">
                            <div
                              className={`confidence-fill ${getConfidenceColor(match.title_similarity!)}`}
                              style={{ width: `${match.title_similarity! * 100}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '0.75rem', width: '40px' }}>{(match.title_similarity! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {match.songwriter_similarity !== null && (
                        <div className="confidence-bar">
                          <span style={{ fontSize: '0.75rem', width: '60px' }}>Writer</span>
                          <div className="confidence-meter">
                            <div
                              className={`confidence-fill ${getConfidenceColor(match.songwriter_similarity!)}`}
                              style={{ width: `${match.songwriter_similarity! * 100}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '0.75rem', width: '40px' }}>{(match.songwriter_similarity! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {match.vector_similarity !== null && (
                        <div className="confidence-bar">
                          <span style={{ fontSize: '0.75rem', width: '60px' }}>Vector</span>
                          <div className="confidence-meter">
                            <div
                              className={`confidence-fill ${getConfidenceColor(match.vector_similarity!)}`}
                              style={{ width: `${match.vector_similarity! * 100}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '0.75rem', width: '40px' }}>{(match.vector_similarity! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {match.ai_reasoning && (
                    <div className="ai-reasoning">
                      <div className="ai-reasoning-label">
                        <Bot size={14} style={{ display: 'inline', marginRight: '0.25rem' }} />
                        AI Reasoning
                      </div>
                      {match.ai_reasoning}
                    </div>
                  )}

                  {!match.is_confirmed && !match.is_rejected && (
                    <div className="match-actions">
                      <button
                        className="btn btn-danger"
                        onClick={() => reviewMutation.mutate({ matchId: match.id, action: 'reject' })}
                        disabled={reviewMutation.isPending}
                      >
                        <XCircle size={16} />
                        Reject
                      </button>
                      <button
                        className="btn btn-success"
                        onClick={() => reviewMutation.mutate({ matchId: match.id, action: 'confirm' })}
                        disabled={reviewMutation.isPending}
                      >
                        <CheckCircle size={16} />
                        Confirm
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <FileQuestion className="empty-state-icon" />
              <p>No {activeTab} records found</p>
            </div>
          )
        )}

        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </button>
            <span>Page {page} of {totalPages}</span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= totalPages}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
