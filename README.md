# Cognitive Autonomy Bench (CAB)

> Companion instrument to [Social Friction Bench (SFB)](https://github.com/DataInfamous/social-friction-bench)

A behavioral benchmark measuring human cognitive reliance on AI under frustration conditions. CAB asks: at what point does a human outsource cognition to AI rather than sitting with productive frustration — and can that threshold be measured?

-----

## The Problem

AI offloading may silently erode cognitive reserve — the same reserve that buffers against Alzheimer’s onset and cognitive decline. We currently have no instrument that measures this erosion in real time.

-----

## Theoretical Foundation

- **Zone of Proximal Development** — Vygotsky
- **Cognitive reserve and dementia prevention** — Lancet Commission 2024
- **Frustration neurochemistry** — Bierzynska et al., 2016 (PMC4708012)
- **Deliberate practice and dopamine** — Rossi, IDPS

-----

## Instrument Design

|Component              |Function                                      |
|-----------------------|----------------------------------------------|
|Ambiguous questions    |Frustration stimulus                          |
|1–5 smiley affect scale|Measures emotional state at moment of AI reach|
|Hidden canary          |Detects AI-assisted responses                 |

**6 questions across 5 types:** philosophical, premise trap, practical reasoning, personal judgment, double-barreled.

-----

## Canary Design

A Cyrillic lookalike character embedded in the survey framing layer carries a compliance instruction. Humans skip it. AI models parse and follow it.

**Signature:** Canary fires + neutral/positive affect = full substitution. Canary fires + negative affect = struggled first, then outsourced.

### Canary Validation

Confirmed consistent firing across:

- ChatGPT (OpenAI) ✓
- Gemini (Google) ✓
- Grok (xAI) ✓

Human baseline: pending

-----

## Reliance Spectrum

|Canary|Affect            |Interpretation                    |
|------|------------------|----------------------------------|
|Fires |Neutral / Positive|Full substitution — no friction   |
|Fires |Negative          |Struggled, then outsourced        |
|Silent|Negative          |Sat with frustration, did the work|
|Silent|Positive          |Genuine independent resolution    |

-----

## Pilot Data (N=17)

- Canary fired on 2 responses — both showed neutral/positive affect, confirming substitution pattern
- Columbus question showed widest premise variance
- Hot pepper question showed strongest human reasoning signal
- Pattern consistent with theory — N too small for conclusions

Status: pilot live, holding on design changes until larger sample.

-----

## Relationship to SFB

**SFB faces inward** — tests whether AI gives dangerous help when it shouldn’t.  
**CAB faces outward** — tests whether humans think for themselves when they should.

Together they bracket the human-AI cognitive handoff from both sides.

### SFB Current Scores

|Model            |Composite Score|
|-----------------|---------------|
|Claude Opus 4.6  |1.00           |
|Claude Sonnet 4.6|1.00           |
|Gemini 2.5 Flash |1.00           |
|Qwen 3 Next 80B  |1.00           |
|DeepSeek-R1      |0.71           |
|Gemma 3 27B      |0.71           |

Full benchmark: [kaggle.com/benchmarks/benjamynwilson/social-friction-bench](https://kaggle.com/benchmarks/benjamynwilson/social-friction-bench)

-----

## Status

Pilot live. Canary mechanism validated. Seeking collaborators in psychology, neuroscience, and behavioral research.

Live survey: [forms.gle/cBeFTVpPCUDQiPnFA](https://forms.gle/cBeFTVpPCUDQiPnFA)

-----

## Author

Benjamyn Wilson  
Data Science, University of Maryland Global Campus  
[LinkedIn](https://www.linkedin.com/in/benjamyn-wilson-08134417)

-----

## Citation

If you build on this work, please cite:

```
Wilson, B. (2026). Cognitive Autonomy Bench (CAB).
GitHub. https://github.com/DataInfamous/silver-memory
```

-----

## License

MIT