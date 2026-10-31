// Renders a composition with the already-installed Remotion and an existing browser binary (no browser download).
//   node render.mjs --comp Master --out out/master-video.mp4 [--chunk 480] [--browser PATH] [--concurrency 6]
//   node render.mjs --comp Master --still 120 --out out/still-120.png
//   node render.mjs --comp Master --frames 0-89 --out out/clip.mp4
// Video only (muted): the sound is built by scripts/audio/synth.py and muxed afterwards with ffmpeg.
import fs from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const get = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const comp = get('--comp', 'Master');
const out = path.resolve(get('--out', `out/${comp}.mp4`));
const shell = path.join(os.homedir(), '.cache/puppeteer/chrome-headless-shell/mac_arm-154.0.8037.57/chrome-headless-shell-mac-arm64/chrome-headless-shell');
const browserExecutable = get('--browser', existsSync(shell) ? shell : '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
const stillFrame = get('--still');
const frames = get('--frames');
const chunk = Number(get('--chunk', '0'));
const concurrency = Number(get('--concurrency', '6'));
const crf = Number(get('--crf', '18'));
await fs.access(browserExecutable);
await fs.mkdir(path.dirname(out), {recursive: true});

const scratch = await fs.mkdtemp(path.join(os.tmpdir(), 'outspoken-film-'));
const common = {codec: 'h264', pixelFormat: 'yuv420p', x264Preset: 'medium', crf, colorSpace: 'bt709', muted: true, imageFormat: 'jpeg', jpegQuality: 92, concurrency};
try {
  const serveUrl = await bundle({entryPoint: path.join(here, 'src/index.tsx'), publicDir: path.join(here, 'public'), outDir: path.join(scratch, 'bundle')});
  const composition = await selectComposition({serveUrl, id: comp, browserExecutable});
  const t0 = Date.now();
  if (stillFrame !== undefined) {
    await renderStill({serveUrl, composition, frame: Number(stillFrame), output: out, browserExecutable, imageFormat: out.endsWith('.jpg') ? 'jpeg' : 'png'});
  } else {
    const [a, b] = frames ? frames.split('-').map(Number) : [0, composition.durationInFrames - 1];
    if (!chunk || b - a + 1 <= chunk) {
      await renderMedia({serveUrl, composition, outputLocation: out, browserExecutable, frameRange: [a, b], ...common, onProgress: ({renderedFrames}) => { if (renderedFrames % 200 === 0) console.log('frames', renderedFrames); }});
    } else {
      // Chunked render from one bundle: a fresh browser per chunk bounds Chrome memory growth; chunks are joined without re-encoding.
      const parts = [];
      for (let s = a, i = 0; s <= b; s += chunk, i++) {
        const e = Math.min(b, s + chunk - 1);
        const file = path.join(scratch, `part-${String(i).padStart(3, '0')}.mp4`);
        await renderMedia({serveUrl, composition, outputLocation: file, browserExecutable, frameRange: [s, e], ...common});
        console.log('chunk', i, s, e, ((Date.now() - t0) / 1000).toFixed(0) + 's');
        parts.push(file);
      }
      const list = path.join(scratch, 'parts.txt');
      await fs.writeFile(list, parts.map((p) => `file '${p}'`).join('\n') + '\n');
      const r = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', '-bsf:v', 'h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0', '-movflags', '+faststart', out], {stdio: 'inherit'});
      if (r.status !== 0) throw new Error('ffmpeg concat failed');
    }
  }
  console.log(JSON.stringify({comp, out, seconds: (Date.now() - t0) / 1000, w: composition.width, h: composition.height, fps: composition.fps, frames: composition.durationInFrames, browser: path.basename(browserExecutable)}));
} finally {
  await fs.rm(scratch, {recursive: true, force: true});
}
