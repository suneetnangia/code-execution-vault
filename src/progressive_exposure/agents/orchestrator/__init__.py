import logging
import os
from pathlib import Path

import agent_framework.azure
import azure.identity
from progressive_exposure.agents.orchestrator import orchestrator_agent
from . import subprocess_inline_script_runner
from . import subprocess_file_script_runner
from . import remote_script_runner

logger = logging.getLogger(__name__)

# Discover skills from the orchestrator 'skills' directory
skills_dir = Path(__file__).parent / "skills"
skill_files = list(skills_dir.glob("*/SKILL.md"))
if not skill_files:
    logger.warning("No valid skills found in %s", skills_dir)
else:
    logger.info("Discovered %d skill(s) in %s", len(skill_files), skills_dir)

run_code_skill = agent_framework.Skill(
    name="run-python-code",
    description=(
        "Executes dynamically generated Python code in an isolated subprocess and returns the output. "
        "Use this skill when the user asks to perform mathematical calculations, data transformations, "
        "string manipulation, algorithmic problem-solving, or any task that benefits from precise "
        "programmatic computation rather than plain-text reasoning. "
        "Also suitable for generating formatted output, validating logic, or prototyping small scripts."
    ),
    content="""
# Run Python Code

## When to use this skill
Use this skill when the user needs to:
- Perform mathematical calculations or numeric analysis
- Run a Python code snippet or prototype a small script
- Do data transformations, string manipulation, or formatting
- Solve algorithmic problems or validate logic programmatically
- Any task that benefits from precise programmatic computation rather than plain-text reasoning

## Usage
Run the `execute` script with the `code` parameter containing the Python source code.
The code runs in an isolated subprocess with a 30-second timeout.

## Limitations
- Maximum code size: 10 KB
- Execution timeout: 30 seconds
- No access to environment variables or secrets
- Output is truncated at 50,000 characters
    """,
)


@run_code_skill.script(
    name="execute",
    description="Execute Python code and return the output.",
)
def execute_code(code: str) -> str:
    return subprocess_inline_script_runner.inline_script_runner(code)


# Discover plugins from the orchestrator 'plugins' directory
plugins_dir = Path(__file__).parent / "plugins"
plugin_files = sorted(plugins_dir.glob("*.md"))
if plugin_files:
    logger.info("Discovered %d plugin(s) in %s", len(plugin_files), plugins_dir)
    plugin_docs = "\n\n".join(f.read_text() for f in plugin_files)
else:
    logger.warning("No plugins found in %s", plugins_dir)
    plugin_docs = "(No plugins available)"

