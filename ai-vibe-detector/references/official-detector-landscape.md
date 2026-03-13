# Official Detector Landscape

This file summarizes how major public AI detectors describe themselves and their limits.

## Shared Takeaways

- Detectors output probability-like risk signals, not proof of authorship.
- Results are weaker on short text, heavily edited text, and mixed-authorship text.
- Low scores should not be over-interpreted.
- Detector results should be combined with human review.

## Turnitin

Key public positioning:
- Distinguishes AI-generated text from AI-paraphrased text in newer reporting flows.
- Uses thresholding and does not surface very low-confidence percentages.
- Explicitly says the report should not be the sole basis for disciplinary action.

What this means for the skill:
- Do not treat “some AI signal” as proof.
- Add a separate “AI-polished / AI-paraphrased” category.

## GPTZero

Key public positioning:
- Uses a multi-component model, not a single heuristic.
- Continually updates training coverage as models change.
- Emphasizes uncertainty and human review.

What this means for the skill:
- Avoid over-relying on shallow rules like one connective or one punctuation pattern.
- Prefer multi-signal analysis with confidence levels.

## Copyleaks

Key public positioning:
- Publicly discusses signals like perplexity, burstiness, repetitive phrasing, and lack of personal style.
- Also acknowledges false positives and imperfect detection.

What this means for the skill:
- It is reasonable to discuss low textual variability and repetitive phrasing.
- It is not reasonable to claim certainty from a few stylistic markers.

## OpenAI Historical Lesson

OpenAI retired its own AI text classifier due to limited reliability.

What this means for the skill:
- Keep humility in the output.
- Always include false-positive risk.
- Never promise reliable authorship attribution from style alone.
