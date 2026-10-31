import type { Meta, StoryObj } from '@storybook/react-vite';
import type { CSSProperties } from 'react';
import { ThreeTiltButton, type ThreeTiltButtonProps } from '../index';

const tones = ['navy', 'marigold', 'silver'] as const;
const variants = ['primary', 'secondary', 'quiet'] as const;
const matrixStyle: CSSProperties = {display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(240px,1fr))',gap:32,maxWidth:1080,padding:32};
function Matrix({disabled=false,loading=false}:{disabled?:boolean;loading?:boolean}) {
  return <div style={matrixStyle}>{variants.flatMap(variant=>tones.map(tone=><section key={`${variant}-${tone}`} style={{display:'grid',gap:14,alignContent:'start'}}><p style={{font:'500 13px/1.5 Inter,system-ui',margin:0}}>{variant} · {tone}</p><ThreeTiltButton data-focus-specimen variant={variant} tone={tone} disabled={disabled} loading={loading}>{loading?'Preparing':disabled?'Unavailable':`${variant[0].toUpperCase()+variant.slice(1)} ${tone}`}</ThreeTiltButton></section>))}</div>;
}
const meta = {
  title:'Experience V4/Button catalog',component:ThreeTiltButton,tags:['autodocs'],
  parameters:{layout:'padded',docs:{description:{component:'Actual ThreeTiltButton API. Nine supported tone/variant combinations, native loading/disabled, real keyboard focus and optional arrow. Pointer hover/press are real interactions; no simulated state prop or CSS-only 3D claim.'}}},
  args:{children:'Book an intro call',variant:'primary',tone:'navy',loading:false,disabled:false,arrow:true},
  argTypes:{variant:{control:'select',options:variants},tone:{control:'select',options:tones},loading:{control:'boolean'},disabled:{control:'boolean'},arrow:{control:'boolean'}},
} satisfies Meta<typeof ThreeTiltButton>;
export default meta;
type Story=StoryObj<typeof meta>;
export const Playground:Story={};
export const AllToneVariantCombinations:Story={render:()=> <Matrix/>};
export const DisabledMatrix:Story={render:()=> <Matrix disabled/>};
export const LoadingMatrix:Story={render:()=> <Matrix loading/>};
export const FocusAndKeyboard:Story={render:()=> <><p>Use Tab and Shift+Tab to inspect the native focus ring. Enter and Space activate the focused button. Each target stays fixed while its decorative mesh tilts.</p><Matrix/></>,play:async({canvasElement})=>{canvasElement.querySelector<HTMLButtonElement>('[data-focus-specimen]')?.focus();}};
export const ArrowOptions:Story={render:()=> <div style={{display:'flex',flexWrap:'wrap',gap:32,padding:32}}><ThreeTiltButton arrow>With directional arrow</ThreeTiltButton><ThreeTiltButton arrow={false}>Without arrow</ThreeTiltButton></div>};
export const LongLabel:Story={args:{children:'Discuss the story you want the right buyers to understand',arrow:false},render:(args:ThreeTiltButtonProps)=><div style={{maxWidth:360,padding:24}}><ThreeTiltButton {...args}/></div>};
