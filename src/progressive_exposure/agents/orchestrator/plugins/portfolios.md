# portfolios

Provides access to portfolio holdings data in the remote QuickJS environment.

## Import
```javascript
import * as portfolios from 'portfolios';
```

## Functions

### `portfolios.get()`
Returns all portfolio holdings with summary as a JSON string.

**Returns:** string | null — JSON object containing `summary` and `holdings` array, or `null` if no data is available

## Example
```javascript
import * as portfolios from 'portfolios';

function handler(e) {
  const raw = portfolios.get();
  if (raw !== null) {
    const portfolio = JSON.parse(raw);
    return { result: portfolio.summary.total_market_value };
  }
  return { result: null };
}

export { handler };
```

## Notes
- Returns `null` when no results are found — always check before calling `JSON.parse()`
- When non-null, `JSON.parse()` the return value — it is a string, not an object
