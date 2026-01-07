import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Folder, Clock, CheckCircle, XCircle, Loader, Trash2 } from 'lucide-react';
import { getBatches, deleteBatch } from '../services/api';
import { Batch } from '../types';

export default function BatchList() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['batches', page, statusFilter],
    queryFn: () => getBatches(page, 20, statusFilter || undefined),
  });

  const handleDelete = async (batchId: string) => {
    if (!window.confirm('Delete this batch and all its data?')) {
      return;
    }
    try {
      await deleteBatch(batchId);
      refetch();
    } catch (e) {
      console.error('Failed to delete batch:', e);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="badge badge-success">
            <CheckCircle size={10} style={{ marginRight: '4px' }} />
            Done
          </span>
        );
      case 'processing':
        return (
          <span className="badge badge-info">
            <Loader size={10} style={{ marginRight: '4px' }} />
            Running
          </span>
        );
      case 'failed':
        return (
          <span className="badge badge-danger">
            <XCircle size={10} style={{ marginRight: '4px' }} />
            Failed
          </span>
        );
      default:
        return (
          <span className="badge badge-warning">
            <Clock size={10} style={{ marginRight: '4px' }} />
            Pending
          </span>
        );
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Batches</h2>
        <div className="filter-group">
          <select
            className="filter-select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {!data?.batches?.length ? (
        <div className="empty-state">
          <Folder className="empty-state-icon" />
          <p>No batches yet</p>
          <Link to="/" className="btn btn-primary" style={{ marginTop: '16px' }}>
            Upload a file
          </Link>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Status</th>
                  <th>Records</th>
                  <th style={{ color: 'var(--notion-green)' }}>Matched</th>
                  <th style={{ color: 'var(--notion-orange)' }}>Flagged</th>
                  <th style={{ color: 'var(--notion-red)' }}>Unmatched</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.batches.map((batch: Batch) => (
                  <tr key={batch.id}>
                    <td>
                      <Link
                        to={`/batches/${batch.id}`}
                        style={{ color: 'var(--notion-text)', fontWeight: '500' }}
                      >
                        {batch.filename}
                      </Link>
                    </td>
                    <td>{getStatusBadge(batch.status)}</td>
                    <td>{batch.total_records}</td>
                    <td style={{ color: 'var(--notion-green)', fontWeight: '500' }}>{batch.matched_records}</td>
                    <td style={{ color: 'var(--notion-orange)', fontWeight: '500' }}>{batch.flagged_records}</td>
                    <td style={{ color: 'var(--notion-red)', fontWeight: '500' }}>{batch.unmatched_records}</td>
                    <td style={{ fontSize: '13px', color: 'var(--notion-text-secondary)' }}>
                      {formatDate(batch.created_at)}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        onClick={() => handleDelete(batch.id)}
                        title="Delete"
                        style={{ padding: '4px 8px' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.total > data.page_size && (
            <div className="pagination">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </button>
              <span>
                Page {page} of {Math.ceil(data.total / data.page_size)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(data.total / data.page_size)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
