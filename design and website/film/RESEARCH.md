# Research behind the launch film (31 October 2026)

Three independent research strands fed the film: a video analyst, a skills scout, and a conservative editor. Everything here is **evidence with stated limits**, not a verdict that the film will perform.

## 1. Similar company films (video analyst)
Thirteen public films were played in a browser pane; frame change and an audio energy envelope were sampled and twelve thumbnails per film were viewed. Nothing was watched continuously and no audio was listened to (limits in section 4).

| Company | Film | Runtime | How it was analysed |
|---|---|---|---|
| Linear | Introducing Linear Agent | 0:55 | played, sampled |
| Linear | Introducing Linear Releases | 0:30 | played, sampled |
| Framer | Framer is for Founders | 0:30 | played, sampled |
| Framer | That's Framer | 0:38 | played, sampled (pre-roll excluded) |
| Framer | Framer 3.0 | 1:15 | played, sampled |
| Notion | Introducing the new Notion AI | 0:57 | played, sampled |
| Notion | The Search | 0:30 | played, sampled |
| Raycast | New Raycast | 0:39 | played, sampled |
| Cursor | Introducing Cursor 3 | 1:30 | played, sampled |
| Powform | Motion Graphics Promo (SaaS feature launch) | 0:50 | played, sampled |
| SpotDraft | B2B SaaS brand film | 1:15 | played, sampled (pre-roll excluded) |
| Understory | Allbound GTM strategy (agency, first 64 s) | 3:39 | homepage as text; first 64 s played |
| LinkedIn | Everybody's Business trailer | 1:40 | played, sampled (pre-roll excluded) |

Seven competitor homepages were read as text only (none embeds an animated promo); six more returned nothing usable.

Patterns that held across several films (counts out of 13):
- Dark base with one accent hue: 6 (Linear x2, Framer x3, Raycast).
- Short on-screen phrases, 2-6 words, one at a time: 7 mid-film plus 2 end-card-only.
- Hard visual change at least every 0.6-2.1 s: 7 of 9 animated pieces; the two Linear films change only every 5.5-7.5 s and rely on continuous camera drift.
- Close on a wordmark or one-line statement on a near-empty field: 9; none showed a button or URL in the sampled frames.
- Audio falls away in the last bucket: 8 of 12 measured; a build of +4 to +6 dB appears in 4 of 12; peaks sit at 31-67 % of runtime; no drum finale was measured in any film.
- A readable phrase within 3 s: only 4 films; most open with a silent or wordless stretch.
Anti-patterns: a silent first 10 s of meaning, long near-still talking-head stretches, dense low-contrast UI at feed size, constant micro-motion with no breath for 75 s, real platform UI or third-party logo cards, flat loudness with no sound arc.

Decisions taken for this film: a readable line in the first second (the typed open), nine scenes of 6-11 s, a calm pearl act in the middle (the "flip" pattern), a loudness build to the finale, one wordmark close, abstract profile and post cards instead of real platform UI.

## 2. Skills and tools compared (skills scout)
| Candidate | Licence (as read) | Verdict |
|---|---|---|
| Remotion + React (installed 4.0.520) | Remotion licence: free for individuals and for-profit organisations up to 3 people, paid above | **Use** (confirm headcount before a commercial release) |
| FFmpeg 8.1 (installed, GPL build) | GPL v3 binary; rendered output not addressed | **Use** |
| numpy + scipy synthesis (own code) | BSD-style | **Use**; synthetic quality stated honestly |
| remotion-dev/skills (official Remotion agent skills) | none declared in the API | **Reading only**; pin the commit, install only after the safe-installer scan |
| iart-ai/motion-design-skills | MIT | **Reading only** (timing and easing numbers) |
| dev-isaacmello/extreme-motion-design | MIT | **Reading only**: QA thresholds and synth recipes were ported into own code; its scripts fetch dependencies and download music, so not installed |
| emilkowalski/skills | MIT | Reading only (an equivalent is already installed) |
| heygen-com/hyperframes | Apache-2.0 | Reading only: a competing runtime, network use, not installed |
| @remotion/transitions, noise, shapes, paths, effects | Remotion licence / MIT (mixed) | Not installed (project forbids unreviewed additions); equivalents written in `src/kit` |
| FluidSynth + GeneralUser GS soundfont | LGPL / custom | Skip now; the upgrade path to sampled strings after a provenance review |
| pedalboard, pydub, soundfile, SoX, Csound | GPL / MIT / BSD | Skip: scipy and FFmpeg cover the film |
| Cloud music/video skills (ai-music, ace-step, elevenlabs, image-to-video, ...) | n/a | Skip: spend stays 0, outputs are not deterministic |
| reactvideoeditor/remotion-templates, aggregator skill lists | none | Skip: unlicensed code |
Nothing was installed. Any new skill needs the safe installer and the static scan first.

## 3. Conservative-editor rules that shaped the build
Frame 0 is already a finished frame; each line stays on screen at least `max(1.5 s, 0.8 s + words/2.5)`; one visual event every 1-3 s with a rest beat about every 12 s; at most 6-8 bursts, calm after each; flashes at most 3 per second and 3 frames long; no roll, shake or whip pans; all key ideas as burned-in text because feed video autoplays muted; export H.264 High yuv420p BT.709, AAC 48 kHz, loudness about -16 LUFS integrated with true peak at or below -1.5 dBTP (no LinkedIn loudness target exists); render from one bundle in chunks and verify determinism; render the picture muted and mux sound with ffmpeg.

## 4. Limits
- Video analysis used 12 thumbnails per film at 256x144 and a 20 Hz luminance sampler; small text and continuous motion were not seen, and audio was an energy envelope, not listening. Competitor coverage is partial.
- Skills information came from GitHub API summaries read through a summarising model: star counts, licences and dates are approximate and need rechecking; few candidate code files were read and no static scan was run.
- LinkedIn's specification pages were read only partly (ad specs); the Pages and Videos API figures come from search summaries. The feed phone width (about 390 px) and the 13 % bottom reserve are assumptions to verify with a private upload.
