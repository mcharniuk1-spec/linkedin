import type {Meta,StoryObj} from '@storybook/react-vite';
import {useState} from 'react';
import {motion} from 'motion/react';
import {motionRecords,transitions,panelVariants,useMotionPreference} from '../../motion/src/presets';
import {ActionButton,SurfacePlate,EditorialLabel,FounderChapterStudy,DemoFeedbackCard} from '../src';
export default {title:'Motion/Presets',parameters:{layout:'padded'}} satisfies Meta;
function Presets(){const [show,setShow]=useState(true);const reduced=useMotionPreference();return <div className="os-specimen-list"><ActionButton onClick={()=>setShow(!show)}>Replay bounded entrances</ActionButton>{motionRecords.map((p,i)=><section key={p.id}><EditorialLabel>{p.id} · {p.name}</EditorialLabel><motion.div key={`${p.id}-${show}`} variants={panelVariants} initial={reduced?false:'hidden'} animate="visible" transition={reduced?{duration:0}:Object.values(transitions)[i]}><SurfacePlate><p>{p.trigger}. {p.reduced_motion}.</p><p className="os-type-support">Interrupt by replaying. No infinite decorative animation. Video uses explicit secondsToFrames mapping.</p></SurfacePlate></motion.div></section>)}</div>}
export const AllPresets:StoryObj={render:()=> <Presets/>};
function SideArrivalDemo(){const reduced=useMotionPreference();return <motion.div initial={reduced?false:{opacity:0,x:-12}} whileInView={{opacity:1,x:0}} viewport={{once:true}} transition={reduced?{duration:0}:transitions.feedbackArrival}><DemoFeedbackCard/></motion.div>}
export const SideArrival:StoryObj={render:()=> <SideArrivalDemo/>};
export const Chapter:StoryObj={render:()=> <FounderChapterStudy/>};
