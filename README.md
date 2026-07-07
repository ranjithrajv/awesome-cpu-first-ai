# Awesome CPU-First AI [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> Training needs GPUs. Inference usually doesn't. Start with CPU; justify the GPU.

🌐 **Browse as a website:** <https://ranjithrajv.github.io/awesome-cpu-first-ai/>

A curated list of runtimes, formats, tools, and evidence for running AI inference on CPU — the platform you already have everywhere.

---

## Introduction

Most AI practitioners default to GPU for everything because that is where training lives. But once a model is trained, the inference workload often fits comfortably on a modern CPU: smaller batch sizes, modest throughput requirements, and quantized models that slip inside L3 cache. Independent analysis of the Hugging Face ecosystem finds 40–51% of models are sub-7B and 55–65% are sub-13B parameters — 92% of all downloads go to models under 1B params and the median downloaded model is just 406M params. The vast majority of inference workloads people actually run never needed a GPU. This list is for engineers who want to question that GPU default and reach for the right tool instead of the expensive one. It is aimed at practitioners deploying inference on servers, laptops, edge devices, or serverless functions — anywhere a GPU is absent, costly, or simply overkill. The list is GPU-skeptical, not GPU-hostile; the **When You Actually Do Want a GPU** section below is load-bearing, not decorative.

---

## Quick Start

Three paths from zero to CPU inference — no GPU, no CUDA, no container: **llamafile** (desktop, zero install), **ollama** (server / CLI), or **WebLLM** (browser, WebAssembly). All three are listed with source links under Runtimes and Inference Engines below.

See [docs/quickstart.md](docs/quickstart.md) for the full walkthroughs with copy-paste commands and sample code.

---

## When to Opt for CPU vs GPU

| Dimension               | Lean CPU                                                      | Lean GPU                                                   |
| ----------------------- | ------------------------------------------------------------- | ---------------------------------------------------------- |
| **Workload type**       | Inference                                                     | Training, fine-tuning                                      |
| **Model size**          | ≤ 13B params (quantized) — covers ~60% of Hugging Face models | 70B+ params, dense/unquantized — covers < 8% of models     |
| **Throughput need**     | Low-to-medium (single-digit req/s)                            | High (hundreds of req/s, batched)                          |
| **Batch size**          | Batch = 1 or small ad-hoc bursts                              | Large, sustained batched serving                           |
| **Latency SLA**         | Relaxed (100 ms–2 s TTFT tolerable)                           | Tight (< 50 ms TTFT on large models)                       |
| **Context length**      | Short-to-medium (≤ 8 K tokens)                                | Very long (32 K+ tokens, prefill-heavy)                    |
| **Deployment target**   | Edge, on-device, serverless, SBC                              | Dedicated inference cluster                                |
| **Cost / availability** | CPU instances are ubiquitous; no VRAM cap                     | GPU instances cost 5–20× more; VRAM is a hard ceiling      |
| **Modality**            | Text, embeddings, small audio                                 | Real-time diffusion, video generation, large vision models |

---

## Decision Flowchart

```mermaid
flowchart TD
    A([New inference workload]) --> B{Model size\nafter quantization?}

    B -- "≥ 70 B params\nor > 24 GB VRAM needed" --> GPU_SIZE["⛔ GPU\nVRAM requirement alone\nforces the choice"]

    B -- "≤ 13 B params\nfits quantized in RAM" --> C{Throughput\nrequirement?}

    C -- "Hundreds of req/s\nor large sustained batches" --> GPU_TPUT["⛔ GPU\narithmetic throughput\nis decisive at scale"]

    C -- "Single-digit req/s\nor batch = 1" --> D{TTFT latency\nSLA?}

    D -- "< 50 ms TTFT required" --> GPU_LAT["⛔ GPU\nmemory bandwidth needed\nfor large-model latency"]

    D -- "100 ms – 2 s\nTTFT acceptable" --> E{Context\nlength?}

    E -- "> 32 K tokens\nprefill-heavy" --> GPU_CTX["⛔ GPU\nprefill is a large\nmatrix multiply"]

    E -- "≤ 8 K tokens" --> F{Deployment\ntarget?}

    F -- "Edge / SBC / mobile\nbrowser / offline" --> CPU_EDGE["✅ CPU\nllama.cpp · ncnn\nExecuTorch · TFLite"]

    F -- "Cloud / on-prem server" --> G{Traffic\npattern?}

    G -- "Sporadic / bursty\n< 10 req/min average" --> CPU_SLS["✅ Serverless CPU\nLambda arm64 · Fly.io\nModal CPU — pay per use"]

    G -- "Sustained load" --> H{GPU utilization\nif you provisioned one?}

    H -- "Idle > 50 % of the time" --> CPU_IDLE["✅ CPU\nidle CPU instance\ncosts less than idle GPU"]

    H -- "Busy > 50 % of the time" --> GPU_ECON["⛔ GPU\n$/token favours GPU\nat high sustained load"]

    style CPU_EDGE fill:#1b5e20,color:#fff,stroke:#1b5e20
    style CPU_SLS  fill:#1b5e20,color:#fff,stroke:#1b5e20
    style CPU_IDLE fill:#1b5e20,color:#fff,stroke:#1b5e20
    style GPU_SIZE fill:#7f1d1d,color:#fff,stroke:#7f1d1d
    style GPU_TPUT fill:#7f1d1d,color:#fff,stroke:#7f1d1d
    style GPU_LAT  fill:#7f1d1d,color:#fff,stroke:#7f1d1d
    style GPU_CTX  fill:#7f1d1d,color:#fff,stroke:#7f1d1d
    style GPU_ECON fill:#7f1d1d,color:#fff,stroke:#7f1d1d
```

---

## Contents

