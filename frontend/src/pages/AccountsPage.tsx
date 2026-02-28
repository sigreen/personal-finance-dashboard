import { useEffect, useState } from 'react';
import { getAccounts } from '../services/api';
import type { Account } from '../types';
import CreateAccountModal from '../components/CreateAccountModal';
import BankIcon from '../components/BankIcon';

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const data = await getAccounts();
      setAccounts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch accounts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleAccountCreated = (newAccount: Account) => {
    setAccounts([...accounts, newAccount]);
  };

  const getAccountTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      checking: 'Checking',
      savings: 'Savings',
      credit_card: 'Credit Card',
      brokerage: 'Brokerage',
      loan: 'Loan',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p className="font-bold">Error</p>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Accounts</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage your financial accounts
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Create Account
        </button>
      </div>

      {showCreateModal && (
        <CreateAccountModal
          onClose={() => setShowCreateModal(false)}
          onAccountCreated={handleAccountCreated}
        />
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {accounts.map((account) => (
          <div key={account.id} className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center gap-4 mb-4">
              <BankIcon institutionName={account.institution_name} size="lg" />
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-medium text-gray-900 truncate">
                  {account.account_name}
                </h3>
                {account.is_active && (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    Active
                  </span>
                )}
              </div>
            </div>

            <dl className="space-y-2">
              <div>
                <dt className="text-sm text-gray-500">Institution</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {account.institution_name}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Type</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {getAccountTypeLabel(account.account_type)}
                </dd>
              </div>
              {account.account_number_last4 && (
                <div>
                  <dt className="text-sm text-gray-500">Account Number</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    ****{account.account_number_last4}
                  </dd>
                </div>
              )}
              <div>
                <dt className="text-sm text-gray-500">Currency</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {account.currency}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Created</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {new Date(account.created_at).toLocaleDateString()}
                </dd>
              </div>
            </dl>
          </div>
        ))}
      </div>

      {accounts.length === 0 && !loading && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No accounts</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating an account.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create Your First Account
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
