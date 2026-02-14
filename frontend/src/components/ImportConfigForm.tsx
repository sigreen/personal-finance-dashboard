import { useState } from 'react';
import type { Account, CSVPreview } from '../types';

interface ImportConfigFormProps {
  accounts: Account[];
  preview: CSVPreview;
  onSubmit: (config: {
    account_id: string;
    column_mapping?: Record<string, string>;
    date_format?: string;
    negative_means_debit?: boolean;
  }) => void;
  onCancel: () => void;
  loading: boolean;
}

export default function ImportConfigForm({
  accounts,
  preview,
  onSubmit,
  onCancel,
  loading,
}: ImportConfigFormProps) {
  const [accountId, setAccountId] = useState('');
  const [dateColumn, setDateColumn] = useState('');
  const [descriptionColumn, setDescriptionColumn] = useState('');
  const [amountColumn, setAmountColumn] = useState('');
  const [dateFormat, setDateFormat] = useState('%m/%d/%Y');
  const [negativeMeansDebit, setNegativeMeansDebit] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const columnMapping: Record<string, string> = {};
    if (dateColumn) columnMapping[dateColumn] = 'transaction_date';
    if (descriptionColumn) columnMapping[descriptionColumn] = 'description';
    if (amountColumn) columnMapping[amountColumn] = 'amount';

    onSubmit({
      account_id: accountId,
      column_mapping: Object.keys(columnMapping).length > 0 ? columnMapping : undefined,
      date_format: dateFormat,
      negative_means_debit: negativeMeansDebit,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6 space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Import Configuration</h3>

      <div>
        <label htmlFor="account" className="block text-sm font-medium text-gray-700">
          Account *
        </label>
        <select
          id="account"
          value={accountId}
          onChange={(e) => setAccountId(e.target.value)}
          required
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select an account</option>
          {accounts.map((account) => (
            <option key={account.id} value={account.id}>
              {account.account_name} ({account.institution_name})
            </option>
          ))}
        </select>
      </div>

      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Column Mapping</h4>
        <p className="text-xs text-gray-500 mb-4">
          Map CSV columns to transaction fields. Leave blank for auto-detection.
        </p>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="date-column" className="block text-sm font-medium text-gray-700">
              Date Column
            </label>
            <select
              id="date-column"
              value={dateColumn}
              onChange={(e) => setDateColumn(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Auto-detect</option>
              {preview.headers.map((header, index) => (
                <option key={index} value={header}>
                  {header}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="description-column" className="block text-sm font-medium text-gray-700">
              Description Column
            </label>
            <select
              id="description-column"
              value={descriptionColumn}
              onChange={(e) => setDescriptionColumn(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Auto-detect</option>
              {preview.headers.map((header, index) => (
                <option key={index} value={header}>
                  {header}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="amount-column" className="block text-sm font-medium text-gray-700">
              Amount Column
            </label>
            <select
              id="amount-column"
              value={amountColumn}
              onChange={(e) => setAmountColumn(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Auto-detect</option>
              {preview.headers.map((header, index) => (
                <option key={index} value={header}>
                  {header}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Format Settings</h4>

        <div className="space-y-4">
          <div>
            <label htmlFor="date-format" className="block text-sm font-medium text-gray-700">
              Date Format
            </label>
            <select
              id="date-format"
              value={dateFormat}
              onChange={(e) => setDateFormat(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="%m/%d/%Y">MM/DD/YYYY (US format)</option>
              <option value="%d/%m/%Y">DD/MM/YYYY (European format)</option>
              <option value="%Y-%m-%d">YYYY-MM-DD (ISO format)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount Sign Convention
            </label>
            <div className="space-y-2">
              <div className="flex items-center">
                <input
                  id="sign-chase"
                  type="radio"
                  checked={negativeMeansDebit}
                  onChange={() => setNegativeMeansDebit(true)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <label htmlFor="sign-chase" className="ml-3 block text-sm text-gray-700">
                  Chase style: negative = expense, positive = credit/refund
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="sign-amex"
                  type="radio"
                  checked={!negativeMeansDebit}
                  onChange={() => setNegativeMeansDebit(false)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <label htmlFor="sign-amex" className="ml-3 block text-sm text-gray-700">
                  Amex style: positive = expense, negative = credit/payment
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || !accountId}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Import Transactions'}
        </button>
      </div>
    </form>
  );
}
