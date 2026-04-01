# portfolio

Provides access to portfolio holdings data in the remote QuickJS environment.

## Import
```javascript
import * as portfolio from "portfolio";
```

## Functions

### `portfolio.get()`
Returns all portfolio holdings with summary.

**Returns:** Object | null — Object containing `summary` and `holdings` array, or `null` if no data is available

The `summary` object has: `total_market_value` (number), `total_unrealized_pnl` (number), `holdings_count` (number)

Each holding in the `holdings` array has: `ticker` (string), `name` (string), `quantity` (number), `avg_cost` (number), `current_price` (number), `market_value` (number), `unrealized_pnl` (number), `sector` (string), `allocation_percent` (number)

## Example
```javascript
import * as portfolio from "portfolio";

function handler(e) {
  const data = portfolio.get();
  if (data !== null) {
    return data.summary.total_market_value;
  }
  return null;
}

export { handler };
```

## Notes
- Returns `null` when no results are found — always check before accessing properties
- Return values are already typed objects — do NOT call `JSON.parse()`
