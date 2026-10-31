# Film renders (31 October 2026)

What is here and in `../assets/public/assets/film/` (registered binary assets): small **720p previews**, a poster frame, contact sheets, a phone-width montage and the measured QA reports. The full-quality files are **not committed** (they rebuild from source; see `../README.md`). Their identity is recorded below so a rebuild can be compared.

| File | What it is |
|---|---|
| `../assets/public/assets/film/master-preview-720p.mp4` | 80 s master, 1280x720 preview, with the synthesised score (6.2 MB) |
| `../assets/public/assets/film/teaser-preview-720p.mp4` | 29 s teaser re-cut, 1280x720 preview (2.8 MB) |
| `../assets/public/assets/film/poster.jpg` | frame at 2.6 s |
| `../assets/public/assets/film/contact-master.png`, `contact-teaser.png` | one tile every 2.5 s |
| `../assets/public/assets/film/phone-montage.png` | 20 frames at 390 px width, for a legibility check at feed size |
| `qa-master.json`, `qa-teaser.json` | output of `scripts/qa/qa.py` |

## Full-quality files (local, not in Git)
| File | Bytes | SHA-256 |
|---|---:|---|
| film.mp4 (master, 1920x1080, 30 fps, 79.90 s) | 28671989 | a4a18e39911800d5ba2e9c654eefe109265aa33bfd3d6c858814aaef74e31cc4 |
| teaser.mp4 (1920x1080, 30 fps, 29.20 s) | 12787747 | b1bd95eb5ab0102d7d7ac25e11fcaf4da1e18d28bd8f1bd7d57103334bde71b9 |

## Measured results (not taste)
- Master: H.264 High, yuv420p, 1920x1080, 30 fps, faststart, AAC stereo 48 kHz; video and audio both 79.90 s; integrated loudness -16.2 LUFS (LRA 8.9); true peak -2.6 dBTP; no silence gap of 0.4 s or more; no black frames; no frozen picture over 1 s outside the silent typed open and the end card; 136 scripted visual and sound events with a largest gap of 2.6 s; every frame-difference spike coincides with a scripted event (7 spikes: impact, glitch cut, scene wipe, detonation, final hit).
- Advisory warning: the mean-luminance motion measure reads low for seconds 63-66 (the pale "five things" scene), because small element changes barely move it. Judge that scene by eye.
- Teaser: 29.20 s, -15.1 LUFS, true peak -2.5 dBTP, same checks pass.

## What these numbers do not prove
They do not prove the film looks or sounds good, that the voice will sit well over the music, that text is comfortable on a real phone, or that LinkedIn will keep this encoding. The score is code-synthesised, the voiceover is not recorded, all wording and visuals are proposals, and owner acceptance is false.
