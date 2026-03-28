import { useEffect, useState, useMemo } from 'react';
import { getAccounts, getTransactions } from '../services/api';
import type { Account, Transaction } from '../types';
import RecentTransactions from '../components/RecentTransactions';
import BankIcon from '../components/BankIcon';

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [allTransactions, setAllTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [accountsData, recentData, allData] = await Promise.all([
          getAccounts(),
          getTransactions({ limit: 10 }),
          getTransactions({ limit: 1000 }), // Fetch up to 1000 for summaries
        ]);
        setAccounts(accountsData);
        setRecentTransactions(recentData);
        setAllTransactions(allData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Calculate spending by account (credit cards and Citizens checking)
  const accountSpending = useMemo(() => {
    const excludedCategories = ['Transfer', 'Payroll', 'Interest'];
    const spendingAccounts = accounts.filter(a =>
      a.account_type === 'credit_card' ||
      (a.account_type === 'checking' && a.institution_name.toLowerCase().includes('citizens'))
    );
    return spendingAccounts.map(account => {
      const accountTransactions = allTransactions.filter(
        t => t.account_id === account.id &&
        t.transaction_type === 'debit' &&
        !excludedCategories.includes(t.category_name || '')
      );
      const total = accountTransactions.reduce((sum, t) => sum + t.amount, 0);
      return {
        account,
        total,
        count: accountTransactions.length,
      };
    }).sort((a, b) => b.total - a.total);
  }, [accounts, allTransactions]);

  // Calculate spending by category
  const categorySpending = useMemo(() => {
    const excludedCategories = ['Transfer', 'Payroll', 'Interest'];
    const categoryMap = new Map<string, number>();
    allTransactions
      .filter(t =>
        t.transaction_type === 'debit' &&
        !excludedCategories.includes(t.category_name || '')
      )
      .forEach(t => {
        const category = t.category_name || 'Uncategorized';
        categoryMap.set(category, (categoryMap.get(category) || 0) + t.amount);
      });

    return Array.from(categoryMap.entries())
      .map(([category, total]) => ({ category, total }))
      .sort((a, b) => b.total - a.total);
  }, [allTransactions]);

  // Calculate spending by merchant
  const merchantSpending = useMemo(() => {
    const excludedCategories = ['Transfer', 'Payroll', 'Interest'];
    const merchantMap = new Map<string, number>();
    allTransactions
      .filter(t =>
        t.transaction_type === 'debit' &&
        t.merchant &&
        !excludedCategories.includes(t.category_name || '')
      )
      .forEach(t => {
        let merchant = t.merchant || 'Unknown';
        // Replace DDA DEBIT with more readable name
        if (merchant === 'DDA DEBIT') {
          merchant = 'Personal Check Payments';
        }
        merchantMap.set(merchant, (merchantMap.get(merchant) || 0) + t.amount);
      });

    return Array.from(merchantMap.entries())
      .map(([merchant, total]) => ({ merchant, total }))
      .sort((a, b) => b.total - a.total)
      .slice(0, 10); // Top 10 merchants
  }, [allTransactions]);

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
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="mt-1 text-sm text-gray-600">
          Overview of your financial activity
        </p>
      </div>

      {/* Spending by Account Summary */}
      {accountSpending.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Spending by Account
            </h3>
            <div className="space-y-4">
              {accountSpending.map(({ account, total, count }) => (
                <div key={account.id} className="flex items-center gap-3">
                  <BankIcon institutionName={account.institution_name} size="sm" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {account.account_name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {account.institution_name} - {count} transactions
                        </p>
                      </div>
                      <p className="text-lg font-semibold text-red-600">
                        ${total.toFixed(2)}
                      </p>
                    </div>
                    {accountSpending.length > 1 && (
                      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full"
                          style={{
                            width: `${(total / Math.max(...accountSpending.map(s => s.total))) * 100}%`,
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {accountSpending.length > 1 && (
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">Total Spending</p>
                    <p className="text-xl font-bold text-red-600">
                      ${accountSpending.reduce((sum, s) => sum + s.total, 0).toFixed(2)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Spending by Category */}
      {categorySpending.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Spending by Category
            </h3>
            <div className="space-y-3">
              {categorySpending.map(({ category, total }) => (
                <div key={category} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{category}</p>
                      <p className="text-sm font-semibold text-gray-700">
                        ${total.toFixed(2)}
                      </p>
                    </div>
                    <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-purple-500 h-1.5 rounded-full"
                        style={{
                          width: `${(total / categorySpending[0].total) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">Total Spending</p>
                <p className="text-xl font-bold text-purple-600">
                  ${categorySpending.reduce((sum, c) => sum + c.total, 0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Merchants */}
      {merchantSpending.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Top Spending by Merchant
            </h3>
            <div className="space-y-3">
              {merchantSpending.map(({ merchant, total }) => (
                <div key={merchant} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{merchant}</p>
                      <p className="text-sm font-semibold text-gray-700">
                        ${total.toFixed(2)}
                      </p>
                    </div>
                    <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-full"
                        style={{
                          width: `${(total / merchantSpending[0].total) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Transactions
          </h3>
          <RecentTransactions transactions={recentTransactions} />
        </div>
      </div>
    </div>
  );
}
