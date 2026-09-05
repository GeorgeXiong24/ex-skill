---
name: "personality-analysis-skill"
description: "Builds a machine-readable profile of an ex-partner's personality, emotions, and speaking style from uploaded chat logs, documents, and images. Invoke when the user uploads relationship materials."
---

# Personality & Speech Pattern Analysis

Analyze a user's former romantic partner ("the subject") from any uploaded materials and produce a
single, standardized, machine-readable Markdown profile that a downstream AI can use to faithfully
replicate the subject's personality, emotions, mentality, tone, and way of speaking.

This is a **deep** analysis: go beyond surface description to interpret *why* the subject speaks and
behaves the way they do, and reconstruct an inner model — not just a list of surface traits.

## 0. Self-Contained Operation & Initialization

This skill is fully self-contained and has no external preconditions. It runs from its own directory
(`personality-analysis-skill/`) and never depends on files, scripts, services, a database, an
authentication layer, or a specific working directory outside that directory.

### 0.1 Bundled resources (internal, not external)

All required resources are co-located in this skill directory:

- `references/analysis_rubric.md` — scoring anchors for every personality, emotional, mentality, and linguistic dimension.
- `templates/personality_profile.template.md` — the canonical output schema (headings, YAML frontmatter, and JSON contract).

### 0.2 Initialization (pre-flight)

Run this initialization before reading any input:

1. Resolve the skill root as the directory containing this `SKILL.md`. Do **not** assume the invocation working directory.
2. Confirm `references/analysis_rubric.md` exists and load it.
3. Confirm `templates/personality_profile.template.md` exists and load it.
4. If either file is missing, do **not** abort: fall back to the inline schema and rubric in Appendix A and Appendix B of this file, then continue.
5. Confirm the required output sections and JSON keys are known (from the loaded template or Appendix A).
6. Detect available input-processing capabilities. Plain text is always supported; OCR (for images) and text extraction (for PDF/DOCX) are used when available. If a capability is unavailable, degrade gracefully per Section 6 instead of failing.

No network, database, credential, or pre-existing profile is required. The only inputs are the files the
user provides at invocation time; everything else needed to produce the profile ships with this skill.

## 1. Purpose & Scope

- Reconstruct a granular, evidence-backed model of the subject's communication style, emotional life, mentality, and core personality.
- Always separate the **subject's** voice from the **user's** voice; analyze the subject's own turns, not the user's.
- Synthesize *every* uploaded file into one coherent model; resolve contradictions rather than ignoring them.
- Produce ONE profile file that follows the exact schema in `templates/personality_profile.template.md`.

## 2. Supported Input Types

Accept and analyze any combination of the following:

| Category | Extensions / forms |
|----------|--------------------|
| Plain text | `.txt`, `.md`, `.log`, pasted raw text |
| Documents | `.pdf`, `.docx`, `.doc`, `.rtf` |
| Images | `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.gif`, `.bmp` |
| Raw chat transcripts | WeChat / QQ / WhatsApp / Telegram / iMessage exports, with or without inline attachment markers |

Images may contain chat screenshots (OCR them) or visual context (scene, objects, mood). A single
upload may mix several types; a single file may also mix text with inline attachment markers.

## 3. Input Parsing Rules

### 3.1 Identify speakers
- Resolve every message to exactly one speaker: the **user** or the **subject**.
- Infer roles from sender names, the uploader's stated identity, or explicit descriptions.
- If the subject's identity is ambiguous, ask the user to confirm which side is the subject before analyzing.

### 3.2 Chat transcript structure
Recognize and normalize common export formats:
- Date/time headers, e.g. `————— 2024-11-24 —————`.
- `SenderName  HH:MM` followed by the message body on the next line(s).
- Consecutive messages from the same sender count as separate turns.
- Preserve original timestamps for latency analysis.

### 3.3 Inline attachments
Do not discard attachments. Normalize them to placeholders and interpret their meaning:
- `[Image]`, `[Image1]`, `[Photo]` → visual content; if a matching real image is also provided, link it.
- `[Audio] N"` / `[Voice]` → voice message of N seconds; note frequency and implied tone.
- `[Sticker]`, `[Emoji]` → emotional punctuation; count and categorize.
- `[Channel]`, `[Video]`, `[File]`, `[Location]`, `[Link]` → topic / context signals.
- WeChat emoji-bracket markers (`[Smug]`, `[Happy]`, `[Sob]`, `[Grimace]`, `[ThumbsUp]`, …) → treat as emotional markers with intensity.

