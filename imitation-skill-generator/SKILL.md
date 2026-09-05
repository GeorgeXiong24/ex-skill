[SKILL.md](https://github.com/user-attachments/files/31866491/SKILL.md)---
name: "imitation-skill-generator"
description: "Generates a production-ready imitation-skill from a personality-analysis-skill .md profile. Invoke when the user has a personality profile and wants to create an imitation skill."
---

# Imitation Skill Generator

Generate a complete, production-ready `imitation-skill` from the Markdown profile produced by
`personality-analysis-skill`. The generated skill faithfully replicates one subject's personality, tone,
and speaking style for downstream AI simulation.

## 0. Self-Contained Operation & Initialization

This skill is fully self-contained and has no external preconditions. It runs from its own directory
(`imitation-skill-generator/`) and never depends on files, scripts, services, a database, an
authentication layer, network access, or a specific working directory outside that directory.

### 0.1 Bundled resources (internal, not external)

- `templates/imitation-skill.template.md` — the canonical template for the generated imitation skill.

### 0.2 Initialization (pre-flight)

Run this before reading any input:

1. Resolve the skill root as the directory containing this `SKILL.md`. Do **not** assume the invocation working directory.
2. Confirm `templates/imitation-skill.template.md` exists and load it.
3. If the template is missing, do **not** abort: use the inline template in Appendix A of this file.
4. Confirm the input profile schema is known (from Appendix B).
5. Confirm the output skill name convention and validation checklist (Section 5 and Section 7).

No network, database, credential, or pre-existing skill is required. The only input is the profile file
the user provides; everything else needed to generate the imitation skill ships with this skill.

### 0.3 Privacy & local-only constraint

This skill operates entirely locally. It must never upload, publish, push, or otherwise transmit the
subject's profile or the generated imitation skill to any public repository, platform, or remote service.
Generated files are written only to the local filesystem under `.trae/skills/`.

## 1. Purpose & Scope

- Accept one personality profile `.md` produced by `personality-analysis-skill`.
- Extract the subject's identity, linguistic features, tones, emotional profile, and simulation guidance.
- Generate a complete, production-ready imitation skill directory:
  - `SKILL.md` — the imitation instructions (filled from the profile).
  - `references/<alias>_personality_profile.md` — the profile bundled as the single source of truth.
- Validate the generated skill against the framework and privacy rules.

## 2. Input Contract (personality profile)

The input is a single `.md` profile conforming to the `personality-analysis-skill` output schema. If a
required section or key is missing, do not fail silently: record it and degrade gracefully (fill what is
available, mark the rest as gaps).

### 2.1 Required YAML frontmatter keys

`schema_version`, `profile_type`, `subject_alias`, `subject_role`, `generated_at`, `source_files`,
`primary_language`, `confidence`, `status`.

### 2.2 Required markdown sections

1 Executive Summary · 2 Core Personality Metrics · 3 Communication Style · 4 Emotional Profile ·
5 Tonal Characteristics by Context · 6 Mentality & Psychology · 7 Thematic Preferences ·
8 Response Latency & Engagement Dynamics · 9 Idioms, Recurring Phrases & Linguistic Quirks ·
10 Relationship Dynamics & Temporal Evolution · 11 Memory Moments & Significant Events ·
12 Annotated Sample Excerpts · 13 Deep Interpretation & Synthesis · 14 Simulation Guidance ·
15 Machine-Readable Profile (JSON) · 16 Limitations & Disclaimer.

### 2.3 Required top-level JSON keys

`subject`, `confidence`, `status`, `personality_metrics`, `communication_style`, `emotional_profile`,
`tones`, `mentality`, `themes`, `response_latency`, `linguistic_features`, `relationship_dynamics`,
`temporal_evolution`, `memory_moments`, `sample_excerpts`, `interpretation`, `simulation_guidance`,
`limitations`.

## 3. Generation Workflow

1. **Validate the input** against Section 2; note any missing sections/keys.
2. **Extract identity** from frontmatter and `subject`: alias, role, primary language, profile filename.
3. **Extract the subject snapshot** (Section 4.1) from the profile's JSON and prose.
4. **Load the template** from `templates/imitation-skill.template.md` (or Appendix A fallback).
5. **Fill the template variables** using the mapping in Section 4.2.
6. **Bundle the profile** as `references/<alias>_personality_profile.md` in the generated skill directory.
7. **Write the generated skill** to `.trae/skills/<skill-name>/` with `SKILL.md` and the bundled reference.
8. **Validate** the generated skill using the checklist in Section 7; fix any failures.

## 4. Template Variables

### 4.1 Subject snapshot content

The `{{SUBJECT_SNAPSHOT}}` block summarizes, from the profile:

- Subject alias, role, and primary language.
- Top personality metrics (highest `weight` dimensions and scores).
- Dominant tones by context (`tones`).
- Top recurring phrases (`linguistic_features`, highest weights).
- `simulation_guidance.do`, `simulation_guidance.avoid`, and `simulation_guidance.voice_rules`.

Every line in the snapshot must be traceable to the profile; do not invent details.

### 4.2 Variable mapping

| Variable | Source |
|----------|--------|
| `{{SKILL_NAME}}` | `imitation-<alias>` (lowercased, hyphenated) |
| `{{DESCRIPTION}}` | "<Does what> for <alias>. Invoke when the user wants to roleplay as, imitate, or generate messages as <alias>." (keep under 200 chars) |
| `{{TITLE}}` | "Imitation Skill — <alias>" |
| `{{SUBJECT_ALIAS}}` | `subject_alias` |
| `{{PROFILE_FILE}}` | `<alias>_personality_profile.md` |
| `{{SUBJECT_SNAPSHOT}}` | Section 4.1 |

## 5. Output Contract

Generated skill directory:

```
.trae/skills/<skill-name>/
├── SKILL.md
└── references/
    └── <alias>_personality_profile.md
```

The generated `SKILL.md` must have valid frontmatter (`name`, `description` under 200 chars with "what"
and "when") and reference only the bundled profile. No absolute paths and no references outside the
generated skill directory.

## 6. Privacy & Guardrails

- Operate entirely locally; never upload, publish, push, or transmit the profile or generated skill.
- Redact real names, phone numbers, and addresses unless the user explicitly says otherwise.
- Remind the user to use the generated imitation skill responsibly and with consent.
- Do not fabricate traits, quotes, or memories; mark all inference as such.
- Never generate a skill that would expose the private source to a public repository.

## 7. Validation Checklist (generated skill)

- [ ] Directory exists at `.trae/skills/<skill-name>/`.
- [ ] `SKILL.md` has valid `name` and `description` (what + when, under 200 chars).
- [ ] `references/<alias>_personality_profile.md` is bundled and non-empty.
- [ ] `SKILL.md` references only `references/<alias>_personality_profile.md`.
- [ ] No absolute paths, network URLs, or external-file references in the generated skill.
- [ ] The generated skill is self-contained (all resources co-located).

## Appendix A — Inline Fallback Template

Use only if `templates/imitation-skill.template.md` is unavailable. A minimal generated `SKILL.md` must include:

```markdown
---
name: "<skill-name>"
description: "<what it does + when to invoke, under 200 chars>"
---

# Imitation Skill — <subject alias>

Faithfully reproduce <subject alias>'s personality, tone, and speaking style using
`references/<alias>_personality_profile.md` as the single source of truth.

## 1. Purpose & Scope
- Load the profile and treat it as authoritative.
- Never invent traits or memories beyond the profile.

## 2. Replication Rules
- Match tones from the profile's `tones`.
- Mirror sentence structure, segmentation, vocabulary, and emoji habits from `communication_style`.
- Use exact recurring phrases and weights from `linguistic_features`.
- Follow `simulation_guidance.do`, `.avoid`, and `.voice_rules`.

## 3. Workflow
1. Load the profile.
2. Determine context.
3. Select tone.
4. Compose following the rules above.
5. Validate against the profile and return only faithful output.

## 4. Guardrails
- Authorized simulation only; do not impersonate without consent.
- Do not diagnose; keep hypotheses as hypotheses.
- Preserve privacy; redact sensitive identifiers.
```

## Appendix B — Inline Profile Schema Fallback

Use only when the input profile's schema is unclear. The required sections and JSON keys are listed in
Section 2 above; treat any of the following as the minimal extraction targets:

- Identity: `subject_alias`, `subject_role`, `primary_language`.
- Voice: `linguistic_features`, `communication_style`, `tones`.
- Psychology: `personality_metrics`, `emotional_profile`, `mentality`.
- Simulation rules: `simulation_guidance`, `memory_moments`, `sample_excerpts`.
