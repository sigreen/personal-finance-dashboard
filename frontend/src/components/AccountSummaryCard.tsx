import type { Account } from '../types';
import BankIcon from './BankIcon';

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

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <BankIcon institutionName={account.institution_name} size="md" />
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