### 3.4 Multilingual content
- Handle mixed-language text (e.g. Chinese + English) without forcing one language.
- Preserve original phrasing in excerpts; add translations only when genuinely helpful.

## 4. Deep Analysis Methodology

Run **every** layer below, then synthesize them (Section 4.10). Every claim must be backed by at
least one concrete excerpt or a pattern statistic. Distinguish clearly between **observed fact** and
**interpretation / inference**.

### 4.1 Communication patterns (linguistic fingerprint)
- **Sentence structure**: length distribution, complexity, fragmentation, run-ons, question-vs-statement ratio.
- **Message segmentation**: how one thought is split across messages, multi-message bursts, one-word replies.
- **Vocabulary & register**: casual/formal, code-switching, filler words, intensifiers, pet names, honorifics.
- **Address terms & nicknames**: what the subject calls the user, themselves, and third parties; changes over time.
- **Code-switching triggers**: when/why the subject switches language (e.g. jokes, emphasis, affection, borrowed phrases).
- **Slang & colloquialisms**: internet slang, dialectal markers, abbreviations, playful misspellings (e.g. "米有" for "没有").
- **Punctuation habits**: ellipses, stacked exclamation marks, question marks, wave dashes, tilde (`～`), full-width vs half-width.
- **Capitalization & formatting**: all-caps, spacing, line breaks, emoji placement.
- **Emoji / sticker / audio usage**: frequency, categories, emotional function, when audio replaces text.

### 4.2 Emotional profile
- **Emotional range & dominant emotions**: which feelings recur (joy, anxiety, affection, frustration, boredom, pride).
- **Emotional intensity & expressiveness**: how strongly feelings come through (exclamations, stacked emoji, dramatic phrasing).
- **Emotional triggers**: what provokes joy, anxiety, annoyance, or affection (topics, people, situations).
- **Emotion regulation style**: how the subject manages strong feelings (laugh it off, deflect, reassure, withdraw, spiral).
- **Affection signaling**: how care and interest are expressed (praise, reassurance, teasing, check-ins, emoji).
- **Mood fluctuation & stability**: consistency of tone across time and contexts.
- **Attachment-style cues**: infer (as a hypothesis, never a diagnosis) whether patterns look secure, anxious, avoidant, or disorganized.

### 4.3 Tonal characteristics
Classify tone across different contexts (playful, reserved, sarcastic, empathetic, formal, teasing,
encouraging, deflective, dismissive). Score each and note the context where it appears.

### 4.4 Core personality traits
Infer traits from behavioral patterns, decision-making descriptions, and interaction style. Use the
scoring rubric in `references/analysis_rubric.md`. Report a confidence-weighted score (0.0–1.0) per dimension.

### 4.5 Mentality & psychology
- **Worldview & values**: what the subject cares about, prioritizes, and dismisses.
- **Self-perception & self-esteem signals**: confidence vs self-deprecation, how praise/criticism is handled.
- **Motivation & goals**: academic, personal, and social drives revealed in conversation.
- **Defense mechanisms & coping**: humor-as-deflection, self-deprecation, avoidance, rationalization, problem-solving.
- **Decision-making style**: impulsive vs deliberate, seeks input vs self-reliant.
- **Relationship attitudes & expectations**: how the subject views the bond, boundaries, and reciprocity.
- **Cognitive style**: literal vs abstract, detail-oriented vs big-picture, reflective vs reactive.

### 4.6 Thematic preferences
Extract recurring topics (school/studies, sports, hobbies, mutual friends, food, media), and how the
subject engages with each (initiates, expands, deflects, jokes).

### 4.7 Response latency & engagement dynamics
From timestamps, estimate typical reply speed, burst-vs-gap behavior, and what latency implies about
interest or mood. Note **asymmetry**: who initiates, who keeps the conversation alive, who ends it.

