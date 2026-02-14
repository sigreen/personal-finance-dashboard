import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ImportPage from './pages/ImportPage';
import TransactionsPage from './pages/TransactionsPage';
import AccountsPage from './pages/AccountsPage';

function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const linkClass = (path: string) => `px-3 py-2 rounded-md text-sm font-medium ${
    isActive(path)
      ? 'bg-blue-700 text-white'
      : 'text-gray-300 hover:bg-blue-600 hover:text-white'
  }`;

  return (
    <nav className="bg-blue-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold">Finance Dashboard</h1>
            </div>
            <div className="ml-10 flex items-baseline space-x-4">
              <Link to="/" className={linkClass('/')}>
                Dashboard
              </Link>
              <Link to="/import" className={linkClass('/import')}>
                Import
              </Link>
              <Link to="/transactions" className={linkClass('/transactions')}>
                Transactions
              </Link>
              <Link to="/accounts" className={linkClass('/accounts')}>
                Accounts
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/import" element={<ImportPage />} />
            <Route path="/transactions" element={<TransactionsPage />} />
            <Route path="/accounts" element={<AccountsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
