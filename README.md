# Advance Progressive Exposure with MAF

Demonstrates progressive exposure techniques for LLMs by combining Skills with dynamic code generation, built on the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework).

An orchestrator agent delegates tasks to skills: fetching web pages, running dynamically generated Python or JavaScript code, and performing portfolio risk analysis by chaining multiple Financial Data APIs.

The project includes **mock Financial Data APIs**, a **Code Execution API** for remote JavaScript execution, and two **risk analysis skills** (composed and decomposed) that demonstrate how an LLM agent can chain API calls with different execution strategies.

## Why Dynamic Code Generation?

> See [Why Dynamic Code Generation?](docs/why-dynamic-code-generation.md)

## Why a Secure Sandbox is Non-Negotiable

> See [Why a Secure Sandbox is Non-Negotiable](docs/why-secure-sandbox.md)

## Getting Started

This project includes a [Dev Container](https://containers.dev/) configuration that provides all required tooling (Python 3.13, uv, Azure CLI, Ruff) out of the box.

1. Open the repository in VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) installed.
2. When prompted, select **Reopen in Container** (or run **Dev Containers: Reopen in Container** from the Command Palette).
3. Dependencies are installed automatically when the container is created.

## Setup

### Configure environment variables

Copy the example file and fill in your Azure OpenAI details:

```bash
cp src/progressive_exposure/agents/.env.example src/progressive_exposure/agents/.env
```

Edit `src/progressive_exposure/agents/.env`:

```env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment-name>
REMOTE_CODE_EXECUTION_URL=http://localhost:8100
```

`REMOTE_CODE_EXECUTION_URL` defaults to `http://localhost:8100` and only needs to be changed when pointing at a remote execution service.

### Authenticate with Azure

Sign in to Azure before running the solution, the agent uses `DefaultAzureCredential` which relies on an active Azure CLI session:

```bash
az login
```

## Running

All commands below use `uv run`, which automatically manages the virtual environment with no need to activate it manually.

### CLI

```bash
uv run progressive-exposure
```

This starts an interactive loop where you can type messages to the orchestrator agent. Type `exit` or `quit` to stop.

### DevUI

Launch the Agent Framework DevUI for a browser-based interface:

```bash
uv run devui src/progressive_exposure/agents --port 8080
```

Then open `http://localhost:8080` in your browser.

### Debugging in VS Code

Launch configurations are provided in `.vscode/launch.json`:

- **Debug DevUI**: starts the DevUI server on port 8080
- **Debug CLI**: runs the interactive CLI
- **Stock Quotes API (:8001)**: runs the stock quotes API standalone
- **Portfolio Holdings API (:8002)**: runs the portfolio holdings API standalone
- **Market Indices API (:8003)**: runs the market indices API standalone
- **All Financial APIs (:8000)**: runs all 3 APIs on a single server

A compound configuration **All APIs + Dev UI** launches all 3 individual APIs plus the DevUI simultaneously.

Press **F5** and select a configuration to start debugging.

## Financial Data APIs

Three mock FastAPI services providing financial data, useful for demonstrating API chaining with the agent.

### Running

Start all APIs on a single server:

```bash
uv run uvicorn progressive_exposure.financial_apis.app:app --host 0.0.0.0 --port 8000 --reload
```

Or run each API individually:

```bash
uv run uvicorn progressive_exposure.financial_apis.stocks_app:app --host 0.0.0.0 --port 8001 --reload
uv run uvicorn progressive_exposure.financial_apis.portfolio_app:app --host 0.0.0.0 --port 8002 --reload
uv run uvicorn progressive_exposure.financial_apis.indices_app:app --host 0.0.0.0 --port 8003 --reload
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/stocks` | All stock quotes (10 tickers) |
| GET | `/api/v1/stocks/{ticker}` | Single stock quote (e.g., AAPL, MSFT, NVDA) |
| GET | `/api/v1/portfolio` | Portfolio holdings with summary (total value, P&L) |
| GET | `/api/v1/indices` | Market indices (S&P 500, NASDAQ, Dow Jones) |
| GET | `/api/v1/indices/{symbol}` | Single index (SPX, IXIC, DJI) |

Swagger UI is available at `http://localhost:8000/docs`.

## Code Execution API

A PoC FastAPI stub that accepts JavaScript code, logs it to the console, and returns a fixed response. This serves as a stand-in for a real remote code execution service (e.g., a QuickJS sandbox).

### Running

```bash
uv run uvicorn progressive_exposure.code_execution_api.app:app --host 0.0.0.0 --port 8100 --reload
```

Or via the project script:

```bash
uv run code-execution-api
```

