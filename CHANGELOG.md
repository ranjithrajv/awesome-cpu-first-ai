# Changelog

All notable additions and changes to awesome-cpu-first-ai.

---

## 2026-07-13

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
