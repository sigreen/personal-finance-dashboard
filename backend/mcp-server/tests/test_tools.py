"""Test MCP server tools."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.transactions import get_transactions, search_transactions
from src.tools.accounts import get_account_summary
from src.tools.analytics import get_spending_by_category, get_merchant_spending, get_cash_flow


async def test_get_account_summary():
    """Test get_account_summary tool."""
    print("\n=== Testing get_account_summary ===")
    try:
        result = await get_account_summary()
        print(f"Found {result['total_accounts']} accounts")
        print(f"Active accounts: {result['active_accounts']}")
        if result['accounts']:
            print(f"First account: {result['accounts'][0]['account_name']}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_get_transactions():
    """Test get_transactions tool."""
    print("\n=== Testing get_transactions ===")
    try:
        result = await get_transactions(limit=10)
        print(f"Total transactions: {result['total']}")
        print(f"Returned: {len(result['transactions'])} transactions")
        if result['transactions']:
            tx = result['transactions'][0]
            print(f"Latest transaction: {tx['description']} - ${tx['amount']}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_search_transactions():
    """Test search_transactions tool."""
    print("\n=== Testing search_transactions ===")
    try:
        result = await search_transactions(query="amazon", limit=5)
        print(f"Found {result['total']} transactions matching 'amazon'")
        if result['transactions']:
            for tx in result['transactions'][:3]:
                print(f"  - {tx['description']}: ${tx['amount']}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_get_spending_by_category():
    """Test get_spending_by_category tool."""
    print("\n=== Testing get_spending_by_category ===")
    try:
        result = await get_spending_by_category()
        print(f"Found {result['category_count']} categories")
        print(f"Total spending: ${result['total_spending']:.2f}")
        if result['categories']:
            top_category = result['categories'][0]
            print(f"Top category: {top_category['category_name']} - ${top_category['total_amount']:.2f}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_get_merchant_spending():
    """Test get_merchant_spending tool."""
    print("\n=== Testing get_merchant_spending ===")
    try:
        result = await get_merchant_spending(top_n=5)
        print(f"Found {result['merchant_count']} top merchants")
        if result['merchants']:
            for merchant in result['merchants'][:3]:
                print(f"  - {merchant['merchant']}: ${merchant['total_amount']:.2f} ({merchant['transaction_count']} txs)")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def test_get_cash_flow():
    """Test get_cash_flow tool."""
    print("\n=== Testing get_cash_flow ===")
    try:
        result = await get_cash_flow(granularity="monthly")
        print(f"Cash flow analysis ({result['granularity']})")
        print(f"Total income: ${result['summary']['total_income']:.2f}")
        print(f"Total expenses: ${result['summary']['total_expenses']:.2f}")
        print(f"Net total: ${result['summary']['net_total']:.2f}")
        if result['periods']:
            print(f"Periods analyzed: {len(result['periods'])}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Personal Finance MCP Server - Tool Tests")
    print("=" * 50)

    tests = [
        test_get_account_summary,
        test_get_transactions,
        test_search_transactions,
        test_get_spending_by_category,
        test_get_merchant_spending,
        test_get_cash_flow
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\nFATAL ERROR in {test.__name__}: {e}")
            results.append((test.__name__, False))

    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
