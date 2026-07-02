# Quick Start

Three paths from zero to CPU inference — no GPU, no CUDA, no container.

---

## Contents

- [Desktop (llamafile — zero install)](#desktop-llamafile--zero-install)
- [Server / CLI (ollama)](#server--cli--ollama)
- [Browser (WebLLM — WASM / CPU fallback)](#browser-webllm--wasm--cpu-fallback)
- [See also](#see-also)

---

## Desktop (llamafile — zero install)

A self-contained executable that runs on Linux, macOS, and Windows with no dependencies.

```bash
curl -LO https://huggingface.co/mozilla-ai/llamafile_0.10/resolve/main/Qwen3.5-0.8B-Q8_0.llamafile
chmod +x Qwen3.5-0.8B-Q8_0.llamafile
./Qwen3.5-0.8B-Q8_0.llamafile        # opens chat UI at http://localhost:8080
```

---

## Server / CLI (ollama)

Manages model downloads and exposes an OpenAI-compatible API endpoint.

```bash
curl -fsSL https://ollama.com/install.sh | sh   # Linux / macOS
ollama run llama3.2:3b                           # pulls Llama-3.2 3B Q4 (~2 GB) and opens CLI chat
```

---

## Browser (WebLLM — WASM / CPU fallback)

Runs the model in a browser tab — no server, no API key.

```bash
npm install @mlc-ai/web-llm
```

```javascript
import { CreateMLCEngine } from "@mlc-ai/web-llm";
const engine = await CreateMLCEngine("Llama-3.2-1B-Instruct-q4f32_1-MLC");
const { choices } = await engine.chat.completions.create({
  messages: [{ role: "user", content: "Hello" }],
});
console.log(choices[0].message.content);
```

*(WebLLM uses WebGPU when available and falls back to WebAssembly on CPU-only browsers.)*

---

## See also

- [CPU Inference Deployment Guide](cpu-inference-deployment.md)
- [Model Conversion Guide](model-conversion-guide.md)
- [Serverless CPU Patterns](serverless-patterns.md)