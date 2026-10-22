import {motion,useSpring,useTransform,type MotionValue} from 'motion/react';
import {NeuronField} from '../../packages/experience-v3';
import {MobileChapter} from './MobileChapter';
import './mobile-expertise.css';

function ExpertiseScene({progress,still}:{progress:MotionValue<number>;still:boolean}){
  const scene=useSpring(progress,{stiffness:140,damping:28,mass:.6,restDelta:.0001,restSpeed:.0001});
  const introOpacity=useTransform(scene,[0,.13,.27],[1,1,0]);
  const introY=useTransform(scene,[.13,.29],[0,-20]);
  const brainY=useTransform(scene,[0,.12,.34],[130,105,0]);
  const brainScale=useTransform(scene,[0,.12,.34],[.68,.74,1]);
  const boardOpacity=useTransform(scene,[.81,.88],[0,1]);
  const boardY=useTransform(scene,[.64,.84],[32,0]);
  const boardRotate=useTransform(scene,[.64,.84],[3,0]);
  return <div className="m-expertise__scene">
    <motion.div className="m-expertise__intro" style={still?undefined:{opacity:introOpacity,y:introY}}>
      <p className="eyebrow">From what you know to what buyers understand</p>
      <h2>Your experience.<br/>Your <span className="highlight">edge.</span></h2>
      <p>We uncover the experience, methods, tools and product judgment inside your business. Then we connect the evidence to the customer’s question.</p>
    </motion.div>
    <motion.div className="m-expertise__brain" style={still?undefined:{y:brainY,scale:brainScale}}><NeuronField compact modelSrc="/assets/revisions/v3/neural/human-reference-brain-web.glb" imageSrc="/assets/revisions/v3/nature/04-neural-constellation.webp" progress={scene} staticOnly={still}/></motion.div>
    <motion.div className="m-expertise__board" data-positioning="combined" style={still?undefined:{opacity:boardOpacity,y:boardY,rotateX:boardRotate}}>
      <p className="eyebrow">Five perspectives. One coherent direction.</p>
      <h3>Your personal<br/>brand positioning.</h3>
      <div className="m-expertise__card-space" aria-hidden="true"/>
      <p className="m-expertise__outcome">A clear position. A story buyers can follow.<br/>Built from the substance of your company.</p>
      <div className="m-expertise__terms"><span>Positioning</span><span>Profile</span><span>Content</span><span>Distribution</span></div>
    </motion.div>
    <p className="m-expertise__footnote">An artistic metaphor for expertise. The five categories describe our editorial process.</p>
  </div>;
}

export function MobileExpertise(){
  return <MobileChapter id="approach" className="m-expertise" pages={3.6} ariaLabel="From founder experience to brand positioning">{(progress,still)=><ExpertiseScene progress={progress} still={still}/>}</MobileChapter>;
}
