# Multimodal CPU Workloads

Speech, audio, text-to-speech, and optical character recognition are among the most common production AI workloads that rarely need a GPU. Modern ASR engines run efficiently on CPU with INT8 quantization, TTS engines synthesize in real time using lightweight ONNX models, and OCR toolchains have been CPU-native for decades — with deep learning models now matching traditional engine accuracy while running on commodity x86 and ARM hardware.

---

## Contents

- [Speech / Audio](#speech--audio)
  - [ASR / STT](#asr--stt)
  - [Audio Embeddings & Classification](#audio-embeddings--classification)
  - [Voice Activity Detection & Speaker Diarization](#voice-activity-detection--speaker-diarization)
- [Text](#text)
  - [TTS](#tts)
  - [Text Embeddings](#text-embeddings)
- [Documents](#documents)
  - [Document Classification](#document-classification)
  - [OCR](#ocr)
- [Images](#images)
  - [Image Classification](#image-classification)
  - [Image Segmentation](#image-segmentation)
  - [Image Generation](#image-generation)
  - [Background Removal](#background-removal)
  - [Face Analysis](#face-analysis)
- [References](#references)

---

## Speech / Audio

### ASR / STT

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Reimplementation of OpenAI Whisper using CTranslate2; up to 4× faster than the original with INT8 quantization on CPU and lower memory usage. Benchmarks on Intel Xeon Gold report 2m04s for 13 minutes of audio (small model, INT8, 8 threads) vs 10m31s for openai/whisper. ([Official benchmarks](https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#small-model-on-cpu))
- [Vosk](https://alphacephei.com/vosk/) — Offline speech recognition toolkit supporting 20+ languages with models as small as 50 MB; runs on Raspberry Pi, Android, and x86 servers using a single CPU core per recognizer with streaming API support. ([GitHub](https://github.com/alphacep/vosk-api))
- [transcribe.cpp](https://github.com/handy-computer/transcribe.cpp) — General-purpose ggml/GGUF speech-to-text inference library covering 16+ ASR model families beyond Whisper — Parakeet, Canary, Canary-Qwen, Moonshine, Qwen3-ASR, Voxtral, Granite Speech, GigaAM, SenseVoice, FunASR Nano, Nemotron, Cohere Transcribe, and MedASR — with 60+ pre-built, WER-validated GGUF variants, streaming and batch modes, a `transcribe-quantize` tool (F16/Q8_0/Q6_K/Q5_K_M/Q4_K_M), and Python / TypeScript / Rust / Swift bindings. CPU is the default path via Justine Tunney's tinyBLAS (`llamafile_sgemm`) kernels, with optional OpenBLAS giving ~10–15× host-decoder speedup; Metal/Vulkan/CUDA are opt-in accelerators. Mozilla-AI sponsored. ([Hugging Face GGUFs](https://huggingface.co/handy-computer))
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) — Whisper port to ggml (also listed under Runtimes); on CPU with OpenVINO backend it transcribes 13 minutes of audio in 1m45s (small model, FP32) vs 6m58s for openai/whisper, with ARM NEON and AVX SIMD paths and a 3–5× real-time factor on Raspberry Pi 5 for the tiny model.

### Audio Embeddings & Classification

- [CLAP](https://github.com/LAION-AI/CLAP) — Contrastive Language-Audio Pretraining; embeds audio and text into a shared space for zero-shot sound classification, audio search, and tagging. Models under 600M params run on CPU via ONNX Runtime in a few milliseconds per sample. ([CLAP-ONNX CPU benchmarks](https://github.com/Lednik7/CLIP-ONNX))
- [YAMNet](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet) — MobileNet-based model for 521 audio event classes (sirens, music, applause, etc.); ~10 MB, entirely CPU-native with no GPU dependency, single forward pass ~1 ms on modern x86.

### Voice Activity Detection & Speaker Diarization

- [Silero VAD](https://github.com/snakers4/silero-vad) — De facto standard voice activity detection model; single ONNX file < 2 MB, runs 10,000 audio samples in < 1 ms on a single CPU core. Used as the front-end for most production ASR pipelines to segment audio before transcription.
- [pyannote-audio](https://github.com/pyannote/pyannote-audio) — Speaker diarization pipeline (who spoke when) using CPU-friendly segmentation and clustering models; commonly chained with whisper.cpp or faster-whisper to produce speaker-attributed transcripts.

---

## Text

### TTS

- [Piper](https://github.com/OHF-Voice/piper1-gpl) — Fast local neural TTS using VITS exported to ONNX; achieves real-time synthesis (RTF 0.15) on a Raspberry Pi 5 with no GPU and roughly 10× real time on desktop CPU. Ships 30+ languages, 100+ voices in quality tiers from x_low (16 kHz, smallest) to high (22 kHz), with a single ONNX file per voice. Default TTS engine in Home Assistant. ([samples](https://rhasspy.github.io/piper-samples/), [Piper TTS Setup Guide 2026](https://localaimaster.com/blog/piper-tts-setup-guide))
- [Coqui TTS](https://github.com/idiap/coqui-tts) — Open-source TTS with 17+ languages and multi-speaker models including XTTSv2 for voice cloning; provides a CPU-only Docker image (`tts-cpu`) and Python/CLI APIs. XTTSv2 supports streaming inference with <200 ms latency and cross-language voice cloning. ([CPU Docker docs](https://docs.coqui.ai/en/latest/docker_images.html), [XTTS docs](https://docs.coqui.ai/en/stable/models/xtts.html))
- [PocketTTS](https://github.com/kyutai-labs/pocket-tts) — Lightweight TTS from Kyutai Labs (100M params, MIT); designed from the ground up for CPU — the authors note they "did not observe a speedup" on GPU vs CPU at batch=1. Achieves ~6× real-time on a MacBook Air M4 (2 CPU cores) with ~200 ms to first audio chunk; supports zero-shot voice cloning from a short audio sample and 6 languages (en, fr, de, pt, it, es). [PocketTTS.cpp](https://github.com/VolgaGerm/PocketTTS.cpp) is a single-file C++/ONNX-Runtime port achieving 9.2× real-time (INT8) on a Ryzen 7 3800X with ~30 ms TTFA, an OpenAI-compatible HTTP server, and a WASM build for browser deployment. ([tech report](https://kyutai.org/blog/2026-01-13-pocket-tts), [paper](https://arxiv.org/abs/2509.06926))

### Text Embeddings

- [sentence-transformers with ONNX backend](https://sbert.net/docs/sentence_transformer/usage/efficiency.html) — Official Sentence Transformers library supporting ONNX Runtime CPU backend for embedding models; up to 1.4× speedup over PyTorch CPU with ONNX optimization, and up to 3× with INT8 quantization (AVX-512 VNNI). Supports all popular models including all-MiniLM-L6-v2, BGE, and GTE series. ([ONNX benchmark gist](https://gist.github.com/kylediaz/7e8df0a19e2137ef10fc62b5421e4d9a))
- [BGE-M3 ONNX](https://huggingface.co/Sophia-AI/bge-m3-onnx) — BAAI/bge-m3 exported to ONNX for CPU inference; produces dense (1024-d), sparse, and ColBERT multi-vector representations in a single forward pass. 1.27× faster than PyTorch CPU and eliminates the PyTorch dependency for lighter deployments. ([ONNX Community variant](https://huggingface.co/onnx-community/bge-m3-ONNX))
- [all-MiniLM-L6-v2 ONNX](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) — The most widely deployed embedding model (22.7M params, 384-d output); trivial to convert to ONNX with `optimum-cli export onnx` and runs in single-digit milliseconds on any modern CPU. Suited for RAG, clustering, and semantic search pipelines at any scale.

---

## Documents

### Document Classification

- [BART-large-MNLI ONNX](https://huggingface.co/Maxi-Lein/bart-large-mnli-onnx) — Zero-shot document classifier using Facebook's BART-large-MNLI exported to ONNX; classifies text against arbitrary label sets without task-specific fine-tuning. Runs on CPU via ONNX Runtime or Transformers.js with quantized weights for reduced memory footprint. ([Haystack integration](https://docs.haystack.deepset.ai/docs/transformerszeroshotdocumentclassifier))
- [cross-encoder/nli-distilroberta-base](https://huggingface.co/cross-encoder/nli-distilroberta-base) — Lightweight zero-shot classification model (82M params) using distilled RoBERTa for natural language inference; ~5× faster than BART-large with minimal accuracy drop. Runs entirely on CPU with ONNX Runtime, suitable for batch document classification pipelines.

### OCR

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — The de facto open-source OCR engine with 100+ language packs; entirely CPU-native with no GPU dependency, supporting LSTM-based recognition since v4. Widely used in document processing pipelines and production deployments.
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) — Baidu's OCR toolkit with CPU-optimized inference via MKL-DNN/OneDNN and OpenVINO; PP-OCRv4 mobile models run detection in ~57 ms and recognition in ~47 ms on Intel Xeon Gold (FP32, 8 threads). Supports 80+ languages with text detection, recognition, and table structure recognition. ([Training benchmarks](https://github.com/PaddlePaddle/PaddleOCR/tree/main/benchmark), [CPU optimization guide](https://deepwiki.com/PaddlePaddle/PaddleOCR/8.3-cpu-optimization))
- [Surya OCR 2](https://github.com/datalab-to/surya) — 650M-parameter multilingual OCR model scoring 83.3% on olmOCR-bench (top under 3B params); runs on CPU via llama.cpp (GGUF-quantized) with a throughput of ~0.1 pages/s on Apple Silicon (~30 W) and supports full-page OCR, layout analysis, reading order, and table recognition in a single VLM. ([Announcement](https://www.datalab.to/blog/surya-2))

---

## Images

### Image Classification

- [MobileNetV3 / EfficientNet-Lite (TFLite ONNX)](https://tildalice.io/mobilenetv3-vs-efficientnet-lite-arm-latency/) — ARM CPU latency benchmarks on Raspberry Pi 4: MobileNetV3-Small achieves 23 ms (INT8, single-threaded) and EfficientNet-Lite0 reaches 49 ms with 6% higher accuracy; both models exportable to ONNX and TFLite with optional INT8 quantization. Multi-threaded (4 threads) closes the gap to ~24 ms for both. ([MobileNet vs EfficientNet comparison](https://tildalice.io/mobilenet-vs-efficientnet-lite-pi4-latency-benchmark/))
- [EfficientNet ONNX Runtime CPU](https://github.com/zhangchaosd/ModelInferBench) — Benchmark of EfficientNet-B4 via ONNX Runtime on CPU: 12 ms per image (batch=1) vs 172 ms for PyTorch CPU, with OpenVINO at 11 ms. Demonstrates 14× speedup over naive PyTorch inference through ONNX export alone. ([PyTorch to ONNX deployment guide](https://genmind.ch/posts/From-PyTorch-to-Production-Deploy-ML-Models-Locally-with-ONNX/))

### Image Segmentation

- [MobileSAM](https://github.com/ChaoningZhang/MobileSAM) — Segment Anything with a 5M-param Tiny-ViT encoder (vs 632M in original SAM) enabling CPU inference; exports to ONNX for ~3 s per image on desktop CPU. ([Hugging Face demo](https://huggingface.co/spaces/dhkim2810/MobileSAM), [ONNX notebook](https://github.com/ChaoningZhang/MobileSAM/blob/master/notebooks/onnx_model_example.ipynb))
- [SAM2 ONNX](https://github.com/pagarcia/sam2-onnx-cpp) — Meta SAM2 exported to ONNX Runtime with C++ and Python bindings; supports point/box/video prompts on CPU with INT8 encoder quantization reducing encoder latency to ~2 s on modern x86. ([SAM2 ONNX benchmark](https://people.ac.upc.edu/rtous/publications/conf_2025iwann.pdf))

### Image Generation

- [OpenVINO Stable Diffusion (Optimum Intel)](https://huggingface.co/docs/optimum-intel/openvino/tutorials/diffusers) — Image generation via Stable Diffusion exported to OpenVINO IR and run through Optimum Intel; supports text-to-image, image-to-image, and inpainting on CPU with INT8 weight compression and static reshaping for faster inference. ([OpenVINO SD notebook](https://docs.openvino.ai/2024/notebooks/stable-diffusion-text-to-image-with-output.html), [SDXL on OpenVINO](https://docs.openvino.ai/2024/notebooks/stable-diffusion-xl-with-output.html))

### Background Removal

- [rembg](https://github.com/danielgatis/rembg) — Popular open-source background removal tool using U2-Net and IS-Net models exported to ONNX Runtime; runs on CPU with single-command `pip install rembg[cpu]`. U2-Net achieves ~1 s per image on desktop CPU and ~2.7 s on browser WASM. ([CPU benchmarks](https://bunn-io.github.io/rembg-web/api/index.html))

### Face Analysis

- [InsightFace](https://github.com/deepinsight/insightface) — Face detection, recognition, and analysis toolkit using ONNX Runtime CPU backend; buffalo_l model family delivers 99.83% LFW accuracy with detection + recognition + landmark + age/gender in a single pipeline. OpenVINO export path further accelerates CPU inference. ([OpenVINO export guide](https://www.insightface.ai/guides/convert-onnx-to-tensorrt-openvino))

---

See also: [Vision on CPU (README)](../README.md#vision-on-cpu) · [Model Conversion Guide](model-conversion-guide.md) · [CPU Inference Deployment Guide](cpu-inference-deployment.md) · [Benchmark Methodology](benchmark-methodology.md)

---

## References

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Official benchmarks](https://github.com/SYSTRAN/faster-whisper?tab=readme-ov-file#small-model-on-cpu)
- [Vosk](https://alphacephei.com/vosk/)
- [GitHub](https://github.com/alphacep/vosk-api)
- [transcribe.cpp](https://github.com/handy-computer/transcribe.cpp)
- [Hugging Face GGUFs](https://huggingface.co/handy-computer)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- [CLAP](https://github.com/LAION-AI/CLAP)
- [CLAP-ONNX CPU benchmarks](https://github.com/Lednik7/CLIP-ONNX)
- [YAMNet](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [pyannote-audio](https://github.com/pyannote/pyannote-audio)
- [Piper](https://github.com/OHF-Voice/piper1-gpl)
- [samples](https://rhasspy.github.io/piper-samples/)
- [Piper TTS Setup Guide 2026](https://localaimaster.com/blog/piper-tts-setup-guide)
- [Coqui TTS](https://github.com/idiap/coqui-tts)
- [CPU Docker docs](https://docs.coqui.ai/en/latest/docker_images.html)
- [XTTS docs](https://docs.coqui.ai/en/stable/models/xtts.html)
- [PocketTTS](https://github.com/kyutai-labs/pocket-tts)
- [tech report](https://kyutai.org/blog/2026-01-13-pocket-tts)
- [paper](https://arxiv.org/abs/2509.06926)
- [PocketTTS.cpp](https://github.com/VolgaGerm/PocketTTS.cpp)
- [sentence-transformers with ONNX backend](https://sbert.net/docs/sentence_transformer/usage/efficiency.html)
- [ONNX benchmark gist](https://gist.github.com/kylediaz/7e8df0a19e2137ef10fc62b5421e4d9a)
- [BGE-M3 ONNX](https://huggingface.co/Sophia-AI/bge-m3-onnx)
- [ONNX Community variant](https://huggingface.co/onnx-community/bge-m3-ONNX)
- [all-MiniLM-L6-v2 ONNX](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [BART-large-MNLI ONNX](https://huggingface.co/Maxi-Lein/bart-large-mnli-onnx)
- [Haystack integration](https://docs.haystack.deepset.ai/docs/transformerszeroshotdocumentclassifier)
- [cross-encoder/nli-distilroberta-base](https://huggingface.co/cross-encoder/nli-distilroberta-base)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [Training benchmarks](https://github.com/PaddlePaddle/PaddleOCR/tree/main/benchmark)
- [CPU optimization guide](https://deepwiki.com/PaddlePaddle/PaddleOCR/8.3-cpu-optimization)
- [Surya OCR 2](https://github.com/datalab-to/surya)
- [Announcement](https://www.datalab.to/blog/surya-2)
- [MobileNetV3 / EfficientNet-Lite (TFLite ONNX)](https://tildalice.io/mobilenetv3-vs-efficientnet-lite-arm-latency/)
- [MobileNet vs EfficientNet comparison](https://tildalice.io/mobilenet-vs-efficientnet-lite-pi4-latency-benchmark/)
- [EfficientNet ONNX Runtime CPU](https://github.com/zhangchaosd/ModelInferBench)
- [PyTorch to ONNX deployment guide](https://genmind.ch/posts/From-PyTorch-to-Production-Deploy-ML-Models-Locally-with-ONNX/)
- [MobileSAM](https://github.com/ChaoningZhang/MobileSAM)
- [Hugging Face demo](https://huggingface.co/spaces/dhkim2810/MobileSAM)
- [ONNX notebook](https://github.com/ChaoningZhang/MobileSAM/blob/master/notebooks/onnx_model_example.ipynb)
- [SAM2 ONNX](https://github.com/pagarcia/sam2-onnx-cpp)
- [SAM2 ONNX benchmark](https://people.ac.upc.edu/rtous/publications/conf_2025iwann.pdf)
- [OpenVINO Stable Diffusion (Optimum Intel)](https://huggingface.co/docs/optimum-intel/openvino/tutorials/diffusers)
- [OpenVINO SD notebook](https://docs.openvino.ai/2024/notebooks/stable-diffusion-text-to-image-with-output.html)
- [SDXL on OpenVINO](https://docs.openvino.ai/2024/notebooks/stable-diffusion-xl-with-output.html)
- [rembg](https://github.com/danielgatis/rembg)
- [CPU benchmarks](https://bunn-io.github.io/rembg-web/api/index.html)
- [InsightFace](https://github.com/deepinsight/insightface)
- [OpenVINO export guide](https://www.insightface.ai/guides/convert-onnx-to-tensorrt-openvino)