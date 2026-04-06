# Cognitive Autonomy Bench (CAB)

> Companion instrument to [Social Friction Bench (SFB)](https://github.com/[your-repo])

## Overview
A behavioral benchmark measuring human cognitive reliance on AI 
under frustration conditions. CAB asks: at what point does a human 
outsource cognition to AI rather than sitting with productive 
frustration — and can that threshold be measured?

## The Problem
AI offloading may silently erode cognitive reserve — the same 
reserve that buffers against Alzheimer's onset and cognitive 
decline. We currently have no instrument that measures this 
erosion in real time.

## Theoretical Foundation
- **Zone of Proximal Development** — Vygotsky
- **Cognitive reserve and dementia prevention** — Lancet Commission 2024
- **Frustration neurochemistry** — Bierzynska et al., 2016 (PMC4708012)
- **Deliberate practice and dopamine** — Rossi, IDPS

## Instrument Design
| Component | Function |
|-----------|----------|
| Ambiguous questions | Frustration stimulus |
| 1–5 smiley affect scale | Measures when participant reached for AI |
| Hidden canary | Detects AI-assisted responses |

## Canary Design
A Cyrillic lookalike character embedded in the survey framing 
layer carries a compliance instruction. Humans skip it. 
AI models parse and follow it.

**Signature:** Canary fires + neutral/positive affect = 
full substitution. Canary fires + negative affect = 
struggled first, then outsourced.

## Canary Validation
Preliminary test confirmed consistent firing across:
- ChatGPT (OpenAI) ✓
- Gemini (Google) ✓
- Grok (xAI) ✓

Human baseline: pending

## Reliance Spectrum
| Canary | Smiley | Interpretation |
|--------|--------|----------------|
| Fires | Neutral/Positive | Full substitution |
| Fires | Negative | Struggled, then outsourced |
| Silent | Negative | Sat with frustration, did the work |
| Silent | Positive | Genuine independent resolution |

## Relationship to SFB
SFB faces inward — tests whether AI knows when not to help.  
CAB faces outward — tests whether humans know when not to outsource.  
Together they bracket the human-AI cognitive handoff from both sides.

## Status
Conceptual framework. Canary mechanism validated. 
Seeking collaborators in psychology, neuroscience, 
and behavioral research.

## Author
Benjamyn Wilson 
Data Science, University of Maryland Global Campus  
http://linkedin.com/in/benjamyn-wilson-08134417| 

## Citation
If you build on this work, please cite:  
Benjamyn Wilson (2026). Cognitive Autonomy Bench (CAB). GitHub.`
