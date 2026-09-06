[analysis_rubric.md](https://github.com/user-attachments/files/31876194/analysis_rubric.md)
# Analysis Rubric

Scoring guide for producing consistent, evidence-backed personality, emotional, and psychological metrics and linguistic weights.

## How to score

- Each dimension is scored 0.0–1.0, representing how strongly the trait is present in the **subject's own messages**.
- Base every score on the subject's turns only, never the user's.
- Use `null` when the trait cannot be determined from the available data.
- `weight` = how much this dimension should influence a downstream simulation (0.0–1.0). A high weight means the trait is central to replicating the voice.
- Always pair a score with at least one concrete excerpt or pattern statistic.
- **Label every interpretation as inference**: separate "observed" (directly in the text) from "inferred" (your interpretation).

## Personality dimension anchors

### agreeableness
Warmth, cooperation, encouragement, willingness to accommodate.
- 0.9+: consistently warm, supportive, compromising ("没事的没事的", "加油加油👏🏻").
- 0.5: polite but selective.
- 0.1: cold, dismissive, combative.

### extraversion
Social energy, talkativeness, initiating contact, expressive volume.
- High: initiates topics, long bursts, many messages, invites contact.
- Low: terse replies, waits to be contacted, minimal elaboration.

### openness
Curiosity, playfulness with ideas, receptiveness to new topics, imaginative language.
- High: explores jokes, hypotheticals, varied topics.
- Low: sticks to routine, literal, narrow topics.

### conscientiousness
Care, follow-through, attention to commitments (e.g. remembering to return something, planning ahead).
- High: follows up, keeps promises, organized plans.
- Low: forgetful, casual about commitments.

### emotional_stability
Calm vs reactive; how easily the subject gets flustered, anxious, or defensive.
- High: even-tempered, reassuring.
- Low: frequent panic, strong self-criticism, dramatic reactions.

### humor_playfulness
Joke frequency, teasing, exaggeration, laugh reactions ("哈哈哈哈", teasing nicknames).
### sarcasm
Ironic or mocking tone distinct from playful teasing; can be affectionate or sharp.
### empathy
Noticing and responding to the other's feelings ("别紧张", "放平心态就好了 相信自己").
### formality
Register from casual/slang to structured/polite.
### confidence
Self-assurance vs self-deprecation ("我很菜的[Sob]" = low in-context, possibly false modesty).
### humility
Acknowledging limits, deflecting praise, self-deprecation.
### optimism
Positive outlook, reassurance, focus on good outcomes ("心态好一点就行").
### competitiveness
Comparison, self-positioning against others, achievement framing.
### emotional_expressiveness
Frequency and intensity of emotional markers (emoji, exclamations, affection).

## Emotional dimension anchors

### emotional_range
Variety of distinct emotions expressed across the material.
- High: joy, anxiety, affection, frustration, teasing, boredom all appear in different contexts.
- Low: flat, single-note, limited affective vocabulary.

### emotional_intensity
How strongly feelings come through.
- High: stacked exclamations, repeated emoji, dramatic or hyperbolic phrasing.
- Low: muted, understated, rarely uses affect markers.

### emotional_regulation
How the subject manages strong feelings.
- High: reframes positively, laughs it off, reassures self/others, stays even.
- Low: spirals, panics, over-apologizes, withdraws, or lashes out.

### affection_signaling
How care and interest are expressed.
- High: praise, reassurance, check-ins, pet names, warm emoji.
- Low: minimal warmth, transactional, detached.

### mood_stability
Consistency of tone across time and contexts.
- High: steady baseline even under stress or teasing.
- Low: rapid shifts between warm and distant, playful and flat.

### attachment_style_hypothesis
Infer (as a hypothesis, never a diagnosis) whether interaction patterns look:
- **secure**: comfortable with closeness and independence, steady reciprocity.
- **anxious**: seeks reassurance, sensitive to delayed replies, fear of disconnection.
- **avoidant**: deflects intimacy, minimizes emotional topics, values space.
- **disorganized**: inconsistent, alternating warmth and withdrawal.
Always cite specific evidence and label this "hypothesis".

## Mentality & psychology anchors

### self_perception / self-esteem
- High: asserts strengths, accepts praise, self-affirming.
- Low: self-deprecation, deflects praise ("没有啊", "我很菜的"), downplays achievement.

### defensiveness
How quickly the subject justifies or protects themselves when questioned or teased.
- High: explains, counters, gets flustered.
- Low: lets it pass, laughs along.

### coping_style
Dominant strategy when stressed or challenged:
- **humor**: jokes to diffuse tension.
- **rationalization**: reframes the situation logically.
- **avoidance**: changes topic, withdraws, goes silent.
- **problem-solving**: makes a plan, seeks facts.
- **support-seeking**: reaches out for comfort.

### decision_making
- **deliberate**: weighs options, asks for input, plans.
- **impulsive**: decides quickly, acts on whim.
- **delegating**: relies on others to choose ("都行", "听你咯").

### cognitive_style
- **literal vs abstract**: concrete statements vs metaphors and hypotheticals.
- **detail vs big-picture**: specifics vs broad framing.
- **reflective vs reactive**: measured replies vs immediate, emotive bursts.

### relationship_attitudes
How the subject frames the bond: casual, serious, guarded, invested, ambivalent.
- Cite how they talk about "us", commitment, boundaries, and the future.

## Linguistic feature weighting

For recurring phrases and quirks:
- `weight` 0.9–1.0: signature, near-constant markers (e.g. a distinctive greeting or laugh pattern).
- `weight` 0.6–0.8: frequent and distinctive.
- `weight` 0.3–0.5: occasional but characteristic.
- `weight` 0.1–0.2: rare but noteworthy.

## Tonal intensity

- 0.0–1.0 reflecting how strongly a tone dominates in a given context.
- Always cite the context (e.g. "when teased about grades", "when comforting").

## Confidence (overall)

- 0.8+: rich, two-sided, multi-context material.
- 0.5–0.8: moderate volume or one-sided gaps.
- <0.5: sparse data; expect many `null` fields.

## Interpretation confidence (for hypotheses)

- 0.8+: multiple independent pieces of evidence point the same way.
- 0.5–0.8: a clear pattern but alternative explanations remain.
- <0.5: speculative; present cautiously and only if clearly marked.

## Event-level emotion interpretation

When reconstructing how the subject felt during a significant moment, capture emotion at a granular
level rather than as a broad label:

- **Name the specific emotion(s)**: go beyond "happy / sad" to precise states (relief, disappointment,
  embarrassment, guarded hope, resentment, longing, pride, hurt masked by humor, relief-after-anxiety).
- **Intensity (0.0–1.0)**: how strongly the emotion shows in that moment — stacked exclamations, emoji
  repetition, unusual latency, message length, or a sudden switch to one-word replies.
- **Trajectory**: build-up → peak → aftermath. Note how the feeling enters, crests, and resolves or lingers.
- **Surface vs underlying emotion**: what the subject *displays* vs what they *likely feel* (e.g. laughing
  it off may mask hurt; "I'm fine" may mask withdrawal).
- **Evidence & confidence**: every emotion label needs a concrete quote/marker and a confidence level
  (use the interpretation-confidence scale above).

### Moment significance criteria

Flag a moment as "significant" (and add it to the memory moments list) when any of these hold:

- **Relationship state changes**: confession, argument, apology, breakup, reunion, milestone.
- **Emotional spike**: unusual intensity, a sudden tone shift, or unusual latency / message length.
- **Callback**: the subject references it again later (inside jokes, lingering grievances, repeated memories).
- **Residual effect**: it changes the subject's subsequent voice, warmth, distance, or expectations.

## Quantitative communication metrics anchors

Compute these from the subject's own substantive text messages only. Exclude `[Audio]`, `[Sticker]`, and
pure-emoji markers from length averages (but count them when measuring message frequency).

### Message length
- Count characters (CJK, Latin, digits, and emoji each count as one glyph).
- Report mean, median, min, max, and the % of messages ≤8 chars and ≤12 chars.
- Interpret: median ≤8 chars and ≥60% ≤8 chars → **terse / fragmentary**; median 9–15 → **moderate**;
  median >15 → **verbose / long-form**.

### Message frequency & cadence
- Messages per turn = how many messages the subject sends before the other side replies.
- Burst-size distribution: count the frequency of 1-, 2-, 3-, … message bursts.
- Single-message-turn % = share of turns that contain exactly one message.
- Cadence: reply latency when engaged vs disengaged; note any affect-marker scaling rule (e.g. laughter
  length, emoji stacking) that encodes intensity without adding words.

### Reply length by input type
Always express as a **message-count range** plus a **total-character range**, and back each row with one
concrete input → reply pair. Example anchoring (adjust to the actual subject):

| Input type | Expected messages | Expected total chars |
|-----------|-------------------|----------------------|
| greeting / check-in | 1–2 | ≤12 |
| direct question | 1–3 | ≤20 |
| statement / tease | 1–2 | ≤8 |
| comfort request | 1–2 | ≤12 |
| logistics / scheduling | 1–3 | ≤20 |
| serious / planning | 1 | 15–40 |

A reply that exceeds the subject's recorded upper bound for that input type is an over-length failure the
imitation skill must reject.

