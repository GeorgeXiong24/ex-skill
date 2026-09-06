[personality_profile.template.md](https://github.com/user-attachments/files/31876208/personality_profile.template.md)
---
schema_version: "1.0"
profile_type: "personality-speech-analysis"
subject_alias: "<alias>"
subject_role: "ex-partner"
generated_at: "<ISO-8601 timestamp>"
source_files:
  - "<filename>"
primary_language: "<zh-CN | en | mixed | ...>"
confidence: 0.0
status: "complete"
---

# Personality & Speech Profile — <subject_alias>

<!-- Fill every section. Keep heading names and YAML/JSON keys EXACTLY as written.
     Use `null` (or `[]`) for anything that cannot be determined. Do not invent data.
     Label every interpretation as inference; only present text-grounded claims as observed. -->

## 1. Executive Summary
<!-- 3–5 sentences capturing the subject's dominant traits, emotional style, mentality, and speaking voice. -->

## 2. Core Personality Metrics
<!-- One row per dimension. Score is 0.0–1.0; weight is relative importance for simulation. -->
| Dimension | Score | Weight | Evidence |
|-----------|-------|--------|----------|
| agreeableness | 0.0 | 0.0 |  |
| extraversion | 0.0 | 0.0 |  |
| openness | 0.0 | 0.0 |  |
| conscientiousness | 0.0 | 0.0 |  |
| emotional_stability | 0.0 | 0.0 |  |
| humor_playfulness | 0.0 | 0.0 |  |
| sarcasm | 0.0 | 0.0 |  |
| empathy | 0.0 | 0.0 |  |
| formality | 0.0 | 0.0 |  |
| confidence | 0.0 | 0.0 |  |
| humility | 0.0 | 0.0 |  |
| optimism | 0.0 | 0.0 |  |
| competitiveness | 0.0 | 0.0 |  |
| emotional_expressiveness | 0.0 | 0.0 |  |

## 3. Communication Style
### 3.1 Sentence structure
<!-- Length, complexity, fragmentation, question vs statement ratio. -->
### 3.2 Message segmentation
<!-- How one thought is split across messages; bursts vs one-word replies. -->
### 3.3 Vocabulary & register
<!-- Register, code-switching, fillers, intensifiers, honorifics. -->
### 3.4 Address terms & nicknames
<!-- What the subject calls the user, themselves, third parties; changes over time. -->
### 3.5 Slang & colloquialisms
<!-- Internet slang, dialect, abbreviations, playful misspellings. -->
### 3.6 Punctuation, capitalization & formatting
<!-- Ellipses, stacked punctuation, tildes, full/half-width, all-caps, line breaks. -->
### 3.7 Emoji, sticker & audio usage
<!-- Frequency, categories, emotional function; when audio replaces text. -->

### 3.8 Quantitative Communication Metrics (benchmarks)
<!-- Data-backed numbers a downstream imitation skill must enforce. Compute from the subject's own turns. -->
#### 3.8.1 Message length
<!-- mean / median / min / max chars; % ≤8 chars; % ≤12 chars; length histogram (1-4 / 5-8 / 9-12 / 13-16 / 17-20 / 21+). -->
#### 3.8.2 Message frequency
<!-- messages per turn (mean / median); burst-size distribution; % single-message turns. -->
#### 3.8.3 Reply length by input type
| Input type | Expected messages | Expected total chars | Example input → reply |
|-----------|-------------------|----------------------|----------------------|
|  | 1–3 | ≤20 |  |
#### 3.8.4 Tone modulation & cadence
<!-- Per tonal context: intensity, typical message length, emoji/sticker density. Reply latency engaged vs disengaged; affect-marker scaling rules. -->

## 4. Emotional Profile
### 4.1 Emotional range & dominant emotions
### 4.2 Emotional intensity & expressiveness
### 4.3 Emotional triggers
<!-- What provokes joy, anxiety, annoyance, affection. -->
### 4.4 Emotion regulation style
### 4.5 Affection signaling
<!-- How care and interest are expressed. -->
### 4.6 Mood fluctuation & stability
### 4.7 Attachment-style hypothesis
<!-- Inference only, with evidence; never a diagnosis. -->

## 5. Tonal Characteristics by Context
| Context | Dominant tone | Intensity (0–1) | Example |
|---------|---------------|-----------------|---------|
|  |  | 0.0 |  |

## 6. Mentality & Psychology
### 6.1 Worldview & values
### 6.2 Self-perception & self-esteem signals
### 6.3 Motivation & goals
### 6.4 Defense mechanisms & coping
### 6.5 Decision-making style
### 6.6 Relationship attitudes & expectations
### 6.7 Cognitive style

## 7. Thematic Preferences
| Topic | Engagement (initiate / expand / deflect) | Example |
|-------|------------------------------------------|---------|
|  |  |  |

## 8. Response Latency & Engagement Dynamics
<!-- Typical reply speed, burst vs gap behavior, initiation asymmetry, who keeps the conversation alive. -->

## 9. Idioms, Recurring Phrases & Linguistic Quirks
| Phrase / quirk | Type | Weight (0–1) | Example |
|----------------|------|--------------|---------|
|  |  | 0.0 |  |

## 10. Relationship Dynamics & Temporal Evolution
### 10.1 Power balance & reciprocity
### 10.2 Affection asymmetry
### 10.3 Conflict & teasing patterns
### 10.4 Temporal evolution
<!-- How the subject's voice, warmth, and distance changed across the timeline. -->

## 11. Memory Moments & Significant Events
<!-- The relationship's "memory": a chronological reconstruction of what actually happened and the
     subject's detailed emotional experience in each significant moment. Goal: let a downstream AI
     (or the user) recall the story and relive its emotional beats.
     For every event: what happened (observed) → subject's role → observed emotional markers →
     detailed emotion interpretation (inference, with intensity + trajectory + surface-vs-underlying).
     Do not invent events; mark gaps when materials are fragmentary. -->

### 11.1 Event list
| # | Period / timestamp | Event (what happened) | Subject's role | Observed emotional markers | Detailed emotional interpretation (inference) | Intensity (0–1) | Evidence quote |
|---|--------------------|-----------------------|----------------|----------------------------|-----------------------------------------------|-----------------|----------------|
| 1 |  |  |  |  |  | 0.0 |  |

### 11.2 Event-level emotional narrative
<!-- A running, event-by-event account of the subject's emotional journey: how each significant moment
     built on the last, what it reveals about the subject's inner state, and how the relationship changed.
     Separate surface emotion from underlying emotion; label all inference. -->

## 12. Annotated Sample Excerpts
<!-- For each excerpt: quote → observation → what it reveals. -->

## 13. Deep Interpretation & Synthesis
<!-- Reconcile contradictions across sources; infer underlying motives, unmet needs, unspoken emotions.
     Label each item as inference and give evidence + confidence. -->

## 14. Simulation Guidance (for downstream AI)
### 14.1 Do
<!-- Behaviors to reproduce. -->
### 14.2 Avoid
<!-- Behaviors to steer away from. -->
### 14.3 Voice rules
<!-- Concrete instructions for imitating sentence rhythm, word choice, tone, emotional expression. -->

## 15. Machine-Readable Profile (JSON)
```json
{
  "schema_version": "1.0",
  "subject": {
    "alias": "",
    "role": "ex-partner",
    "primary_language": ""
  },
  "confidence": 0.0,
  "status": "complete",
  "personality_metrics": [
    { "dimension": "agreeableness", "score": 0.0, "weight": 0.0, "evidence": "" }
  ],
  "communication_style": {
    "sentence_structure": "",
    "message_segmentation": "",
    "vocabulary_register": "",
    "address_terms": [],
    "code_switching_triggers": [],
    "slang": [],
    "punctuation_capitalization": [],
    "emoji_sticker_audio_usage": ""
  },
  "communication_metrics": {
    "message_length": {
      "mean_chars": 0.0,
      "median_chars": 0,
      "min_chars": 0,
      "max_chars": 0,
      "pct_le_8_chars": 0.0,
      "pct_le_12_chars": 0.0,
      "length_buckets": {}
    },
    "message_frequency": {
      "messages_per_turn_mean": 0.0,
      "messages_per_turn_median": 0,
      "single_message_turn_pct": 0.0,
      "burst_distribution": {}
    },
    "reply_length_by_input_type": [
      {
        "input_type": "",
        "expected_messages_min": 0,
        "expected_messages_max": 0,
        "expected_total_chars_max": 0,
        "example_input": "",
        "example_reply": ""
      }
    ],
    "tone_modulation": [
      { "context": "", "intensity": 0.0, "typical_length_chars": 0, "emoji_density": "" }
    ],
    "cadence": {
      "reply_latency_engaged": "",
      "reply_latency_disengaged": "",
      "laughter_length_scale": "",
      "voice_note_when": ""
    }
  },
  "emotional_profile": {
    "range": "",
    "dominant_emotions": [],
    "intensity": 0.0,
    "expressiveness": 0.0,
    "regulation": "",
    "affection_signaling": "",
    "mood_stability": 0.0,
    "triggers": [],
    "attachment_style_hypothesis": ""
  },
  "tones": [
    { "context": "", "tone": "", "intensity": 0.0, "example": "" }
  ],
  "mentality": {
    "worldview": "",
    "values": [],
    "self_perception": "",
    "motivation": [],
    "defense_mechanisms": [],
    "decision_making": "",
    "relationship_attitudes": "",
    "cognitive_style": ""
  },
  "themes": [
    { "topic": "", "engagement": "", "example": "" }
  ],
  "response_latency": "",
  "linguistic_features": [
    { "phrase": "", "type": "", "weight": 0.0, "example": "" }
  ],
  "relationship_dynamics": {
    "power_balance": "",
    "reciprocity": "",
    "affection_asymmetry": "",
    "conflict_style": "",
    "closeness": ""
  },
  "temporal_evolution": [
    { "period": "", "summary": "", "notable_change": "" }
  ],
  "memory_moments": [
    {
      "period": "",
      "event": "",
      "subject_role": "",
      "observed_markers": "",
      "emotion_interpretation": {
        "emotion": "",
        "intensity": 0.0,
        "trajectory": "",
        "surface_vs_underlying": "",
        "evidence": "",
        "confidence": 0.0
      },
      "relationship_impact": ""
    }
  ],
  "sample_excerpts": [
    { "quote": "", "observation": "", "reveals": "" }
  ],
  "interpretation": [
    { "hypothesis": "", "evidence": "", "confidence": 0.0 }
  ],
  "simulation_guidance": {
    "do": [],
    "avoid": [],
    "voice_rules": []
  },
  "limitations": []
}
```

## 16. Limitations & Disclaimer
<!-- What is uncertain, what data is missing, and a responsible-use reminder. -->
