import React, {useLayoutEffect, useRef} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {mulberry32} from './rng';

export type Burst = {
  f: number; // scene-local start frame
  x: number; // px from the left of the composition
  y: number; // px from the top
  n: number; // particle count
  seed: number;
  speed: [number, number]; // px per frame at birth
  drag?: number; // per-frame exponential drag, default 0.06
  gravity?: number; // px per frame^2, positive pulls down
  life: [number, number]; // frames
  size: [number, number]; // px radius
  colors: string[];
  angle?: [number, number]; // radians, default full circle
  shape?: 'dot' | 'spark' | 'ring';
  trail?: number; // spark trail multiplier
};

const withAlpha = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

const sprites = new Map<string, HTMLCanvasElement>();
const sprite = (color: string) => {
  let s = sprites.get(color);
  if (!s) {
    s = document.createElement('canvas');
    s.width = s.height = 64;
    const g = s.getContext('2d')!;
    const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, color);
    grad.addColorStop(0.35, color);
    grad.addColorStop(1, withAlpha(color, 0));
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
    sprites.set(color, s);
  }
  return s;
};

/** Closed-form particle bursts: the position at frame t is computed, never simulated, so any frame renders alone. */
export const Particles: React.FC<{bursts: Burst[]; blend?: GlobalCompositeOperation; opacity?: number}> = ({bursts, blend = 'lighter', opacity = 1}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    const g = cv.getContext('2d')!;
    g.clearRect(0, 0, width, height);
    g.globalCompositeOperation = blend;
    for (const b of bursts) {
      const t = frame - b.f;
      if (t < 0) continue;
      const rnd = mulberry32(b.seed);
      const k = b.drag ?? 0.06;
      const grav = b.gravity ?? 0;
      const a0 = b.angle?.[0] ?? 0;
      const a1 = b.angle?.[1] ?? Math.PI * 2;
      for (let i = 0; i < b.n; i++) {
        const ang = a0 + rnd() * (a1 - a0);
        const sp = b.speed[0] + rnd() * (b.speed[1] - b.speed[0]);
        const life = b.life[0] + rnd() * (b.life[1] - b.life[0]);
        const size = b.size[0] + rnd() * (b.size[1] - b.size[0]);
        const color = b.colors[Math.floor(rnd() * b.colors.length)];
        if (t > life) continue;
        const vx = Math.cos(ang) * sp;
        const vy = Math.sin(ang) * sp;
        const d = (1 - Math.exp(-k * t)) / k;
        const px = b.x + vx * d;
        const py = b.y + vy * d + 0.5 * grav * t * t;
        const u = t / life;
        const alpha = Math.max(0, 1 - u * u) * opacity;
        if (alpha <= 0.01) continue;
        const shape = b.shape ?? 'dot';
        if (shape === 'spark') {
          const dd = Math.exp(-k * t);
          const tx = px - vx * dd * (b.trail ?? 3);
          const ty = py - vy * dd * (b.trail ?? 3) - grav * t * (b.trail ?? 3) * 0.5;
          g.globalAlpha = alpha;
          g.strokeStyle = color;
          g.lineCap = 'round';
          g.lineWidth = Math.max(1, size * (1 - u * 0.6));
          g.beginPath();
          g.moveTo(tx, ty);
          g.lineTo(px, py);
          g.stroke();
        } else if (shape === 'ring') {
          g.globalAlpha = alpha * 0.6;
          g.strokeStyle = color;
          g.lineWidth = Math.max(1.5, size * 0.25);
          g.beginPath();
          g.arc(px, py, size * (1 + u * 2.4), 0, Math.PI * 2);
          g.stroke();
        } else {
          const r = size * (1 - u * 0.5) * 2.2;
          g.globalAlpha = alpha;
          g.drawImage(sprite(color), px - r, py - r, r * 2, r * 2);
        }
      }
    }
    g.globalAlpha = 1;
    g.globalCompositeOperation = 'source-over';
  });
  return <canvas ref={ref} width={width} height={height} style={{position: 'absolute', inset: 0, width, height, pointerEvents: 'none'}} />;
};
