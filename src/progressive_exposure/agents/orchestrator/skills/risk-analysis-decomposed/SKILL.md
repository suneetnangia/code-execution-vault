---
name: risk-analysis-decomposed
description: >
  Performs risk analysis on a portfolio by calling Financial Data APIs one at a time in separate steps.
  Use when the user asks about portfolio risk exposure, holdings sensitivity to market moves, unrealized P&L
  benchmarking, or identifying correlated risk across positions. Unlike risk-analysis, this skill makes each
  API call as a separate run-python-code or javascript-code invocation, allowing the model to reason over
  intermediate results before deciding the next call. Requires the financial APIs to be running at http://localhost:8000.
metadata:
  author: progressive-exposure
  version: "1.0"
---

# Risk Analysis (Decomposed)

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

When this skill is triggered, you MUST call the Financial Data APIs **one at a time**, each as a separate code execution invocation using either `run-python-code` or `javascript-code`. After each call, examine the returned data and decide what to call next.

Do NOT chain all API calls in a single code block. Each step should be a separate execution.

Choose the language based on user preference. If the user does not specify, either language is acceptable. You may mix languages across steps if useful.

Do NOT answer from general knowledge. Always call the live APIs to get current data.

### Step-by-step workflow

1. **Step 1**: Call ONE API endpoint via `run-python-code` or `javascript-code`. Read the output.
2. **Step 2**: Based on the results, decide which API to call next. Call it via another code execution invocation.
3. **Step 3**: Continue calling APIs one at a time until you have all the data needed.
4. **Step 4**: Once all data is collected, use a final code execution call to compute risk metrics and format the output.

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

Each code execution call should contain a small, focused snippet that:
- Calls exactly ONE API endpoint
- Uses `http://localhost:8000` as the base URL
- Prints the JSON response so you can read it

Use either **Python** (via `run-python-code`) or **JavaScript** (via `javascript-code`).

### Python template for each API call

```python
import json
import urllib.request

url = "http://localhost:8000/api/v1/<endpoint>"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())
print(json.dumps(data, indent=2))
```

### JavaScript template for each API call (QuickJS-compliant)

For any external API call, use the built-in `fetch` module:

```javascript
import * as fetch from "fetch";
function handler(e) { return { result: fetch.fetch(e) }; }

const response = handler("http://localhost:8000/api/v1/<endpoint>");
const data = JSON.parse(response.result);
console.log(JSON.stringify(data, null, 2));

export { handler };
```

### Template for final computation step

After collecting all data from previous steps, write a final code execution invocation that:
- Hardcodes the collected data as dicts/lists (Python) or objects/arrays (JavaScript)
- Computes the risk metrics (relative performance, exposure ranking, etc.)
- Formats and prints a readable table or summary

## Analysis Patterns

### Pattern 1: Exposure Analysis

When the user asks which holdings are most exposed to an index movement:

- **Call 1** (Python or JS): `GET /api/v1/indices` — Read market index snapshots. Note the change% for each index.
- **Call 2** (Python or JS): `GET /api/v1/portfolio` — Read holdings. Note each holding's ticker and sector.
- **Call 3** (Python or JS): `GET /api/v1/stocks/{ticker}` — For the most relevant holdings, fetch their stock quote one at a time. Note each stock's change%.
- **Final step** (Python or JS): Compute relative performance per holding (`stock_change% - benchmark_change%`), sort by worst first, and print a risk report.

### Pattern 2: P&L vs Benchmark Comparison

When the user asks about unrealized P&L relative to market performance:

- **Call 1** (Python or JS): `GET /api/v1/portfolio` — Read total unrealized P&L and all holdings with allocation%.
- **Call 2** (Python or JS): `GET /api/v1/indices` — Read all benchmark index changes.
- **Call 3** (Python or JS): `GET /api/v1/stocks` — Read all stock daily changes.
- **Final step** (Python or JS): Compute `holding_change% - benchmark_change%` per holding, sort underperformers first, and print a comparison table with outperformer/underperformer counts.