_JS_SKILL_CONTENT = f"""
# Run JavaScript Code (Remote)

## When to use this skill
Use this skill when the user needs to:
- Execute JavaScript code for calculations, data processing, or logic
- Prototype a JavaScript snippet or validate JS-based logic
- Perform tasks that specifically require JavaScript (e.g., JSON manipulation, regex, string operations)
- Any task where JavaScript is preferred over Python

## Usage
Run the `execute` script with the `code` parameter containing the JavaScript source code.
The code is sent to a remote execution service running QuickJS.

## CRITICAL — Data Access
QuickJS has NO built-in HTTP capability. There is no global `fetch()`, no `XMLHttpRequest`, no `http` module.

To access financial data, you MUST use the provided plugins:
```javascript
import * as indices from "indices";
import * as stocks from "stocks";
import * as portfolio from "portfolio";

const allIndices = indices.get();                     // Array | null
const nasdaq = indices.get("IXIC");                   // Object | null
const allStocks = stocks.get();                       // Array | null
const apple = stocks.get("AAPL");                     // Object | null
const portfolioData = portfolio.get();                // Object | null

// Always check for null before accessing properties
if (nasdaq !== null) {{
  const changePercent = nasdaq.change_percent;
}}
```

**NEVER use `fetch()`, `http`, or any URL-based API call.** They do not exist.
You MUST use the plugin imports above to retrieve data.
All plugin `.get()` methods return `null` when no results are found — always check before accessing properties.
Plugin return values are already typed objects — do NOT call `JSON.parse()` on them.

## CRITICAL — Handler Function Format
All generated code MUST be wrapped in a `handler` function that is exported. The remote execution
environment calls this function at runtime. Code that is not wrapped in a handler will fail.

**Required structure:**
```javascript
import * as indices from "indices";

function handler(e) {{
  const dji = indices.get("DJI");
  if (dji !== null) {{
    return dji;
  }}
  return null;
}}

export {{ handler }};
```

Rules:
- ALL imports go at the top of the file, before the handler function
- ALL logic MUST be inside the `handler(e)` function
- The handler MUST be exported via `export {{ handler }};` as the last line
- Do NOT place any executable code outside the handler function
- Do NOT use `console.log()` for output — return data from the handler instead
- **NEVER use single quotes.** All strings MUST use double quotes (e.g., `"AAPL"`, not `'AAPL'`)

## Code Guidelines — QuickJS Compliance
All generated code MUST be QuickJS-compliant. QuickJS supports ES2023 syntax but is NOT Node.js.

### Supported
- `function handler(e) {{ ... }}` with `export {{ handler }};` — required structure for all code
- `const` and `let` for variable declarations
- Arrow functions, template literals, destructuring, spread/rest operators
- `async`/`await` and Promises
- Standard built-in objects: `JSON`, `Math`, `Date`, `RegExp`, `Map`, `Set`, `Array`, `Object`, `String`, `Number`, `BigInt`, `Symbol`, `Proxy`, `Reflect`
- `for...of`, `for...in`, generators, iterators
- Classes, optional chaining (`?.`), nullish coalescing (`??`)
- Plugins provided by the remote API via `import * as <name> from "<name>"` (see Plugins section below)

### NOT Supported (do NOT use)
- **`fetch()` — does NOT exist.** Use the `indices`, `stocks`, and `portfolio` plugins instead
- `require()` — use `import * as <name> from "<name>"` for plugins only
- Node.js built-in modules (`fs`, `path`, `http`, `https`, `crypto`, `url`, `child_process`, etc.)
- `XMLHttpRequest` or any other network APIs
- URL-based API calls of any kind — use plugins
- Browser APIs (`document`, `window`, `alert`, `setTimeout`, `setInterval`, etc.)
- `Buffer`, `process`, `__dirname`, `__filename`
- npm packages of any kind
- `import` of arbitrary modules — only plugin modules provided by the remote API are available

## Plugins

The remote QuickJS environment provides dependency-injected plugins for functionality not natively available.
Import them using ES module syntax: `import * as <name> from "<name>"`

{plugin_docs}

## Limitations
- Maximum code size: 10 KB
- Execution timeout: 60 seconds
- No access to environment variables or secrets
- Output is truncated at 50,000 characters
- No external modules or packages — only ECMAScript built-ins and remote API plugins
"""

run_js_remote_skill = agent_framework.Skill(
    name="run-javascript-code-remote",
    description=(
        "Sends dynamically generated JavaScript code to a remote execution service and returns the output. "
        "Use this skill when the user asks to perform tasks using JavaScript, such as data transformations, "
        "string manipulation, algorithmic problem-solving, JSON processing, access financial data, or any task that benefits from "
        "precise programmatic computation using JavaScript rather than Python. "
        "The code runs in a remote QuickJS environment. All generated code must be QuickJS-compliant."
    ),
    content=_JS_SKILL_CONTENT,
)


@run_js_remote_skill.script(
    name="execute",
    description="Execute JavaScript code remotely and return the output.",
)
def execute_js_code(code: str) -> str:
    return remote_script_runner.remote_script_runner(code)


skills_provider = agent_framework._skills.SkillsProvider(
    skill_paths=skills_dir,
    skills=[run_code_skill, run_js_remote_skill],
    script_runner=subprocess_file_script_runner.subprocess_script_runner,
)

history_provider = agent_framework.InMemoryHistoryProvider()

chat_client = agent_framework.azure.AzureOpenAIChatClient(
    endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    credential=azure.identity.DefaultAzureCredential(),
)

agent = orchestrator_agent.OrchestratorAgent(
    chat_client, context_providers=[skills_provider, history_provider]
)