### 4.8 Idioms, recurring phrases & linguistic quirks
Collect exact recurring phrases, catchphrases, emotive exclamations, and unique spellings. Attach a
frequency/weight (0.0–1.0) and a representative example to each.

### 4.9 Relationship dynamics & temporal evolution
- **Power balance & reciprocity**: who leads, who accommodates, who concedes.
- **Affection asymmetry**: differences in warmth, initiation, and investment.
- **Conflict & teasing patterns**: how disagreements or jabs are handled.
- **Temporal evolution**: how the subject's voice, warmth, and distance change across the relationship timeline (milestones, drifting apart, reunions).

### 4.10 Cross-source synthesis & deep interpretation
After the layers above, merge everything into one coherent model:
- Combine chat transcripts, descriptions, profiles, and image context; weigh direct evidence over second-hand claims.
- **Resolve contradictions** explicitly (e.g. a profile claims "high-cold" but chats show warmth — reconcile, don't ignore).
- Infer **underlying motives, unmet needs, and unspoken emotions**; label every such inference as a hypothesis with its supporting evidence and a confidence level.
- Identify what the materials *do not* show, and note it as a gap rather than filling it with guesses.

### 4.11 Significant memory moments & event-level emotion interpretation
Capture the relationship's key moments so the profile can reconstruct **what actually happened** and the
subject's **detailed emotional experience inside each event** — not just aggregate traits. This is the
profile's "memory": it lets a downstream AI (or the user) recall the story and relive its emotional beats.

- **Identify significant events**: scan every material for moments with narrative weight — first meeting, confession, argument, apology, celebration, separation, reunion, milestones, inside jokes, gifts, plans made, promises kept or broken. Flag any moment where emotion spikes or the relationship state changes.
- **Record "what happened"**: for each moment, give a short factual account grounded only in the materials (who, what, when, where, outcome). Never invent details.
- **Capture the subject's role**: what the subject said, did, initiated, avoided, or failed to do in that moment.
- **Extract observed emotional markers**: the concrete words, emoji, punctuation, latency, or attachment signals that reveal the subject's state at that instant (e.g. stacked exclamation marks, a sudden switch to one-word replies, an unexpected voice note).
- **Reconstruct detailed emotions**: interpret the subject's likely feelings in that moment at a granular level — name the *specific* emotion(s), their *intensity*, and their *trajectory* (build-up → peak → aftermath). Separate **surface emotion** from **underlying emotion** (e.g. laughing it off may mask hurt or embarrassment). Label every interpretation as inference with evidence and a confidence level.
- **Link moments to the timeline**: place each moment chronologically and note how it changed the subject's subsequent voice, warmth, distance, or expectations (tie back to Section 4.9).
- **Preserve the subject's perspective**: reconstruct how the subject likely experienced the event from *their* side, not just the user's account. Note when the material only shows one side.
- **Do not force a narrative**: if materials are fragmentary, record only the moments that exist and mark gaps explicitly rather than inventing a story.

## 5. Output Requirements

- Write the profile to a single `.md` file that follows `templates/personality_profile.template.md` exactly.
- Keep section headings and YAML/JSON keys stable so downstream systems can parse them.
- Every weighted metric must be numeric; every trait must carry a score and evidence.
- Include annotated sample excerpts in the form: quote → observation → what it reveals.
- Include a dedicated **Deep Interpretation & Synthesis** section and an **Emotional Profile** section.
- Include a dedicated **Memory Moments & Significant Events** section that reconstructs what happened and the subject's detailed, event-level emotions.

## 6. Error Handling

Apply these rules before and during analysis:

- **Unsupported file type**: do not fail. List the file, mark it `status: unsupported`, and continue with the remaining materials.
- **Corrupted / unreadable upload**: attempt recovery (re-OCR, text-layer extraction). If unrecoverable, mark `status: unreadable`, exclude it, and note the reason.
- **Insufficient data**: if the subject has too few substantive turns (fewer than ~10) or only one-sided material, lower the overall `confidence`, set undeterminable dimensions to `null`, and state what additional data would improve the profile.
- **Ambiguous subject identity**: stop and ask for clarification rather than guessing.
- **No usable content at all**: emit a minimal profile with `status: failed` and an actionable explanation.

## 7. Workflow

1. Inventory and classify every uploaded file.
2. Parse and normalize text; OCR images; extract document text.
3. Separate subject turns from user turns.
4. Apply **all** analysis layers (Section 4.1–4.9), citing evidence.
5. Score personality and emotional dimensions using the rubric.
6. Extract significant memory moments and reconstruct event-level emotions (Section 4.11).
7. Synthesize across sources and produce the deep interpretation layer (Section 4.10).
8. Render the profile from the template, filling every section.
9. Self-check: every claim has evidence; inference is labeled; every required key is present; every significant moment is captured; `confidence` is honest.

## 8. Guardrails

- Be neutral and non-judgmental; do not pathologize or diagnose (attachment style and motives are hypotheses, not facts).
- Do not fabricate messages, traits, or feelings unsupported by the material; mark all inference explicitly.
- Preserve privacy: redact real names, phone numbers, and addresses unless the user says otherwise.
- If the profile will be used to imitate a real person, remind the user to use it responsibly and consensually.

## 9. References (all bundled in this skill directory)

- Output schema: `templates/personality_profile.template.md`
- Scoring rubric: `references/analysis_rubric.md`
- Fallback schema and rubric: Appendix A and Appendix B of this file (use only if the bundled files above are unavailable)

All paths are relative to the directory containing this `SKILL.md`. This skill has no external file,
service, or configuration dependencies.

## Appendix A — Minimal Output Schema (fallback)

Use this only if `templates/personality_profile.template.md` is unavailable. The section headings and the
JSON contract must remain stable so downstream systems can parse the profile.

### A.1 Required YAML frontmatter keys

`schema_version`, `profile_type`, `subject_alias`, `subject_role`, `generated_at`, `source_files`,
`primary_language`, `confidence`, `status`.

### A.2 Required markdown sections (headings must match)

1 Executive Summary · 2 Core Personality Metrics · 3 Communication Style · 4 Emotional Profile ·
5 Tonal Characteristics by Context · 6 Mentality & Psychology · 7 Thematic Preferences ·
8 Response Latency & Engagement Dynamics · 9 Idioms, Recurring Phrases & Linguistic Quirks ·
10 Relationship Dynamics & Temporal Evolution · 11 Memory Moments & Significant Events ·
12 Annotated Sample Excerpts · 13 Deep Interpretation & Synthesis · 14 Simulation Guidance ·
15 Machine-Readable Profile (JSON) · 16 Limitations & Disclaimer.

### A.3 Required top-level JSON keys

`subject`, `confidence`, `status`, `personality_metrics`, `communication_style`, `emotional_profile`,
`tones`, `mentality`, `themes`, `response_latency`, `linguistic_features`, `relationship_dynamics`,
`temporal_evolution`, `memory_moments`, `sample_excerpts`, `interpretation`, `simulation_guidance`,
`limitations`.

## Appendix B — Minimal Scoring Rubric (fallback)

Use this only if `references/analysis_rubric.md` is unavailable.

- Score every dimension 0.0–1.0 based on the subject's own turns only; use `null` when undeterminable.
- Every score must carry at least one concrete excerpt or pattern statistic.
- Label every interpretation as inference; separate observed from inferred.

### B.1 Personality dimensions

`agreeableness`, `extraversion`, `openness`, `conscientiousness`, `emotional_stability`,
`humor_playfulness`, `sarcasm`, `empathy`, `formality`, `confidence`, `humility`, `optimism`,
`competitiveness`, `emotional_expressiveness`.

### B.2 Emotional dimensions

`emotional_range`, `emotional_intensity`, `emotional_regulation`, `affection_signaling`,
`mood_stability`, `attachment_style_hypothesis` (always a hypothesis, never a diagnosis).

### B.3 Mentality & psychology

`self_perception`/self-esteem, `defensiveness`, `coping_style`, `decision_making`, `cognitive_style`,
`relationship_attitudes`.

### B.4 Linguistic feature weights

- 0.9–1.0: signature markers; 0.6–0.8: frequent and distinctive; 0.3–0.5: occasional but characteristic; 0.1–0.2: rare.
