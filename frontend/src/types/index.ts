export interface Batch {
  id: string;
  filename: string;
  total_records: number;
  processed_records: number;
  matched_records: number;
  unmatched_records: number;
  flagged_records: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface Work {
  id: number;
  work_code: string;
  title: string;
  songwriters: string[];
  iswc?: string;
}

export interface UsageRecord {
  id: number;
  recording_title?: string;
  recording_artist?: string;
  work_title?: string;
  songwriter?: string;
  row_number: number;
}

export interface Match {
  id: number;
  usage_record: UsageRecord;
  work: Work;
  confidence_score: number;
  match_type: 'exact' | 'high_confidence' | 'medium_confidence' | 'low_confidence' | 'ai_matched';
  title_similarity?: number;
  songwriter_similarity?: number;
  vector_similarity?: number;
  ai_reasoning?: string;
  is_confirmed: boolean;
  is_rejected: boolean;
  reviewed_at?: string;
  created_at: string;
}

export interface ProcessingProgress {
  stage: string;
  message?: string;
  batch_id?: string;
  total_records?: number;
  processed?: number;
  matched?: number;
  unmatched?: number;
  flagged?: number;
  percentage?: number;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
}

export interface BatchListResponse extends PaginatedResponse<Batch> {
  batches: Batch[];
}

export interface MatchListResponse extends PaginatedResponse<Match> {
  matches: Match[];
}

export interface UnmatchedListResponse extends PaginatedResponse<UsageRecord> {
  records: UsageRecord[];
}
