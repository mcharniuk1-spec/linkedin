import type { Meta,StoryObj } from '@storybook/react-vite';
import {useMotionValue} from 'motion/react';
import {NeuronField} from '../index';
const meta={title:'Experience V3/Founder constellation',component:NeuronField,args:{imageSrc:'/assets/revisions/v3/nature/04-neural-constellation.webp'},parameters:{layout:'fullscreen'}} satisfies Meta<typeof NeuronField>;
export default meta;type Story=StoryObj<typeof meta>;
export const FullField:Story={render:args=><div style={{background:'#071024',height:800}}><NeuronField {...args}/></div>};
export const Static:Story={args:{staticOnly:true},render:args=><div style={{background:'#071024',height:700}}><NeuronField {...args}/></div>};
export const Progress:Story={render:args=>{const progress=useMotionValue(0);return <div style={{background:'#071024',color:'#fff'}}><label style={{display:'block',padding:24}}>Story progress <input aria-label="Story progress" type="range" min="0" max="1" step=".01" defaultValue="0" onChange={e=>progress.set(Number(e.target.value))}/></label><div style={{height:700}}><NeuronField {...args} progress={progress}/></div></div>}};
