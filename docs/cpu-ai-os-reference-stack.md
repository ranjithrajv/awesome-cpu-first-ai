# Reference Stack — An 8 GB CPU-Only AI OS

A concrete, memory-budgeted model suite for building an AI operating system that runs entirely on CPU, in **8 GB of RAM**, across both x86 and ARM. Every pick is CPU-native, quantized, and drawn from the project's [model catalog](cpu-native-models.md) and [multimodal workloads](multimodal-cpu.md); popularity signals ("#1 on the Hub") come from the [HF Landscape data](ecosystem-evidence.md).

The governing constraint is not any single model — it is that they must **coexist** in 8 GB. This doc is organized around that.

---

## Contents

- [Design Principles](#design-principles)
- [Portable Inference Layer](#portable-inference-layer)
- [The Suite](#the-suite)
  - [STT — speech-to-text](#stt--speech-to-text)
  - [TTS — text-to-speech](#tts--text-to-speech)
  - [STS — speech-to-speech](#sts--speech-to-speech)
  - [OCR](#ocr)
  - [LLM and other tasks](#llm-and-other-tasks)
- [Memory Budget](#memory-budget)
- [Speech-to-Speech Pipeline](#speech-to-speech-pipeline)
- [Android Devices](#android-devices)
- [Model Manifest](#model-manifest)
- [See also](#see-also)

---

## Design Principles

1. **Don't keep everything resident.** Reserve ~2.5 GB for the OS. That leaves ~5 GB for AI. Keep a tiny always-on core (~0.3 GB), let **one** heavy model (the LLM) anchor the budget, and mmap everything else.
2. **mmap + LRU load/evict.** GGUF and ONNX both memory-map from disk, so on-demand models share the OS page cache. Peak RAM = `core + LLM + largest single on-demand model`, never the sum.
3. **Two runtimes, not ten.** The whole suite runs on the **ggml family** (llama.cpp / whisper.cpp) plus **ONNX Runtime CPU EP**. Minimizing runtime sprawl is a first-class OS concern.
4. **One heavy task at a time.** Serialize the expensive models (LLM, Whisper, VLM-OCR) behind a model manager; run the tiny ones (VAD, embeddings, intent) concurrently.
5. **Avoid the CPU-weak categories.** Per the [gap map](cpu-ai-gap-map.md), segmentation and diffusion are CPU Stage 2–3 — keep them off the resident path (on-demand, batch-only) so they never blow the budget.

---

## Portable Inference Layer

The suite targets **both x86 and ARM from one build**. The trick is choosing runtimes that do runtime CPU-feature detection, and treating ISA-specific accelerators as optional plugins — never core dependencies.

| Layer | Choice | Portability note |
|---|---|---|
| Core runtime A | [llama.cpp](https://github.com/ggerganov/llama.cpp) / [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (GGUF) | Auto-detects AVX2 / AVX-512 / NEON at load; mmap built in |
| Core runtime B | [ONNX Runtime CPU EP](https://onnxruntime.ai/docs/execution-providers/) | Same dynamic dispatch; INT8 accelerated by VNNI (x86) *and* i8mm (ARMv8.6+) |
| Optional accel plugin | OpenVINO (x86), Arm KleidiAI/SME2 (ARM) | Model manager loads *if present* for a speed bump — the suite runs without them |

**Portable quant defaults** (good on both ISAs, no lock-in):

- LLM & Whisper → **GGUF Q4_K_M** (Q5_K_M for Whisper if accuracy-sensitive).
- Embeddings, TTS, OCR, vision → **ONNX INT8 dynamic** — accelerated by both VNNI and i8mm.
- **Avoid TFLite-only** models; take e.g. MobileNetV3 via ONNX so one loader covers every task on both architectures.

---

## The Suite

Footprints are approximate on-disk / resident sizes at the recommended quantization.

### STT — speech-to-text

| Model | Footprint | Runtime | Why |
|---|---|---|---|
| **whisper-base / small** (Q5) | 80 / 180 MB | [whisper.cpp](https://github.com/ggerganov/whisper.cpp) | Default. 3–5× real-time on Pi 5 (tiny); NEON + AVX paths |
| **Silero VAD** | <2 MB | ONNX | Resident front-end — gate audio before waking Whisper |
| whisper-large-v3-turbo (809M) | ~0.8 GB | whisper.cpp | On-demand, when accuracy matters |
| [transcribe.cpp](https://github.com/handy-computer/transcribe.cpp) (Moonshine/Parakeet) | varies | ggml | Non-Whisper ASR families, WER-validated GGUFs |

### TTS — text-to-speech

| Model | Footprint | Runtime | Why |
|---|---|---|---|
| **[Piper](https://github.com/OHF-Voice/piper1-gpl)** (VITS) | 20–60 MB/voice | ONNX | OS default. RTF 0.15 on Pi 5; 100+ voices |
| **[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)** | ~160 MB | ONNX | #1 TTS on the Hub (11.3M dl/30d) — higher quality |
| **[PocketTTS](https://github.com/kyutai-labs/pocket-tts)** (100M) | ~100 MB | ONNX/C++ | CPU-first by design; zero-shot voice cloning |

### STS — speech-to-speech

End-to-end S2S is GPU-scale; on 8 GB the CPU-native approach is a **streaming cascade** that reuses already-warm models — see [Speech-to-Speech Pipeline](#speech-to-speech-pipeline) below.

### OCR

| Model | Footprint | Runtime | Why |
|---|---|---|---|
| **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** PP-OCRv4 mobile | 10–20 MB | ONNX/OpenVINO | OS default. ~57 ms detect + 47 ms recognize; 80+ languages |
| **[Tesseract](https://github.com/tesseract-ocr/tesseract)** | ~langpacks | native | Simplest fallback, 100+ langs, CPU-native |
| [Surya OCR 2](https://github.com/datalab-to/surya) (650M) | ~500 MB | llama.cpp (GGUF) | On-demand: full-page layout, tables, reading order |

### LLM and other tasks

| Task | Model | Footprint | Notes |
|---|---|---|---|
| **LLM (the brain)** | Qwen2.5-3B-Instruct Q4 (or 1.5B Q4) | ~2.0 / ~1.0 GB | Anchor model. Also [BitNet b1.58-2B4T](https://huggingface.co/microsoft/bitnet-b1.58-2B-4T) (ternary, ~0.4 GB) |
| **Text embeddings** (search, RAG) | [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | ~90 MB | #1 model on the Hub (253M dl/30d); single-digit ms. Resident. Multilingual → e5-small |
| **Reranker** | ms-marco-MiniLM-L6 | ~90 MB | Tiny cross-encoder; big retrieval-precision win |
| **Intent / zero-shot routing** | [nli-distilroberta-base](https://huggingface.co/cross-encoder/nli-distilroberta-base) (82M) | ~120 MB | Route commands without a full LLM call |
| **Image classification** | MobileNetV3 (INT8, ONNX) | 3–10 MB | ~23 ms/image; screenshot/photo tagging |
| **Background removal** (opt) | [rembg](https://github.com/danielgatis/rembg) (U²-Net) | ~170 MB | On-demand, ~1 s/image |
| **Face analysis** (opt) | [InsightFace](https://github.com/deepinsight/insightface) buffalo_l | ~300 MB | On-demand |

---

## Memory Budget

```
OS + apps                        ~2.5 GB
── AI core (always resident) ──   ~0.3 GB   Silero VAD + all-MiniLM + Piper voice + intent classifier
── LLM (anchor)              ──   ~2.0 GB   Qwen2.5-3B Q4   (drop to 1.5B Q4 = 1.0 GB for more slack)
── on-demand (mmap, 1 at a time)  ~0.2–0.8 GB peak   Whisper / Kokoro / PaddleOCR / Surya / rembg
                                 ─────────
                          ≈ 5.0–5.6 GB, fits with page-cache headroom
```

Everything except the resident core loads via mmap and is evicted after use, so the peak is `core + LLM + largest single on-demand model`, not the sum.

---

## Speech-to-Speech Pipeline

```
mic ─▶ Silero VAD ─▶ whisper.cpp (STT) ─▶ [Qwen LLM: rewrite/translate] ─▶ TTS ─▶ speaker
       <2MB, always   base/small Q5        optional, reuse the anchor       Piper│Kokoro│PocketTTS
       resident       streaming            LLM — no extra model             pick by need
```

**Model choice per mode:**

| Mode | Path | Models | Peak add'l RAM |
|---|---|---|---|
| Fast round-trip (assistant reply aloud) | STT → LLM → TTS | Whisper-base + Qwen-1.5B + Piper | ~1.3 GB |
| Speech **translation** | Whisper `translate` (or STT→Qwen MT) → TTS in target voice | Whisper + Qwen + Kokoro | ~1.4 GB |
| **Keep the speaker's voice** (cloning) | STT → [edit] → cloned TTS | Whisper + PocketTTS (zero-shot from 3–5 s ref) | ~0.3 GB |
| Highest-quality cloning | same, heavier | XTTS-v2 | ~1.8 GB (on-demand only) |

**Why cascade over true voice-conversion models:** VC models that preserve prosody while changing content/language are GPU-leaning and won't fit alongside the rest. Cascade + a cloning TTS (PocketTTS) gets ~90% of the experience on CPU: extract a speaker embedding from the input, synthesize the reply in that voice.

**Latency budget (conversational target < ~1 s/turn):**

- Silero VAD ~1 ms · Whisper-base streaming ~0.3–0.5× RTF · PocketTTS **~30 ms to first audio, ~9× RTF** (Kokoro streams too).
- Keep STT + VAD **warm** for the whole conversation; only the TTS voice model loads/evicts.
- Overlap STT chunks with TTS playback so perceived latency ≈ first-chunk time, not full-utterance time.
- The LLM step is the variable cost — use 1.5B Q4, or skip it entirely for pure translate/echo modes.

**Peak RAM during a live session** = core (0.3) + Whisper (0.18) + one TTS (0.1–1.8) + optional LLM (1.0) → **~1.6 GB with Piper/PocketTTS**, well inside 5 GB. XTTS pushes it to ~3.3 GB, still fine if the LLM isn't resident simultaneously.

---

## Android Devices

Android is ARM, so the [portable inference layer](#portable-inference-layer) and the model picks above carry over directly — but three things change the design: RAM is **shared with the Android runtime**, sustained inference is **thermally throttled**, and most devices ship an **NPU you can selectively offload to** (vendor-locked). This section adapts the stack for a phone/tablet OS.

### What changes vs a desktop CPU OS

| Factor | Implication |
|---|---|
| **Tighter RAM** | On a 6–8 GB phone, Android + system UI + foreground app already use ~3–4 GB. AI budget is ~2–3 GB — smaller than the 8 GB desktop case. Shrink the anchor LLM. |
| **Battery & thermal** | Sustained CPU decode throttles on fanless devices within minutes. Prefer NPU/GPU for *always-on* light tasks; reserve CPU for *burst* LLM decode. Quantize aggressively (Q4/INT4). |
| **NPU available** | Vision, embeddings, ASR-classification map well to the NPU (Qualcomm Hexagon, Samsung ENN, MediaTek APU). LLM *decode* is memory-bandwidth-bound and usually **stays fastest on CPU** — see [Mobile Phone CPU Inference](mobile-cpu-inference.md). |
| **System AI services** | On recent Pixel/Samsung, a system-level LLM ([Gemini Nano via AICore](https://developer.android.com/ai/gemini-nano)) is shared across apps at **zero per-app RAM cost** — use it as the anchor where present, fall back to your own GGUF model elsewhere. |

### Android runtime layer

| Role | Choice | Notes |
|---|---|---|
| CPU LLM / STT (portable) | [llama.cpp Android](https://github.com/ggml-org/llama.cpp/blob/master/docs/android.md), whisper.cpp | GGUF, sideload any model; the most flexible path |
| PyTorch-native production | [ExecuTorch](https://github.com/pytorch/executorch) | Ships on Samsung/Meta devices; XNNPACK CPU + delegate to NPU |
| ONNX models (embeddings, TTS, OCR, vision) | [ONNX Runtime Mobile](https://onnxruntime.ai/docs/) + NNAPI/QNN delegate | Same models as desktop; delegate offloads to NPU when available |
| Speech via one library | [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | STT + TTS + VAD in a single on-device runtime with Android bindings |
| GPU/NPU LLM (optional) | [MLC-LLM Android](https://github.com/mlc-ai/mlc-llm) | OpenCL/Vulkan path; useful on some SoCs, benchmark vs CPU first |
| System OCR / face / barcode | [Google ML Kit](https://developers.google.com/ml-kit) | Free, NPU-accelerated on-device; skip shipping your own for these |
| Free ISA speedup | [Arm KleidiAI / SME2](https://www.arm.com/technologies/sme2/accelerate-on-device-ai) | Up to 6× on ARMv9.3+ CPUs (integrated in XNNPACK, ExecuTorch, ONNX RT, llama.cpp) with no code change |

### Android suite adjustments

| Task | Desktop pick | Android pick | Why |
|---|---|---|---|
| **LLM** | Qwen2.5-3B Q4 | **Gemini Nano (AICore)** where present, else **Gemma-2-2B / Qwen2.5-1.5B Q4** | System model = 0 app RAM; else a ~1 GB anchor fits the tighter budget |
| **STT** | whisper.cpp base | whisper.cpp / **sherpa-onnx** (Whisper or Moonshine) | Moonshine is lighter for streaming on-device |
| **TTS** | Piper / Kokoro | **Piper / Kokoro via sherpa-onnx** | One speech runtime for STT+TTS+VAD |
| **OCR** | PaddleOCR | **ML Kit Text Recognition** (or PaddleOCR mobile) | System OCR is NPU-accelerated and free |
| **Embeddings** | all-MiniLM (ONNX) | all-MiniLM via **ONNX Runtime Mobile + NNAPI** | Offload to NPU to save CPU/battery |
| **Image classification / face** | MobileNetV3 / InsightFace | **ML Kit** / LiteRT + NNAPI | Hardware-accelerated, always-on friendly |

### Phone memory & power budget (6–8 GB device)

```
Android OS + system UI + foreground app   ~3.5–4.5 GB
── AI core (resident)                ──    ~0.2 GB   Silero VAD + all-MiniLM (NNAPI) + Piper voice
── anchor LLM                        ──    0 GB (Gemini Nano/AICore)  OR  ~1.0 GB (Gemma-2-2B Q4)
── on-demand (mmap, 1 at a time)     ──    ~0.1–0.3 GB   Whisper / Kokoro / OCR
                                          ─────────
                                   ≈ fits in 2–3 GB AI budget on a 6–8 GB phone
```

**Battery/thermal rules of thumb:** route always-on tasks (VAD, embeddings, ML Kit OCR/vision) to the **NPU via NNAPI/QNN**; keep **LLM decode on CPU** (2–4 big cores, KleidiAI/SME2) but cap sustained generation and measure throughput over 5+ minutes, not one burst — see the thermal notes in [Mobile Phone CPU Inference](mobile-cpu-inference.md).

---

## Model Manifest

A starting point for a model-manager config — task → model → quant → footprint → runtime → residency. Sizes are approximate; verify against your target hardware with the [benchmark methodology](benchmark-methodology.md).

```toml
[core]                     # always resident (~0.3 GB total)
vad        = { model = "silero-vad",              fmt = "onnx",  mb = 2,   runtime = "onnxruntime" }
embed      = { model = "all-MiniLM-L6-v2",        fmt = "onnx-int8", mb = 90, runtime = "onnxruntime" }
intent     = { model = "nli-distilroberta-base",  fmt = "onnx-int8", mb = 120, runtime = "onnxruntime" }
tts_fast   = { model = "piper-<voice>",           fmt = "onnx",  mb = 40,  runtime = "onnxruntime" }

[anchor]                   # one resident LLM
llm        = { model = "Qwen2.5-3B-Instruct",     fmt = "gguf-q4_k_m", mb = 2000, runtime = "llama.cpp" }
# lean alt: Qwen2.5-1.5B-Instruct (1000 MB) · ternary alt: BitNet-b1.58-2B4T (400 MB)

[on_demand]                # mmap, LRU, one heavy at a time
stt        = { model = "whisper-base",            fmt = "gguf-q5",  mb = 80,  runtime = "whisper.cpp" }
stt_hq     = { model = "whisper-large-v3-turbo",  fmt = "gguf-q5",  mb = 800, runtime = "whisper.cpp" }
tts_hq     = { model = "Kokoro-82M",              fmt = "onnx",     mb = 160, runtime = "onnxruntime" }
tts_clone  = { model = "pocket-tts",              fmt = "onnx",     mb = 100, runtime = "onnxruntime" }
ocr        = { model = "paddleocr-ppv4-mobile",   fmt = "onnx",     mb = 20,  runtime = "onnxruntime" }
ocr_doc    = { model = "surya-ocr-2",             fmt = "gguf",     mb = 500, runtime = "llama.cpp" }
imgcls     = { model = "mobilenetv3",             fmt = "onnx-int8", mb = 8,  runtime = "onnxruntime" }
rembg      = { model = "u2net",                   fmt = "onnx",     mb = 170, runtime = "onnxruntime" }
```

---

## See also

- [CPU-Native Model Catalog](cpu-native-models.md) — full model catalog by size and quant
- [Multimodal CPU Workloads](multimodal-cpu.md) — STT/TTS/OCR/vision engines with CPU benchmarks
- [CPU AI Gap Map](cpu-ai-gap-map.md) — which of these tasks are CPU-mature vs weak
- [The CPU-First Case, in Hub Data](ecosystem-evidence.md) — adoption evidence behind the picks
- [Hardware Reference](hardware-reference.md) — expected throughput by device tier
- [Model Conversion Guide](model-conversion-guide.md) — exporting these models to GGUF / ONNX INT8
