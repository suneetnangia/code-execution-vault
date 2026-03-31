---
name: javascript-code
description: >
  Executes QuickJS-compliant JavaScript code on a remote execution service and returns the output.
  Use when the user asks to run JavaScript code, or when a task would benefit from
  JavaScript execution (e.g., JSON manipulation, string processing, algorithmic problems,
  or computations). Also use this skill when the user provides code in Python
  or another language and asks to convert it to JavaScript before running it.
  All generated code MUST be compatible with the QuickJS engine.
metadata:
  author: progressive-exposure
  version: "1.0"
---

# Run JavaScript Code (QuickJS)

## When to use this skill

Use this skill when the user needs to:
- Run a JavaScript code snippet or prototype a small script
- Perform calculations, data transformations, or string manipulation in JavaScript
- Convert Python or other language code to JavaScript and execute it
- Solve algorithmic problems using JavaScript
- Work with JSON data processing or manipulation
- Any task where the user explicitly asks for JavaScript execution

**All generated code must be QuickJS-compliant.**

## How it works

1. If the user provides code in **Python or another language**, first **convert** it to equivalent JavaScript.
2. Generate or use the provided JavaScript code.
3. Send the JavaScript code to the remote execution service via the `scripts/run_js.py` script.
4. Return the execution output to the user.

## Usage

Run the `scripts/run_js.py` script with `--code <JAVASCRIPT_CODE>`:

The `--code` argument should contain the complete JavaScript source code as a string.

### Example

To run a simple calculation:
```
--code "console.log(2 + 2)"
```

To convert and run Python code:
- User provides: `print(sum(range(1, 101)))`
- Convert to JavaScript: `console.log(Array.from({length: 100}, (_, i) => i + 1).reduce((a, b) => a + b, 0))`
- Run the converted JavaScript code via the script

## Output format

The script returns the stdout output from the JavaScript execution. If there is an error, the error message is returned.

## Guidelines

- **All code MUST be QuickJS-compliant** — the remote execution service runs QuickJS, not Node.js or a browser
- Use `console.log()` to produce output (equivalent to Python's `print()`)
- When converting from Python, ensure language-specific constructs are properly translated
- The code is executed on a remote service — do not assume access to the local filesystem

### QuickJS compatibility rules

- **Supported**: ES2023 syntax including `let`, `const`, arrow functions, destructuring, template literals, `for...of`, `async`/`await`, classes, generators, proxies, `BigInt`, `Promise`
- **Supported built-ins**: `Math`, `JSON`, `Date`, `Array`, `String`, `Map`, `Set`, `WeakMap`, `WeakSet`, `Symbol`, `RegExp`, `ArrayBuffer`, `DataView`, typed arrays
- **NOT available**: `require()` (no CommonJS modules)
- **NOT available**: Node.js APIs (`fs`, `path`, `http`, `process`, `Buffer`, `__dirname`, `__filename`)
- **NOT available**: Browser/Web APIs (`DOM`, `window`, `document`, `setTimeout`, `setInterval`, `XMLHttpRequest`)
- **NOT available**: `TextEncoder`, `TextDecoder`, `URL`, `URLSearchParams`
- Use `console.log()` for output

### Making HTTP requests

When the code needs to call an external API, use the built-in `fetch` module. The code **must** use the following pattern, where `e` is the API endpoint URL:

```javascript
import * as fetch from "fetch";
function handler(e) { return { result: fetch.fetch(e) }; }
export { handler };
```

For example, to call `http://localhost:8000/api/v1/stocks`:

```javascript
import * as fetch from "fetch";
function handler(e) { return { result: fetch.fetch(e) }; }
const response = handler("http://localhost:8000/api/v1/stocks");
console.log(response.result);
export { handler };
```
