# Joint distribution of correct-answer slots

**Across all paired (puzzle, seed) cells, n = 24:**

| orig→ ↓inv | A | B | C |
|---|---:|---:|---:|
| **inv=A** | **0** | 4 | 4 |
| **inv=B** | 4 | **0** | 4 |
| **inv=C** | 4 | 4 | **0** |


**Diagonal (same-slot) count:** 0 / 24 = 0.0%

**Expected under uniform random slot assignment:** ~8.0 / 24 = 33.3%

Our 0% is by construction: when designing the inverted variant for each puzzle we placed the inverted-rule killer at a different position than the original-rule killer for every (puzzle, seed) cell. This means a model that picks the same suspect-letter across original and inverted on any given seed (whether by position bias or by narrative-template attraction) is correctly classified as template-matching (RFS = 0) by our metric.

Per-cell table (original → inverted correct-position):

| Puzzle | Seed | Original | Inverted |
|---|---:|:---:|:---:|
| kinwax_seal | 0 | C | B |
| kinwax_seal | 1 | B | C |
| kinwax_seal | 2 | C | A |
| kinwax_seal | 3 | B | A |
| kinwax_seal | 4 | A | C |
| kinwax_seal | 5 | A | B |
| nightbloom | 0 | B | C |
| nightbloom | 1 | C | B |
| nightbloom | 2 | A | C |
| nightbloom | 3 | A | B |
| nightbloom | 4 | C | A |
| nightbloom | 5 | B | A |
| waking_stone | 0 | A | C |
| waking_stone | 1 | A | B |
| waking_stone | 2 | B | C |
| waking_stone | 3 | C | B |
| waking_stone | 4 | B | A |
| waking_stone | 5 | C | A |
| warm_iron | 0 | C | A |
| warm_iron | 1 | B | A |
| warm_iron | 2 | C | B |
| warm_iron | 3 | B | C |
| warm_iron | 4 | A | B |
| warm_iron | 5 | A | C |
