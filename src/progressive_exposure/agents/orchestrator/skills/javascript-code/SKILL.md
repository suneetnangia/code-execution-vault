---
name: javascript-code
description: >
  Executes JavaScript code on a remote execution service and returns the output.
  Use when the user asks to run JavaScript code, or when a task would benefit from
  JavaScript execution (e.g., JSON manipulation, string processing, algorithmic problems,
  or web-related computations). Also use this skill when the user provides code in Python
  or another language and asks to convert it to JavaScript before running it.
metadata:
  author: progressive-exposure
  version: "1.0"
---

# Run JavaScript Code

## When to use this skill

Use this skill when the user needs to:
- Run a JavaScript code snippet or prototype a small script
- Perform calculations, data transformations, or string manipulation in JavaScript
- Convert Python or other language code to JavaScript and execute it
- Solve algorithmic problems using JavaScript
- Work with JSON data processing or manipulation
- Any task where the user explicitly asks for JavaScript execution

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

- Always generate valid JavaScript (ES6+ syntax is supported)
- Use `console.log()` to produce output (equivalent to Python's `print()`)
- When converting from Python, ensure language-specific constructs are properly translated
- The code is executed on a remote service — do not assume access to the local filesystem
- Do not include `require()` or `import` statements for external packages unless you know they are available on the remote service
- Standard built-in JavaScript objects and methods are available (Math, JSON, Array, String, etc.)
