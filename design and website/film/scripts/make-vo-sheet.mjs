// Builds the voiceover sheet, SRT and CSV from src/script.json (single source of truth for scene timing and VO lines).
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const script = JSON.parse(await fs.readFile(path.join(root, 'src/script.json'), 'utf8'));
const fps = script.fps;
const t2 = (s) => s.toFixed(2);
const srtTime = (s) => {
  const ms = Math.round(s * 1000);
  const h = Math.floor(ms / 3600000), m = Math.floor((ms % 3600000) / 60000), sec = Math.floor((ms % 60000) / 1000), r = ms % 1000;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')},${String(r).padStart(3, '0')}`;
};

const lines = [];
for (const s of script.scenes) for (const v of s.vo) lines.push({scene: s.id, title: s.title, sceneStart: s.startFrame / fps, sceneEnd: (s.startFrame + s.frames) / fps, text: v.text, start: s.startFrame / fps + v.start, end: s.startFrame / fps + v.end, words: v.words});

// Fit check: each line starts at its planned time; at a different reading pace it must still end before the next line starts and before its scene ends.
const paces = [2.0, 2.2, 2.4, 2.7];
const fit = paces.map((p) => {
  let over = 0;
  const detail = [];
  lines.forEach((l, i) => {
    const end = l.start + l.words / p;
    const limit = i + 1 < lines.length ? Math.min(lines[i + 1].start - 0.15, l.sceneEnd) : l.sceneEnd;
    if (end > limit + 1e-6) { over++; detail.push(`${l.scene} "${l.text.slice(0, 28)}" overruns by ${t2(end - limit)} s`); }
  });
  return {pace: p, wpm: Math.round(p * 60), over, detail};
});

let md = `# Outspoken launch film: voiceover sheet\n\nGenerated from \`src/script.json\` by \`npm run vo\`. Language: English. Status of all wording: **proposed** (owner and founders approve; the line "Every trade-off, a scar" in particular needs approval).\n\n`;
md += `- Film length: **${t2(script.totalFrames / fps)} s** (${script.totalFrames} frames at ${fps} fps), ${script.totalWords} spoken words, ${lines.length} lines in ${script.scenes.length} scenes.\n- Planned reading pace: **${script.wordsPerSecond} words per second (about ${Math.round(script.wordsPerSecond * 60)} wpm)** for the speech itself; the pauses are written into the timing below.\n- Speech time at that pace: ${t2(script.totalWords / script.wordsPerSecond)} s of ${t2(script.totalFrames / fps)} s. The rest is designed pauses, impacts and visual-only beats.\n- Delivery: calm, close to the microphone, a little dangerous. The picture and sound do the shouting; the voice never does.\n\n`;
md += `## How to record\n1. Read each line as its own take with 0.5 s of room tone before and after. One file per line is easiest: \`S1-L1.wav\`, \`S1-L2.wav\`, and so on.\n2. Record 48 kHz, 24-bit, mono, no processing. Leave levels low enough that nothing clips.\n3. Do not rush to fill the pauses. A silence is part of the line (see the pause column).\n4. Send the takes back. The film is retimed per line from the real words (the Whisper model on this project can give word timestamps); the picture beats are built to move by about plus or minus 0.3 s without breaking.\n\n`;
md += `## Timing table (global time, seconds)\n\n| Scene | Line | Start | End (planned) | Words | Seconds | Pause after |\n|---|---|---:|---:|---:|---:|---:|\n`;
lines.forEach((l, i) => {
  const next = lines[i + 1];
  const pause = next && next.scene === l.scene ? next.start - l.end : 0;
  md += `| ${l.scene} ${l.title} | ${l.text} | ${t2(l.start)} | ${t2(l.end)} | ${l.words} | ${t2(l.end - l.start)} | ${pause ? t2(pause) : '-'} |\n`;
});
md += `\n## What if your pace is different?\n\nEach line keeps its start time; the table shows which lines would run into the next line or past the end of their scene.\n\n| Pace | wpm | Lines that overrun | Detail |\n|---:|---:|---:|---|\n`;
for (const f of fit) md += `| ${f.pace} wps | ${f.wpm} | ${f.over} | ${f.detail.length ? f.detail.join('; ') : 'none'} |\n`;
md += `\nIf the real read is slower than about ${fit.find((f) => f.over > 0 && f.pace < 2.4) ? '2.4' : '2.2'} words per second, the cut gets retimed (scene lengths stretch by the overrun) rather than the voice being rushed.\n\n## Scene by scene\n\n`;
for (const s of script.scenes) {
  md += `### ${s.id} ${s.title} (${t2(s.startFrame / fps)} to ${t2((s.startFrame + s.frames) / fps)} s)\n\n`;
  for (const v of s.vo) md += `> ${v.text}\n\n`;
}
await fs.writeFile(path.join(root, 'voiceover/VOICEOVER.md'), md);

let srt = '';
lines.forEach((l, i) => { srt += `${i + 1}\n${srtTime(l.start)} --> ${srtTime(l.end)}\n${l.text}\n\n`; });
await fs.writeFile(path.join(root, 'voiceover/captions.srt'), srt);
let csv = 'scene,title,start_s,end_s,words,text\n';
for (const l of lines) csv += `${l.scene},"${l.title}",${t2(l.start)},${t2(l.end)},${l.words},"${l.text.replace(/"/g, '""')}"\n`;
await fs.writeFile(path.join(root, 'voiceover/vo-timing.csv'), csv);
console.log('vo sheet', lines.length, 'lines', fit.map((f) => `${f.pace}:${f.over}`).join(' '));
