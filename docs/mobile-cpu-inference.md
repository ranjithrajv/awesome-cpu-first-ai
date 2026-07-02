# Mobile Phone CPU Inference

Modern flagship phones run billion-parameter LLMs on-device — no cloud round-trip, no GPU required. The CPU path is the most portable, vendor-independent option for mobile inference: it works across all devices regardless of NPU vendor lock-in, and for LLMs it often matches or exceeds NPU throughput due to more mature tooling and the memory-bandwidth-bound nature of token generation. This doc covers mobile chipsets, on-device runtimes, benchmarks, and deployment guides for CPU-first inference on phones.

> NPU TOPS figures are included for reference. For generative LLM workloads, CPU throughput is frequently competitive with or better than NPU on current hardware — the bottleneck is memory bandwidth, not compute.

---

## Contents

- [SoCs and Platforms](#socs-and-platforms)
- [Runtimes and Apps](#runtimes-and-apps)
- [Benchmarks and Deployment Guides](#benchmarks-and-deployment-guides)
- [References](#references)

---

## SoCs and Platforms

- [Apple A19 Pro (iPhone 17 Pro, 2025)](https://www.apple.com/iphone/) — Apple's flagship mobile SoC with 6-core CPU and 16-core Neural Engine (~35 TOPS); Llama-3.1 8B INT4 via MLC-LLM on CPU achieves 7–12 tok/s (TTFT ~380 ms), often outperforming the NPU path due to unified memory (8–12 GB) and mature inference stacks. The A18 Pro (iPhone 16 Pro) reaches 6–10 tok/s on the same workload. ([PocketLLM iPhone Bake-Off](https://pocketllm.app/blog/llama-3-vs-phi-3-vs-gemma-2-iphone/))
- [Qualcomm Snapdragon 8 Elite (Galaxy S25 / Xiaomi 15, 2025)](https://www.qualcomm.com/products/mobile/snapdragon/smartphones/snapdragon-8-series-mobile-platforms/snapdragon-8-elite) — Qualcomm's flagship mobile platform with custom Oryon CPU cores and Hexagon NPU (~60 TOPS); Llama-3.1 8B INT4 via llama.cpp on CPU reaches 8–12 tok/s — frequently faster than the NPU path because CPU stacks (llama.cpp, ExecuTorch) are more mature than Qualcomm's QNN tooling for LLM workloads. Earlier Snapdragon 8 Gen 3 (Galaxy S24) still achieves 18–25 tok/s on 3B models. ([Qualcomm AI Hub](https://aihub.qualcomm.com/))
- [Samsung Exynos 2500 (Galaxy Z Flip 7, 2025)](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2500/) — Samsung's 3nm GAA flagship SoC with a 10-core Arm CPU cluster and 59 TOPS NPU (39% uplift over Exynos 2400); supports ExecuTorch natively for PyTorch model deployment. The Exynos AI Studio toolchain handles model compression, graph optimization, and NPU/CPU deployment from ONNX/TFLite/PyTorch inputs. ([Exynos AI Studio overview](https://semiconductor.samsung.com/news-events/tech-blog/unpacking-samsungs-comprehensive-on-device-ai-sdk-toolchain-strategy/))
- [MediaTek Dimensity 9500 / 9400+ (2026)](https://i.mediatek.com/mediatek-dimensity-ai) — MediaTek's flagship SoC with Arm Cortex-X925 CPU and NPU 890 (~50 TOPS); CPU inference via ExecuTorch or MLC-LLM runs Llama-3.1 8B at 5–8 tok/s. As the most widely adopted Android SoC by volume, Dimensity is the default target for broad mobile CPU inference deployment.
- [Google Tensor G5 (Pixel 10, 2025)](https://store.google.com/pixel_10) — Google's custom SoC with Arm CPU cores and a dedicated TPU; on-device LLM inference defaults to CPU in practice — LiteRT's TPU delegate requires an experimental SDK. Llama-3.1 8B via LiteRT CPU (XNNPACK) achieves ~10 tok/s. The earlier Tensor G4 (Pixel 9) uses CPU inference exclusively for LLMs with no NPU path available. ([LiteRT](https://ai.google.dev/edge/litert))

---

## Runtimes and Apps

- [MLC-LLM on iOS and Android](https://github.com/mlc-ai/mlc-llm) — Cross-platform LLM inference app shipping pre-quantized models (Llama 3.1 8B, Qwen 2.5 7B, Phi-3) via GPU backends (Metal on iOS, OpenCL/Vulkan on Android) with an OpenAI-compatible API. Achieves 6–12 tok/s on flagship phones for 7B INT4 models; the only mainstream runtime shipping identical checkpoints across iOS, Android, and Web from one toolchain. ([iOS deployment guide](https://github.com/mlc-ai/mlc-llm/blob/main/docs/deploy/ios.rst), [Android deployment guide](https://github.com/mlc-ai/mlc-llm/blob/main/docs/deploy/android.rst))
- [Apple Core AI (WWDC 2026)](https://developer.apple.com/videos/play/wwdc2026/324/) — Apple's on-device AI inference framework, successor to Core ML and the engine behind Apple Intelligence; runs across CPU, GPU, and Neural Engine under a single Swift API with ahead-of-time compilation and zero-copy data paths. Supports models from 3B to 70B on iPhone, iPad, and Mac. ([InfoQ overview](https://www.infoq.com/news/2026/06/apple-core-ai-wwdc/))
- [llama.cpp Android](https://github.com/ggerganov/llama.cpp/blob/master/docs/android.md) — Cross-compiled llama.cpp for Android ARM; runs any GGUF model entirely on CPU with no GPU or NPU dependency, achieving 9–12 tok/s on Snapdragon 8 Elite for 7B Q4 models. The most flexible option for sideloading arbitrary models on Android. *(Also listed under On-Device, Edge, ARM, and SBCs in the README.)*
- [Qualcomm AI Hub](https://aihub.qualcomm.com/) — Model zoo with pre-optimized INT8/INT4 models for Snapdragon platforms, deployable via LiteRT, ONNX Runtime, and Qualcomm AI Engine Direct SDKs. The Hexagon NPU path delivers 12–25 tok/s on flagship Snapdragon but is Snapdragon-only; CPU fallback is always available for cross-device compatibility. ([QNN SDK](https://developer.qualcomm.com/software/qualcomm-ai-engine-direct-sdk))
- [Arm SME2 & KleidiAI](https://www.arm.com/technologies/sme2/accelerate-on-device-ai) — Scalable Matrix Extension 2 CPU instructions with the KleidiAI operator library deliver up to 6× faster AI inference on Arm v9.3+ mobile CPUs (iPhone 16/17, vivo X300 series) with no code changes — integrated in XNNPACK, ExecuTorch, ONNX Runtime, llama.cpp, and MNN.

---

## Benchmarks and Deployment Guides

- [On-Device LLMs: State of the Union 2026 (Vikas Chandra / Meta)](https://v-chandra.github.io/on-device-llms/) — Comprehensive survey of on-device LLM deployment across mobile chipsets (Apple A19 Pro, Snapdragon 8 Elite Gen 5, Dimensity 9400+); covers NPU TOPS, memory bandwidth constraints, model compression strategies, and runtime recommendations (ExecuTorch for production, llama.cpp for prototyping, MLX for Apple ecosystem).
- [Mobile LLM benchmark: A19 Pro vs Snapdragon 8 Elite Gen 5 vs Dimensity 9500 vs Tensor G5 (Beebom, Apr 2026)](https://gadgets.beebom.com/stories/i-tested-on-device-ai-on-android-and-iphone-results-not-even-close) — Head-to-head benchmark across four flagship chipsets; Apple A19 Pro CPU delivers the fastest decode (36.99 tok/s) while Tensor G5 is forced to CPU-only (10.42 tok/s) due to inaccessible TPU delegates. Documents the Android NPU fragmentation problem.
- [LLMs on iPhone and Android 2026: What Actually Works (CraftRigs, Apr 2026)](https://craftrigs.com/articles/run-llm-android-ios-2026-hardware-app-guide/) — Practical deployment guide with real tok/s numbers and thermal measurements for 7B models on iPhone 16 Pro and Galaxy S25 via MLC-LLM and llama.cpp, including thermal throttling behavior under sustained load.
- [Best mobile AI runtimes 2026 tier list (RunLocalAI, May 2026)](https://www.runlocalai.co/guides/best-mobile-ai-runtimes) — Comparison of MLC LLM, llama.cpp, ExecuTorch, ONNX Runtime Mobile, and Qualcomm AI Hub across iOS and Android with NPU path support, model formats, and setup complexity ratings.

---

See also: [On-Device, Edge, ARM, and SBCs (README)](../README.md#on-device-edge-arm-and-sbcs) · [Model Conversion Guide](model-conversion-guide.md) · [CPU Inference Deployment Guide](cpu-inference-deployment.md) · [Benchmark Methodology](benchmark-methodology.md)

---

## References

- [Apple A19 Pro (iPhone 17 Pro, 2025)](https://www.apple.com/iphone/)
- [PocketLLM iPhone Bake-Off](https://pocketllm.app/blog/llama-3-vs-phi-3-vs-gemma-2-iphone/)
- [Qualcomm Snapdragon 8 Elite (Galaxy S25 / Xiaomi 15, 2025)](https://www.qualcomm.com/products/mobile/snapdragon/smartphones/snapdragon-8-series-mobile-platforms/snapdragon-8-elite)
- [Qualcomm AI Hub](https://aihub.qualcomm.com/)
- [Samsung Exynos 2500 (Galaxy Z Flip 7, 2025)](https://semiconductor.samsung.com/processor/mobile-processor/exynos-2500/)
- [Exynos AI Studio overview](https://semiconductor.samsung.com/news-events/tech-blog/unpacking-samsungs-comprehensive-on-device-ai-sdk-toolchain-strategy/)
- [MediaTek Dimensity 9500 / 9400+ (2026)](https://i.mediatek.com/mediatek-dimensity-ai)
- [Google Tensor G5 (Pixel 10, 2025)](https://store.google.com/pixel_10)
- [LiteRT](https://ai.google.dev/edge/litert)
- [MLC-LLM on iOS and Android](https://github.com/mlc-ai/mlc-llm)
- [iOS deployment guide](https://github.com/mlc-ai/mlc-llm/blob/main/docs/deploy/ios.rst)
- [Android deployment guide](https://github.com/mlc-ai/mlc-llm/blob/main/docs/deploy/android.rst)
- [Apple Core AI (WWDC 2026)](https://developer.apple.com/videos/play/wwdc2026/324/)
- [InfoQ overview](https://www.infoq.com/news/2026/06/apple-core-ai-wwdc/)
- [llama.cpp Android](https://github.com/ggerganov/llama.cpp/blob/master/docs/android.md)
- [QNN SDK](https://developer.qualcomm.com/software/qualcomm-ai-engine-direct-sdk)
- [Arm SME2 & KleidiAI](https://www.arm.com/technologies/sme2/accelerate-on-device-ai)
- [On-Device LLMs: State of the Union 2026 (Vikas Chandra / Meta)](https://v-chandra.github.io/on-device-llms/)
- [Mobile LLM benchmark: A19 Pro vs Snapdragon 8 Elite Gen 5 vs Dimensity 9500 vs Tensor G5 (Beebom, Apr 2026)](https://gadgets.beebom.com/stories/i-tested-on-device-ai-on-android-and-iphone-results-not-even-close)
- [LLMs on iPhone and Android 2026: What Actually Works (CraftRigs, Apr 2026)](https://craftrigs.com/articles/run-llm-android-ios-2026-hardware-app-guide/)
- [Best mobile AI runtimes 2026 tier list (RunLocalAI, May 2026)](https://www.runlocalai.co/guides/best-mobile-ai-runtimes)