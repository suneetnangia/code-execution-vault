/**
 * Simple JavaScript code execution API.
 *
 * POST /api/execute
 * Body: { "code": "<javascript source>" }
 * Response: plain-text stdout output from the executed code.
 *
 * The code runs in an isolated child process with a timeout.
 * No external dependencies — uses only Node.js built-in modules.
 */

const http = require("http");
const { execFile } = require("child_process");
const path = require("path");

const PORT = process.env.PORT || 3000;
const EXECUTION_TIMEOUT = 30_000; // 30 seconds
const MAX_CODE_SIZE = 10 * 1024; // 10 KB
const MAX_OUTPUT_SIZE = 50_000; // characters
const MAX_BODY_SIZE = 64 * 1024; // 64 KB request body limit

/**
 * Execute JavaScript code in a child process and return the output.
 */
function executeCode(code) {
  return new Promise((resolve) => {
    const child = execFile(
      process.execPath, // path to node binary
      ["-e", code],
      {
        timeout: EXECUTION_TIMEOUT,
        maxBuffer: MAX_OUTPUT_SIZE * 2,
        env: {
          // Minimal environment — no leaking of host env vars
          PATH: "/usr/local/bin:/usr/bin:/bin",
          NODE_ENV: "sandbox",
        },
        cwd: "/tmp",
      },
      (error, stdout, stderr) => {
        if (error) {
          if (error.killed) {
            resolve(`Error: Execution timed out after ${EXECUTION_TIMEOUT / 1000} seconds.`);
            return;
          }
          // Include stderr for syntax/runtime errors
          const errOutput = stderr || error.message;
          resolve(`Error: ${errOutput}`);
          return;
        }

        let output = stdout;
        if (stderr) {
          output += `\nStderr:\n${stderr}`;
        }

        // Truncate if too large
        if (output.length > MAX_OUTPUT_SIZE) {
          output = output.slice(0, MAX_OUTPUT_SIZE) + "\n... (output truncated)";
        }

        resolve(output);
      }
    );
  });
}

const server = http.createServer(async (req, res) => {
  // Only accept POST /api/execute
  if (req.method === "POST" && req.url === "/api/execute") {
    let body = "";
    let bodySize = 0;

    req.on("data", (chunk) => {
      bodySize += chunk.length;
      if (bodySize > MAX_BODY_SIZE) {
        res.writeHead(413, { "Content-Type": "text/plain" });
        res.end("Error: Request body too large.");
        req.destroy();
        return;
      }
      body += chunk;
    });

    req.on("end", async () => {
      let code;
      try {
        const parsed = JSON.parse(body);
        code = parsed.code;
      } catch {
        res.writeHead(400, { "Content-Type": "text/plain" });
        res.end("Error: Invalid JSON. Expected { \"code\": \"...\" }");
        return;
      }

      if (!code || typeof code !== "string" || !code.trim()) {
        res.writeHead(400, { "Content-Type": "text/plain" });
        res.end("Error: No code provided.");
        return;
      }

      if (code.length > MAX_CODE_SIZE) {
        res.writeHead(400, { "Content-Type": "text/plain" });
        res.end(`Error: Code exceeds maximum size of ${MAX_CODE_SIZE} bytes.`);
        return;
      }

      const output = await executeCode(code);
      res.writeHead(200, { "Content-Type": "text/plain" });
      res.end(output);
    });

    return;
  }

  // Health check
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  res.writeHead(404, { "Content-Type": "text/plain" });
  res.end("Not found");
});

server.listen(PORT, () => {
  console.log(`JS execution API listening on http://localhost:${PORT}`);
});
