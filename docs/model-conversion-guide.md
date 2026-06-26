# Model Conversion Guide

Practical walkthroughs for converting Hugging Face checkpoints to CPU-friendly formats — GGUF (for llama.cpp) and ONNX (for ONNX Runtime / OpenVINO).

---

## Contents

- [HF → GGUF (llama.cpp Quantize)](#hf--gguf)

## HF → GGUF

### Prerequisites

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j
# or for ARM: cmake -B build && cmake --build build --config Release
```

### Convert + Quantize in One Step

```bash
# Download a model from Hugging Face
pip install huggingface-hub
huggingface-cli download meta-llama/Llama-3.2-3B-Instruct \
  --local-dir ./models/Llama-3.2-3B-Instruct

# Convert to FP16 GGUF, then quantize to Q4_K_M
python convert_hf_to_gguf.py ./models/Llama-3.2-3B-Instruct \
  --outfile ./models/llama-3.2-3b-fp16.gguf

./quantize ./models/llama-3.2-3b-fp16.gguf \
  ./models/llama-3.2-3b-q4_k_m.gguf Q4_K_M
```

### Choosing a Quantization Level

| Quant | Size vs FP16 | Quality | Use case |
|---|---|---|---|
| Q2_K | ~25% | Significant loss | Extreme memory constraints |
| Q3_K_S | ~33% | Noticeable loss | Very constrained RAM |
| Q4_K_M | ~45% | Minimal loss | **Recommended default** |
| Q5_K_M | ~55% | Near-lossless | Quality-sensitive, enough RAM |
| Q6_K | ~60% | Virtually lossless | Generous RAM budget |
| Q8_0 | ~75% | Lossless (weights) | Full precision feel |

Q4_K_M is the recommended default for CPU inference — best trade-off between speed, memory, and quality.

### Verify the Conversion

```bash
./llama-cli \
  --model ./models/llama-3.2-3b-q4_k_m.gguf \
  --prompt "Hello, world" \
  --threads 8 \
  -n 32
```

If you see coherent output, the conversion succeeded.

---

## PyTorch → ONNX (via Optimum)

### Prerequisites

```bash
pip install optimum[onnxruntime] transformers
```

### Export

```python
from optimum.onnxruntime import ORTModelForCausalLM
from transformers import AutoTokenizer

model_id = "meta-llama/Llama-3.2-3B-Instruct"

# Export to ONNX
model = ORTModelForCausalLM.from_pretrained(model_id, export=True)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Save
model.save_pretrained("./llama-3.2-3b-onnx")
tokenizer.save_pretrained("./llama-3.2-3b-onnx")
```

### Quantize to INT8

```python
from optimum.onnxruntime import ORTQuantizer
from optimum.onnxruntime.configuration import AutoCalibrationConfig

# Post-training quantization
quantizer = ORTQuantizer.from_pretrained(model)
calibration_dataset = quantizer.get_calibration_dataset(
    "dataset_name",
    calibration_config=AutoCalibrationConfig.minmax(calibration_dataset),
)
quantizer.quantize(
    save_dir="./llama-3.2-3b-onnx-int8",
    calibration_tensors_range=quantizer.compute_calibration(calibration_dataset),
)
```

### Validate

```python
from optimum.onnxruntime import ORTModelForCausalLM
from transformers import AutoTokenizer

model = ORTModelForCausalLM.from_pretrained(
    "./llama-3.2-3b-onnx-int8",
    use_cache=True,
    use_io_binding=False,
)
tokenizer = AutoTokenizer.from_pretrained("./llama-3.2-3b-onnx-int8")
inputs = tokenizer("Hello, world", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=32)
print(tokenizer.decode(outputs[0]))
```

---

## Troubleshooting

### "File is too large for 32-bit mmap"

The model exceeds the 4 GB mmap limit on 32-bit systems or containers without large file support. Use `--no-mmap` in llama.cpp or switch to a 64-bit environment.

### OOM during conversion

Reduce the `--context-size` in the convert script or quantize on a machine with more RAM. For very large models (70B+), use the `--split` flag to produce sharded GGUF files.

### ONNX export fails on custom ops

Some model architectures use unsupported operators. Check the [ONNX Runtime operator support matrix](https://onnxruntime.ai/docs/operators/) and consider using a model variant that avoids custom ops.

### "CUDA error: out of memory" during export

The export step may briefly load the model in FP32 on GPU. Force CPU:

```python
model = ORTModelForCausalLM.from_pretrained(
    model_id, export=True, torch_dtype="cpu"
)
```
