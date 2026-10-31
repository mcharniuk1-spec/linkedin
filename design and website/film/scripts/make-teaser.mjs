// Builds the teaser's sound from the master mix with the same segments and crossfades as the Teaser composition, then muxes it.
//   node scripts/make-teaser.mjs out/teaser-video.mp4 out/teaser.mp4
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const [video, out] = [process.argv[2] ?? 'out/teaser-video.mp4', process.argv[3] ?? 'out/teaser.mp4'];
const script = JSON.parse(await fs.readFile(path.join(root, 'src/script.json'), 'utf8'));
const teaser = JSON.parse(await fs.readFile(path.join(root, 'src/teaser.json'), 'utf8'));
const fps = script.fps;
const xf = teaser.crossfadeFrames / fps;
const scene = Object.fromEntries(script.scenes.map((s) => [s.id, s.startFrame / fps]));

const parts = teaser.segments.map((s, i) => {
  const a = scene[s.scene] + s.from;
  const b = scene[s.scene] + s.to;
  return `[0:a]atrim=start=${a.toFixed(3)}:end=${b.toFixed(3)},asetpts=PTS-STARTPTS[a${i}]`;
});
let chain = '';
let last = 'a0';
for (let i = 1; i < teaser.segments.length; i++) {
  chain += `;[${last}][a${i}]acrossfade=d=${xf.toFixed(3)}:c1=tri:c2=tri[x${i}]`;
  last = `x${i}`;
}
const graph = parts.join(';') + chain;
const r = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', path.join(root, 'audio-out/mix.wav'), '-filter_complex', graph, '-map', `[${last}]`, '-ar', '48000', '-c:a', 'pcm_s24le', path.join(root, 'out/teaser-audio.wav')], {stdio: 'inherit'});
if (r.status !== 0) throw new Error('teaser audio failed');
const m = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', path.join(root, video), '-i', path.join(root, 'out/teaser-audio.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', '-shortest', path.join(root, out)], {stdio: 'inherit'});
if (m.status !== 0) throw new Error('teaser mux failed');
console.log('teaser', out);
