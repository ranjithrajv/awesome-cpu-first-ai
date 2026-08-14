# Changelog

All notable additions and changes to awesome-cpu-first-ai.

---

## 2026-08-14

- **On-Device**: Added Off Grid AI (OGAM) — an MIT-licensed cross-platform offline AI suite (Android, iOS, macOS; React Native) that runs any GGUF model via llama.cpp on CPU (15–30 tok/s on flagship) with optional OpenCL (Adreno) / Metal (Apple Silicon) GPU and experimental Snapdragon Hexagon NPU acceleration behind automatic backend detection, plus on-device vision (SmolVLM, Qwen3-VL), Whisper speech-to-text, Stable Diffusion image generation, tool calling, MCP integration, a project knowledge base with on-device embeddings, and local-network OpenAI-compatible server support. Fully offline, no account or API key; per-model RAM management with lean/balanced/aggressive loading policies. Added to the On-device apps listing under Mobile Phone CPUs and to the End-User Apps subsection of docs/mobile-cpu-inference.md.
- **On-Device / MoE**: Added BigMoeOnEdge — an Android + desktop engine built on llama.cpp's public API (not a fork) that runs MoE models larger than the device's RAM on CPU alone, losslessly, by keeping the always-needed layers resident and reading only the experts each token routes to from flash storage, with a capped expert cache and multi-shard gguf support (no merge step). Runs DeepSeek V4 Flash 0731 (284B params, ~91 GB on disk) on a 12 GB phone at ~1 tok/s, plus gpt-oss-120b, Qwen3-30B-A3B, and Gemma-4-26B-A4B, with byte-identical output to the fully resident run (Apache 2.0). Added to On-Device, Edge, ARM, and SBCs and cross-listed under Mixture-of-Experts on CPU, and mapped in the R&D ideas playbook matrix as the phone manifestation of the four-idea streaming playbook.
- **On-Device**: Added RunAnywhere SDKs — production cross-device local-AI SDK toolkit (Android, iOS, React Native, Flutter, web, C++, server) over one C++ core covering LLM chat, VLM, speech, TTS, voice agents, embeddings, RAG, and image generation, offline by design with a capability registry routing each call to the best engine on the device (llama.cpp-based LLM path). Flagged with a non-OSI license caveat (free for individuals, small orgs <$1M funding, education, nonprofits; commercial license beyond). Also added cactus — low-latency hybrid edge-cloud AI engine for mobile devices and wearables (Apple, Samsung, Pixel SoCs) with CPU/GPU kernels, rotation-based quantization, zero-copy computation graph, built-in RAG, and OpenAI-compatible text/speech/vision APIs; flagged with the same commercial-gated license caveat (<$2M funding/revenue threshold).
- **Runtimes**: Added TinyChatEngine — MIT Han Lab's on-device LLM/VLM inference library (MLSys 2024 Best Paper) implementing AWQ W4A16 low-precision weights in from-scratch C/C++, running on x86, ARM (Apple M1/M2, Raspberry Pi), and CUDA (MIT; last updated 2024). Added a row to the runtime comparison table. Also added Qualcomm GenieX — the community version of Qualcomm's GENIE on-device GenAI runtime, running any GGUF model across Hexagon NPU, Adreno GPU, or CPU with CLI/Python/Kotlin/Docker/OpenAI-compatible-server interfaces (BSD-3-Clause, Snapdragon-only); added to Runtimes, the NPU runtime table, and On-Device. (GenieX is the successor home of the former NexaAI/nexa-sdk project.)

## 2026-08-05

