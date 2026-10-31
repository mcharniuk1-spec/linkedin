# Outspoken launch film: voiceover sheet

Generated from `src/script.json` by `npm run vo`. Language: English. Status of all wording: **proposed** (owner and founders approve; the line "Every trade-off, a scar" in particular needs approval).

- Film length: **79.90 s** (2397 frames at 30 fps), 152 spoken words, 24 lines in 9 scenes.
- Planned reading pace: **2.4 words per second (about 144 wpm)** for the speech itself; the pauses are written into the timing below.
- Speech time at that pace: 63.33 s of 79.90 s. The rest is designed pauses, impacts and visual-only beats.
- Delivery: calm, close to the microphone, a little dangerous. The picture and sound do the shouting; the voice never does.

## How to record
1. Read each line as its own take with 0.5 s of room tone before and after. One file per line is easiest: `S1-L1.wav`, `S1-L2.wav`, and so on.
2. Record 48 kHz, 24-bit, mono, no processing. Leave levels low enough that nothing clips.
3. Do not rush to fill the pauses. A silence is part of the line (see the pause column).
4. Send the takes back. The film is retimed per line from the real words (the Whisper model on this project can give word timestamps); the picture beats are built to move by about plus or minus 0.3 s without breaking.

## Timing table (global time, seconds)

| Scene | Line | Start | End (planned) | Words | Seconds | Pause after |
|---|---|---:|---:|---:|---:|---:|
| S1 The Charge | Let's talk about you. | 1.80 | 3.47 | 4 | 1.67 | 0.50 |
| S1 The Charge | The brilliant one. The quiet one. | 3.97 | 6.47 | 6 | 2.50 | 0.50 |
| S1 The Charge | The one the right buyers still haven't heard of. | 6.97 | 10.72 | 9 | 3.75 | - |
| S2 Exhibit A | Exhibit A. | 11.42 | 12.25 | 2 | 0.83 | 0.50 |
| S2 Exhibit A | Every decision, a trade-off. Every trade-off, a scar. | 12.75 | 16.08 | 8 | 3.33 | 0.50 |
| S2 Exhibit A | All of it. In your head. | 16.58 | 19.08 | 6 | 2.50 | - |
| S3 The Silence | And out here? | 19.78 | 21.03 | 3 | 1.25 | 1.00 |
| S3 The Silence | One word. Founder. | 22.03 | 23.28 | 3 | 1.25 | 1.00 |
| S3 The Silence | Nothing else. | 24.28 | 25.12 | 2 | 0.83 | - |
| S4 Ignition | We take what's in your head: the decisions, the trade-offs, the product. | 25.82 | 30.82 | 12 | 5.00 | 0.50 |
| S4 Ignition | Then we make it public. In your voice. | 31.32 | 34.65 | 8 | 3.33 | - |
| S5 The Spread | Then it can travel. | 35.35 | 37.02 | 4 | 1.67 | 0.30 |
| S5 The Spread | From you, to your team, to buyers, to partners. | 37.32 | 41.07 | 9 | 3.75 | 0.30 |
| S5 The Spread | One voice, many accounts. | 41.37 | 43.03 | 4 | 1.67 | - |
| S6 The Work | Positioning. Your profile. Content strategy. Writing. Visuals. Campaigns, LinkedIn ads included. | 43.75 | 48.33 | 11 | 4.58 | 0.30 |
| S6 The Work | Six jobs, each built on what makes you different. | 48.63 | 52.38 | 9 | 3.75 | - |
| S7 The Verdict | The verdict. | 53.08 | 53.92 | 2 | 0.83 | 0.50 |
| S7 The Verdict | Anyone can list features. Only you can explain why you chose them. | 54.42 | 59.42 | 12 | 5.00 | 0.40 |
| S7 The Verdict | That difference is the asset. | 59.82 | 61.90 | 5 | 2.08 | - |
| S8 Five Things To Watch | We don't promise outcomes. | 62.62 | 64.28 | 4 | 1.67 | 0.40 |
| S8 Five Things To Watch | We agree five things to observe, separately: time, recognition, voice, sales usefulness, conversations. | 64.68 | 70.10 | 13 | 5.42 | - |
| S9 The Invitation | Outspoken. | 70.82 | 71.23 | 1 | 0.42 | 0.50 |
| S9 The Invitation | Make the right buyers care about you and what you're building. | 71.73 | 76.32 | 11 | 4.58 | 0.50 |
| S9 The Invitation | Book an intro call. | 76.82 | 78.48 | 4 | 1.67 | - |

