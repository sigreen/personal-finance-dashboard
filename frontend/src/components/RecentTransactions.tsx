import type { Transaction } from '../types';

interface RecentTransactionsProps {
  transactions: Transaction[];
}

export default function RecentTransactions({ transactions }: RecentTransactionsProps) {
  if (transactions.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        No transactions yet
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      <ul className="divide-y divide-gray-200">
        {transactions.map((transaction) => (
          <li key={transaction.id} className="py-4">
            <div className="flex items-center space-x-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {transaction.merchant || transaction.description}
                </p>
                <p className="text-sm text-gray-500 truncate">
                  {transaction.transaction_date}
                </p>
              </div>
              <div className="flex-shrink-0">
                <span
                  className={`inline-flex text-sm font-semibold ${
                    transaction.transaction_type === 'debit'
                      ? 'text-red-600'
                      : 'text-green-600'
                  }`}
                >
                  {transaction.transaction_type === 'debit' ? '-' : '+'}$
                  {transaction.amount.toFixed(2)}
                </span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
