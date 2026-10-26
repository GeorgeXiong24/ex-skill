# ex-skill

> 语言 / Language：[中文版](README_zh.md)

A self-contained suite of AI skills that analyzes a user's past relationship evidence and produces an
imitation companion that reproduces the ex-partner's personality, tone, and speaking style.

## What it does

The pipeline has three stages:

```
evidence (chat logs, documents, images)
        │
        ▼
personality-analysis-skill  ──►  <subject>_personality_profile.md
        │
        ▼
imitation-skill-generator  ──►  imitation-<alias>/  (a ready-to-use imitation skill)
        │
        ▼
imitation skill  ──►  messages in the subject's voice
```

1. **Analyze** — `personality-analysis-skill` reads uploaded chat logs, documents, and images about an
   ex-partner and produces a single, machine-readable Markdown profile.
2. **Generate** — `imitation-skill-generator` reads that profile and generates a complete, production-ready
   imitation skill.
3. **Imitate** — the generated imitation skill replicates the subject's tone, rhythm, vocabulary, emotional
   style, and memory.

## Skills

| Skill | Purpose | Input | Output |
|-------|---------|-------|--------|
| `personality-analysis-skill` | Deep analysis of a former partner's personality, emotions, mentality, and speech | Chat logs, `.txt`/`.pdf`/`.docx`, images, chat exports | A single `<subject>_personality_profile.md` |
| `imitation-skill-generator` | Turns a personality profile into a working imitation skill | A personality profile `.md` | `imitation-<alias>/` skill directory |

The generator creates `skills/imitation-<alias>/` as a local output when you use it; generated profiles and skills are
not included in this repository.

### personality-analysis-skill

- Parses and normalizes chat transcripts, OCRs images, and extracts document text.
- Separates the subject's voice from the user's voice.
- Scores personality, emotional, mentality, and linguistic dimensions using a bundled rubric.
- Reconstructs significant memory moments and event-level emotions.
- Emits one profile that follows `templates/personality_profile.template.md` exactly, with a
  machine-readable JSON contract.

### imitation-skill-generator

- Validates the input profile schema.
- Extracts identity, top traits, tones, signature phrases, and simulation guidance.
- Fills a bundled template and bundles the profile as the single source of truth.
- Emits a validated, self-contained imitation skill under `skills/`.

## Directory layout

```
ex-skill/
├── skills/                            # bundled skills
│   ├── personality-analysis-skill/
│   ├── imitation-skill-generator/
├── README.md / README_zh.md
└── qq-plugin.md / qq-plugin_zh.md
```

Each registered skill contains a `SKILL.md` (frontmatter + instructions) plus any bundled resources it
needs (`references/`, `templates/`). Skills are self-contained: they carry their own schemas, rubrics, and
templates, and do not require network access, databases, or files outside their own directories as skill resources.
Model inference is handled by the host agent runtime and may use its configured provider. Generated profiles, source
evidence, and `imitation-<alias>/` outputs are user data and are not included in the bundled skill directories.

## How to build / set up

There is no compilation step — these are declarative Markdown skills loaded by the skill framework.

1. Clone this repository.
2. Place each skill directory under `skills/<skill-name>/`.
   Each directory must contain a `SKILL.md` with a valid `name` and `description` frontmatter.
3. Keep the bundled resources co-located with each skill (for example
   `personality-analysis-skill/references/analysis_rubric.md` and
   `personality-analysis-skill/templates/personality_profile.template.md`).
4. Verify the structure: every `SKILL.md` must have `name`, `description` (under 200 characters,
   stating what it does and when to invoke it), and only reference files inside its own directory.

A skill is valid when it matches the `skill-creator` layout:

```
skills/<skill-name>/
├── SKILL.md
└── <bundled resources>
```

## Usage

1. Provide relationship materials (chat logs, documents, images) and invoke `personality-analysis-skill`
   to produce a profile.
2. Provide that profile to `imitation-skill-generator` to produce an `imitation-<alias>` skill.
3. Invoke the generated imitation skill with a conversation prompt to receive messages in the subject's
   voice.

## Privacy & security

- The skills do not include code that publishes or uploads profiles or generated skills. Files are written to the
  workspace, but the AI runtime may send prompts and supplied materials to its configured model provider. Check the
  provider's data-handling terms and your runtime configuration; use an appropriately local model if the materials must
  not leave your device.
- Source evidence and any profile containing real names or chat quotes are private and should not be committed
  to a public repository.
- The generic skills (`personality-analysis-skill`, `imitation-skill-generator`) contain no personal data
  and are safe to share.
- Use the imitation skills responsibly and only with consent; treat psychological findings as hypotheses,
  not diagnoses.

## Validation

The bundled skill directories include a `TEST_REPORT.md` documenting structural checks, schema validity,
self-containment, and privacy checks. Re-run these checks after modifying a bundled skill to confirm it
still loads and runs standalone.

## QQ integration guide

For the complete workflow to connect a generated imitation skill to QQ with SnowLuma, qq-bridge, and DeepSeek
Harness, see the [QQ plugin integration guide](qq-plugin.md).
