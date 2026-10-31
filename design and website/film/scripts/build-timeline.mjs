// Merges src/script.json (scene timing, voiceover windows) with each scene's events.json into src/timeline.json for the audio synth.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const script = JSON.parse(await fs.readFile(path.join(root, 'src/script.json'), 'utf8'));
const fps = script.fps;

// Musical energy per scene (0-1): drives string brightness, density of plucks and wind level.
const ENERGY = {S1: 0.2, S2: 0.32, S3: 0.12, S4: 0.58, S5: 0.64, S6: 0.55, S7: 0.72, S8: 0.4, S9: 1.0};
const scenes = script.scenes.map((s) => ({id: s.id, start: s.startFrame / fps, end: (s.startFrame + s.frames) / fps, energy: ENERGY[s.id] ?? 0.5}));
const byId = Object.fromEntries(scenes.map((s) => [s.id, s]));

const cues = [];
for (const s of script.scenes) {
  const events = JSON.parse(await fs.readFile(path.join(root, `src/scenes/${s.id}.events.json`), 'utf8'));
  for (const e of events) cues.push({...e, t: Math.round((byId[s.id].start + e.t) * 1000) / 1000, scene: s.id});
}
cues.sort((a, b) => a.t - b.t);

const vo = script.scenes.flatMap((s) => s.vo.map((v) => ({start: byId[s.id].start + v.start, end: byId[s.id].start + v.end})));
const finaleStart = byId.S9.start;
const first = 1.3; // the S1 impact: strings enter with it
const bars = 23; // from the impact to the finale start, whole bars
const timeline = {
  fps,
  duration: script.totalFrames / fps,
  bar: (finaleStart - first) / bars,
  bar_offset: first,
  finale_start: finaleStart,
  roll_len: 1.5,
  // real silences (music and wind carry on only where the film says so): before the S1 impact, the S3 void, the pre-finale hush
  silence: [{start: 0, end: first}, {start: byId.S3.start + 0.2, end: byId.S3.start + 5.35}, {start: finaleStart - 2.6, end: finaleStart - 0.55}],
  scenes,
  cues,
  vo,
};
await fs.writeFile(path.join(root, 'src/timeline.json'), JSON.stringify(timeline, null, 1) + '\n');
console.log('timeline', timeline.duration, 's', cues.length, 'cues', vo.length, 'vo windows', 'bar', timeline.bar.toFixed(4));
