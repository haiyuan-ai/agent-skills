# Research Limitations

This file captures the main research-side caution signals for AI text detection.

## Current Consensus

- Authorship detection is materially harder than identifying “generic polished style”.
- False positives matter, especially under strict low-FPR settings.
- Mixed-authorship and AI-polished text are common and hard to separate cleanly.
- Detection quality varies by language, genre, and editing level.

## Practical Implications

### 1. Style is not authorship

A text can look “AI-like” because it is:
- corporate
- academic
- translated
- heavily edited
- written to a strict template

### 2. AI-polished text is its own category

Many modern texts are:
- human draft + AI cleanup
- AI draft + human revision
- human text + paraphraser

Treat this separately from “pure AI-generated”.

### 3. Short text is unreliable

Very short inputs do not provide enough structure for confident judgments.

### 4. Multilingual transfer is fragile

Rules borrowed from English do not map cleanly to Chinese.
Signals like burstiness, connective density, and sentence variety can behave differently by language and genre.

## Recommended Output Discipline

- Give a label, not a verdict.
- Include confidence.
- Include false-positive risk.
- Show the evidence that led to the label.
