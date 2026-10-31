import type {Meta,StoryObj} from '@storybook/react-vite';
import './website.css';
import './identity-v10.css';
import {Icon,type IconName} from './Icon';
const names:IconName[]=['mic','time','recognition','voice','usefulness','conversations','profile','strategy','writing','design','automation','marketing','advertising','measurement'];
const meta={title:'V10/Identity (proposed)',parameters:{layout:'padded'},tags:['autodocs']} satisfies Meta;export default meta;type Story=StoryObj<typeof meta>;
const v='/assets/identity/v10/';
export const Marks:Story={render:()=> <div style={{display:'grid',gap:24}}>
 <div style={{display:'flex',gap:32,alignItems:'flex-end',flexWrap:'wrap'}}><img src={v+'mark-b01.svg'} alt="OUTSPOKEN microphone mark, colour" width="160" height="212"/><div style={{background:'#162760',padding:20}}><img src={v+'mark-b01-inverse.svg'} alt="OUTSPOKEN microphone mark, inverse" width="160" height="212"/></div><img src={v+'mark-b01-mono.svg'} alt="OUTSPOKEN microphone mark, one colour" width="160" height="212"/></div>
 <div style={{display:'flex',gap:20,alignItems:'flex-end'}}>{[24,32,64,128].map(s=><img key={s} src={v+'mark-b01-24.svg'} alt="" width={s} height={s}/>)}</div>
 <div style={{display:'grid',gap:16,justifyItems:'start'}}><img src={v+'lockup-b01.svg'} alt="OUTSPOKEN lockup" width="268" height="46"/><div style={{background:'#162760',padding:20}}><img src={v+'lockup-b01-inverse.svg'} alt="OUTSPOKEN lockup, inverse" width="268" height="46"/></div></div></div>};
export const Icons:Story={render:()=> <div style={{display:'grid',gap:24}}>{[24,32,56].map(s=><div key={s} style={{display:'flex',gap:14,flexWrap:'wrap',color:'#162760'}}>{names.map(n=><Icon key={n} name={n} size={s}/>)}</div>)}<div style={{background:'#162760',color:'#F1F3F6',padding:20,display:'flex',gap:14,flexWrap:'wrap'}}>{names.map(n=><Icon key={n} name={n} size={40}/>)}</div></div>};