### Endpoint

| Method | Path | Description |
|--------|------|-------------|
| POST | `/execute` | Execute JavaScript code remotely |

**Request:**
```json
{
  "code": "console.log('hello')"
}
```

**Response:**
```json
{
  "output": "Code received and logged successfully.",
  "exit_code": 0,
  "timed_out": false
}
```

Swagger UI is available at `http://localhost:8100/docs`.

### Configuration

The `run-javascript-code-remote` skill sends code to this API. The URL is controlled by the `REMOTE_CODE_EXECUTION_URL` environment variable (defaults to `http://localhost:8100`). To point at a real remote execution service, set:

```env
REMOTE_CODE_EXECUTION_URL=https://your-remote-service.example.com
```

## Skills

### read-web-page

Fetches and extracts readable content from a web page given a URL.

### risk-analysis-composed

Performs portfolio risk analysis by generating Python code that **chains all 3 Financial Data APIs in a single execution**. The agent writes code that calls indices, portfolio, and stock endpoints together, computes risk metrics, and runs it via the `run-python-code` skill.

### risk-analysis-decomposed

Performs the same risk analysis but **calls each API separately** in individual `run-python-code` invocations. The agent examines each response before deciding the next call, enabling step-by-step reasoning over intermediate results.

### run-javascript-code-remote

Sends dynamically generated JavaScript code to a remote execution service (the Code Execution API) and returns the output. All generated code must be **QuickJS-compliant** (ES2023 syntax, standard built-in objects only). Use `console.log()` for output. Functionality not natively available in QuickJS (e.g., HTTP requests) is provided via **plugins** — see below.

### QuickJS Plugins

The remote QuickJS environment provides dependency-injected plugins for functionality not natively available. Plugins are imported using ES module syntax (`import * as <name> from "<name>"`).

Plugin documentation lives in `src/progressive_exposure/agents/orchestrator/plugins/` as individual `.md` files. At startup, all plugin docs are automatically loaded and included in the `run-javascript-code-remote` skill content sent to the LLM.

**Current plugins:**

| Plugin | Import | Description |
|--------|--------|-------------|
| `indices` | `import * as indices from "indices"` | Market index data via `indices.get()` / `indices.get(symbol)` |
| `stocks` | `import * as stocks from "stocks"` | Stock quote data via `stocks.get()` / `stocks.get(ticker)` |
| `portfolios` | `import * as portfolios from "portfolios"` | Portfolio holdings via `portfolios.get()` |

#### Adding a new plugin

1. Create a new `.md` file in `src/progressive_exposure/agents/orchestrator/plugins/` (e.g., `crypto.md`)
2. Follow the standard template:

   ```markdown
   # <plugin-name>

   <Brief description of what the plugin provides.>

   ## Import
   ```javascript
   import * as <name> from "<name>";
   ```

   ## Functions

   ### `<name>.<function>(args)`
   <Description of what the function does.>

   **Parameters:**
   - `<arg>` (<type>) — <description>

   **Returns:** <type> — <description>

   ## Example
   ```javascript
   import * as <name> from "<name>";
   // usage example
   ```

   ## Notes
   - <Any important caveats or restrictions>
   ```

3. Restart the agent — the plugin docs are loaded automatically at startup. No changes to `__init__.py` or any SKILL.md files are needed.

### Persona & Example Prompts

Both risk analysis skills implement **[Persona 3: Emily, 30, Risk Analyst at a hedge fund](src/progressive_exposure/financial_apis/PERSONAS.md#persona-3-risk-analyst)**. Example prompts:

- *"If the NASDAQ drops 2% today, which of our holdings are most exposed?"*
- *"What's our total unrealized P&L and how does each position's daily move compare to its benchmark index?"*

See [`PERSONAS.md`](src/progressive_exposure/financial_apis/PERSONAS.md) for all 3 finance personas and their API chaining scenarios.

## Development

All tasks use [poethepoet](https://poethepoet.naber.me/) and can be run with `poe`:

```bash
poe lint            # Lint with ruff
poe format          # Format with ruff
poe format-check    # Check formatting
poe typecheck       # Type check with pyright
poe test            # Run tests with pytest
poe check           # Run all of the above
```

## Next Steps

- **Scalable skill configuration** — Find a more robust way to provide configuration values (e.g., API base URLs, feature flags) to skill definitions at runtime, rather than relying on string substitution or hardcoded defaults scattered across SKILL.md files.
- **Formal plugin specification** — Replace the current free-form Markdown plugin docs with a structured, machine-readable spec (similar to OpenAPI) that can be validated, versioned, and used to auto-generate the plugin documentation injected into skill content.
