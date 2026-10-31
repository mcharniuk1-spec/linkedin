import script from './script.json';

export const FPS = script.fps;
export type SceneInfo = {id: string; title: string; startFrame: number; frames: number; vo: {text: string; start: number; end: number}[]};
export const SCENES = script.scenes as SceneInfo[];
export const TOTAL_FRAMES = script.totalFrames;
export const sceneById = (id: string) => SCENES.find((s) => s.id === id)!;
/** seconds (scene-local) to frames */
export const sf = (seconds: number) => Math.round(seconds * FPS);