- **Runtimes / MoE**: Added kimi-k3-in-c — portable C99 inference engine running the 2.78T-parameter Kimi K3 MoE model on a single CPU in 8.24 GB RAM (measured peak RSS), streaming the 1.45 TB of routed experts from disk in packed mxfp4 form with no BLAS/framework/GPU; produces byte-identical output at any memory budget from 8 GB to 224 GB (Apache 2.0). Added to Runtimes, Mixture-of-Experts on CPU, and the runtime comparison table. Also added midge — spec-driven C engine running gpt-oss/Mixtral/Qwen3-MoE on ordinary CPU machines by streaming packed 4-bit experts from disk, with an OpenAI-compatible server (Apache 2.0) — and hummingbird — zero-dependency C17 runtime unifying SSD/RAM/VRAM with io_uring-backed expert streaming, model-agnostic across GPT-OSS/GLM/DeepSeek/Qwen (Apache 2.0, placeholder LICENSE). Both added to Runtimes, Mixture-of-Experts on CPU, and the comparison table.
- **On-Device**: Added turbo-fieldfare — model-specific Swift + Metal runtime running Gemma 4 26B-A4B in ~2 GB RAM on any Apple Silicon Mac (even 8 GB) by streaming only the routed experts needed per token from SSD (Apache 2.0). Flagged as executing on Apple's Metal GPU rather than the CPU; listed for its expert-streaming memory-efficiency approach on on-device ARM hardware. Also added four Apple-Silicon expert-streaming engines to the same section with the same Metal/MLX caveat: mlx-od-moe (mmap'd experts + shadow-model prefetch, Kimi-K2.5 375 GB in 192 GB RAM, MIT), moe-stream (Rust + Metal SSD streaming, 80B models on 24 GB Macs, Apache 2.0), s-moe (NVMe streaming with Direct I/O prefetch, Qwen3-235B on 48 GB MacBooks, MIT), and sparsify (SSD expert paging, Mixtral 26.3 GB in 3.33 GB RSS, MIT).
- **Docs**: Added [CPU-First Inference R&D Ideas](docs/cpu-first-rd-ideas.md) — documents the four core ideas behind kimi-k3-in-c (bounded resident working set, storage streaming, on-demand expert loading, expert LRU caching) with a living R&D idea tracker scoped to more ideas accelerating CPU-first inference. Added a new "R&D ideas & techniques" subsection to the README Docs section. Extended the doc with a lineage section tracing the neuron-level hot/cold split (PowerInfer, SOSP 2024) to today's expert-level disk streaming, and added tracker rows for learned shadow-model prefetch (mlx-od-moe), OS page-cache/mmap paging (midge, mlx-od-moe), io_uring/Direct I/O pumps (hummingbird, s-moe), and spec-driven model-agnostic engines (midge, hummingbird). Further enhanced the doc with six Mermaid diagrams (engine architecture, memory-budget dial, cache hit/miss sequence, idea dependency chain, lineage timeline, bottleneck shift) plus new sections: "The Memory Budget Dial" (measured `laptop` 8.24 GB @ 32.69 s/token vs `server` 127.92 GB @ 10.69 s/token endpoints and the max(compute, storage) cost model) and "The Playbook Across the Ecosystem" (a matrix mapping which of the four ideas each engine in the lineage implements).
- **Papers/Articles**: Added "Kimi K3 runs on 8GB CPU, No GPU" (Data Science in Your Pocket, Aug 2026) to Talks, Papers, and Articles.

## 2026-07-16

- **Runtimes**: Added distributed-llama — MIT-licensed tensor-parallel inference that splits a model's compute and RAM across a cluster of ARM/x86 AVX2 CPU nodes (power-of-2 node counts), letting commodity or Raspberry Pi devices jointly run models too large for a single machine; experimental Vulkan GPU support. Added a row to the runtime comparison table

## 2026-07-28

- **Runtimes**: Added ArcLight — many-core CPU inference framework for NUMA systems with tensor parallelism (OpenBMB, MIT, 46% higher throughput than llama.cpp). Added cpubrrr — from-scratch NEON/SME kernels in Rust for MoE inference on Apple M4 (Apache 2.0, claims 110 tok/s for gpt-oss:20b). Added Ferrite — CPU-native Rust inference engine with pure Rust SIMD, no GPU code paths (Apache 2.0). Added MojoLlama — high-throughput CPU inference engine built on Modular MAX with Mojo backend, MoE-optimized (Apache 2.0). Added Project Zero — pure C BitNet inference engine requiring no SIMD, ~1,000 tok/s on 1.58-bit models (MIT). Added Reame — CPU-first inference server on llama.cpp with disk KV cache and self-regulating speculation (MIT). Updated runtime comparison table with all six entries.
- **Papers**: Added FairyFuse — multiplication-free ternary inference on CPU, 3.6× speedup over GGML (arXiv:2607.17751). Added AdaptiveSD — speculative decoding for CPU-only inference, 1.9× speedup (arXiv:2603.19254). Added SMEPilot — ARM SME instruction optimization for CPU inference (arXiv:2607.11141).

## 2026-07-15

- **Runtimes**: Added bitnet.cpp — Microsoft's official inference framework for 1-bit / 1.58-bit ternary LLMs, with CPU-optimized x86/ARM kernels (2.4–6.2× speedup, 71.9–82.2% energy reduction on x86 vs llama.cpp; runs a 100B b1.58 model on a single CPU at 5–7 tok/s); added a row to the runtime comparison table
- **Quantization**: Added "Ternary / 1-bit models (BitNet b1.58 lineage)" entry explaining ternary/binary weights as a CPU-native technique, with Bonsai 27B (PrismML, Jul 2026 — 1-bit ~3.9 GB / 1.58-bit ~5.9 GB GGUF, Apache 2.0, ~11 tok/s on iPhone 17 Pro CPU) as a flagship example. Vendor-reported benchmarks flagged as such
- **Mobile Phone CPUs**: Noted the Bonsai 27B on-phone-CPU datapoint as evidence of ternary quantization pushing 27B-class models onto phones

