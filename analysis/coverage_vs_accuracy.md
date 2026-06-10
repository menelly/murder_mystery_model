# Coverage vs Accuracy — disentangling format-following from reasoning

Three numbers per model, all reported (Ren, 2026-06-10): **coverage** = parseable/total (did it emit a usable answer at all — instruction-following + truncation); **parseable accuracy** = correct/parseable (reasoning, given a parseable answer); **strict accuracy** = correct/total (unparseable counted as failure — the conjunction).

| Model | N | coverage | parseable acc | strict acc |
|---|---:|---:|---:|---:|
| RWKV v6 Finch 1.6B | 72 | 15% | 36% | 6% |
| SmolLM 135M Instruct | 72 | 54% | 33% | 18% |
| Pythia 1.4B | 72 | 61% | 41% | 25% |
| Liquid LFM 2.5 1.2B | 72 | 68% | 39% | 26% |
| SmolLM 360M Instruct | 72 | 69% | 34% | 24% |
| Qwen 3 14B | 72 | 82% | 100% | 82% |
| DeepSeek V4 Pro | 72 | 85% | 97% | 82% |
| DeepSeek R1 0528 | 72 | 88% | 98% | 86% |
| SmolLM 1.7B Instruct | 72 | 92% | 30% | 28% |
| OpenAI o4-mini-high | 72 | 93% | 100% | 93% |
| Phi-2 | 72 | 93% | 34% | 32% |
| Qwen 3 235B A22B Thinking | 72 | 94% | 100% | 94% |
| Qwen 3 32B | 72 | 96% | 93% | 89% |
| DeepSeek R1 | 72 | 96% | 97% | 93% |
| Gemini 3.5 Flash | 72 | 97% | 86% | 83% |
| Gemini 2.5 Pro | 72 | 99% | 89% | 88% |
| OpenAI o3 | 72 | 99% | 97% | 96% |
| TinyLlama 1.1B Chat | 72 | 99% | 39% | 39% |
| Llama 3.1 8B Instruct | 72 | 100% | 49% | 49% |
| OpenAI o1 | 72 | 100% | 100% | 100% |
| Qwen 3 8B | 72 | 100% | 90% | 90% |
| GPT-5.5 | 72 | 100% | 100% | 100% |
| Hermes 3 Llama 3.2 3B | 72 | 100% | 44% | 44% |
| Claude Sonnet 4.6 | 72 | 100% | 83% | 83% |
| DeepSeek V3.1 Terminus | 72 | 100% | 51% | 51% |
| Claude Opus 4.7 | 72 | 100% | 90% | 90% |
| Qwen 3 235B A22B | 72 | 100% | 93% | 93% |
| Llama 3 70B Instruct | 72 | 100% | 68% | 68% |
| Gemini 3.1 Pro Preview | 72 | 100% | 83% | 83% |
| GPT-4.1 | 72 | 100% | 82% | 82% |
| Gemini 2.5 Flash | 72 | 100% | 79% | 79% |
| Hermes 3 Llama 3.1 8B | 72 | 100% | 49% | 49% |
| GPT-4o 2024-05-13 | 72 | 100% | 83% | 83% |
| Claude Opus 4.6 | 72 | 100% | 96% | 96% |
| Grok 4.3 | 72 | 100% | 60% | 60% |
| Phi-4-mini Instruct (OR) | 72 | 100% | 44% | 44% |
| Claude Opus 4.1 | 72 | 100% | 50% | 50% |
| GPT-3.5-turbo | 72 | 100% | 44% | 44% |
| GPT-4 Turbo | 72 | 100% | 76% | 76% |
| DeepSeek V3.2 | 72 | 100% | 65% | 65% |
| AI21 Jamba Large 1.7 | 72 | 100% | 49% | 49% |
| Llama 3.3 70B Instruct | 72 | 100% | 74% | 74% |
| Gemma 4 31B IT | 72 | 100% | 97% | 97% |
| Gemma 3 4B IT | 72 | 100% | 46% | 46% |
| Liquid LFM 2 24B A2B | 72 | 100% | 44% | 44% |
| Mistral Nemo 12B | 72 | 100% | 56% | 56% |
| Claude Haiku 4.5 | 72 | 100% | 65% | 65% |
| Llama 4 Maverick | 72 | 100% | 67% | 67% |
| Qwen 2.5 7B Instruct | 72 | 100% | 54% | 54% |
| Claude Opus 4.5 | 72 | 100% | 90% | 90% |
| Claude Opus 4 | 72 | 100% | 64% | 64% |
| Mistral 7B Instruct v0.3 | 72 | 100% | 53% | 53% |
| Gemma 2 27B IT | 72 | 100% | 65% | 65% |
| Qwen 2.5 0.5B Instruct | 72 | 100% | 38% | 38% |
| Claude 3.5 Haiku | 72 | 100% | 49% | 49% |
| Gemma 3 12B IT | 72 | 100% | 58% | 58% |
| Mistral Small 24B 2603 | 72 | 100% | 56% | 56% |
| Claude Opus 4.8 | 72 | 100% | 93% | 93% |
| Gemini 3 Flash Preview | 72 | 100% | 79% | 79% |
| Llama 3 8B Instruct | 72 | 100% | 46% | 46% |
| Qwen 2.5 72B Instruct | 72 | 100% | 78% | 78% |
| Llama 3.1 70B Instruct | 72 | 100% | 75% | 75% |
| Gemma 3 27B IT | 72 | 100% | 76% | 76% |
| DeepSeek Chat | 72 | 100% | 53% | 53% |

## How to read it
- **Floor models** (RWKV, SmolLM-135M/360M, Pythia, Liquid LFM 2.5): low coverage AND ~chance parseable accuracy = both a format-following floor and a reasoning floor.
- **SmolLM-1.7B / Phi-2**: high coverage (~92%) but ~30% parseable accuracy = a clean reasoning floor with format-following intact (the cleanest evidence the floor is partly genuine reasoning failure).
- **Frontier reasoners** (Qwen-3-14B, o4-mini, DeepSeek R1): coverage 82-96% but parseable accuracy 97-100% = their lower coverage is extended-thinking truncation, not error; strict accuracy understates them.

So "Where does understanding begin?" has two emergence curves, not one: a format/instruction-following curve and a reasoning curve. Reporting both denominators separates them instead of conflating them in a single accuracy number.