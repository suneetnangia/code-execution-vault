---
name: risk-analysis-composed
description: >
  Performs risk analysis on a portfolio by chaining Financial Data APIs (Stock Quotes, Portfolio Holdings, Market Indices).
  Use when the user asks about portfolio risk exposure, holdings sensitivity to market moves, unrealized P&L benchmarking,
  or identifying correlated risk across positions. This skill instructs you to generate code that calls the
  financial APIs and computes risk metrics, then execute it using either the run-python-code skill or the javascript-code skill.
  Requires the financial APIs to be running at http://localhost:8000.
metadata:
  author: progressive-exposure
  version: "1.0"
---

# Risk Analysis

## Persona

**Emily, 30, Risk Analyst at a hedge fund.**
Goal: Assess portfolio sensitivity to market moves and identify correlated risk.

## When to use this skill

Use this skill when the user needs to:
- Assess which portfolio holdings are most exposed to a market index drop
- Compare each position's daily move against its benchmark index
- Calculate total unrealized P&L and relative performance vs market
- Identify correlated risk across portfolio sectors
- Answer questions like:
  - "If the NASDAQ drops 2% today, which of our holdings are most exposed?"
  - "What's our total unrealized P&L and how does each position's daily move compare to its benchmark index?"

## How it works

When this skill is triggered, you MUST:
1. Generate code that chains the Financial Data APIs documented below — either **Python** or **JavaScript** (QuickJS-compliant)
2. Execute that code using either:
   - The `run-python-code` skill (via its `execute` script with the `code` parameter) for Python, OR
   - The `javascript-code` skill (via its `scripts/run_js.py` script with the `--code` parameter) for JavaScript

Choose the language based on user preference. If the user does not specify, either language is acceptable.

Do NOT answer from general knowledge. Always call the live APIs to get current data.

## Available Financial Data APIs

Base URL: `http://localhost:8000`

### Stock Quotes API

**`GET /api/v1/stocks`** — Returns all stock quotes.
```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "price": 227.63,
    "change": 3.41,
    "change_percent": 1.52,
    "volume": 58432100,
    "market_cap": 3480000000000,
    "timestamp": "2026-03-27T15:30:00Z"
  }
]
```

**`GET /api/v1/stocks/{ticker}`** — Returns a single stock quote by ticker (e.g., AAPL, MSFT, NVDA). Returns 404 if ticker not found.

### Portfolio Holdings API

**`GET /api/v1/portfolio`** — Returns all holdings with a summary.
```json
{
  "summary": {
    "total_market_value": 154634.35,
    "total_unrealized_pnl": 10134.85,
    "holdings_count": 6
  },
  "holdings": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "quantity": 150,
      "avg_cost": 195.40,
      "current_price": 227.63,
      "market_value": 34144.50,
      "unrealized_pnl": 4834.50,
      "sector": "Technology",
      "allocation_percent": 22.1
    }
  ]
}
```

### Market Indices API

**`GET /api/v1/indices`** — Returns all market indices (S&P 500, NASDAQ, Dow Jones).
```json
[
  {
    "name": "S&P 500",
    "symbol": "SPX",
    "value": 5987.42,
    "change": 28.63,
    "change_percent": 0.48,
    "timestamp": "2026-03-27T15:30:00Z"
  }
]
```

**`GET /api/v1/indices/{symbol}`** — Returns a single index by symbol (SPX, IXIC, DJI). Returns 404 if symbol not found.

## Sector-to-Index Benchmark Mapping

Use these mappings when comparing holdings to their benchmark index:
- **Technology** → NASDAQ Composite (`IXIC`)
- **Financials** → Dow Jones Industrial Average (`DJI`)
- **Healthcare** → S&P 500 (`SPX`)
- **Consumer Discretionary** → S&P 500 (`SPX`)

## Code Generation Guidelines

Generate code in **either Python or JavaScript**. Use `http://localhost:8000` as the base URL for all API calls.

### Python guidelines

When generating Python code to execute via `run-python-code`:
- Use only `urllib.request` and `json` from the standard library (no external packages)
- Set a 10-second timeout on requests
- Handle HTTP errors gracefully (check response codes before parsing)
- Format output as readable tables or summaries with aligned columns
- Include both absolute and relative performance metrics
- Sort results by risk exposure (most exposed first)

#### Helper pattern (Python)

```python
import json
import urllib.request

BASE_URL = "http://localhost:8000"

def api_get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())
```

### JavaScript guidelines (QuickJS-compliant)

When generating JavaScript code to execute via `javascript-code`:
- Code must be QuickJS-compliant (no Node.js or browser APIs)
- Use the built-in `fetch` module for HTTP requests (see helper pattern below)
- Format output as readable tables or summaries
- Use `console.log()` for output
- Sort results by risk exposure (most exposed first)

#### Helper pattern (JavaScript)

For any external API call, use the built-in `fetch` module with this pattern:

```javascript
import * as fetch from "fetch";
function handler(e) { return { result: fetch.fetch(e) }; }

const BASE_URL = "http://localhost:8000";

function apiGet(path) {
  const response = handler(BASE_URL + path);
  return JSON.parse(response.result);
}

export { handler };
```

## Analysis Patterns

### Pattern 1: Exposure Analysis

When the user asks which holdings are most exposed to an index movement:

1. Call `GET /api/v1/indices` to get all index snapshots
2. Call `GET /api/v1/portfolio` to get all holdings with sectors
3. For each holding, call `GET /api/v1/stocks/{ticker}` to get its daily change
4. Map each holding's sector to its benchmark index using the sector-to-index mapping
5. Compute relative performance: `stock_change_percent - benchmark_change_percent`
6. Sort by relative performance (worst first = most exposed)
7. Print a table: ticker, name, sector, stock change%, benchmark symbol, benchmark change%, relative %
8. Flag the most exposed holding with its market value at risk

### Pattern 2: P&L vs Benchmark Comparison

When the user asks about unrealized P&L relative to market performance:

1. Call `GET /api/v1/portfolio` to get all holdings, their unrealized P&L, and allocation
2. Call `GET /api/v1/stocks` to get all stock daily changes
3. Call `GET /api/v1/indices` to get all benchmark index changes
4. For each holding, compute: `holding_change_percent - benchmark_change_percent`
5. Sort by relative performance (underperformers first)
6. Print total unrealized P&L and total market value
7. Print a table: ticker, allocation%, day change%, benchmark, benchmark change%, relative performance%, unrealized P&L
8. Summarize count of outperformers vs underperformers
