---
name: risk-analysis-decomposed
description: >
  Performs risk analysis on a portfolio by calling Financial Data APIs one at a time in separate steps.
  Use when the user asks about portfolio risk exposure, holdings sensitivity to market moves, unrealized P&L
  benchmarking, or identifying correlated risk across positions. Unlike risk-analysis-composed, this skill makes each
  API call as a separate code execution invocation, allowing the model to reason over intermediate results
  before deciding the next call. Uses either run-python-code (Python) or run-javascript-code-remote (JavaScript)
  depending on user request. Defaults to Python. Requires the financial APIs to be running at http://localhost:8000.
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

First, determine the execution language based on the user's request:
- If the user asks for **JavaScript** or **JS**: use the `run-javascript-code-remote` skill for all code execution
- Otherwise (default): use the `run-python-code` skill for all code execution

Then, you MUST call the Financial Data APIs **one at a time**, each as a separate invocation of the chosen skill. After each call, examine the returned data and decide what to call next.

Do NOT chain all API calls in a single code block. Each step should be a separate execution.

Do NOT answer from general knowledge. Always call the live APIs to get current data.

### Step-by-step workflow

1. **Step 1**: Call ONE API endpoint via the chosen skill. Read the output.
2. **Step 2**: Based on the results, decide which API to call next. Call it via another invocation.
3. **Step 3**: Continue calling APIs one at a time until you have all the data needed.
4. **Step 4**: Once all data is collected, use a final invocation to compute risk metrics and format the output.

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

General guidelines (both languages):
- Each invocation should call exactly ONE API endpoint
- Use `http://localhost:8000` as the base URL
- Set a 10-second timeout on the request
- Print the JSON response so you can read it

### Python (when using `run-python-code`)

- Use only `urllib.request` and `json` from the standard library

#### Template for each API call

```python
import json
import urllib.request

url = "http://localhost:8000/api/v1/<endpoint>"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode())
print(json.dumps(data, indent=2))
```

#### Template for final computation step

After collecting all data from previous steps, write a final `run-python-code` invocation that:
- Hardcodes the collected data as Python dicts/lists (copy from previous step outputs)
- Computes the risk metrics (relative performance, exposure ranking, etc.)
- Formats and prints a readable table or summary

### JavaScript (when using `run-javascript-code-remote`)

- All code MUST be QuickJS-compliant — see the `run-javascript-code-remote` skill for full guidelines and available plugins
- Use the `fetch` plugin for HTTP requests (`import * as fetch from 'fetch'`)
- Use `console.log()` for output

#### Template for each API call

```javascript
import * as fetch from 'fetch';

const body = fetch.fetch("http://localhost:8000/api/v1/<endpoint>");
const data = JSON.parse(body);
console.log(JSON.stringify(data, null, 2));
```

#### Template for final computation step

After collecting all data from previous steps, write a final `run-javascript-code-remote` invocation that:
- Hardcodes the collected data as JavaScript objects/arrays (copy from previous step outputs)
- Computes the risk metrics (relative performance, exposure ranking, etc.)
- Formats and prints a readable table or summary via `console.log()`

## Analysis Patterns

### Pattern 1: Exposure Analysis

When the user asks which holdings are most exposed to an index movement:

- **Call 1**: `GET /api/v1/indices` — Read market index snapshots. Note the change% for each index.
- **Call 2**: `GET /api/v1/portfolio` — Read holdings. Note each holding's ticker and sector.
- **Call 3**: `GET /api/v1/stocks/{ticker}` — For the most relevant holdings, fetch their stock quote one at a time. Note each stock's change%.
- **Final step**: Compute relative performance per holding (`stock_change% - benchmark_change%`), sort by worst first, and print a risk report.

Use the same skill (either `run-python-code` or `run-javascript-code-remote`) consistently across all steps.

### Pattern 2: P&L vs Benchmark Comparison

When the user asks about unrealized P&L relative to market performance:

- **Call 1**: `GET /api/v1/portfolio` — Read total unrealized P&L and all holdings with allocation%.
- **Call 2**: `GET /api/v1/indices` — Read all benchmark index changes.
- **Call 3**: `GET /api/v1/stocks` — Read all stock daily changes.
- **Final step**: Compute `holding_change% - benchmark_change%` per holding, sort underperformers first, and print a comparison table with outperformer/underperformer counts.

Use the same skill (either `run-python-code` or `run-javascript-code-remote`) consistently across all steps.