- [Quick Start](#quick-start)
- [When to Opt for CPU vs GPU](#when-to-opt-for-cpu-vs-gpu)
- [Decision Flowchart](#decision-flowchart)
- [Runtimes and Inference Engines](#runtimes-and-inference-engines)
- [Quantization and Model Formats](#quantization-and-model-formats)
- [Performance Tuning](#performance-tuning)
- [Mixture-of-Experts on CPU](#mixture-of-experts-on-cpu)
- [Benchmarks and Evidence](#benchmarks-and-evidence)
- [On-Device, Edge, ARM, and SBCs](#on-device-edge-arm-and-sbcs)
- [Vision on CPU](#vision-on-cpu)
- [Multimodal CPU Workloads](#multimodal-cpu-workloads)
- [Cloud ARM Servers](#cloud-arm-servers)
- [Mobile Phone CPUs](#mobile-phone-cpus)
- [Cost and Deployment Economics](#cost-and-deployment-economics)
- [When You Actually Do Want a GPU](#when-you-actually-do-want-a-gpu)
- [CPU Fine-Tuning](#cpu-fine-tuning)
- [Talks, Papers, and Articles](#talks-papers-and-articles)
- [Docs](#docs)

---

## Runtimes and Inference Engines

- [candle](https://github.com/huggingface/candle) - Hugging Face's Rust ML framework; CPU execution is the primary target, with optional CUDA support compiled in separately.
- [ctransformers](https://github.com/marella/ctransformers) - Python bindings for GGUF models; lets Python callers run quantized models on CPU without touching C++.
- [ExecuTorch](https://github.com/pytorch/executorch) - PyTorch's on-device inference runtime; designed for mobile and embedded, with CPU kernels for ARM (XNNPACK backend) as the primary deployment target and cross-compilation support for Android, iOS, and Linux. *(Also listed under On-Device, Edge, ARM, and SBCs.)*
- [ggml](https://github.com/ggerganov/ggml) - The tensor library underlying llama.cpp; hand-optimized CPU kernels using SIMD intrinsics for AVX2, AVX-512, NEON, and SVE.
- [Intel Extension for Transformers](https://github.com/intel/intel-extension-for-transformers) - Drop-in optimization layer for Hugging Face Transformers that applies CPU-specific INT4/INT8 kernels, AMX acceleration, and weight-only quantization.
- [llamafile](https://github.com/mozilla-ai/llamafile) - Distributable single-file LLM executables (built on llama.cpp + Cosmopolitan libc) that run on CPU across Linux, macOS, and Windows with no install.
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - C/C++ LLM inference engine designed from day one for CPU; optional GPU offload of individual layers rather than GPU-first design.
- [llama2.c](https://github.com/karpathy/llama2.c) - Andrej Karpathy's minimal C implementation of LLaMA 2 inference; a pedagogical reference showing that CPU inference requires no ML framework, only a few hundred lines of C.
- [MNN](https://github.com/alibaba/MNN) - Alibaba's inference engine for mobile and edge; CPU is the primary target, with quantization-aware kernels for ARM NEON and x86 SSE/AVX.
- [ncnn](https://github.com/Tencent/ncnn) - Mobile and embedded neural network inference framework optimized for ARM and x86 CPUs; no dependencies, builds for Raspberry Pi, Jetson (CPU-only mode), and RISC-V with no OS-level GPU driver requirement.
- [ONNX Runtime (CPU EP)](https://onnxruntime.ai/docs/execution-providers/) - The CPU Execution Provider in ONNX Runtime; production-grade, supports operator fusion and quantized INT8 models natively on x86 and ARM.
- [ollama](https://github.com/ollama/ollama) - Local model runner that falls back to full CPU execution when no GPU is present; convenient for development and low-traffic deployments. *(Note: GPU is used when available; included here for its CPU fallback path and single-binary packaging story.)*
- [OpenVINO](https://github.com/openvinotoolkit/openvino) - Intel's model optimization and inference toolkit; targets x86 CPU as first-class hardware with graph optimization passes specific to Intel µarchs.
- [rwkv.cpp](https://github.com/RWKV/rwkv.cpp) - CPU inference library for RWKV v4–v7 language models (INT4/INT5/INT8 and FP16); RWKV's recurrent state requires O(1) memory per token at inference time with no growing KV cache, making it especially suited to CPU inference under long context lengths where transformer KV-cache memory becomes prohibitive.
- [Transformers.js](https://github.com/huggingface/transformers.js) - Hugging Face's in-browser transformer inference library; runs ONNX models via WebAssembly (CPU) or WebGPU, supporting 200+ architectures across NLP, vision, and audio with zero server dependency. CPU execution uses ONNX Runtime Web's WebAssembly backend with INT8 quantization.
- [WebLLM](https://github.com/mlc-ai/web-llm) - In-browser LLM inference engine built on MLC LLM and Apache TVM; uses WebGPU when available and falls back to WebAssembly for CPU-only execution, delivering an OpenAI-compatible API callable from browser JavaScript with no server required.
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Port of OpenAI Whisper to ggml; runs speech-to-text inference entirely on CPU with explicit ARM NEON and AVX paths; on Raspberry Pi 5, the base model achieves 3–5× real-time throughput and the JFK benchmark completes in approximately 9 s with the float32 tiny model.

**Runtime comparison at a glance**

| Runtime                     | Native Format     | CPU Arch              | OS                           |
| --------------------------- | ----------------- | --------------------- | ---------------------------- |
| llama.cpp                   | GGUF              | x86, ARM, RISC-V      | Linux, macOS, Windows        |
| ONNX Runtime                | ONNX              | x86, ARM, WebAssembly | Linux, macOS, Windows        |
| OpenVINO                    | OpenVINO IR       | x86                   | Linux, Windows               |
| ncnn                        | ncnn              | x86, ARM, RISC-V      | Linux, Windows, Android      |
| MNN                         | MNN               | x86, ARM              | Linux, Windows, Android, iOS |
| candle                      | GGUF, safetensors | x86, ARM              | Linux, macOS, Windows        |
| Transformers.js             | ONNX              | WebAssembly           | Browser                      |
| WebLLM                      | MLC               | WebAssembly, WebGPU   | Browser                      |
| ExecuTorch                  | ExecuTorch        | x86, ARM              | Linux, Android, iOS          |
| TensorFlow Lite             | TFLite            | x86, ARM              | Linux, Windows, Android, iOS |
| Intel Ext. for Transformers | PyTorch, ONNX     | x86                   | Linux, Windows               |
| whisper.cpp                 | GGUF              | x86, ARM              | Linux, macOS, Windows        |

---

## Quantization and Model Formats

- [GGUF](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md) - The successor to GGML format; single-file container for quantized weights plus model metadata, designed for memory-mapped loading that avoids RAM copies on CPU.
- [Intel Neural Compressor](https://github.com/intel/neural-compressor) - Framework-agnostic post-training quantization and pruning toolkit targeting CPU inference; supports ONNX, PyTorch, and TensorFlow backends.
- [Optimum](https://github.com/huggingface/optimum) - Hugging Face's optimization toolkit; the `optimum[onnxruntime]` and `optimum-intel` paths export and quantize models for CPU inference via ONNX Runtime and OpenVINO respectively.
- [AutoGPTQ](https://github.com/AutoGPTQ/AutoGPTQ) - GPTQ quantization library. *(Caveat: primarily targets GPU inference; include only when the produced GPTQ checkpoints are subsequently converted to GGUF for CPU use. Do not assume CPU parity.)*
- [llama.cpp quantize tool](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md) - Built-in `llama-quantize` binary converting Hugging Face checkpoints to GGUF; covers k-quants (Q4_K_M, Q5_K_M, Q6_K) and importance-matrix–guided i-quants (IQ3_XS, IQ4_XS) that route more bits to high-impact weights — IQ4_XS saves ~400 MB vs Q4_K_M on a 7B model at comparable accuracy. Pair with `--imatrix` for any format below Q5_K_M.
- [llama.cpp imatrix tool](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md) - Calibration pass that runs a small corpus through the unquantized model and records per-layer weight importance; the resulting `.imatrix` file is passed to `llama-quantize` and significantly improves output quality at aggressive compression ratios (IQ3_XS, IQ4_XS, Q3_K_S).

---

## Performance Tuning

- [llama.cpp token generation performance tips](https://github.com/ggml-org/llama.cpp/blob/master/docs/development/token_generation_performance_tips.md) - Official guidance on setting `--threads`, `--threads-batch`, CPU affinity masks, and NUMA-aware memory allocation for multi-socket servers.
- [OpenBLAS](https://github.com/OpenMathLib/OpenBLAS) - Optimized BLAS implementation with auto-tuned kernels for x86 (SSE/AVX/AVX-512) and ARM; a drop-in dependency for frameworks that delegate GEMM to BLAS.
- [Intel MKL / oneMKL](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html) - Intel's math kernel library with AVX-512 and AMX-optimized GEMM; free to use and typically the fastest BLAS on recent Xeon hardware.
- [Intel AMX (Advanced Matrix Extensions)](https://www.intel.com/content/www/us/en/products/docs/accelerator-engines/what-is-intel-amx.html) - Hardware matrix multiplication tiles in Sapphire Rapids and later Xeon CPUs; AMX delivers 2,048 INT8 operations per cycle vs 256 for AVX-512 VNNI — an 8× arithmetic throughput improvement for quantized inference on the same silicon; llama.cpp and ONNX Runtime both expose AMX code paths. [(Intel AMX solution brief)](https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2022-12/accelerate-ai-with-amx-sb.pdf)
- [numactl](https://github.com/numactl/numactl) - Linux utility to bind a process to specific NUMA nodes and CPU cores; essential for avoiding cross-socket memory latency on multi-socket inference servers.
- [perf + Linux PMU](https://perfwiki.github.io/main/) - Standard Linux profiling tool; useful for measuring LLC miss rates and memory bandwidth saturation during inference, which are the dominant bottlenecks on CPU.
- [likwid](https://github.com/RRZE-HPC/likwid) - Hardware performance counter tool suite for x86; provides memory bandwidth and FLOP/s measurements useful for diagnosing inference throughput limits on specific µarchs.

---

## Mixture-of-Experts on CPU

Mixture-of-Experts (MoE) architectures are often assumed to require GPU because of their large total parameter counts, but the sparse routing mechanism — activating only a subset of experts per token — creates a different compute profile that can benefit CPU deployment. The activated parameters are typically 5–10% of total (e.g., 37B activated out of 671B total in DeepSeek-R1), so aggressive quantization brings the working set within reach of CPU instances with sufficient RAM.

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (DeepSeek, Jan 2025)](https://arxiv.org/abs/2501.12948) - Introduces DeepSeek-R1 (671B total, 37B activated per token) and distilled dense variants from 1.5B to 70B; the dense distillations run on any CPU with llama.cpp at Q4, and the full MoE model with IQ1_S quantization fits within ~10 GB RAM on CPU.
- [Deploy DeepSeek-R1 on Arm Servers with llama.cpp (Arm Learning Paths, Apr 2026)](https://learn.arm.com/learning-paths/servers-and-cloud-computing/deepseek-cpu/) - Walkthrough for DeepSeek-R1-Distill-Qwen-7B Q4_K_M on AWS Graviton4; benchmarks 18–22 tok/s generation and ~420 tok/s prompt processing on 24 vCPU, 192 GB RAM with ~5.8 GB model RAM use.
- [DeepSeek-R1 7B on OCI Ampere A1: Full CPU Inference Guide (asknikhil.com, May 2026)](https://www.asknikhil.com/post/deepseek-r1-7b-on-oci-ampere-a1-full-cpu-inference-guide-no-gpu-required) - Practitioner guide deploying DeepSeek-R1-Distill-Qwen-7B Q4_K_M on OCI Ampere A1 free-tier ARM instances; reports ~18–22 tok/s generation, ~420 tok/s prompt processing, and ~5.8 GB RAM utilisation with no CUDA/driver setup required.

---

## Benchmarks and Evidence

- [llama.cpp performance tracking](https://github.com/ggml-org/llama.cpp/issues/4167) - Community-maintained thread with tokens/second figures for various models across CPU and GPU hardware; useful as a real-world comparison baseline.
- [LLM Inference Benchmarking Cheat-Sheet (llm-tracker.info)](https://llm-tracker.info/howto/LLM-Inference-Benchmarking-Cheat%E2%80%91Sheet-for-Hardware-Reviewers) - Canonical reference explaining llama.cpp benchmark metrics (pp512/tg128), quantization naming conventions, and how to correctly interpret and compare community-reported figures across hardware platforms.
- [MyAIHardware — llama.cpp benchmarks](https://www.myaihardware.com/llama-cpp-benchmarks) - Aggregated llama.cpp benchmark scoreboard across CPUs, GPUs, and NPUs under standardized test conditions; useful for hardware selection and cross-platform throughput comparison.
- [MLPerf Inference — edge CPU submissions](https://mlcommons.org/benchmarks/inference-edge/) - Industry-audited inference benchmark with CPU-only submissions in the edge category; provides verified latency/throughput figures under defined, reproducible test conditions.
- [MLPerf Inference v5.0 — datacenter CPU submissions (MLCommons, Apr 2025)](https://mlcommons.org/2025/04/mlperf-inference-v5-0-results/) - Industry-audited inference benchmark with CPU-only datacenter submissions on Intel Xeon 6 Granite Rapids; reports GPT-J at 316 tok/s (INT4), Llama-3.1-8B at 450 tok/s (server) and 1,196 tok/s (offline). Intel remains the only vendor submitting server CPU results, holding through the v5.1 round (Sept 2025). *(last verified: 2026-07)* ([Dell 2S-GNR results](https://github.com/mlcommons/inference_results_v5.0/tree/main/closed/Dell/results/1-node-2S-GNR_86C), [Supermicro results](https://github.com/mlcommons/inference_results_v5.0/tree/main/closed/Supermicro/results/1-node-2S-GNR_128C))
- [ONNX Runtime GenAI CPU benchmark (ISE Developer Blog, May 2025)](https://devblogs.microsoft.com/ise/running-rag-onnxruntime-genai/) - Production benchmark comparing ONNX Runtime GenAI, llama.cpp, and Hugging Face Optimum for Phi-3 on CPU; ONNX Runtime achieved 137.6 tok/s vs 109.5 for llama.cpp and 108.3 for Optimum — 1.2–1.6× higher throughput across prompt lengths with equivalent latency.
- [OpenVINO Model Hub benchmarks (Intel, 2025)](https://www.intel.com/content/www/us/en/developer/tools/openvino-toolkit/model-hub.html) - Intel's centralized benchmark catalog for LLMs on Xeon CPUs with INT4/INT8/FP16 precision; reports DeepSeek-R1-Distill-Llama-8B at 155.4 tok/s and Llama-3-8B at 376 tok/s (OpenVINO Model Server) on Intel Xeon Platinum. ([OpenVINO LLM benchmark tool](https://github.com/openvinotoolkit/openvino.genai/tree/master/tools/llm_bench), [white paper](https://www.intel.com/content/dam/develop/public/us/en/documents/llm-with-model-server-white-paper.pdf))
- [Simon Willison's llama.cpp experiments](https://simonwillison.net/tags/llama-cpp/) - Practitioner write-ups with real-world timing data across diverse CPU hardware; useful for calibrating expectations before purchasing cloud instances.
- [Model size distribution on Hugging Face](https://huggingface.co/blog/huggingface/state-of-os-hf-spring-2026) - Independent analyses of the Hugging Face ecosystem find 40–51% of models are sub-7B and 55–65% are sub-13B parameters, with 92% of all downloads going to models under 1B params and the median downloaded model at 406M params. ([MoClaw, Apr 2026](https://moclaw.ai/blog/huggingface-hub-state-2026), [HF model stats, Oct 2025](https://huggingface.co/blog/lbourdois/huggingface-models-stats))

---

## On-Device, Edge, ARM, and SBCs

- [Core ML](https://developer.apple.com/machine-learning/core-ml/) - Apple's on-device inference framework for iOS, macOS, and visionOS; runs models on the CPU (ANE/GPU also supported but optional) with optimized kernels for Apple Silicon M-series chips. Supports model conversion from PyTorch and TensorFlow via [`coremltools`](https://github.com/apple/coremltools).
- [ExecuTorch](https://github.com/pytorch/executorch) - PyTorch's on-device inference runtime; designed for mobile and embedded, with CPU kernels for ARM (XNNPACK backend) as the primary deployment target.
- [XNNPACK](https://github.com/google/XNNPACK) - Google's accelerated neural network inference library for ARM and x86; used as the CPU backend in TFLite, ExecuTorch, and ONNX Runtime's mobile path.
- [TensorFlow Lite](https://www.tensorflow.org/lite) - Google's inference runtime for mobile and embedded; the default execution path is CPU (ARM/x86), with delegate APIs for optional hardware accelerators.
- [MLC LLM (WebAssembly/CPU target)](https://github.com/mlc-ai/mlc-llm) - Compiles LLMs to native CPU code or WebAssembly via TVM; the browser/WebAssembly target is inherently CPU-only. *(Note: also targets GPU; relevant here specifically for its WebAssembly/CPU compilation path.)*
- [llama.cpp Android build](https://github.com/ggerganov/llama.cpp/blob/master/docs/android.md) - Official docs for cross-compiling llama.cpp for Android ARM; runs on-device without network access or cloud inference costs.
- [V-Seek — LLM inference on RISC-V server CPUs (arxiv:2503.17422)](https://arxiv.org/abs/2503.17422) - Paper documenting LLM inference optimizations on the Sophon SG2042, the first commercially available many-core RISC-V server CPU (64 RVV-capable cores); achieves 13 tok/s for 7B models and 5.5× throughput over baseline llama.cpp by exploiting RISC-V Vector (RVV) extensions with vectorized GEMM kernels.
- [Intel Core Ultra with OpenVINO (Intel, 2024)](https://www.intel.com/content/www/us/en/developer/articles/technical/chatbot-on-your-laptop-phi-2-core-ultra-processors.html) - Demonstrates Phi-2 INT4 quantization and inference on Intel Core Ultra laptop CPUs via OpenVINO + Optimum; CPU handles the LLM workload on AI PC hardware where the NPU is present but not required for generative inference.
- [AMD Ryzen AI Software (AMD, 2025)](https://ryzenai.docs.amd.com/en/latest/) - AMD's AI inference stack for Ryzen AI PC processors; deploys ONNX models via Vitis AI Execution Provider with automatic CPU fallback for unsupported operators, supporting INT4/INT8/BF16 precision across CPU and NPU. ([ONNX Runtime VitisAI EP docs](https://onnxruntime.ai/docs/execution-providers/Vitis-AI-ExecutionProvider.html))
- [MediaTek Genio 720 / 520 (MediaTek, 2025)](https://www.mediatek.com/press-room/mediatek-unveils-genio-720-and-genio-520-iot-platforms-for-generative-ai-applications) - Edge AI IoT platforms (6 nm) with octa-core Arm CPU (2× Cortex-A78 + 6× Cortex-A55) and 10 TOPS NPU; supports LLMs (Llama, Phi, DeepSeek) on-device via LiteRT and ONNX Runtime with CPU fallback. ([Genio AI Developer Guide](https://genio.mediatek.com/doc/iot-yocto/latest/sw/yocto/iot-ai-hub.html))

---

## Vision on CPU

Computer vision inference — object detection, classification, and segmentation — is often cheaper to run on CPU than GPU, especially in video analytics pipelines where multiple camera feeds must be processed concurrently on the same host. Modern runtimes like OpenVINO and ONNX Runtime deliver server-grade throughput for YOLO models on Intel Xeon and commodity x86 hardware.

- [YOLOv8 with OpenVINO (Ultralytics, 2025)](https://docs.ultralytics.com/integrations/openvino/) - Official Ultralytics integration exporting YOLOv8–YOLO26 models to OpenVINO IR; benchmarks on Intel Xeon show the largest FP32 models exceeding 360 fps in async mode and smallest models approaching 5,000 fps with up to 14× throughput improvement over native PyTorch CPU. ([Lenovo Press: YOLO on Xeon 6](https://lenovopress.lenovo.com/lp2345-accelerating-real-time-object-detection-yolo-models-intel-xeon-6-openvino))
- [Ultralytics OpenVINO on CPU — Production Guide](https://academy.ultralytics.com/courses/yolo-in-production/openvino-on-cpu) - Practical guide comparing PyTorch CPU, ONNX, and OpenVINO for YOLO inference; reports OpenVINO delivers 2–3× speedup over ONNX Runtime and 5× over PyTorch CPU on Intel hardware, with INT8 quantization halving latency.
- [CLIP-ONNX — CPU benchmarks](https://github.com/Lednik7/CLIP-ONNX/blob/main/benchmark.md) - Benchmark comparing ONNX Runtime and PyTorch for CLIP ViT-B/32 on CPU (Xeon 2.3 GHz); ONNX achieves ~2.5 img/s at batch=2 for image encoding with 3× improvement over PyTorch at larger batch sizes.
- [clip.cpp — CLIP inference in GGML](https://github.com/monatis/clip.cpp) - Dependency-free CLIP model inference using ggml with 4/5/8-bit quantization; supports text-only and vision-only modes, short startup time suitable for serverless deployments.
- [DFN5B-CLIP-ViT-H-14-378 — INT8 ONNX on CPU](https://huggingface.co/pritam-scientiaai/Quantized_DFN5B-CLIP-ViT-H-14-378_ONNX_INT8) - Large CLIP model (~5B params) quantized to INT8 ONNX; runs 2.3× faster on CPU with cosine similarity 0.985 vs FP32; benchmarks show 405 ms/image and ~20 text seq/s on current-gen Intel i7.

---

## Multimodal CPU Workloads

Speech, audio, text-to-speech, and optical character recognition are among the most common production AI workloads that rarely need a GPU. Modern ASR engines run efficiently on CPU with INT8 quantization, TTS engines synthesize in real time using lightweight ONNX models, and OCR toolchains have been CPU-native for decades — with deep learning models now matching traditional engine accuracy while running on commodity x86 and ARM hardware.

Key tools: [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [whisper.cpp](https://github.com/ggerganov/whisper.cpp), [Piper](https://github.com/OHF-Voice/piper1-gpl), [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), [Tesseract](https://github.com/tesseract-ocr/tesseract), [MobileSAM](https://github.com/ChaoningZhang/MobileSAM), [rembg](https://github.com/danielgatis/rembg), [InsightFace](https://github.com/deepinsight/insightface).

See [docs/multimodal-cpu.md](docs/multimodal-cpu.md) for the full catalogue — ASR/STT, audio embeddings, VAD/diarization, TTS, text embeddings, document classification, OCR, image classification, segmentation, generation, background removal, and face analysis with baseline CPU latency and throughput figures.

---

## Cloud ARM Servers

Cloud instances where Arm CPUs are the primary inference platform. These are not edge devices — they are datacenter-class Arm cores with high core counts, large memory bandwidth, and SVE/NEON acceleration — and they are increasingly competitive with x86 on both throughput and cost.

- [OCI Ampere Altra A1 instances](https://blogs.oracle.com/ai-and-datascience/post/introducing-meta-llama-3-on-oci-ampere-a1) - Oracle Cloud shapes based on Ampere Altra (Neoverse N1); benchmarked at 119 tok/s aggregate throughput for Llama-2 7B with 16 concurrent users using an optimized llama.cpp stack, with up to 152% improvement over upstream llama.cpp reported. *(last verified: 2026-07)*
- [Azure Cobalt 100 (Neoverse N2)](https://developer.arm.com/community/arm-community-blogs/b/servers-and-cloud-computing-blog/posts/accelerate-llm-inference-with-onnx-runtime-on-arm-neoverse-powered-microsoft-cobalt-100) - Microsoft's 128-core Neoverse N2 processor; Arm-optimized ONNX Runtime (KleidiAI kernels) delivers 1.9× higher token-generation throughput and 2.8× better price/performance compared to AMD Genoa-based instances for LLM inference. *(last verified: 2026-07)*
- [Azure Cobalt 200 (Neoverse V3)](https://azure.microsoft.com/en-us/blog/new-azure-cobalt-200-vms-deliver-50-performance-improvement-fully-optimized-for-modern-agentic-ai-workloads/) - Microsoft's 132-core Neoverse V3 processor on TSMC 3 nm; delivers up to 50% better CPU performance over Cobalt 100 and is positioned explicitly for agentic AI inference workloads; early-access VMs available as of Build 2026. *(last verified: 2026-06)*
- [AWS Graviton4 — c8g instances](https://aws.amazon.com/ec2/instance-types/c8g/) - Amazon's Neoverse V2-based fourth-generation Graviton; up to 30% better performance and up to 3× more vCPUs than Graviton3 (c7g) at the largest sizes; llama.cpp MMLA kernels are supported and distributed multi-node inference is documented in the [Arm Learning Paths guide](https://learn.arm.com/learning-paths/servers-and-cloud-computing/distributed-inference-with-llama-cpp/). *(last verified: 2026-06)*
- [Google Axion (Neoverse V2)](https://developer.arm.com/community/arm-community-blogs/b/servers-and-cloud-computing-blog/posts/ai-inference-on-google-axion-cpu) - Google Cloud's custom Neoverse V2 processor (C4A instances); benchmarked with llama.cpp on Llama-3.1 8B and reports up to 2× better prompt-processing and token-generation performance vs current-generation x86 instances. *(last verified: 2026-07)*
- [aarch64.cloud — Graviton vs Axion vs Cobalt benchmark](https://aarch64.cloud/arm-chip-benchmark-test-for-hyperscale-cloud-providers.html) - Independent benchmark comparing AWS Graviton3, Google Axion, and Azure Cobalt 100 on llama.cpp with Llama-3.1 8B and Llama-3.2 1B; documents tokens/s and price/performance ratios. *(Note: predates Graviton4 and Cobalt 200; use as a Graviton3-generation baseline.)*

---

## Mobile Phone CPUs

Modern flagship phones run billion-parameter LLMs on-device — no cloud round-trip, no GPU required. The CPU path is the most portable, vendor-independent option for mobile inference: it works across all devices regardless of NPU vendor lock-in, and for LLMs it often matches or exceeds NPU throughput due to more mature tooling and the memory-bandwidth-bound nature of token generation.

Key platforms: [Apple A19 Pro](https://www.apple.com/iphone/), [Snapdragon 8 Elite](https://www.qualcomm.com/products/mobile/snapdragon/smartphones/snapdragon-8-series-mobile-platforms/snapdragon-8-elite), [Exynos 2500](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2500/), [Dimensity 9500](https://i.mediatek.com/mediatek-dimensity-ai), [Tensor G5](https://store.google.com/pixel_10).

See [docs/mobile-cpu-inference.md](docs/mobile-cpu-inference.md) for the full catalogue — chipsets, runtimes (MLC-LLM, Apple Core AI, llama.cpp Android, Qualcomm AI Hub, Arm SME2/KleidiAI), and benchmarks (State of the Union 2026, Beebom, CraftRigs) with tok/s and thermal measurements.

---

## Cost and Deployment Economics

- [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/) - Serverless compute priced per GB-second on CPU; viable for low-throughput embedding and small-model inference without a persistent GPU instance.
- [Hetzner dedicated servers](https://www.hetzner.com/dedicated-rootserver/) - Example of high-core-count x86 servers at commodity pricing; a useful reference point when constructing cost-per-token calculations to compare against GPU instances.
- [Fly.io CPU machines](https://fly.io/docs/machines/overview/) - Container-level CPU VMs with per-second billing; commonly used for llama.cpp-backed inference APIs at low traffic volumes where a persistent GPU instance would be idle most of the time.
- [Modal — GPU selection guide](https://modal.com/docs/guide/gpu) - Serverless platform that makes the CPU/GPU choice explicit at the function level; useful for hybrid deployments where embeddings run CPU-side and generation runs GPU-side.

**The short version.** At sustained batch=32 load a GPU has a ~40× $/token advantage on Llama-3 8B. The CPU economic case rests on three factors that table does not capture:

1. **Idle cost dominates sporadic workloads.** A c7g.4xlarge at $0.58/hr is 42% cheaper than a g5.xlarge sitting idle; near-zero traffic makes the GPU minimum cost pure overhead.
2. **Serverless CPU eliminates the idle floor entirely** — Lambda arm64, Fly.io, and Modal CPU bill per-invocation.
3. **VRAM is a hard ceiling; system RAM is not.** A 12 GB quantized model runs on any instance with ≥ 16 GB RAM at commodity pricing; on GPU it requires a VRAM class that costs $1+/hr regardless of utilization.

A worked production example (1 req/s, 730 hrs/month, 7B Q4) shows **CPU saves $5,740/yr** on a c7g.2xlarge vs g5.xlarge — the gap closes only after GPU utilization exceeds ~50%.

See [docs/cost-calculator.md](docs/cost-calculator.md) for the full cost-per-token table, TCO worked example, pricing reference, break-even formula, and a runnable bash calculator script.

---

## When You Actually Do Want a GPU

This section is load-bearing. The CPU-first default breaks down in the following real scenarios — reaching for a GPU here is the right call, not a failure of discipline.

**High-throughput batched serving at scale.** When serving hundreds of concurrent requests with large batch sizes, GPU memory bandwidth dominates and arithmetic throughput advantage becomes decisive. CPU cores serialize; GPU SIMT parallelism does not. Self-hosted GPU breakeven requires ≥ 50% utilization for 7B models and ≥ 10% for 13B models — below those thresholds CPU or serverless often wins on total cost; above them GPU $/token falls sharply as batch size grows. ([dasroot.net, Feb 2026](https://dasroot.net/posts/2026/02/cpu-vs-gpu-inference-llm-cost-1m-tokens/); methodology: [arxiv:2606.11690](https://arxiv.org/abs/2606.11690))

**Tight low-latency SLAs on large models.** If your SLA requires < 50 ms time-to-first-token on a 34B+ parameter model, no current CPU can match A100/H100 memory bandwidth. The token generation phase is memory-bound; GPUs have 5–10× the off-chip bandwidth of a modern CPU.

**Long-context prefill.** Prefilling a 32 K+ token prompt is a large matrix multiply. This scales with context length and is exactly the workload GPUs were built for. On a 128 K-context model, CPU prefill latency can be tens of seconds — unacceptable for interactive use cases.

**Real-time diffusion and video generation.** Stable Diffusion and video generation models require hundreds of TFLOPS per generated frame. CPU throughput is too low for any real-time or near-real-time requirement here; this is not a quantization-fixable problem.

**Continuous batching serving infrastructure.** Frameworks like vLLM and TGI are purpose-built for GPU-resident KV cache management, paged attention, and continuous batching. These optimizations exist because the GPU memory hierarchy enables them; the tradeoffs do not translate cleanly to CPU.

**Large multi-modal models.** Vision-language models with large image encoders add substantial FLOPs to the inference path. Running these at interactive speed on models above 34B currently requires GPU for most deployment configurations.

---

## CPU Fine-Tuning

Fine-tuning adapts a pre-trained model to a specific domain or task. While full-parameter training remains GPU territory, parameter-efficient fine-tuning (PEFT) methods — LoRA, QLoRA, DoRA — can run on CPU for small base models (≤ 7B) at moderate batch sizes, especially when the base model is pre-quantized and only adapter weights are updated. This section covers tools and patterns for fine-tuning on CPU.

- [Unsloth](https://github.com/unslothai/unsloth) - GPU-accelerated LoRA/QLoRA fine-tuning library; included here because it produces GGUF-compatible LoRA adapters that can be merged and deployed on CPU via llama.cpp. Fine-tune on GPU (or free Colab T4), export adapter, run inference on CPU.
- [llama.cpp fine-tuning](https://github.com/ggml-org/llama.cpp/tree/master/examples/training) - Built-in fine-tuning example in llama.cpp supporting LoRA-style adapter training on CPU; produces `.lora` files loadable by `llama-cli` at inference time. Suited for small-scale domain adaptation (classification heads, instruction tuning on 1K–10K examples). Runs entirely on CPU with no GPU dependency at any stage.
- [LoRAX](https://github.com/predibase/lorax) - Multi-LoRA inference server that serves thousands of fine-tuned adapters from a single base model; designed for GPU by default but the LoRA-weight merging pattern applies to CPU deployments — pre-merge adapters into a single GGUF with `llama.cpp`'s `export-lora` for CPU serving.
- [PEFT](https://github.com/huggingface/peft) - Hugging Face's parameter-efficient fine-tuning library (LoRA, IA³, Prefix Tuning, AdaLoRA); runs on CPU for small models when `device="cpu"` is set, though throughput is 10–50× slower than a single GPU. Practical for models ≤ 3B where training data is small (< 5K examples) and iteration time is not critical.
- [LlamaFactory](https://github.com/hiyouga/LLaMAFactory) - Unified fine-tuning framework supporting LoRA, QLoRA, full-parameter, and DoRA; CPU mode works for small-scale adapter training (batch size 1–2, ≤ 3B base models) with `CUDA_VISIBLE_DEVICES=""` to force CPU execution.
- [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) - Flexible fine-tuning toolkit supporting QLoRA and multi-GPU training; provides CPU-offloaded optimizer states via `deepspeed` ZeRO-3 CPU offload, keeping activations on GPU while optimizer states reside in system RAM — a hybrid approach that reduces GPU VRAM requirements for larger models.

**CPU fine-tuning economics in practice.** Fine-tuning a Llama-3.2 3B model using LoRA on a c7g.2xlarge (8 vCPU, 16 GB RAM) with 1,000 examples for 3 epochs completes in approximately 6–12 hours depending on sequence length. The total compute cost at $0.35/hr is $2–4 per fine-tune run. The same run on a g5.xlarge GPU instance ($1.006/hr) completes in 15–30 minutes at $0.25–0.50 per run. GPU is faster and cheaper for the fine-tuning *event*, but the fine-tuned adapter then deploys on CPU at the inference costs documented in [Cost and Deployment Economics](#cost-and-deployment-economics) — the overall TCO depends on how many inference queries you serve after fine-tuning.

**Rule of thumb.** Fine-tune on GPU when you have one (even a rented one); the time savings justify the marginal cost. Fine-tune on CPU when you have no GPU access, are iterating on a tiny dataset, or want a fully offline pipeline with no cloud dependency. The adapter format is interchangeable — LoRA weights trained on GPU load identically on CPU.

---

## Talks, Papers, and Articles

- [llama.cpp — initial commit thread (Georgi Gerganov, Jan 2023)](https://github.com/ggerganov/llama.cpp/commit/26c084662903ddaca19bef982831bfb0856e8257) - The discussion that kicked off serious community interest in CPU-first LLM inference; the commit and issue thread document the initial benchmark results that made the case.
- ["Efficient LLM Inference on CPUs" (Intel Labs, 2023)](https://arxiv.org/abs/2311.00502) - Describes weight-only quantization for CPU inference on Sapphire Rapids: weights stored in INT4/INT8 while activations compute in BF16, reducing memory bandwidth pressure without sacrificing activation precision; a key technique behind Intel Extension for Transformers.
- ["Highly Optimized Kernels and Fine-Grained Codebooks for LLM Inference on Arm CPUs" (Arm, Dec 2024)](https://arxiv.org/abs/2501.00032) - Proposes Q4_0_8_8 and related kernels exploiting SVE/NEON MMLA instructions on Neoverse V1/V2; reports 3–3.2× prefill and up to 2× decode throughput improvement on Graviton3 vs standard Q4_0, with fine-grained codebooks that recover accuracy at the same bit-width.
- ["Accelerate LLM Inference with ONNX Runtime on Arm Neoverse-powered Cobalt 100" (Arm, 2024)](https://developer.arm.com/community/arm-community-blogs/b/servers-and-cloud-computing-blog/posts/accelerate-llm-inference-with-onnx-runtime-on-arm-neoverse-powered-microsoft-cobalt-100) - Documents KleidiAI kernel optimizations integrated into ONNX Runtime GenAI, delivering 28–51% performance uplift across different Cobalt 100 instance sizes for LLM token generation; includes int4/int8/bf16 precision results.
- ["Benchmarking AI Workloads on Intel Xeon with AMX" (itsabout.ai, 2024)](https://itsabout.ai/benchmarking-ai-workloads-on-intel-xeon-with-amx-best-practices-and-performance-insights/) - Practical benchmark guide for AMX on Sapphire Rapids; measures sustained GEMM throughput across batch sizes and establishes the 8× INT8 ops/cycle advantage of AMX over AVX-512 VNNI in the context of quantized LLM inference.
- ["LLM Optimization and Deployment on SiFive RISC-V Intelligence Processors" (SiFive, Jan 2026)](https://www.sifive.com/blog/llm-optimization-and-deployment-on-sifive-intellig) - End-to-end deployment of TinyLlama and Llama-2-7B-Q4 on RISC-V using the IREE compiler with RVV vectorization; includes MLPerf accuracy validation and demonstrates readiness of open-hardware RISC-V for LLM inference.
- ["Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone" (Microsoft, Apr 2024)](https://arxiv.org/abs/2404.14219) - Reports Phi-3-mini (3.8B) quantized to 4-bit fits in 1.8 GB and achieves 12+ tok/s on iPhone 14 CPU fully offline, establishing small models as viable for on-device CPU inference.
- ["Llama 3.2 vs Phi-3 Mini vs Gemma 2: iPhone Bake-Off" (PocketLLM, Apr 2026)](https://pocketllm.app/blog/llama-3-vs-phi-3-vs-gemma-2-iphone/) - Head-to-head benchmark of Llama 3.2 3B, Phi-3.5 Mini 3.8B, and Gemma 2 2B on iPhone 15 Pro (Q4); reports 25–38 tok/s generation and 300–500 ms first-token latency on CPU-only inference, with Gemma 2 fastest and Llama 3.2 most versatile.
- ["The Business Value of CPU-Based Inference" (Lenovo Press, 2025)](https://lenovopress.lenovo.com/lp2460-the-business-value-of-cpu-based-inference) - Enterprise TCO analysis of on-prem CPU inference (Intel Xeon 6) vs cloud GPU; reports $1.02M net savings over 5 years and 4.5-month breakeven vs cloud rental for sustained LLM workloads.
- ["ML Model Server Resource Saving – Transition From GPUs to Intel CPUs" (NAVER / PyTorch Blog, 2024)](https://pytorch.org/blog/ml-model-server-resource-saving/) - Production case study migrating 15 GPU instances to Intel CPUs across Korea/Japan data centers; achieved equivalent serving quality with 3× scale-out and ~$340K annual cost savings using IPEX and oneDNN optimizations.
- ["WebLLM: A High-Performance In-Browser LLM Inference Engine" (MLCo/CMU, Dec 2024)](https://arxiv.org/abs/2412.15803) - Demonstrates LLM inference running entirely in-browser via WebGPU and WebAssembly; the WebAssembly path handles CPU workloads including grammar-constrained generation and KV-cache management, retaining up to 80% of native device performance; ships an OpenAI-compatible browser-side API.
- ["Why CPUs Also Make Sense for AI Inference" (Scaleway / Ampere CTO Jeff Wittich)](https://www.scaleway.com/en/blog/why-cpus-also-make-sense-for-ai-inference/) - Interview with Ampere Computing CTO arguing that GPUs are compute overkill for inference; includes a concrete power-efficiency figure: the 128-core Ampere Altra consumes 3.6× less power per inference than an Nvidia A10 and 5.6× less than a Tesla T4, measured on OpenAI Whisper — a strong argument for CPU in energy-constrained or cost-per-watt–sensitive deployments.
- [Tim Dettmers — "Which GPU for Deep Learning"](https://timdettmers.com/2023/01/30/which-gpu-for-deep-learning/) - GPU-centric guide that nonetheless clearly articulates when GPU matters and when it does not; useful as a foil for the CPU-first argument.

---

## Docs

Companion documents for planning, converting, deploying, benchmarking, and troubleshooting CPU inference:

- [Quick Start Guide](docs/quickstart.md) - Full walkthroughs with copy-paste commands and sample code for llamafile, ollama, and WebLLM.
- [CPU Inference Deployment Guide](docs/cpu-inference-deployment.md) - Docker CPU tuning, Kubernetes NUMA-aware scheduling, system optimization (numactl, frequency scaling, SMT), and serving patterns for real-time and batch workloads.
- [Cost Calculator](docs/cost-calculator.md) - Reusable TCO methodology with a break-even analysis for comparing CPU vs GPU inference costs across cloud instances. Includes an interactive [Streamlit app](calculator/cost-calculator.py) (`uv run streamlit run calculator/cost-calculator.py`).
- [Green Inference Guide](docs/green-inference.md) - Power-per-inference comparisons (Ampere Altra: 3.6× vs A10, 5.6× vs T4 on Whisper), TDP reference table, data-center PUE arithmetic, water consumption (WUE) analysis, carbon footprint by grid region, CO₂ measurement with CodeCarbon and Cloud Carbon Footprint, and CPU power-management tuning (cpufreq governor, RAPL caps, turbo settings). Includes an interactive [power calculator](calculator/power-calculator.py) (`uv run streamlit run calculator/power-calculator.py`).
- [Green Inference Cheat Sheet](docs/green-inference-cheat-sheet.md) - One-page quick reference of power, water, and carbon comparison tables for sustainability reporting.
- [Multimodal CPU Workloads](docs/multimodal-cpu.md) - ASR/STT, TTS, text embeddings, document classification, OCR, image classification/segmentation/generation, background removal, and face analysis on CPU — with baseline latency and throughput figures.
- [Mobile Phone CPU Inference](docs/mobile-cpu-inference.md) - Apple A19 Pro, Snapdragon 8 Elite, Exynos 2500, Dimensity 9500, Tensor G5; runtimes (MLC-LLM, Core AI, llama.cpp Android, Qualcomm AI Hub, Arm SME2/KleidiAI); benchmarks and deployment guides with tok/s and thermal data.
- [Model Conversion Guide](docs/model-conversion-guide.md) - Practical walkthroughs for converting Hugging Face checkpoints to GGUF (llama.cpp quantize) and PyTorch to ONNX (via Optimum), including INT8 post-training quantization.
- [Serverless CPU Patterns](docs/serverless-patterns.md) - Recipes for deploying CPU inference on AWS Lambda (arm64), Fly.io, and Modal, with cost-per-invocation worked examples.
- [Benchmark Methodology](docs/benchmark-methodology.md) - Standardized metrics (pp512, tg128, TTFT, TPOT), reporting template, and run procedure for producing comparable CPU inference benchmarks.
- [Hardware Reference](docs/hardware-reference.md) - Canonical hardware performance catalogue for mobile, laptop, SBC, and server CPU inference — single source of truth for throughput figures across all device tiers.
- [Benchmark Suite Proposal](docs/benchmark-suite-proposal.md) - Proposal for a community-maintained, standardized CPU inference benchmark suite to reduce fragmentation across runtimes and architectures.
- [Edge & Mobile CPU Inference Playbook](docs/edge-mobile-playbook.md) - Definitive reference for deploying open-weight models on phones, tablets, laptops, and SBCs — entirely on CPU with no GPU dependency.
- [CPU vs NVIDIA Decision Framework](docs/cpu-vs-nvidia-decision-framework.md) - Structured comparison and decision matrix for CPU vs NVIDIA GPU inference, covering batch workloads, total cost, and migration steps.
- [Community Hackathon](docs/community-hackathon.md) - Structured, sponsor-backed hackathon to generate real-world CPU inference examples, benchmarks, and deployment patterns.
- [Roadmap](ROADMAP.md) - Quarterly milestones aligned with enterprise inference adoption cycles.
- [Troubleshooting](docs/troubleshooting.md) - Diagnosis and fixes for common CPU inference issues: OOM, low throughput, NUMA misconfiguration, thread oversubscription, thermal throttling, and container/Kubernetes problems.

---

## Contributing

Contributions welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first. Every entry must be:

1. Genuinely CPU-native or directly relevant to the CPU-vs-GPU inference decision.
2. Accompanied by a one-line neutral description in your own words.
3. Not a duplicate of an existing entry.
4. Not a GPU framework that runs on CPU only as a slow fallback.

If you are unsure whether a tool belongs, open an issue rather than a PR and describe why you think it qualifies.

---

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, the maintainers of awesome-cpu-first-ai have waived all copyright and related or neighboring rights to this work.
