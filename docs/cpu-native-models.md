# CPU-Native Model Catalog

A catalogue of models designed or well-suited for CPU inference — with recommended runtimes, quantization formats, and measured performance ranges. This is not a list of every model that *can* run on CPU (most can, given enough quantization), but a guide to models whose architecture or size makes them *good* on CPU without GPU compromise.

---

## Contents

- [Why Some Models Fit CPU Better](#why-some-models-fit-cpu-better)
- [Dense Models ≤ 8B](#dense-models--8b)
- [Dense Models 8B–13B](#dense-models-8b13b)
- [MoE Models (high activation sparsity)](#moe-models-high-activation-sparsity)
- [Ternary / 1-bit Models](#ternary--1-bit-models)
  - [Why ≤3B and Ternary Lead on CPU Cost Advantage](#why-3b-dense-and-ternary-models-lead-on-cpu-cost-advantage)
  - [Coming Soon / In Development](#coming-soon-in-development)
- [Mobile-Friendly Models](#mobile-friendly-models)
- [Small Embedding Models](#small-embedding-models)
- [Vision Models](#vision-models)
- [ASR / TTS Models](#asr--tts-models)
- [Model Selection Tools](#model-selection-tools)
- [See also](#see-also)

---

## Why Some Models Fit CPU Better

CPU inference is **memory-bandwidth-bound** for token generation, and **compute-bound** for prefill. A model is CPU-friendly when:

- **Total size after quantization fits in RAM** — Q4 quantized 7B uses ~4.5 GB; Q4 13B uses ~8 GB. Systems with 16 GB RAM handle either comfortably.
- **Activation sparsity is high** — MoE models that route each token to a subset of experts (DeepSeek-R1, Qwen3 MoE) activate only 5–15% of total parameters.
- **KV cache grows predictably** — Recurrent architectures (RWKV, Mamba) use O(1) memory per token; transformers with quantized KV (IQ4, TurboQuant) keep cache fits small.
- **Embedding or encoder-only** — Single-pass models with no autoregressive decode (BERT, CLIP, Whisper encoder) are naturally CPU-friendly.

---

## Dense Models ≤ 8B

The sweet spot for CPU inference. Q4 quantized these fit in 2–5 GB RAM and run on any modern laptop or server CPU.

| Model | Params | Q4 Size | Recommended Runtime | Reported CPU Throughput | Notes |
|---|---|---|---|---|---|
| [Llama 3.2 3B](https://huggingface.co/meta-llama/Llama-3.2-3B) | 3B | ~2 GB | llama.cpp Q4_K_M | 25–38 tok/s (iPhone 15 Pro) | [PocketLLM bake-off](../README.md#talks-papers-and-articles) |
| [Phi-3.5 Mini](https://huggingface.co/microsoft/Phi-3.5-mini-instruct) | 3.8B | ~2.5 GB | ONNX Runtime, llama.cpp | 137.6 tok/s (ONNX on Xeon) | [ISE benchmark](../README.md#benchmarks-and-evidence) |
| [Qwen3 4B](https://huggingface.co/Qwen/Qwen3-4B) | 4B | ~2.8 GB | llama.cpp Q4_K_M, eLLM | 20–35 tok/s on desktop CPU | Strong multilingual support |
| [Gemma 2 2B](https://huggingface.co/google/gemma-2-2b) | 2B | ~1.5 GB | llama.cpp Q4_K_M | 35–45 tok/s on M-series Mac | Highest tok/s in its class |
| [TinyLlama 1.1B](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) | 1.1B | ~0.8 GB | llama.cpp, MLC | 50+ tok/s on any CPU | Minimum viable model for testing |
| [Llama 3.2 1B](https://huggingface.co/meta-llama/Llama-3.2-1B) | 1B | ~0.7 GB | llama.cpp, ONNX Runtime | 60+ tok/s on modern CPU | Good for classification/rewriting |
| [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) | 7B | ~4.5 GB | llama.cpp Q4_K_M | 18–22 tok/s on Graviton4 | [Arm walkthrough](../README.md#mixture-of-experts-on-cpu) |
| [Qwen3-Coder-8B](https://qwenlm.github.io/blog/qwen3-coder/) | 8B | ~5 GB | llama.cpp, eLLM | 15–25 tok/s on desktop CPU | Code generation, uses L3 cache well |

---

## Dense Models 8B–13B

Pushes the boundary of comfortable CPU inference. Requires ≥ 16 GB RAM for Q4. Viable for low-throughput serving and batch workloads.

| Model | Params | Q4 Size | Recommended Runtime | Notes |
|---|---|---|---|---|
| [Llama 3.1 8B](https://huggingface.co/meta-llama/Llama-3.1-8B) | 8B | ~5.5 GB | llama.cpp, ONNX Runtime | 450 tok/s server, 1,196 tok/s offline (Xeon 6) per MLPerf |
| [Qwen3 8B](https://huggingface.co/Qwen/Qwen3-8B) | 8B | ~5.5 GB | llama.cpp, eLLM | Good multilingual coverage |
| [Mistral 7B v0.3](https://huggingface.co/mistralai/Mistral-7B-v0.3) | 7B | ~4.5 GB | llama.cpp, candle | Strong English benchmark performance |
| [DeepSeek-R1-Distill-Llama-8B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B) | 8B | ~5.5 GB | OpenVINO, llama.cpp | 155.4 tok/s on Xeon via OpenVINO |
| [Gemma 3 12B](https://huggingface.co/google/gemma-3-12b-it) | 12B | ~8 GB | llama.cpp Q4_K_M | Fits in 16 GB RAM; ~8–12 tok/s on desktop |
| [Qwen3 14B](https://huggingface.co/Qwen/Qwen3-14B) | 14B | ~9 GB | llama.cpp Q4_K_M | Requires 16 GB+; ~6–10 tok/s |

---

## MoE Models (high activation sparsity)

MoE architectures activate only a fraction of parameters per token, making their *effective* size much smaller than total params. These can run on CPU when aggressively quantized and the working set fits in RAM.

| Model | Total | Active | Q4 RAM Use | Runtime | Notes |
|---|---|---|---|---|---|
| [Qwen3 30B-A3B](https://huggingface.co/Qwen/Qwen3-30B-A3B) | 30B | 3B | ~6 GB | llama.cpp, eLLM | ~3B active per token; excellent CPU fit |
| [Gemma 4 26B-A4B](https://ai.google.dev/gemma) | 26B | 4B | ~5.5 GB | llama.cpp, fucina | 7 tok/s on 2013 Ivy Bridge Xeon |
| [Inkling 975B-A41B](https://huggingface.co/thinkingmachines/Inkling) | 975B | 41B | ~8 GB (IQ1_S) | llama.cpp | Multimodal; fits with extreme quantization |
| [DeepSeek-R1 671B](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 671B | 37B | ~10 GB (IQ1_S) | llama.cpp | [MoE on CPU](../README.md#mixture-of-experts-on-cpu) |
| [GLM-5.2](https://github.com/THUDM/GLM) | 744B | 44B | ~16 GB (INT4) | llama.cpp, fucina | Disk-streamed experts |
| [MiniMax M2.5](https://github.com/MiniMax-AI/MiniMax-M2.5) | 456B | 46B | varies | eLLM | Prefill-heavy use cases |
| [DeepSeek V4 Flash 284B-A13B](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) | 284B | 13B | ~8 GB (Q4_K) | fucina | Native MTP speculative decoding |

---

## Ternary / 1-bit Models

Models using {−1, 0, +1} or {−1, +1} weights turn multiply-accumulate into addition, dramatically reducing memory bandwidth requirements — the dominant bottleneck on CPU. This makes ternary models the single strongest argument for CPU-first inference: a 100B model fits in ~7 GB and runs on a single CPU core at human reading speed.

| Model | Bits | Total Size | Runtime | Reported Throughput | Notes |
|---|---|---|---|---|---|---|
| [BitNet b1.58 2B4T](https://huggingface.co/microsoft/bitnet-b1.58-2B-4T) | 1.58-bit | ~0.4 GB | bitnet.cpp | 20–30 tok/s (Apple M2) | First open-source native ternary LLM; MIT license |
| [Bonsai 27B (PrismML)](https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf) | 1-bit / 1.58-bit | ~3.9 GB / ~5.9 GB | llama.cpp, bitnet.cpp | ~11 tok/s (iPhone 17 Pro CPU) | Multimodal; Apache 2.0 |
| [BitNet b1.58 100B](https://github.com/microsoft/BitNet) | 1.58-bit | ~7 GB | bitnet.cpp | 5–7 tok/s on single CPU | [bitnet.cpp](../README.md#runtimes-and-inference-engines) |
| [DeepSeek-R1 671B (IQ1_S)](https://huggingface.co/deepseek-ai/DeepSeek-R1) | ~1-bit | ~10 GB | llama.cpp IQ1_S | 2–4 tok/s on 64 GB server | Extreme quantization of MoE |

### Why ≤3B Dense and Ternary Models Lead on CPU Cost Advantage

≤3B dense models (Q4, ~2 GB) and ternary models of any size share a decisive economic property: **they fit entirely in system RAM with no GPU needed**. The CPU cost advantage is clearest here because:

- **Widest deployment base** — every laptop, server, and phone already has a CPU. GPU inference requires dedicated hardware that most devices lack.
- **Memory-bandwidth bound** — LLM token generation is bottlenecked by how fast weights reach the compute unit, not by compute itself. Ternary models reduce this by 8–16× (1.58-bit vs 16-bit), and ≤3B dense models have few enough weights that even modest DDR bandwidth suffices.
- **Zero accelerator cost** — no GPU purchase, no cloud GPU rental, no CUDA compatibility to maintain. The CPU is already paid for.
- **Energy per token** — ternary addition replaces FP16 multiplication (~70× less energy per operation on 7nm); ≤3B dense models at Q4 draw < 30 W system power vs 150–600 W for a GPU running the same model.

This combination — minimal hardware investment, universal availability, and energy-efficient arithmetic — makes ≤3B dense and ternary models the highest-ROI entry point for CPU-first AI deployment.

### Coming Soon / In Development

The ternary ecosystem is evolving rapidly. The following models and capabilities are announced or in active development but not yet shipping:

| Project | What's Coming | Stage | Expected |
|---|---|---|---|
| [BitNet v2](https://arxiv.org/abs/2506.23025) (Microsoft Research) | Next-gen ternary architecture with 4-bit activations via Hadamard transformation; preserves ternary weights while reducing activation quantization error | Paper (2025) | Model TBA |
| Larger native ternary models (7B+) | Microsoft acknowledges only 2B scale released; 7B, 13B, and 70B native ternary models not yet trained; community post-training ternary conversions (e.g., Llama3-8B-1.58-100B-tokens) exist but lack native training quality | Research gap | Dependent on training cost reductions |
| [Spectra 1.1 TriLM](https://arxiv.org/abs/2506.23025) (NolanoOrg) | Scaling ternary language models to 1.2T tokens; models up to 3.6B params with scaling law validation that TriLMs match FP performance at equivalent bit budgets | Paper + models (2025) | 3.6B weights available |
| bitnet.cpp NPU backend | NPU inference kernels for ternary models (Qualcomm, Apple ANE, MediaTek) — listed as "coming next" in the BitNet repository | In development | TBA |
| [TWLA](https://arxiv.org/abs/2606.13054) | Post-training quantization achieving ternary weights + low-bit activations jointly, enabling PTQ-based ternarization without expensive QAT | Paper (Jun 2026) | Model TBA |

---

## Mobile-Friendly Models

Models that run well on phone CPUs — balancing size, quantization, and thermal constraints. Phone CPUs have less aggressive cooling than laptops, so sustained throughput after thermal stabilisation is lower than peak burst. However, **2025–2026 SoCs represent an inflection point**: the Apple A19 Pro introduces vapour-chamber cooling (40% better sustained performance vs A18 Pro), and the Snapdragon 8 Elite Gen 5 delivers 35% better CPU efficiency on the same 3nm N3P node. On these chips sustained throughput now reaches 65–85% of burst for models ≤3B, whereas older SoCs typically sustain 40–60%. The sweet spot remains ≤ 3B params at Q4 (~2 GB), with ternary models pushing much larger effective sizes into phone RAM.

| Model | Params | Quant | RAM Use | Runtime | Mobile Throughput | Notes |
|---|---|---|---|---|---|---|
| [Llama 3.2 3B](https://huggingface.co/meta-llama/Llama-3.2-3B) | 3B | Q4_K_M | ~2 GB | MLC-LLM, llama.cpp | 25–38 tok/s (iPhone 15 Pro) | [PocketLLM bake-off](../README.md#talks-papers-and-articles); best quality/size tradeoff |
| [Llama 3.2 1B](https://huggingface.co/meta-llama/Llama-3.2-1B) | 1B | Q4_K_M | ~0.7 GB | MLC-LLM, ExecuTorch | 50–60+ tok/s (flagship) | Good for classification/rewriting; runs on any phone |
| [Phi-3.5 Mini](https://huggingface.co/microsoft/Phi-3.5-mini-instruct) | 3.8B | Q4_K_M | ~2.5 GB | MLC-LLM, ONNX Runtime | 12+ tok/s (iPhone 14) | [Microsoft Phi-3 report](../README.md#talks-papers-and-articles); fits 1.8 GB at 4-bit |
| [Gemma 2 2B](https://huggingface.co/google/gemma-2-2b) | 2B | Q4_K_M | ~1.5 GB | llama.cpp Android | 35–45 tok/s on M-series Mac | Highest tok/s per watt in its class |
| [Qwen3 4B](https://huggingface.co/Qwen/Qwen3-4B) | 4B | Q4_K_M | ~2.8 GB | MLC-LLM, ExecuTorch | 15–25 tok/s (Snapdragon 8 Elite) | Strong multilingual support; largest comfy on 8 GB phones |
| [BitNet b1.58 2B4T](https://huggingface.co/microsoft/bitnet-b1.58-2B-4T) | 2B | 1.58-bit | ~0.4 GB | bitnet.cpp, MLC-LLM | 20–30 tok/s (M2) | Open-source native ternary; first 1-bit LLM at 2B scale; MIT |
| [Gemma 3 12B](https://huggingface.co/google/gemma-3-12b-it) | 12B | Q4_K_M | ~8 GB | MLC-LLM, llama.cpp | 3–6 tok/s (A19 Pro) | Fits 12 GB iPhones only; thermal throttling after ~2 min |
| [TinyLlama 1.1B](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) | 1.1B | Q4_K_M | ~0.8 GB | llama.cpp, MLC | 50+ tok/s on any phone | Best for always-on, low-power scenarios |
| [Bonsai 27B (PrismML)](https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf) | 27B | 1-bit / 1.58-bit | ~3.9 GB / ~5.9 GB | llama.cpp, bitnet.cpp | ~11 tok/s (iPhone 17 Pro CPU) | Ternary quantization pushes a 27B model into phone RAM; [vendor-reported](../README.md#quantization-and-model-formats) |
| [Qwen3 30B-A3B](https://huggingface.co/Qwen/Qwen3-30B-A3B) | 30B total / 3B active | Q4_K_M | ~6 GB | llama.cpp, MLC-LLM | 5–10 tok/s (A19 Pro) | MoE activates only 3B per token; fits 8 GB phones with thermal headroom |
| [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) | 7B | Q4_K_M | ~4.5 GB | llama.cpp Android | 7–12 tok/s (Snapdragon 8 Elite) | Largest dense model that fits 8 GB phones comfortably |

**Key mobile runtimes:** [MLC-LLM](https://github.com/mlc-ai/mlc-llm) (iOS + Android, Metal/OpenCL/Vulkan, 6–12 tok/s for 7B INT4), [llama.cpp Android](https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md) (CPU-only, any GGUF, 9–12 tok/s on SD8 Elite), [ExecuTorch](https://github.com/pytorch/executorch) (PyTorch-native, ARM XNNPACK), [Apple Core AI](https://developer.apple.com/videos/play/wwdc2026/324/) (Swift API, CPU/GPU/ANE, WWDC 2026). For the cost-advantage analysis of ≤3B and ternary models on mobile, and a coming-soon tracker for in-development ternary projects (BitNet v2, larger native ternary models, NPU backends), see [Ternary / 1-bit Models](#ternary--1-bit-models).

**Mobile-specific caveats:**
- **Sustained vs burst (SoC generation matters):** Most phone benchmarks report burst throughput (first 30–60 s). Sustained tok/s after thermal stabilisation depends heavily on the SoC generation:<br> • **Apple A19 Pro** — vapour-chamber cooling delivers ~40% better sustained performance vs A18 Pro; Wikipedia explicitly cites LLM processing as a beneficiary. Geekbench 6 multi-core ~11,054 at ~11 W, outstanding perf/watt.<br> • **Snapdragon 8 Elite Gen 5** — 35% CPU efficiency improvement over Gen 4; multi-core ~12,546 at ~20 W peak (highest raw throughput of any mobile SoC). Best sustained on Android.<br> • **Older SoCs (A18 Pro, SD8 Gen 3, Dimensity 9300)** — sustained throughput typically 50–65% of burst; no vapour chamber.<br>As a rule of thumb, expect **65–85% of burst sustained** on 2025–2026 flagships vs **50–65%** on prior generations for models ≤3B.
- **Memory pressure:** iOS uses unified memory (8–12 GB on flagships); Android reserves ~2–3 GB for the OS. A 7B Q4 model (~4.5 GB) leaves < 2 GB headroom on 8 GB phones — expect app kills under load.
- **NPU fragmentation:** NPU paths (Qualcomm QNN, MediaTek NeuroPilot, Samsung ENN) are vendor-specific, have immature LLM tooling, and often underperform CPU on generative workloads due to memory-bandwidth limits. The CPU path is the most portable and frequently the fastest option for LLM inference on phones today.

See [docs/mobile-cpu-inference.md](mobile-cpu-inference.md) for the full mobile hardware catalogue — chipsets, runtimes, benchmarks, and thermal measurements.

---

## Small Embedding Models

Embedding models are computationally light — a single forward pass producing a small vector. CPU is the natural deployment target.

| Model | Size | Runtime | Latency | Notes |
|---|---|---|---|---|
| [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | 22M | ONNX Runtime CPU | single-digit ms on any CPU | Most widely deployed embedding model |
| [BGE-M3](https://huggingface.co/Sophia-AI/bge-m3-onnx) | 326M | ONNX Runtime CPU | ~15 ms on modern CPU | Multi-lingual, supports dense + sparse |
| [BGE-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) | 24M | ONNX Runtime CPU | ~5 ms | Fastest viable retrieval embedding |
| [GTE-small](https://arxiv.org/abs/2402.17035) | 22M | ONNX Runtime CPU | ~5 ms | Good quality/speed tradeoff |

---

## Vision Models

Detection and classification models achieve high throughput on CPU with modern runtimes.

| Model | Runtime | CPU Throughput | Notes |
|---|---|---|---|
| [YOLOv8/v9/v10/v11](https://docs.ultralytics.com/integrations/openvino/) | OpenVINO | 360+ fps (large), ~5000 fps (small) on Xeon | GPUs unnecessary for most video pipelines |
| [EfficientNet ONNX](https://github.com/zhangchaosd/ModelInferBench) | ONNX Runtime CPU | 12 ms/image (14× over PyTorch CPU) | INT8 quantization support |
| [MobileNetV3 TFLite](https://www.tensorflow.org/lite) | TFLite XNNPACK | 23 ms INT8 on Pi 4 | Standard for edge vision |
| [MobileSAM](https://github.com/ChaoningZhang/MobileSAM) | ONNX Runtime CPU | ~3 s/image | Acceptable for batch segmentation |

---

## ASR / TTS Models

Speech workloads are CPU-friendly — most achieve real-time or faster on commodity hardware.

| Model | Runtime | CPU Performance | Notes |
|---|---|---|---|
| [Whisper base/small](https://github.com/ggerganov/whisper.cpp) | whisper.cpp | 3–5× real-time on Pi 5 | ARM NEON + x86 AVX paths |
| [Whisper large-v3](https://github.com/ggerganov/whisper.cpp) | whisper.cpp | ~1× real-time on M-series Mac | Best accuracy, still CPU-viable |
| [Piper](https://github.com/OHF-Voice/piper1-gpl) | Piper ONNX | RTF 0.15 on Pi 5 | Home Assistant default TTS |
| [PocketTTS](https://github.com/kyutai-labs/pocket-tts) | PocketTTS | ~6× real-time on M4 CPU | CPU-only by design |
| [Qwen3-TTS 0.6B/1.7B](https://github.com/gabriele-mastrapasqua/qwen3-tts) | qwen3-tts | RTF 0.52 INT4 on M1 CPU | Pure C engine, 10 languages |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | PaddleOCR | ~57 ms detection, ~47 ms recognition | CPU-optimized with MKL-DNN |

---

## Model Selection Tools

Tools that help you choose a model for your specific hardware:

- **[llmfit](https://github.com/AlexsJones/llmfit)** — Detects your RAM/CPU/GPU and ranks hundreds of models by a Fit score (0–100) across memory fit, speed, quality, and context length.
- **[whichllm](https://github.com/Andyyyy64/whichllm)** — CLI that auto-detects hardware and ranks models by recency-aware benchmarks.
- **[Local AI Master Model Recommender](https://localaimaster.com/tools/model-recommender)** — Browser-based recommender for RAM/VRAM budget, with Q4 memory requirements and tok/s estimates.

---

## See also

- [Runtimes and Inference Engines](../README.md#runtimes-and-inference-engines) — The runtimes that serve these models
- [Quantization and Model Formats](../README.md#quantization-and-model-formats) — GGUF, IQ, ternary formats
- [Benchmarks and Evidence](../README.md#benchmarks-and-evidence) — Measured throughput across hardware
- [Hardware Reference](hardware-reference.md) — CPU performance by device tier
- [Model Conversion Guide](model-conversion-guide.md) — Converting HF checkpoints to GGUF/ONNX
