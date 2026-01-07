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
  Sparkles
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
        return <span className="badge badge-success">Exact</span>;
      case 'high_confidence':
        return <span className="badge badge-success">High</span>;
      case 'ai_matched':
        return (
          <span className="badge badge-info">
            <Sparkles size={10} style={{ marginRight: '4px' }} />
            AI
          </span>
        );
      case 'medium_confidence':
        return <span className="badge badge-warning">Medium</span>;
      case 'low_confidence':
        return <span className="badge badge-danger">Low</span>;
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
          <Link to="/batches" className="btn btn-primary" style={{ marginTop: '16px' }}>
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
      <Link to="/batches" className="back-link">
        <ArrowLeft size={16} />
        Batches
      </Link>

      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">{batch.filename}</h2>
            <p style={{ color: 'var(--notion-text-secondary)', fontSize: '12px', marginTop: '4px' }}>
              {new Date(batch.created_at).toLocaleString()}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <a href={exportFlagged(batch.id)} className="btn btn-secondary" download>
              <Download size={14} />
              Flagged
            </a>
            <a href={exportUnmatched(batch.id)} className="btn btn-secondary" download>
              <Download size={14} />
              Unmatched
            </a>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat-card total">
            <div className="stat-value">{batch.total_records}</div>
            <div className="stat-label">Total</div>
          </div>
          <div className="stat-card matched">
            <div className="stat-value">{batch.matched_records}</div>
            <div className="stat-label">Matched</div>
          </div>
          <div className="stat-card flagged">
            <div className="stat-value">{batch.flagged_records}</div>
            <div className="stat-label">Flagged</div>
          </div>
          <div className="stat-card unmatched">
            <div className="stat-value">{batch.unmatched_records}</div>
            <div className="stat-label">Unmatched</div>
          </div>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'matched' ? 'active' : ''}`}
            onClick={() => { setActiveTab('matched'); setPage(1); }}
          >
            <CheckCircle size={14} style={{ marginRight: '6px' }} />
            Matched ({batch.matched_records})
          </button>
          <button
            className={`tab ${activeTab === 'flagged' ? 'active' : ''}`}
            onClick={() => { setActiveTab('flagged'); setPage(1); }}
          >
            <AlertTriangle size={14} style={{ marginRight: '6px' }} />
            Flagged ({batch.flagged_records})
          </button>
          <button
            className={`tab ${activeTab === 'unmatched' ? 'active' : ''}`}
            onClick={() => { setActiveTab('unmatched'); setPage(1); }}
          >
            <FileQuestion size={14} style={{ marginRight: '6px' }} />
            Unmatched ({batch.unmatched_records})
          </button>
        </div>

        {isLoading ? (
          <div className="loading">
            <div className="spinner" />
          </div>
        ) : activeTab === 'unmatched' ? (
          unmatched?.records?.length ? (
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
                  {unmatched.records.map((record: UsageRecord) => (
                    <tr key={record.id}>
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
          ) : (
            <div className="empty-state">
              <CheckCircle className="empty-state-icon" style={{ color: 'var(--notion-green)' }} />
              <p>All records have been matched</p>
            </div>
          )
        ) : (
          matches?.matches?.length ? (
            <div>
              {matches.matches.map((match: Match) => (
                <div key={match.id} className="match-card">
                  <div className="match-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {getMatchTypeBadge(match.match_type)}
                      {match.is_confirmed && (
                        <span className="badge badge-success">
                          <CheckCircle size={10} style={{ marginRight: '4px' }} /> Confirmed
                        </span>
                      )}
                      {match.is_rejected && (
                        <span className="badge badge-danger">
                          <XCircle size={10} style={{ marginRight: '4px' }} /> Rejected
                        </span>
                      )}
                    </div>
                    <div
                      className="match-score"
                      style={{
                        color: match.confidence_score >= 0.85
                          ? 'var(--notion-green)'
                          : match.confidence_score >= 0.7
                            ? 'var(--notion-orange)'
                            : 'var(--notion-red)'
                      }}
                    >
                      {(match.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="match-details">
                    <div className="match-section">
                      <div className="match-section-title">Usage Record #{match.usage_record.row_number}</div>
                      <div><strong>Title:</strong> {match.usage_record.work_title || match.usage_record.recording_title}</div>
                      <div><strong>Writer:</strong> {match.usage_record.songwriter || '-'}</div>
                      {match.usage_record.recording_artist && (
                        <div><strong>Artist:</strong> {match.usage_record.recording_artist}</div>
                      )}
                    </div>
                    <div className="match-section">
                      <div className="match-section-title">Matched Work {match.work.work_code}</div>
                      <div><strong>Title:</strong> {match.work.title}</div>
                      <div><strong>Writers:</strong> {match.work.songwriters.join(', ')}</div>
                      {match.work.iswc && (
                        <div><strong>ISWC:</strong> {match.work.iswc}</div>
                      )}
                    </div>
                  </div>

                  <div style={{ marginTop: '12px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--notion-text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '500' }}>
                      Similarity Scores
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                      {match.title_similarity !== null && (
                        <div className="confidence-bar">
                          <span style={{ fontSize: '12px', width: '48px', color: 'var(--notion-text-secondary)' }}>Title</span>
                          <div className="confidence-meter">
                            <div
                              className={`confidence-fill ${getConfidenceColor(match.title_similarity!)}`}
                              style={{ width: `${match.title_similarity! * 100}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '12px', width: '32px', textAlign: 'right' }}>{(match.title_similarity! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {match.songwriter_similarity !== null && (
                        <div className="confidence-bar">
                          <span style={{ fontSize: '12px', width: '48px', color: 'var(--notion-text-secondary)' }}>Writer</span>
                          <div className="confidence-meter">
                            <div
                              className={`confidence-fill ${getConfidenceColor(match.songwriter_similarity!)}`}
                              style={{ width: `${match.songwriter_similarity! * 100}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '12px', width: '32px', textAlign: 'right' }}>{(match.songwriter_similarity! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      {match.vector_similarity !== null && (
                        <div className="confidence-bar">
                          <span style={{ fontSize: '12px', width: '48px', color: 'var(--notion-text-secondary)' }}>Vector</span>
                          <div className="confidence-meter">
                            <div
                              className={`confidence-fill ${getConfidenceColor(match.vector_similarity!)}`}
                              style={{ width: `${match.vector_similarity! * 100}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '12px', width: '32px', textAlign: 'right' }}>{(match.vector_similarity! * 100).toFixed(0)}%</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {match.ai_reasoning && (
                    <div className="ai-reasoning">
                      <div className="ai-reasoning-label">
                        <Sparkles size={12} />
                        AI
                      </div>
                      <div style={{ color: 'var(--notion-text)' }}>{match.ai_reasoning}</div>
                    </div>
                  )}

                  {!match.is_confirmed && !match.is_rejected && (
                    <div className="match-actions">
                      <button
                        className="btn btn-danger"
                        onClick={() => reviewMutation.mutate({ matchId: match.id, action: 'reject' })}
                        disabled={reviewMutation.isPending}
                      >
                        <XCircle size={14} />
                        Reject
                      </button>
                      <button
                        className="btn btn-success"
                        onClick={() => reviewMutation.mutate({ matchId: match.id, action: 'confirm' })}
                        disabled={reviewMutation.isPending}
                      >
                        <CheckCircle size={14} />
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
              <p>No {activeTab} records</p>
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
