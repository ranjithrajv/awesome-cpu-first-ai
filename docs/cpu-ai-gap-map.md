# CPU AI Gap Map

A scored, sourced assessment of the CPU-first AI tooling landscape — grading every major tool on CPU-nativeness, CPU performance, architecture coverage, and adoption — to identify where the CPU ecosystem is mature and where gaps remain.

Inspired by the [AI Potluck Open Source AI Gap Map](https://www.aipotluck.org/map) (which scores *openness*), this map scores **CPU-nativeness** — the degree to which a tool is designed for CPU inference rather than treating it as a secondary fallback.

---

## Contents

- [Methodology](#methodology)
- [Scoring Axes](#scoring-axes)
- [CPU-Nativeness Rubric](#cpu-nativeness-rubric)
- [Architecture Coverage Grid](#architecture-coverage-grid)
- [Maturity Stages](#maturity-stages)
- [Gap Types](#gap-types)
- [Category Scorecards](#category-scorecards)
  - [1. LLM Inference (Decode)](#1-llm-inference-decode)
  - [2. LLM Prompt Processing (Prefill)](#2-llm-prompt-processing-prefill)
  - [3. ASR / STT](#3-asr--stt)
  - [4. TTS](#4-tts)
  - [5. Embeddings](#5-embeddings)
  - [6. Vision — Detection & Classification](#6-vision--detection--classification)
  - [7. Vision — Segmentation](#7-vision--segmentation)
  - [8. OCR](#8-ocr)
  - [9. Image Generation (Diffusion)](#9-image-generation-diffusion)
  - [10. Fine-Tuning (LoRA / QLoRA)](#10-fine-tuning-lora--qlora)
- [Summary Dashboard](#summary-dashboard)
- [Limitations](#limitations)
- [See also](#see-also)

---

## Methodology

Every tool currently listed in this awesome list is scored on four axes. Scores are assigned from primary sources — benchmark figures already documented in this repo, tool READMEs, and adoption registries (GitHub, PyPI). Model-level adoption and ecosystem signals (download volume, size distribution, task mix) come from the [HF Landscape](https://huggingface.co/spaces/ranjithraj/hf-landscape) weekly Hub crawl; see [The CPU-First Case, in Hub Data](ecosystem-evidence.md) for the reproducible queries behind those figures. The scored set is the tools in this list, not a census; the long tail of unlisted tools is not graded.

The CPU-nativeness framework descends from this list's [CONTRIBUTING.md](../CONTRIBUTING.md) criterion #4: *"Not a GPU framework that runs on CPU only as a slow fallback."* The gap map makes that criterion quantitative.

---

## Scoring Axes

| Axis | Scale | What it measures | Source family |
|---|---|---|---|
| **CPU-nativeness** | 0–5 | Is CPU the primary target, or a slow fallback? | Tool README, docs, architecture |
| **CPU performance** | 0–5 | Documented throughput/latency on commodity CPU | Benchmarks in this repo, vendor benchmarks, community data |
| **Arch coverage** | grid | Which ISAs have optimized kernels | Tool docs, build flags, kernel source |
| **Adoption** | 1–5 | Real deployment signal (downloads, production use) | PyPI, npm, GitHub, Hugging Face |

**CPU performance scores are within-category.** A 4 in LLM decode is not comparable to a 4 in OCR — the grade is relative to what is achievable for that workload type on CPU.

**Adoption scoring** (adapted from the [AI Potluck methodology](https://www.aipotluck.org/map/methodology)):

| Score | Signal | Cap |
|---|---|---|
| 5 | > 100K daily downloads or > 50K GitHub stars | — |
| 4 | 10K–100K daily downloads or 10K–50K stars | — |
| 3 | 1K–10K daily downloads or 1K–10K stars | Stars alone never raise above 3 |
| 2 | 100–1K daily downloads or 100–1K stars | — |
| 1 | < 100 daily downloads or < 100 stars | — |

---

## CPU-Nativeness Rubric

The core axis. Only tools scoring ≥ 4 advance a category's maturity stage. Tools at 2–3 are used only to detect gaps, not to credit maturity.

| Score | Definition | CPU is... | Examples |
|---|---|---|---|
| **5** | Designed for CPU from day one; the only or clearly primary target | The only target | llama.cpp, whisper.cpp, PocketTTS, clip.cpp |
| **4** | CPU is a first-class target alongside optional GPU; CPU kernels are hand-optimized, not inherited | A first-class target | ONNX Runtime, OpenVINO, ExecuTorch, ncnn, XNNPACK, candle |
| **3** | CPU path works and is documented, but GPU is the assumed default; CPU is supported, not optimized-first | The secondary target | ollama, MLC LLM, WebLLM, LiteRT.js |
| **2** | CPU works but is clearly secondary; README leads with GPU; CPU kernels are generic, not hand-tuned | A fallback | PyTorch (inference only), most generic ML frameworks |
| **1** | CPU is a slow fallback with no optimized kernels; would be excluded by CONTRIBUTING rule #4 | Barely functional | (excluded from this list) |
| **0** | No real CPU path | Nonexistent | (excluded) |

---

## Architecture Coverage Grid

Architecture coverage is a matrix, not a single score. Each tool marks which ISAs have hand-optimized or verified kernels (not just "compiles on").

| Symbol | CPU meaning | GPU meaning | 🧠 NPU meaning |
|---|---|---|---|---|
| ✅ | Hand-optimized SIMD kernels (NEON, AVX2, RVV, WASM SIMD) | Production GPU backend (CUDA, Metal, Vulkan) | Production NPU backend (QNN, ANE, Intel NPU, XDNA) |
| ✅† | NEON + hand-optimized SVE/SVE2 kernels (Neoverse V1/V2/V3, Cobalt 100/200) | — | — |
| ⚠️ | Works but no hand-optimized kernels; relies on generic C/BLAS | Experimental or limited GPU support | Experimental NPU support or vendor-specific only |
| ❌ | Not supported or no evidence | No GPU path / CPU-only | No NPU path / CPU-only |

**ISA columns:**

- **x86** — AVX2, AVX-512, AMX (Intel Xeon Sapphire Rapids+)
- **ARM** — NEON (baseline); ✅† indicates additional hand-optimized SVE/SVE2 kernels (Neoverse V1/V2/V3, Cobalt 100/200)
- **RISC-V** — RVV (RISC-V Vector Extension)
- **WASM** — WebAssembly SIMD, XNNPACK WASM
- **GPU** — CUDA / Metal / Vulkan / DirectML backend presence and maturity
- **NPU** — Qualcomm QNN / Apple ANE / Intel NPU / AMD XDNA / MediaTek NeuroPilot backend presence (vendor-locked)

---

## Maturity Stages

Each category is placed on a maturity stage from 0 (Void) to 5 (Mature). Only tools scoring **≥ 4 on CPU-nativeness** advance a category's stage — tools at 2–3 ("CPU works but secondary") are used solely to detect gaps, not to credit maturity.

| Stage | Label | Criteria |
|---|---|---|
| **5** | Mature CPU ecosystem | ≥ 2 mature CPU-native tools (score ≥ 4.5) with optimized kernels across both x86 and ARM |
| **4** | Competitive CPU ecosystem | ≥ 1 mature CPU-native tool (score ≥ 4.5), but fewer than 2 |
| **3** | Viable CPU alternatives | No mature CPU-native tool, but the best CPU-native option is strong (score ≥ 3.5) |
| **2** | Emerging CPU alternatives | No mature CPU-native tool; best CPU-native option is promising but limited (score ≥ 2.5) |
| **1** | CPU experiments | CPU-native options exist but are weak on both performance and adoption (score < 2.5) |
| **0** | Void | No usable CPU-native option exists |

The **maturity score** per tool is a weighted blend: `score = (0.4 × CPU_perf + 0.6 × adoption)` for end-user tools, `score = (0.6 × CPU_perf + 0.4 × adoption)` for infrastructure. A tool is "mature" at score ≥ 4.5 — a deliberately demanding bar.

### 🧠 NPU Maturity Note

NPU maturity is assessed separately from CPU maturity. The NPU landscape is fragmented by vendor (Qualcomm Hexagon, Apple ANE, Intel NPU, AMD XDNA, MediaTek NPU, Samsung ENN) with no cross-platform standard — a model compiled for one NPU will not run on another without recompilation through a different SDK. NPU maturity stages in this gap map follow the same 0–5 scale but are **vendor-specific**: an NPU may be Stage 5 on Snapdragon (via QNN) but Stage 0 on everything else. CPU is the only universal deployment target across all vendors.

---

## Gap Types

Each category carries zero or more gaps:

| Gap | Meaning |
|---|---|
| **Void** | No CPU-native option exists for this workload |
| **Performance** | A CPU-native option exists but its throughput is too low for practical use |
| **Architecture** | Works on x86 but not ARM/RISC-V (or vice versa) — an ISA-specific kernel gap |
| **Maturity** | CPU-native options exist, but none are production-ready |
| **Coverage** | Only one architecture has optimized kernels — no cross-arch redundancy |

A fully mature category carries no gaps.

---

## Category Scorecards

---

### 1. LLM Inference (Decode)

**Stage: 5 — Mature CPU ecosystem**
**Gaps: None**

The strongest category in CPU-first AI. Multiple mature, competitive CPU-native runtimes with hand-optimized kernels across x86 and ARM. This is the category that proved CPU inference is viable.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | 5 | 5 | ✅ | ✅† | ✅ | ⚠️ | ✅ | 5 (120K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [ONNX Runtime (CPU EP)](https://onnxruntime.ai) | 4 | 5 | ✅ | ✅† | ⚠️ | ✅ | ✅ | 5 (2.8M dl/day) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [OpenVINO](https://github.com/openvinotoolkit/openvino) | 4 | 5 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 4 (10.5K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [candle](https://github.com/huggingface/candle) | 4 | 4 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 4 (20.6K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [ExecuTorch](https://github.com/pytorch/executorch) | 4 | 4 | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | 3 (4.8K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [eLLM](https://github.com/lucienhuangfu/eLLM) | 5 | 3 | ✅ (AMX) | ❌ | ❌ | ❌ | ❌ | 2 (428★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [ncnn](https://github.com/Tencent/ncnn) | 4 | 4 | ✅ | ✅ | ✅ | ❌ | ✅ | 4 (23.5K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [MNN](https://github.com/alibaba/MNN) | 4 | 4 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 4 (15.6K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [LiteRT.js](https://ai.google.dev/edge/litert/web) | 3 | 3 | ❌ | ❌ | ❌ | ✅ | ❌ | 3 (3K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [WebLLM](https://github.com/mlc-ai/web-llm) | 3 | 3 | ❌ | ❌ | ❌ | ✅ | ✅ | 4 (18.3K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [ollama](https://github.com/ollama/ollama) | 3 | 3 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 5 (176K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [ctransformers](https://github.com/marella/ctransformers) | 4 | 3 | ✅ | ✅ | ⚠️ | ❌ | ❌ | 3 (1.9K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |
| [llamafile](https://github.com/mozilla-ai/llamafile) | 5 | 4 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 4 (25.4K★) | [Runtimes](../README.md#runtimes-and-inference-engines) |

**Gap analysis:** No gaps. The ecosystem is mature with ≥ 8 tools scoring CPU-native ≥ 4, strong cross-arch coverage (x86 + ARM + RISC-V via llama.cpp/ncnn), and the WASM path covered by LiteRT.js/WebLLM. The main limitation is prefill throughput (see next category). eLLM is a promising Rust-based CPU-native addition (AMX-optimized, alpha quality) but limited to Intel Xeon 4th Gen+ and not yet validated with real model weights.

---

### 2. LLM Prompt Processing (Prefill)

**Stage: 4 — Competitive CPU ecosystem**
**Gaps: Architecture (RISC-V kernel coverage thin)**

Prefill is more compute-bound than decode (large matrix multiply), making it the phase where GPU retains the largest advantage. CPU options are competitive on small models but trail on long contexts.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | 5 | 4 | ✅ | ✅† | ✅ | ⚠️ | ✅ | 5 (120K★) | [Benchmarks](../README.md#benchmarks-and-evidence) |
| [ONNX Runtime GenAI](https://onnxruntime.ai) | 4 | 5 | ✅ | ✅† | ⚠️ | ❌ | ✅ | 5 (2.8M dl/day) | [CPU benchmark](../README.md#benchmarks-and-evidence): 137.6 tok/s Phi-3 |
| [OpenVINO](https://github.com/openvinotoolkit/openvino) | 4 | 5 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 4 (10.5K★) | [Model Hub benchmarks](../README.md#benchmarks-and-evidence) |
| [eLLM](https://github.com/lucienhuangfu/eLLM) | 5 | 3 | ✅ (AMX) | ❌ | ❌ | ❌ | ❌ | 2 (428★) | [Runtimes](../README.md#runtimes-and-inference-engines) |

**Gap analysis:** OnNX Runtime GenAI outperforms llama.cpp on prefill (137.6 vs 109.5 tok/s for Phi-3), showing optimized prefill kernels matter. OpenVINO is strong on Intel x86 but ARM support is limited. RISC-V prefill kernels exist only in llama.cpp (via the [V-Seek paper](../README.md#on-device-edge-arm-and-sbcs)). The gap is in cross-arch prefill-specific optimizations — most runtimes optimize decode more aggressively than prefill.

> **Severity:** Medium — affects long-context interactive use cases but avoidable with proper runtime selection (ONNX Runtime GenAI for prefill-heavy workloads).  
> **Recommended action:** Contribute SVE/MMLA-optimized prefill kernels to llama.cpp or ONNX Runtime. Extend OpenVINO prefill optimizations to ARM via KleidiAI integration. Port V-Seek RVV kernels upstream into llama.cpp mainline.

---

### 3. ASR / STT

**Stage: 5 — Mature CPU ecosystem**
**Gaps: None**

Speech-to-text is one of the most CPU-friendly AI workloads. Multiple mature CPU-native engines with real-time or faster-than-real-time throughput on commodity hardware.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [whisper.cpp](https://github.com/ggerganov/whisper.cpp) | 5 | 5 | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | 5 (51.7K★) | [Runtimes](../README.md#runtimes-and-inference-engines): 3–5× RT on Pi 5 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 4 | 5 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 5 (252K dl/day) | [ASR/STT](#asr--stt): 4× faster than openai/whisper |
| [transcribe.cpp](https://github.com/handy-computer/transcribe.cpp) | 5 | 4 | ✅ | ⚠️ | ⚠️ | ⚠️ | ❌ | 2 (168★) | [ASR/STT](#asr--stt): 16+ model families, tinyBLAS CPU |
| [Vosk](https://alphacephei.com/vosk/) | 4 | 4 | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | 4 (14.9K★, 19K dl/day) | [ASR/STT](#asr--stt): 50 MB models, Pi/Android |

**Gap analysis:** No gaps. whisper.cpp and faster-whisper both deliver > real-time on commodity CPU. transcribe.cpp extends coverage to 16+ ASR model families beyond Whisper (Parakeet, Canary, Moonshine, Voxtral) — the breadth gap it fills was the single-model limitation of whisper.cpp. Vosk covers streaming and offline on resource-constrained ARM.

---

### 4. TTS

**Stage: 4 — Competitive CPU ecosystem**
**Gaps: Maturity (PocketTTS is young; Coqui maintenance uncertain)**

TTS has reached real-time CPU synthesis, but the ecosystem is less mature than ASR. Piper leads on edge/embedded; PocketTTS leads on quality + voice cloning but is new (2026).

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [Piper](https://github.com/OHF-Voice/piper1-gpl) | 5 | 5 | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | 4 (4.8K★, 25K dl/day) | [TTS](#tts): RTF 0.15 on Pi 5 |
| [PocketTTS](https://github.com/kyutai-labs/pocket-tts) | 5 | 5 | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | 4 (7.4K★) | [TTS](#tts): ~6× real-time on M4, CPU-only by design |
| [PocketTTS.cpp](https://github.com/VolgaGerm/PocketTTS.cpp) | 5 | 5 | ✅ | ⚠️ | ❌ | ✅ | ❌ | 2 (43★) | [TTS](#tts): 9.2× real-time INT8, OpenAI-compatible API |
| [Coqui TTS](https://github.com/idiap/coqui-tts) | 4 | 4 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 3 (2.3K★, 5.4K dl/day) | [TTS](#tts): XTTSv2 voice cloning, CPU Docker |
| [qwen3-tts](https://github.com/gabriele-mastrapasqua/qwen3-tts) | 5 | 4 | ✅ | ✅ | ❌ | ❌ | ⚠️ | 2 (64★) | [TTS](#tts): Pure C, 0.52 RTF INT4 on M1 CPU |

**Gap analysis:** Maturity gap — Piper is production-proven (Home Assistant default) but uses older VITS architecture; PocketTTS has superior quality and is CPU-first by design (the authors explicitly note no GPU speedup at batch=1), but it is new and the ecosystem of integrations is still forming. Coqui TTS maintenance is uncertain (idiap fork, not the original Coqui). qwen3-tts adds a pure C CPU-native option with 10-language support and hand-tuned NEON/AVX2 kernels — its RTF 0.52 INT4 on M1 CPU is competitive with PocketTTS, though it is newer (64★). The RISC-V WASM path is thin — PocketTTS.cpp has a WASM build but no ARM-optimized kernels yet.

> **Severity:** Low — production needs are met by Piper; the maturity gap is narrowing with multiple CPU-native options (PocketTTS, qwen3-tts).  
> **Recommended action:** Build integration packages (Home Assistant add-on, Ollama plugin, OpenAI-compatible API server). Validate qwen3-tts benchmark claims with independent hardware testing.

---

### 5. Embeddings

**Stage: 5 — Mature CPU ecosystem**
**Gaps: None**

Embedding inference is computationally light — a single forward pass producing a small vector. CPU is the natural deployment target and the ecosystem is well-served.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [sentence-transformers ONNX](https://sbert.net) | 4 | 5 | ✅ | ✅ | ⚠️ | ✅ | ✅ | 5 (928K dl/day) | [Text Embeddings](#text-embeddings): 1.4× speedup, 3× with INT8 |
| [BGE-M3 ONNX](https://huggingface.co/Sophia-AI/bge-m3-onnx) | 4 | 4 | ✅ | ✅ | ⚠️ | ✅ | ✅ | 3 | [Text Embeddings](#text-embeddings) |
| [all-MiniLM-L6-v2 ONNX](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | 4 | 5 | ✅ | ✅ | ⚠️ | ✅ | ✅ | 5 (#1 model on the Hub, 253M dl/30d) | [Text Embeddings](#text-embeddings): single-digit ms on any CPU |

**Gap analysis:** No gaps. The ONNX Runtime CPU backend delivers production-grade embedding inference with INT8 quantization (AVX-512 VNNI). all-MiniLM-L6-v2 is the single most-downloaded model on the entire Hub (253M downloads in 30 days — see [The CPU-First Case, in Hub Data](ecosystem-evidence.md)) and runs in single-digit milliseconds on any modern CPU via ONNX export. The WASM path is well-covered via Transformers.js + ONNX Runtime Web.

---

### 6. Vision — Detection & Classification

**Stage: 5 — Mature CPU ecosystem**
**Gaps: None (RISC-V emerging but not blocking)**

Vision detection/classification on CPU is well-served by OpenVINO and ONNX Runtime, with throughput reaching thousands of fps for small models.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [YOLOv8 + OpenVINO](https://docs.ultralytics.com/integrations/openvino/) | 4 | 5 | ✅ | ⚠️ | ❌ | ❌ | ⚠️ | 4 (via Ultralytics) | [Vision on CPU](../README.md#vision-on-cpu): 360+ fps large, ~5000 fps small |
| [EfficientNet ONNX Runtime](https://github.com/zhangchaosd/ModelInferBench) | 4 | 5 | ✅ | ✅ | ⚠️ | ✅ | ✅ | 3 | [Image Classification](#image-classification): 12 ms/image, 14× over PyTorch |
| [MobileNetV3 TFLite](https://tildalice.io/mobilenetv3-vs-efficientnet-lite-arm-latency/) | 4 | 5 | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | 4 | [Image Classification](#image-classification): 23 ms INT8 on Pi 4 |
| [DFN5B-CLIP INT8 ONNX](https://huggingface.co/pritam-scientiaai/Quantized_DFN5B-CLIP-ViT-H-14-378_ONNX_INT8) | 4 | 4 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 2 | [Vision on CPU](../README.md#vision-on-cpu): 405 ms/image, 2.3× faster |

**Gap analysis:** No gaps for practical deployment. OpenVINO delivers enterprise-grade throughput on Intel x86; TFLite + XNNPACK covers ARM mobile/embedded; ONNX Runtime Web covers browser. RISC-V vision kernels are emerging but not yet a blocker — vision workloads on RISC-V typically use generic ONNX Runtime or ncnn without hand-tuned RVV kernels.

---

### 7. Vision — Segmentation

**Stage: 3 — Viable CPU alternatives**
**Gaps: Performance (latency still seconds-per-image for production-grade models)**

Segmentation is more compute-intensive than classification. MobileSAM makes CPU inference possible but at ~3 s/image — viable for batch, marginal for real-time.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [MobileSAM](https://github.com/ChaoningZhang/MobileSAM) | 4 | 3 | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | 4 (5.8K★) | [Image Segmentation](#image-segmentation): ~3 s/image on CPU |
| [SAM2 ONNX](https://github.com/pagarcia/sam2-onnx-cpp) | 4 | 3 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 1 (18★) | [Image Segmentation](#image-segmentation): ~2 s INT8 encoder |

**Gap analysis:** Performance gap — both options work but latency is 2–3 seconds per image, which is acceptable for batch document processing or offline pipelines but not for real-time video segmentation. The full SAM2 model is significantly heavier; no CPU-native port achieves sub-second latency. The category needs either a more aggressive quantization path or a smaller distilled model to reach real-time on CPU. Coverage gap: ARM kernels for SAM2 are unverified, and RISC-V/WASM paths don't exist.

> **Severity:** Medium — blocks real-time video segmentation on CPU but offline/batch use cases are viable.  
> **Recommended action:** Quantize MobileSAM to INT8 with XNNPACK and validate ARM NEON throughput. Explore distillation of SAM2's image encoder to ~100 MB (MobileSAM-scale) while retaining mask decoder quality. Port the resulting model to ONNX Runtime for cross-arch deployment.

---

### 8. OCR

**Stage: 5 — Mature CPU ecosystem**
**Gaps: None**

OCR has been CPU-native for decades. Deep learning models now match or exceed traditional engines while running on commodity hardware.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | 5 | 4 | ✅ | ✅ | ⚠️ | ❌ | ❌ | 5 (75.3K★) | [OCR](#ocr): CPU-native since v4, 100+ languages |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | 4 | 5 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 5 (85.3K★, 94K dl/day) | [OCR](#ocr): ~57 ms detection, ~47 ms recognition |
| [Surya OCR 2](https://github.com/datalab-to/surya) | 4 | 3 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 4 (21.1K★) | [OCR](#ocr): 83.3% olmOCR-bench, ~0.1 pages/s via llama.cpp |

**Gap analysis:** No gaps. Tesseract is the classical CPU-native baseline; PaddleOCR adds deep learning accuracy with CPU-optimized inference (MKL-DNN/OneDNN, OpenVINO). Surya OCR 2 is the strongest multilingual VLM-based OCR but is slower on CPU (~0.1 pages/s) — suitable for batch, not real-time. The ecosystem covers traditional LSTM (Tesseract), optimized DL (PaddleOCR), and VLM-based (Surya) tiers.

---

### 9. Image Generation (Diffusion)

**Stage: 2 — Emerging CPU alternatives**
**Gaps: Performance (minutes per image; not real-time)**

Stable Diffusion on CPU is computationally heavy — each denoising step is a large U-Net forward pass. OpenVINO makes it possible but throughput is far below interactive.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [OpenVINO Stable Diffusion](https://huggingface.co/docs/optimum-intel/openvino/tutorials/diffusers) | 4 | 2 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 3 | [Image Generation](#image-generation): INT8 weight compression |

**Gap analysis:** Performance gap — OpenVINO enables Stable Diffusion on Intel Xeon CPU with INT8 compression and static reshaping, but throughput is measured in minutes per image for SD 1.5 and tens of minutes for SDXL. This is acceptable for batch generation or testing but not for any interactive or real-time workflow. This is the one category where the [README's "When You Actually Do Want a GPU"](../README.md#when-you-actually-do-want-a-gpu) section explicitly calls out that "CPU throughput is too low for any real-time or near-real-time requirement." No ARM, RISC-V, or WASM paths exist. Void gap for non-x86 architectures.

> **Severity:** High — fundamentally blocks this entire workload class on CPU; the least CPU-amenable category.  
> **Recommended action:** Investigate latent consistency models (LCM) or adversarial diffusion distillation (ADD) for 1–4 step generation, which reduces the U-Net passes from 20–50 to 1–4. Port the distilled model to ONNX Runtime with INT8 quantization for x86 and ARM. If 2–4 tok/s throughput can be achieved at 4-step generation, interactive (5–15 s per image) becomes viable on high-end CPU.

---

### 10. Fine-Tuning (LoRA / QLoRA)

**Stage: 3 — Viable CPU alternatives**
**Gaps: Performance (10–50× slower than a single GPU)**

CPU fine-tuning is possible for small models with PEFT methods but throughput is significantly lower than GPU. The value proposition is offline/no-cloud, not speed.

| Tool | CPU-native | CPU perf | x86 | ARM | RISC-V | WASM | GPU | Adoption | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| [llama.cpp fine-tuning](https://github.com/ggml-org/llama.cpp/tree/master/examples/training) | 5 | 4 | ✅ | ✅ | ⚠️ | ❌ | ❌ | 5 (via llama.cpp) | [CPU Fine-Tuning](../README.md#cpu-fine-tuning): LoRA on CPU, no GPU at any stage |
| [PEFT](https://github.com/huggingface/peft) | 3 | 2 | ✅ | ✅ | ⚠️ | ❌ | ✅ | 5 (358K dl/day) | [CPU Fine-Tuning](../README.md#cpu-fine-tuning): 10–50× slower than GPU |
| [LlamaFactory](https://github.com/hiyouga/LLaMAFactory) | 3 | 2 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 5 (73.2K★) | [CPU Fine-Tuning](../README.md#cpu-fine-tuning): CPU mode with CUDA_VISIBLE_DEVICES="" |
| [Axolotl](https://github.com/OpenAccess-AI-Collective/axolotl) | 3 | 2 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 4 (12.2K★) | [CPU Fine-Tuning](../README.md#cpu-fine-tuning): ZeRO-3 CPU offload for optimizer states |
| [Unsloth](https://github.com/unslothai/unsloth) | 2 | 1 | ✅ | ❌ | ❌ | ❌ | ✅ | 5 (68K★) | [CPU Fine-Tuning](../README.md#cpu-fine-tuning): GPU-accelerated; produces GGUF adapters for CPU |
| [LoRAX](https://github.com/predibase/lorax) | 2 | 2 | ✅ | ⚠️ | ❌ | ❌ | ✅ | 3 (3.8K★) | [CPU Fine-Tuning](../README.md#cpu-fine-tuning): pre-merge adapters for CPU serving |

**Gap analysis:** Performance gap — llama.cpp is the only truly CPU-native fine-tuning path (designed for CPU, no GPU dependency at any stage). PEFT, LlamaFactory, and Axolotl work on CPU but are 10–50× slower than a single GPU; their value is offline/no-cloud, not throughput. Unsloth is GPU-only for training but is included because it produces CPU-deployable LoRA adapters (the training *event* is GPU; the inference *lifecycle* is CPU). The category needs faster CPU LoRA kernels to close the gap — current options rely on generic PyTorch CPU backward passes without hand-tuned gradients.

> **Severity:** Medium — does not block CPU fine-tuning (llama.cpp works for small models at 6–12h for 1K examples) but limits iteration speed for larger datasets.  
> **Recommended action:** Implement hand-tuned LoRA backward pass kernels in llama.cpp using AVX-512/AMX and NEON/SVE, targeting 2–5× speedup over the current generic implementation. Add QLoRA (4-bit base model frozen, LoRA in FP16) to the llama.cpp training path to reduce memory pressure and enable larger base models on the same hardware.

---

## Summary Dashboard

| # | Category | CPU Stage | Gaps | Mature CPU tools | Best CPU option | 🧠 NPU Stage | Best NPU option | GPU alt. |
|---|---|---|---|---|---|---|---|---|---|
| 1 | LLM inference (decode) | **5** | — | 7 | llama.cpp | **3** | QNN (SD8 Elite) | TensorRT |
| 2 | LLM prompt processing (prefill) | **4** | Architecture | 3 | ONNX Runtime GenAI | **2** | — (NPU prefill weak) | TensorRT |
| 3 | ASR / STT | **5** | — | 4 | whisper.cpp | **4** | QNN / ANE | Riva |
| 4 | TTS | **4** | Maturity | 4 | Piper / PocketTTS | **2** | — (NPU TTS rare) | Tortoise |
| 5 | Embeddings | **5** | — | 3 | sentence-transformers ONNX | **4** | QNN / ANE / Intel NPU | — (CPU suff.) |
| 6 | Vision — detection & classification | **5** | — | 4 | YOLOv8 + OpenVINO | **5** | QNN / ANE / Intel NPU | TensorRT |
| 7 | Vision — segmentation | **3** | Performance, Coverage | 0 | MobileSAM | **2** | — (NPU seg. rare) | SAM2 + CUDA |
| 8 | OCR | **5** | — | 3 | PaddleOCR | **3** | QNN (digit only) | — (CPU suff.) |
| 9 | Image generation (diffusion) | **2** | Performance, Arch. | 0 | OpenVINO SD | **1** | — (NPU too small) | SDXL + CUDA |
| 10 | Fine-tuning (LoRA / QLoRA) | **3** | Performance | 1 | llama.cpp fine-tune | **0** | — (NPU train void) | Unsloth |

**At a glance:** 5 of 10 categories are at CPU Stage 5 (mature). 2 categories carry CPU performance gaps (segmentation, diffusion). Fine-tuning on CPU is viable but slow. NPU maturity lags CPU across most categories — only vision detection/classification reaches NPU Stage 5 (QNN and ANE production-ready for YOLO/classifiers). LLM decode on NPU is Stage 3 at best: Qualcomm QNN achieves 12–25 tok/s on Snapdragon 8 Elite but the toolchain is Snapdragon-only and trails CPU for generative LLMs. ASR/STT and embeddings reach NPU Stage 4, while diffusion, segmentation, and fine-tuning remain NPU voids. NPU coverage is vendor-specific — consult the `Best NPU option` column with the understanding that it requires that specific vendor's SDK.

---

## Limitations

- **Curated, not census.** The scored set is the tools currently in this awesome list, not an exhaustive survey. Unlisted tools are not graded.
- **Within-category scores.** CPU performance grades are comparable *within* a category, not across categories. A 4 in LLM decode ≠ a 4 in TTS.
- **Adoption is a proxy.** Download counts and GitHub stars measure *interest*, not *CPU-specific deployment*. A tool with high adoption may be deployed primarily on GPU. Model-download figures are sourced from the reproducible [HF Landscape dataset](ecosystem-evidence.md), but downloads still measure reach — not the production CPU-vs-GPU serving mix.
- **Architecture coverage is documentation-based.** Kernel support is determined from tool docs and build flags, not always verified by running tests on each ISA.
- **Scores are point-in-time.** The ecosystem moves fast — scores should be re-validated quarterly. See the [Roadmap](../ROADMAP.md) for the cadence.
- **Fine-tuning is borderline.** Unsloth and LoRAX are included in the fine-tuning category despite being GPU-first because their *output* (LoRA adapters) deploys on CPU. Their CPU-nativeness score reflects the training phase, not the inference phase.
- **CPU-nativeness scoring involves subjective judgment.** The distinction between a 4 ("first-class target") and a 3 ("secondary target") can be ambiguous for tools with mixed GPU/CPU heritage (e.g., ollama, ExecuTorch). Scores were assigned by the maintainer and may differ from a contributor's assessment — open an issue if you disagree with a specific score.
- **WASM != native CPU performance.** Tools scored in the WASM column (Transformers.js, WebLLM, LiteRT.js) run in a browser sandbox with Wasm SIMD, which typically achieves 40–70% of native CPU throughput. WASM scores are not directly comparable to native x86/ARM scores even within the same category — distinguish "runs in browser on CPU" from "runs on bare-metal CPU" when evaluating deployment options.
- **🧠 NPU scores are vendor-specific, not cross-platform.** An NPU tool scoring Stage 5 on one vendor's hardware (e.g., QNN on Snapdragon) may be Stage 0 on a different vendor's platform (e.g., Exynos). NPU scores in this map reflect the best-case vendor scenario and should be interpreted as "this is possible on the right hardware" rather than a universal rating. CPU remains the only deployment target that works identically across all vendors.

---

## See also

- [Runtimes and Inference Engines](../README.md#runtimes-and-inference-engines) — The full runtime catalogue
- [Runtime comparison table](../README.md#runtimes-and-inference-engines) — Format × CPU arch × OS matrix
- [Benchmarks and Evidence](../README.md#benchmarks-and-evidence) — Primary benchmark sources
- [Hardware Reference](hardware-reference.md) — Throughput figures by device tier
- [The CPU-First Case, in Hub Data](ecosystem-evidence.md) — Reproducible adoption/size/task figures from the HF Landscape crawl
- [Benchmark Suite Proposal](benchmark-suite-proposal.md) — Standardized benchmark methodology
- [Cost Calculator](cost-calculator.md) — TCO comparison tool
- [CPU vs NVIDIA Decision Framework](cpu-vs-nvidia-decision-framework.md) — Workload-level decision matrix
- [Multimodal CPU Workloads](multimodal-cpu.md) — Full tool catalogue with latency figures
- [Mobile Phone CPU Inference](mobile-cpu-inference.md) — Mobile chipset benchmarks
- [AI Potluck Gap Map](https://www.aipotluck.org/map) — The openness-focused gap map that inspired this analysis