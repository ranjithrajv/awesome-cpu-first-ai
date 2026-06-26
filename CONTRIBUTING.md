# Contributing to Awesome CPU-First AI

Thank you for helping make this list better. Please read these guidelines before opening a pull request.

## The bar for inclusion

This list has a thesis — CPU is the default you reach for, GPU is the exception you justify. Every entry should serve that argument. Before adding something, ask:

1. **Is it CPU-native or CPU-first?** The project should target CPU as a primary platform, not as an afterthought or fallback. A GPU framework that happens to compile without CUDA does not qualify.
2. **Is it directly relevant to the CPU-vs-GPU decision?** Benchmarks, cost analyses, papers, and decision frameworks that help someone choose between CPU and GPU are in scope even if they are not CPU-only.
3. **Is it maintained?** Prefer projects with activity in the last 12 months. For archived or unmaintained projects, note that status explicitly in the description.
4. **Does it avoid overlap?** Check existing entries before adding. If a better-maintained alternative is already listed, open an issue to discuss rather than adding a duplicate.

When in doubt, open an issue first and make the case. It is easier to add a link after discussion than to remove one after merging.

## What does not belong

- GPU frameworks that run on CPU only as a slow fallback (PyTorch CPU-only builds, TGI, vLLM, etc.)
- Training tools — this list covers inference
- Projects without a public source repository or verifiable download
- Anything requiring fabricated or unverified benchmark numbers to justify inclusion — use a `<!-- TODO: cite benchmark -->` placeholder instead

## Exception: quantization tools that produce CPU-runnable artifacts

A GPU-side quantization tool is in scope if it satisfies all three conditions:

1. Its primary output is a format consumed by a CPU runtime (GGUF, ONNX, OpenVINO IR, etc.).
2. The entry notes explicitly that the tool itself runs on GPU.
3. The entry links to or describes the CPU deployment step, not just the quantization step.

AutoGPTQ is the canonical example: it runs on GPU to produce GPTQ checkpoints that are subsequently converted to GGUF for llama.cpp. A tool that only quantizes and whose output has no documented CPU inference path does not qualify under this exception.

## Format

Follow the existing style exactly:

```markdown
- [Project Name](https://github.com/owner/repo) — One-line description in your own words; neutral and specific, not marketing copy.
```

- Use an em dash (`—`) between the link and description, with a space on each side.
- Keep descriptions to one sentence. If you need a caveat (see AutoGPTQ), add it as a parenthetical `*(Note: ...)*` on the same line.
- Place the entry in alphabetical order within its section, unless a logical ordering is clearly better.
- Use `<!-- TODO: ... -->` rather than inventing benchmark numbers or latency figures you cannot verify.

## Sections

Add entries to the most specific section that fits. If a project spans multiple sections, pick the primary use case. If no existing section fits, propose a new one in your PR description and explain why the grouping is warranted.

## Pull request checklist

- [ ] The project is CPU-native or directly relevant to the CPU-vs-GPU decision
- [ ] The description is one sentence, neutral, and written in your own words
- [ ] The link is to a stable URL (GitHub repo, docs page, or paper — not a personal blog post that may disappear). Exception: reproducible benchmark data or practitioner experiments from a recognized source may be included if the data can be independently verified.
- [ ] The entry is placed in the correct section and in order
- [ ] You have not introduced any fabricated numbers or unverified claims
- [ ] `README.md` renders correctly with `grip` or GitHub's preview

## Filling in TODOs

The README contains several `<!-- TODO: ... -->` placeholders marking gaps where a benchmark, paper, or cost analysis would strengthen the list but could not be verified at time of writing. Contributions that fill a TODO with a real, citable source are especially welcome. Include the source URL and a brief note on why you trust the figures (e.g., peer-reviewed, MLPerf-audited, reproduced independently).

## Code of conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Be direct, be specific, and be kind.
