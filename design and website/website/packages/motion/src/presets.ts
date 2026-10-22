import {useSyncExternalStore} from 'react';
import type { Transition, Variants } from 'motion/react';
export const ease = [0.22, 1, 0.36, 1] as const;
export const transitions = { feedback:{duration:.16,ease}, panel:{duration:.36,ease}, disclosure:{duration:.22,ease}, continuity:{duration:.28,ease}, message:{duration:.26,ease}, emphasis:{duration:.3,ease}, diagram:{duration:.5,ease}, tilt:{duration:.18,ease}, glint:{duration:.42,ease}, chapter:{duration:.8,ease}, feedbackArrival:{duration:.55,ease} } satisfies Record<string,Transition>;
export const panelVariants:Variants={hidden:{opacity:0,y:12},visible:{opacity:1,y:0},exit:{opacity:0,y:6}};
export const messageVariants:Variants={hidden:{opacity:0,x:-8},visible:{opacity:1,x:0},exit:{opacity:0}};
export const motionRecords=Object.entries(transitions).map(([name,transition],i)=>({id:`OS-M${String(i+1).padStart(3,'0')}`,name,trigger:i===7?'fine-pointer hover, never touch':'explicit interaction or in-view entrance',properties:i===7?['rotateX','rotateY']:['opacity','transform'],units:'seconds, CSS pixels, degrees',duration_or_spring:transition,easing:ease,amplitude:i===7?'3 degrees maximum':'12 pixels maximum for text panels',stagger:0,interrupt_exit:'Motion retargets from current value; caller controls presence',offscreen_pause:'No infinite animation; scene renders on state/resize only',reduced_motion:'Remove translation/rotation; immediate visible content',keyboard_touch:'Stable hit area; native focus and press states',static_export:'Final visible state',fps_mapping_if_video:'secondsToFrames(duration, fps); never reuse web springs',story_ids:['motion-presets--all-presets'],figma_reference:null,review_evidence:[]}));
export function secondsToFrames(seconds:number,fps:number){if(seconds<0||!Number.isFinite(seconds)||!Number.isFinite(fps)||fps<=0)throw Error('Invalid timing');return Math.round(seconds*fps);}
export function usePreset(name:keyof typeof transitions,reduced:boolean|null){return reduced?{duration:0}:transitions[name];}

const subscribeMotion=(notify:()=>void)=>{const query=window.matchMedia("(prefers-reduced-motion: reduce)");query.addEventListener("change",notify);return ()=>query.removeEventListener("change",notify)};
const motionSnapshot=()=>typeof window!=="undefined"&&window.matchMedia("(prefers-reduced-motion: reduce)").matches;
/** Tracks live preference changes as well as the initial value. Server/static rendering stays reduced. */
export function useMotionPreference(){return useSyncExternalStore(subscribeMotion,motionSnapshot,()=>true)}
