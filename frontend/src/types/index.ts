export type AccountType = 'checking' | 'savings' | 'credit_card' | 'brokerage' | 'loan';
export type TransactionType = 'debit' | 'credit';
export type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Account {
  id: string;
  account_type: AccountType;
  institution_name: string;
  account_name: string;
  account_number_last4?: string;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  account_id: string;
  transaction_date: string;
  post_date?: string;
  description: string;
  original_description?: string;
  amount: number;
  transaction_type: TransactionType;
  merchant?: string;
  category_id?: string;
  is_duplicate: boolean;
  created_at: string;
}

export interface ImportLog {
  id: string;
  filename: string;
  account_id?: string;
  import_status: ImportStatus;
  rows_processed: number;
  rows_imported: number;
  rows_failed: number;
  rows_duplicate: number;
  error_details?: Record<string, unknown>;
  started_at: string;
  completed_at?: string;
}

export interface UploadResponse {
  import_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface CSVPreview {
  headers: string[];
  sample_rows: string[][];
  total_rows: number;
  detected_delimiter: string;
  detected_encoding: string;
}

export interface ImportRequest {
  account_id: string;
  column_mapping?: Record<string, string>;
  date_format?: string;
  has_header?: boolean;
  negative_means_debit?: boolean;
}

export interface ImportResult {
  import_id: string;
  status: string;
  stats: {
    processed: number;
    imported: number;
    failed: number;
    duplicate: number;
  };
}

export interface Category {
  id: string;
  name: string;
  parent_category_id?: string;
  category_type: 'income' | 'expense';
  icon?: string;
  color?: string;
  description?: string;
}
