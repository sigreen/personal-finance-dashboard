import { useState } from 'react';
import { createAccount } from '../services/api';
import type { Account } from '../types';

interface CreateAccountModalProps {
  onClose: () => void;
  onAccountCreated: (account: Account) => void;
}

export default function CreateAccountModal({ onClose, onAccountCreated }: CreateAccountModalProps) {
  const [accountName, setAccountName] = useState('');
  const [institutionName, setInstitutionName] = useState('');
  const [accountType, setAccountType] = useState<string>('credit_card');
  const [last4, setLast4] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const account = await createAccount({
        account_type: accountType as any,
        institution_name: institutionName,
        account_name: accountName,
        account_number_last4: last4 || undefined,
        currency,
      });

      onAccountCreated(account);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Create New Account</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <span className="text-2xl">&times;</span>
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="accountName" className="block text-sm font-medium text-gray-700">
              Account Name *
            </label>
            <input
              type="text"
              id="accountName"
              required
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Chase Sapphire Reserve"
            />
          </div>

          <div>
            <label htmlFor="institutionName" className="block text-sm font-medium text-gray-700">
              Institution *
            </label>
            <input
              type="text"
              id="institutionName"
              required
              value={institutionName}
              onChange={(e) => setInstitutionName(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Chase, American Express, etc."
            />
          </div>

          <div>
            <label htmlFor="accountType" className="block text-sm font-medium text-gray-700">
              Account Type *
            </label>
            <select
              id="accountType"
              required
              value={accountType}
              onChange={(e) => setAccountType(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="checking">Checking</option>
              <option value="savings">Savings</option>
              <option value="credit_card">Credit Card</option>
              <option value="brokerage">Brokerage</option>
              <option value="loan">Loan</option>
            </select>
          </div>

          <div>
            <label htmlFor="last4" className="block text-sm font-medium text-gray-700">
              Last 4 Digits (Optional)
            </label>
            <input
              type="text"
              id="last4"
              value={last4}
              onChange={(e) => setLast4(e.target.value.replace(/\D/g, '').slice(0, 4))}
              maxLength={4}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="1234"
            />
          </div>

          <div>
            <label htmlFor="currency" className="block text-sm font-medium text-gray-700">
              Currency
            </label>
            <select
              id="currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="USD">USD</option>
              <option value="CAD">CAD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </select>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
