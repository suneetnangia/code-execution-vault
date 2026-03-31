# fetch

Provides HTTP request capability for code running in the remote QuickJS environment.

## Import
```javascript
import * as fetch from 'fetch';
```

## Functions

### `fetch.fetch(url)`
Performs a synchronous GET request and returns the response body as a string.

**Parameters:**
- `url` (string) — The URL to fetch

**Returns:** string — The response body

**Throws:** Error if the request fails or the URL is unreachable

## Example
```javascript
import * as fetch from 'fetch';

const body = fetch.fetch('https://example.com/api/data');
const data = JSON.parse(body);
console.log(data);
```

## Notes
- This is the **only** way to make HTTP requests in the QuickJS environment
- Do NOT use browser `fetch()`, `XMLHttpRequest`, Node.js `http`/`https`, or any other HTTP mechanism
- Always use `import * as fetch from 'fetch'` — not `require('fetch')`
