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
    if (!window.confirm('Are you sure you want to delete this batch and all its data?')) {
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
            <CheckCircle size={12} style={{ marginRight: '0.25rem' }} />
            Completed
          </span>
        );
      case 'processing':
        return (
          <span className="badge badge-info">
            <Loader size={12} style={{ marginRight: '0.25rem' }} />
            Processing
          </span>
        );
      case 'failed':
        return (
          <span className="badge badge-danger">
            <XCircle size={12} style={{ marginRight: '0.25rem' }} />
            Failed
          </span>
        );
      default:
        return (
          <span className="badge badge-warning">
            <Clock size={12} style={{ marginRight: '0.25rem' }} />
            Pending
          </span>
        );
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
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
        <h2 className="card-title">Processing Batches</h2>
        <div className="filter-group">
          <select
            className="filter-select"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All statuses</option>
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
          <p>No batches found</p>
          <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Upload a file
          </Link>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Records</th>
                  <th>Matched</th>
                  <th>Flagged</th>
                  <th>Unmatched</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.batches.map((batch: Batch) => (
                  <tr key={batch.id}>
                    <td>
                      <Link
                        to={`/batches/${batch.id}`}
                        style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}
                      >
                        {batch.filename}
                      </Link>
                    </td>
                    <td>{getStatusBadge(batch.status)}</td>
                    <td>{batch.total_records}</td>
                    <td style={{ color: 'var(--success)' }}>{batch.matched_records}</td>
                    <td style={{ color: 'var(--warning)' }}>{batch.flagged_records}</td>
                    <td style={{ color: 'var(--danger)' }}>{batch.unmatched_records}</td>
                    <td style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
                      {formatDate(batch.created_at)}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        onClick={() => handleDelete(batch.id)}
                        title="Delete batch"
                      >
                        <Trash2 size={16} />
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
