# Why a Secure Sandbox is Non-Negotiable

LLM-generated code is **untrusted by definition**. Model output is non-deterministic, susceptible to [prompt injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/), and impossible to fully predict. Executing it without isolation exposes the host to data exfiltration, API key leakage, unrestricted network access, resource exhaustion, and filesystem tampering.

Every major platform enforcing code execution has arrived at the same conclusion: **strict sandboxing is mandatory**. OpenAI runs Code Interpreter inside ephemeral sandboxed containers with configurable memory limits (1 GB–64 GB) that [expire after 20 minutes of inactivity](https://developers.openai.com/api/docs/guides/tools-code-interpreter). Cloudflare uses [V8 isolates](https://developers.cloudflare.com/workers/reference/how-workers-works/) lightweight JavaScript runtimes that start in milliseconds, cost a fraction of containers, and are disposable after every execution. [Azure AI Foundry's Code Interpreter](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/code-interpreter) runs Python inside [Azure Container Apps dynamic sessions](https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter) isolated by a Hyper-V boundary, with no outbound network access and automatic session expiry. All three platforms enforce **network isolation**, **resource limits**, and the **principle of least privilege** code can only reach resources it has been explicitly given access to, whether through Cloudflare's [bindings model](https://blog.cloudflare.com/workers-environment-live-object-bindings/), OpenAI's scoped container files, or Foundry's per-session file attachments. Critically, none of these sandboxes expose **API keys to generated code**; authorization is always handled out-of-band by the agent supervisor.

## Sandbox Options

The following technologies can serve as the sandboxing backend for executing LLM-generated code:

### Hyperlight VM

[Hyperlight](https://github.com/hyperlight-dev/hyperlight) is a lightweight Virtual Machine Manager (VMM) and [CNCF sandbox project](https://www.cncf.io/) designed to be embedded within applications. It runs untrusted code inside **micro virtual machines** with millisecond startup and minimal memory overhead, using hardware-level isolation (KVM, mshv, or Windows Hypervisor Platform) — with **no kernel or OS in the guest**. This makes it ideal for ultra-low-latency, high-security sandboxing of individual code snippets where the strongest possible isolation boundary is required. See [hyperlight-vm](https://github.com/suneetnangia/hyperlight-vm) for a reference implementation exploring this approach.

### WebAssembly (Wasm)

[WebAssembly](https://webassembly.org/) is a portable bytecode format with a **memory-safe, sandboxed execution model built in**. Guests run in a linear-memory sandbox with no direct access to the host OS, filesystem, or network. Runtimes such as [Wasmtime](https://wasmtime.dev/) and [WasmEdge](https://wasmedge.org/) deliver near-native speed with fine-grained, capability-based security via [WASI](https://wasi.dev/) — host resources (files, sockets, clocks) are only available if explicitly granted. Wasm's cross-platform portability and small binary size make it well-suited for polyglot code execution scenarios. An [example](https://github.com/bytecodealliance/componentize-py/tree/main/examples/sandbox) of running Python script in a Wasm sandbox is provided here.

### OCI Containers

[OCI-compliant containers](https://opencontainers.org/) (Docker, containerd, [Kata Containers](https://katacontainers.io/)) isolate workloads using Linux namespaces, cgroups, and seccomp profiles with optional hardware VM backing (Kata) for stronger isolation. Containers offer the **broadest ecosystem and tooling support**, including pre-built images, registry infrastructure, and mature orchestration (Kubernetes). Startup is heavier than isolates or micro VMs, but the security model is well-understood, widely audited, and supported by every major cloud provider.

### Subprocess

The simplest approach: spawn a child process on the host to run the generated code ([`subprocess`](https://docs.python.org/3/library/subprocess.html) in Python, `child_process` in Node.js). This is the **lowest-friction option** no extra infrastructure, no images to build, instant startup. However, isolation is limited to OS-level process boundaries; you must layer on your own restrictions (dropping privileges, setting [resource limits](https://man7.org/linux/man-pages/man2/setrlimit.2.html), chroot/unshare, seccomp filters) to approach the security of the other options. Best suited for **trusted or low-risk workloads**, prototyping, and scenarios where the host environment is already hardened.

This repository uses the subprocess approach with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)'s `SkillScriptRunner` extensibility point. See the [MAF Agent Skills & Script Execution](https://devblogs.microsoft.com/agent-framework/whats-new-in-agent-skills-code-skills-script-execution-and-approval-for-python/) blog post for details on how skills can bundle executable scripts with approval gates and custom runners.

## References

| Topic | Link |
|---|---|
| OWASP Top 10 for LLM Applications | <https://owasp.org/www-project-top-10-for-large-language-model-applications/> |
| OpenAI Code Interpreter | <https://developers.openai.com/api/docs/guides/tools-code-interpreter> |
| Cloudflare V8 Isolates | <https://developers.cloudflare.com/workers/reference/how-workers-works/> |
| Cloudflare Bindings Model | <https://blog.cloudflare.com/workers-environment-live-object-bindings/> |
| Azure AI Foundry Code Interpreter | <https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/code-interpreter> |
| Azure Container Apps Dynamic Sessions | <https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter> |
