import { useState, useEffect } from 'react';
import { getAccounts, uploadCSV, previewCSV, processImport, getImportStatus } from '../services/api';
import type { Account, CSVPreview, ImportLog } from '../types';
import FileUpload from '../components/FileUpload';
import CSVPreviewTable from '../components/CSVPreviewTable';
import ImportConfigForm from '../components/ImportConfigForm';

type Step = 'upload' | 'preview' | 'configure' | 'processing' | 'complete';

export default function ImportPage() {
  const [step, setStep] = useState<Step>('upload');
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [importId, setImportId] = useState<string>('');
  const [preview, setPreview] = useState<CSVPreview | null>(null);
  const [importResult, setImportResult] = useState<ImportLog | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const data = await getAccounts();
        setAccounts(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch accounts');
      }
    };
    fetchAccounts();
  }, []);

  const handleFileSelect = async (file: File) => {
    setError(null);
    setLoading(true);

    try {
      const response = await uploadCSV(file);
      setImportId(response.import_id);

      const previewData = await previewCSV(response.import_id);
      setPreview(previewData);
      setStep('configure');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setLoading(false);
    }
  };

  const handleImportSubmit = async (config: {
    account_id: string;
    column_mapping?: Record<string, string>;
    date_format?: string;
    negative_means_debit?: boolean;
  }) => {
    setError(null);
    setLoading(true);
    setStep('processing');

    try {
      await processImport(importId, config);

      const status = await getImportStatus(importId);
      setImportResult(status);
      setStep('complete');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process import');
      setStep('configure');
    } finally {
      setLoading(false);
    }
  };

  const resetImport = () => {
    setStep('upload');
    setImportId('');
    setPreview(null);
    setImportResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Import Transactions</h2>
        <p className="mt-1 text-sm text-gray-600">
          Upload CSV files from your financial institutions
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error}</p>
        </div>
      )}

      {step === 'upload' && (
        <FileUpload onFileSelect={handleFileSelect} loading={loading} />
      )}

      {step === 'configure' && preview && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">CSV Preview</h3>
            <CSVPreviewTable preview={preview} />
            <div className="mt-4 text-sm text-gray-600">
              <p>Total rows: {preview.total_rows}</p>
              <p>Encoding: {preview.detected_encoding}</p>
              <p>Delimiter: {preview.detected_delimiter === ',' ? 'Comma' : preview.detected_delimiter}</p>
            </div>
          </div>

          <ImportConfigForm
            accounts={accounts}
            preview={preview}
            onSubmit={handleImportSubmit}
            onCancel={resetImport}
            loading={loading}
          />
        </div>
      )}

      {step === 'processing' && (
        <div className="bg-white shadow rounded-lg p-12">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-lg text-gray-700">Processing import...</p>
          </div>
        </div>
      )}

      {step === 'complete' && importResult && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <svg
              className="h-8 w-8 text-green-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="ml-3 text-lg font-medium text-gray-900">Import Complete</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600">Processed</p>
              <p className="text-2xl font-bold text-gray-900">{importResult.rows_processed}</p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm text-gray-600">Imported</p>
              <p className="text-2xl font-bold text-green-600">{importResult.rows_imported}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded">
              <p className="text-sm text-gray-600">Duplicates</p>
              <p className="text-2xl font-bold text-yellow-600">{importResult.rows_duplicate}</p>
            </div>
            <div className="bg-red-50 p-4 rounded">
              <p className="text-sm text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-red-600">{importResult.rows_failed}</p>
            </div>
          </div>

          <button
            onClick={resetImport}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Import Another File
          </button>
        </div>
      )}
    </div>
  );
}
