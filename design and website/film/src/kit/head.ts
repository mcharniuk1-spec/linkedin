/**
 * Abstract side-profile head outline (facing right) in a 800 x 900 box, shared by the mind-map scene and the network scene
 * so the account network can ease back into the exact outline the film started in. Geometry is hand-authored, not a likeness.
 */
const CONTROL: [number, number][] = [
  [200, 900], [190, 740], [150, 600], [110, 450], [118, 300], [185, 170], [310, 80], [465, 50], [600, 100], [690, 195],
  [722, 300], [736, 365], [775, 450], [795, 495], [745, 520], [742, 555], [722, 590], [732, 628], [700, 690], [610, 722],
  [545, 765], [522, 840], [520, 900],
];

const catmull = (p0: number[], p1: number[], p2: number[], p3: number[], t: number): [number, number] => {
  const t2 = t * t;
  const t3 = t2 * t;
  const f = (a: number, b: number, c: number, d: number) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
  return [f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1])];
};

const dense: [number, number][] = [];
for (let i = 0; i < CONTROL.length - 1; i++) {
  const p0 = CONTROL[Math.max(0, i - 1)];
  const p1 = CONTROL[i];
  const p2 = CONTROL[i + 1];
  const p3 = CONTROL[Math.min(CONTROL.length - 1, i + 2)];
  for (let k = 0; k < 24; k++) dense.push(catmull(p0, p1, p2, p3, k / 24));
}
dense.push(CONTROL[CONTROL.length - 1]);

const cum: number[] = [0];
for (let i = 1; i < dense.length; i++) cum.push(cum[i - 1] + Math.hypot(dense[i][0] - dense[i - 1][0], dense[i][1] - dense[i - 1][1]));
export const HEAD_LENGTH = cum[cum.length - 1];
export const HEAD_BOX = {w: 800, h: 900} as const;

/** SVG path of the outline (open at the neck). */
export const HEAD_PATH = 'M' + dense.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(' L');

/** n points spaced evenly by arc length along the outline, in the 800 x 900 box. */
export const headPoints = (n: number): [number, number][] => {
  const out: [number, number][] = [];
  for (let i = 0; i < n; i++) {
    const target = (i / (n - 1)) * HEAD_LENGTH;
    let j = 1;
    while (j < cum.length - 1 && cum[j] < target) j++;
    const u = (target - cum[j - 1]) / Math.max(1e-6, cum[j] - cum[j - 1]);
    out.push([dense[j - 1][0] + (dense[j][0] - dense[j - 1][0]) * u, dense[j - 1][1] + (dense[j][1] - dense[j - 1][1]) * u]);
  }
  return out;
};

/** True when (x, y) in the box lies inside the closed head silhouette (neck closed straight across the bottom). */
export const insideHead = (x: number, y: number) => {
  let inside = false;
  const poly = dense;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};
