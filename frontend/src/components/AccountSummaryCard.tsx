import type { Account } from '../types';

interface AccountSummaryCardProps {
  account: Account;
}

export default function AccountSummaryCard({ account }: AccountSummaryCardProps) {
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

  const getIcon = (type: string) => {
    if (type === 'credit_card') {
      return (
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
        />
      );
    }
    return (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    );
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg
              className="h-6 w-6 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {getIcon(account.account_type)}
            </svg>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {account.account_name}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-xs text-gray-500">
                  {account.institution_name}
                </div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
      <div className="bg-gray-50 px-5 py-3">
        <div className="text-sm">
          <span className="font-medium text-gray-900">
            {getAccountTypeLabel(account.account_type)}
          </span>
          {account.account_number_last4 && (
            <span className="text-gray-500 ml-2">
              ****{account.account_number_last4}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
