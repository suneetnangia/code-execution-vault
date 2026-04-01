# indices

Provides access to market index data (S&P 500, NASDAQ, Dow Jones) in the remote QuickJS environment.

## Import
```javascript
import * as indices from "indices";
```

## Functions

### `indices.get()`
Returns all market indices.

**Returns:** Array | null — Array of index objects, or `null` if no data is available

Each index object has: `name` (string), `symbol` (string), `value` (number), `change` (number), `change_percent` (number), `timestamp` (string)

### `indices.get(symbol)`
Returns a single market index by symbol.

**Parameters:**
- `symbol` (string) — The index symbol (e.g., `"SPX"`, `"IXIC"`, `"DJI"`)

**Returns:** Object | null — The index object, or `null` if the symbol is not found

## Example
```javascript
import * as indices from "indices";

function handler(e) {
  // Get all indices
  const allIndices = indices.get();

  // Get a single index (check for null)
  const nasdaq = indices.get("IXIC");
  if (nasdaq !== null) {
    return nasdaq.change_percent;
  }
  return null;
}

export { handler };
```

## Notes
- Available symbols: `SPX` (S&P 500), `IXIC` (NASDAQ), `DJI` (Dow Jones)
- Returns `null` when no results are found — always check before accessing properties
- Return values are already typed objects — do NOT call `JSON.parse()`