## What if your pace is different?

Each line keeps its start time; the table shows which lines would run into the next line or past the end of their scene.

| Pace | wpm | Lines that overrun | Detail |
|---:|---:|---:|---|
| 2 wps | 120 | 15 | S1 "The brilliant one. The quiet" overruns by 0.15 s; S1 "The one the right buyers sti" overruns by 0.40 s; S2 "Every decision, a trade-off." overruns by 0.32 s; S2 "All of it. In your head." overruns by 0.15 s; S4 "We take what's in your head:" overruns by 0.65 s; S4 "Then we make it public. In y" overruns by 0.32 s; S5 "Then it can travel." overruns by 0.18 s; S5 "From you, to your team, to b" overruns by 0.60 s; S6 "Positioning. Your profile. C" overruns by 0.77 s; S6 "Six jobs, each built on what" overruns by 0.40 s; S7 "Anyone can list features. On" overruns by 0.75 s; S7 "That difference is the asset" overruns by 0.05 s; S8 "We don't promise outcomes." overruns by 0.08 s; S8 "We agree five things to obse" overruns by 0.72 s; S9 "Make the right buyers care a" overruns by 0.57 s |
| 2.2 wps | 132 | 7 | S4 "We take what's in your head:" overruns by 0.10 s; S5 "Then it can travel." overruns by 0.00 s; S5 "From you, to your team, to b" overruns by 0.19 s; S6 "Positioning. Your profile. C" overruns by 0.27 s; S7 "Anyone can list features. On" overruns by 0.20 s; S8 "We agree five things to obse" overruns by 0.13 s; S9 "Make the right buyers care a" overruns by 0.07 s |
| 2.4 wps | 144 | 0 | none |
| 2.7 wps | 162 | 0 | none |

If the real read is slower than about 2.4 words per second, the cut gets retimed (scene lengths stretch by the overrun) rather than the voice being rushed.

## Scene by scene

### S1 The Charge (0.00 to 11.07 s)

> Let's talk about you.

> The brilliant one. The quiet one.

> The one the right buyers still haven't heard of.

### S2 Exhibit A (11.07 to 19.43 s)

> Exhibit A.

> Every decision, a trade-off. Every trade-off, a scar.

> All of it. In your head.

### S3 The Silence (19.43 to 25.47 s)

> And out here?

> One word. Founder.

> Nothing else.

### S4 Ignition (25.47 to 35.00 s)

> We take what's in your head: the decisions, the trade-offs, the product.

> Then we make it public. In your voice.

### S5 The Spread (35.00 to 43.40 s)

> Then it can travel.

> From you, to your team, to buyers, to partners.

> One voice, many accounts.

### S6 The Work (43.40 to 52.73 s)

> Positioning. Your profile. Content strategy. Writing. Visuals. Campaigns, LinkedIn ads included.

> Six jobs, each built on what makes you different.

### S7 The Verdict (52.73 to 62.27 s)

> The verdict.

> Anyone can list features. Only you can explain why you chose them.

> That difference is the asset.

### S8 Five Things To Watch (62.27 to 70.47 s)

> We don't promise outcomes.

> We agree five things to observe, separately: time, recognition, voice, sales usefulness, conversations.

### S9 The Invitation (70.47 to 79.90 s)

> Outspoken.

> Make the right buyers care about you and what you're building.

> Book an intro call.

