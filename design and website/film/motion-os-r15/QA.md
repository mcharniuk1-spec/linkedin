# OS motion film R15: measured QA (2 November 2026)

`hyperframes check` (0.9.2): passed, 0 errors; one contrast warning sampled at 7.78 s while the caption pill is fading out (transitional).

Two renders with `-w 2` on an idle machine, `qa_films.py a.mp4 b.mp4 --size 1080x1350 --duration 28`:

```
PASS duration: 28.000 s (expected 28.000)
PASS frame_size: 1080x1350
PASS video_codec: h264 yuv420p
PASS fps: 30/1
PASS audio_present: {"codec_name": "aac", "codec_type": "audio", "sample_rate": "48000", "channels": 2, "r_frame_rate": "0/0"}
PASS loudness: -19.3 LUFS integrated (voice-ready mix without voice; with the voice the target is about -16)
PASS true_peak: -7.2 dBTP
PASS frame_count: 840 frames (expected 840)
PASS isolated_spike_frames: 0 []
PASS flash_rate: luminance jumps > 70 at frames [503]; max 1 per second
PASS determinism_two_renders: 10/10 sampled frames identical ([0, 93, 187, 280, 373, 467, 560, 653, 747, 839])
OVERALL PASS
```

Picture: inspected as a 1-second contact sheet and 0.2-second strips across the cut seam (8 s to 12 s) and the close (23.6 s to 25.2 s); the first render showed a corner-shaped colour field and package cards overlapping the lockup, both fixed before these renders. Not yet inspected frame by frame at full resolution; sound checked by measurement only. The one luminance jump over 70 is the marigold field arriving (one per second, under the flash limit).