## 2026-07-13

- **Model Selection**: Added new "Model Selection and Hardware Fit" section — tools that read your RAM/CPU/GPU and rank which models will actually run well: llmfit (terminal, 0–100 Fit score, Ollama/llama.cpp launch, simulation mode), whichllm (CLI, benchmark-ranked not param-count), and Local AI Master Model Recommender (browser, CPU-only + Apple Silicon aware)
- **Runtimes**: Added LiteRT.js — Google AI Edge's in-browser ML runtime (WebAssembly CPU via XNNPACK, WebGPU optional), with a new row in the runtime comparison table
- **On-Device**: Annotated TensorFlow Lite entry to note LiteRT as its official successor (same `.tflite` format, same XNNPACK CPU backend); expanded XNNPACK entry to cross-link LiteRT/LiteRT.js, ExecuTorch, and ONNX Runtime mobile as consumers
- **Multimodal**: Added PocketTTS (Kyutai Labs, 100M params, CPU-first TTS with voice cloning, ~6× real-time on M4) and PocketTTS.cpp (single-file C++/ONNX port, 9.2× real-time INT8) to TTS subsection and README key-tools line
- **Multimodal**: Added transcribe.cpp (handy-computer, ggml/GGUF STT library for 16+ ASR model families — Parakeet, Canary, Moonshine, Voxtral, etc., CPU-default via tinyBLAS, 60+ WER-validated GGUFs) to ASR/STT subsection and README key-tools line
- **README**: Fixed dangling "Pi-phi TTS" placeholder in *What's New* → PocketTTS
- **Gap Map**: Added [CPU AI Gap Map](docs/cpu-ai-gap-map.md) — a scored assessment of the CPU-first AI tooling landscape across 10 workload categories (LLM decode, LLM prefill, ASR/STT, TTS, embeddings, vision detection, vision segmentation, OCR, image generation, fine-tuning), grading CPU-nativeness, CPU performance, architecture coverage, and adoption. README summary dashboard added between Benchmarks and On-Device sections.

## 2026-06-27

- **MoE**: Added new "Mixture-of-Experts on CPU" section with DeepSeek-R1 paper, Arm Graviton4 deployment guide, and OCI Ampere A1 practitioner guide
- **On-Device**: Added Intel Core Ultra with OpenVINO, AMD Ryzen AI Software (VitisAI EP), and MediaTek Genio 720/520 edge AI platforms
- **Runtimes**: Added runtime comparison matrix (12 runtimes × format × CPU arch × OS)
- **Vision**: Added new "Vision on CPU" section with YOLOv8+OpenVINO benchmarks, Ultralytics production guide, CLIP-ONNX benchmarks, clip.cpp, and DFN5B-CLIP INT8 ONNX
- **Multimodal**: Added new "Multimodal CPU Workloads" section with Speech/Audio (ASR/STT, Audio Embeddings, VAD & Diarization), Text (TTS), Documents (OCR), and Images (Classification, Segmentation, Generation, Background Removal, Face Analysis) subsections

## 2026-06-26

- **Talks**: Added SiFive RISC-V LLM deployment blog post (#2), Phi-3 Technical Report + PocketLLM iPhone bake-off (#5), Lenovo Press TCO analysis + NAVER GPU-to-CPU migration case study (#4)
- **Runtimes**: Added Transformers.js (WebAssembly CPU inference via ONNX Runtime Web)
- **Benchmarks**: Added MLPerf v5.0 datacenter CPU submissions, ONNX Runtime GenAI CPU benchmark, OpenVINO Model Hub benchmarks
- **Cost**: Added TCO worked example (7B Q4, 1 req/s, $5,740/yr savings vs GPU)
- **On-Device**: Added Core ML (Apple Silicon M-series CPU inference)
- **Introduction**: Added Hugging Face model size distribution data (40–51% sub-7B, 55–65% sub-13B, median 406M params)
- **Decision table**: Lean CPU column now reads "~60% of HF models", Lean GPU "< 8% of models"
- **Performance Tuning**: AMX entry now quantifies advantage as 2,048 INT8 ops/cycle vs 256 for AVX-512 VNNI
- **Cloud ARM**: Added Azure Cobalt 200 (Neoverse V3) and AWS Graviton4 (c8g) entries
- **Docs**: Added `docs/cpu-inference-deployment.md` (Docker, K8s, NUMA, system tuning, serving patterns)
- **CONTRIBUTING.md**: Added exception for reproducible benchmark data from recognized practitioners
- **README.md**: Aligned wording of "slow fallback" criterion between README and CONTRIBUTING
- **Infra**: Added `.gitignore`

## 2026-06-25

- Initial public version
