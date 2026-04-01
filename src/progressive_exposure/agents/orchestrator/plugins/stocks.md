# stocks

Provides access to stock quote data in the remote QuickJS environment.

## Import
```javascript
import * as stocks from "stocks";
```

## Functions

### `stocks.get()`
Returns all stock quotes.

**Returns:** Array | null — Array of stock quote objects, or `null` if no data is available

Each stock object has: `ticker` (string), `name` (string), `price` (number), `change` (number), `change_percent` (number), `volume` (number), `market_cap` (number), `timestamp` (string)

### `stocks.get(ticker)`
Returns a single stock quote by ticker.

**Parameters:**
- `ticker` (string) — The stock ticker (e.g., `"AAPL"`, `"MSFT"`, `"NVDA"`)

**Returns:** Object | null — The stock quote object, or `null` if the ticker is not found

## Example
```javascript
import * as stocks from "stocks";

function handler(e) {
  // Get all stocks
  const allStocks = stocks.get();

  // Get a single stock (check for null)
  const apple = stocks.get("AAPL");
  if (apple !== null) {
    return apple.price;
  }
  return null;
}

export { handler };
```

## Notes
- Returns `null` when no results are found — always check before accessing properties
- Return values are already typed objects — do NOT call `JSON.parse()`
