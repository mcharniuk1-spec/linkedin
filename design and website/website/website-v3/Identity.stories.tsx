import {useState,type ReactNode} from 'react';
import type {Meta,StoryObj} from '@storybook/react-vite';
import './website.css';
import './identity-v10.css';
import {Icon,type IconName} from './Icon';
const names:IconName[]=['mic','time','recognition','voice','usefulness','conversations','profile','strategy','writing','design','automation','marketing','advertising','measurement'];
// Story ids stay as they were (`Marks`, `Icons`); the OS stencil family (owner decision, 2 November 2026) is added first, the B01 microphone stories are kept and labelled as the previous identity.
const meta={title:'V10/Identity (proposed)',parameters:{layout:'padded'},tags:['autodocs']} satisfies Meta;export default meta;type Story=StoryObj<typeof meta>;
const v='/assets/identity/v10/';   // previous identity (B01 microphone), kept as history
const o='/assets/identity/v13/';   // current identity: OS stencil mark with the V5 outlined wordmark
const NAVY='#0D1A3B',INK='#162760',PEARL='#F1F3F6';
const ratio=184.16/100;            // the OS mark is wide: viewBox 184.16 x 100
const markW=(h:number)=>Math.round(h*ratio);
const label={font:"500 13px/1.4 'Geist Mono',monospace",letterSpacing:'.04em',textTransform:'uppercase'} as const;
const note={font:"500 14px/1.5 'Mona Sans',sans-serif",maxWidth:'62ch',margin:0} as const;
function Tile({caption,ground='#fff',dark=false,children}:{caption:string;ground?:string;dark?:boolean;children:ReactNode}){
  return <figure style={{margin:0,display:'grid',gap:10,justifyItems:'start'}}>
    <div style={{background:ground,border:dark?'1px solid #1E2D57':'1px solid #D9DEE7',borderRadius:14,padding:20,display:'flex',gap:20,alignItems:'flex-end',flexWrap:'wrap'}}>{children}</div>
    <figcaption style={{...label,color:INK}}>{caption}</figcaption>
  </figure>;
}
function AnimatedMark(){
  const [run,setRun]=useState(0);
  return <div style={{display:'grid',gap:16,justifyItems:'start'}}>
    <div style={{background:'#fff',border:'1px solid #D9DEE7',borderRadius:14,padding:28}}><img key={run} src={`${o}mark-os-animated.svg?play=${run}`} alt="OUTSPOKEN OS mark, animated entrance" width="294" height="160"/></div>
    <button type="button" onClick={()=>setRun(n=>n+1)} style={{...label,color:INK,background:'#fff',border:'1px solid #A9AFBA',borderRadius:14,padding:'12px 18px',minHeight:44,cursor:'pointer'}}>Replay</button>
    <p style={{...note,color:INK}}>Reduced motion: the file carries its own <code>prefers-reduced-motion</code> rule. When the system asks for reduced motion, the finished mark shows at once and nothing moves. The entrance uses the brand ease, cubic-bezier(0.22, 1, 0.36, 1), for the O and S, then a short slash. It plays once and does not loop.</p>
  </div>;
}

export const OsMarks:Story={name:'OS stencil mark (current identity): colour, inverse, mono',render:()=> <div style={{display:'grid',gap:28}}>
  <p style={{...note,color:INK}}>Current identity: a navy stencil O, a Nickel 600 S (#666F7F) and a marigold slash, drawn wide (1.84 to 1). The mark is proposed until the owner accepts the release.</p>
  <div style={{display:'flex',gap:24,flexWrap:'wrap',alignItems:'flex-start'}}>
    <Tile caption="Colour on white · mark-os.svg"><img src={o+'mark-os.svg'} alt="OUTSPOKEN OS mark, colour" width={markW(100)} height="100"/></Tile>
    <Tile caption="Colour on pearl #F1F3F6 · 4.56 to 1 for the S" ground={PEARL}><img src={o+'mark-os.svg'} alt="OUTSPOKEN OS mark, colour, on pearl" width={markW(100)} height="100"/></Tile>
    <Tile caption="Inverse on deep navy #0D1A3B · mark-os-inverse.svg" ground={NAVY} dark><img src={o+'mark-os-inverse.svg'} alt="OUTSPOKEN OS mark, inverse" width={markW(100)} height="100"/></Tile>
  </div>
  <div style={{display:'flex',gap:24,flexWrap:'wrap',alignItems:'flex-start'}}>
    <Tile caption="One colour, navy · mark-os-mono.svg"><img src={o+'mark-os-mono.svg'} alt="OUTSPOKEN OS mark, one colour" width={markW(100)} height="100"/></Tile>
    <Tile caption="One colour, light · mark-os-mono-inverse.svg" ground={NAVY} dark><img src={o+'mark-os-mono-inverse.svg'} alt="OUTSPOKEN OS mark, one colour, inverse" width={markW(100)} height="100"/></Tile>
  </div></div>};

export const OsSolidSmallSizes:Story={name:'OS stencil mark: solid small-size build at 16, 24, 32 and 48 px',render:()=> <div style={{display:'grid',gap:28}}>
  <p style={{...note,color:INK}}>The solid build closes the stencil gaps so the O and S stay whole at small sizes. Sizes are heights; the width follows the 1.84 to 1 shape. In each pair the upper image is the full mark and the lower image is the solid build, at the same height, so the difference can be checked.</p>
  {[{ground:'#fff',dark:false,full:'mark-os.svg',solid:'mark-os-solid.svg',name:'colour'},{ground:NAVY,dark:true,full:'mark-os-inverse.svg',solid:'mark-os-solid-inverse.svg',name:'inverse'}].map(r=>
    <Tile key={r.name} caption={`Full build over solid build, ${r.name}`} ground={r.ground} dark={r.dark}>
      {[16,24,32,48].map(h=><div key={h} style={{display:'grid',gap:10,justifyItems:'start'}}>
        <img src={o+r.full} alt="" width={markW(h)} height={h}/>
        <img src={o+r.solid} alt={`OUTSPOKEN OS mark, solid small-size build, ${r.name}, ${h} pixels high`} width={markW(h)} height={h}/>
        <span style={{...label,color:r.dark?'#B9C7DA':INK}}>{h} px · {markW(h)} wide</span>
      </div>)}
    </Tile>)}
  <Tile caption="One colour solid build · mark-os-solid-mono.svg and mark-os-solid-mono-inverse.svg"><img src={o+'mark-os-solid-mono.svg'} alt="OUTSPOKEN OS mark, solid, one colour" width={markW(48)} height="48"/><span style={{background:NAVY,padding:12,borderRadius:8,display:'inline-flex'}}><img src={o+'mark-os-solid-mono-inverse.svg'} alt="OUTSPOKEN OS mark, solid, one colour, inverse" width={markW(48)} height="48"/></span></Tile></div>};

export const OsLockups:Story={name:'OS stencil lockups (horizontal): colour, inverse, mono',render:()=> <div style={{display:'grid',gap:28,justifyItems:'start'}}>
  <p style={{...note,color:INK}}>The OS mark with the unchanged V5 outlined wordmark: navy OUT and Nickel 600 SPOKEN on light grounds, #F2F5FA and #B9C7DA on deep navy. Natural size 437 by 72.</p>
  <Tile caption="Colour on white · lockup-os.svg"><img src={o+'lockup-os.svg'} alt="OUTSPOKEN lockup" width="437.3" height="72"/></Tile>
  <Tile caption="Inverse on deep navy #0D1A3B · lockup-os-inverse.svg (transparent, place on a navy ground)" ground={NAVY} dark><img src={o+'lockup-os-inverse.svg'} alt="OUTSPOKEN lockup, inverse" width="437.3" height="72"/></Tile>
  <Tile caption="Inverse with its own navy ground · lockup-os-inverse-ground.svg"><img src={o+'lockup-os-inverse-ground.svg'} alt="OUTSPOKEN lockup, inverse, on its own deep navy ground" width="437.3" height="72"/></Tile>
  <Tile caption="One colour, navy · lockup-os-mono.svg"><img src={o+'lockup-os-mono.svg'} alt="OUTSPOKEN lockup, one colour" width="437.3" height="72"/></Tile>
  <Tile caption="Reduced to 160 px wide, for a legibility check"><img src={o+'lockup-os.svg'} alt="OUTSPOKEN lockup reduced to 160 pixels wide" width="160" height="26.3"/></Tile></div>};

export const OsStackedLockups:Story={name:'OS stencil lockups (stacked): colour, inverse, mono',render:()=> <div style={{display:'flex',gap:24,flexWrap:'wrap',alignItems:'flex-start'}}>
  <Tile caption="Colour · lockup-os-stacked.svg"><img src={o+'lockup-os-stacked.svg'} alt="OUTSPOKEN stacked lockup" width="280" height="167.3"/></Tile>
  <Tile caption="Inverse · lockup-os-stacked-inverse.svg" ground={NAVY} dark><img src={o+'lockup-os-stacked-inverse.svg'} alt="OUTSPOKEN stacked lockup, inverse" width="280" height="167.3"/></Tile>
  <Tile caption="One colour · lockup-os-stacked-mono.svg"><img src={o+'lockup-os-stacked-mono.svg'} alt="OUTSPOKEN stacked lockup, one colour" width="280" height="167.3"/></Tile></div>};

export const OsAvatarAndFavicon:Story={name:'OS stencil avatar, favicon tile and touch icon',render:()=> <div style={{display:'grid',gap:28}}>
  <p style={{...note,color:INK}}>Avatar, favicon and touch icon use the light OS mark on a navy ground. The favicon at 16 px uses the gap-closed build (favicon-os-16.svg). The site head links favicon-os.ico, favicon-os-16.svg and apple-touch-os-180.png.</p>
  <div style={{display:'flex',gap:24,flexWrap:'wrap',alignItems:'flex-start'}}>
    <Tile caption="Avatar · avatar-os.svg at 160, 64 and 24 (avatar-os-24.svg)"><img src={o+'avatar-os.svg'} alt="OUTSPOKEN avatar" width="160" height="160"/><img src={o+'avatar-os.svg'} alt="OUTSPOKEN avatar, 64 pixels" width="64" height="64"/><img src={o+'avatar-os-24.svg'} alt="OUTSPOKEN avatar, 24 pixels" width="24" height="24"/></Tile>
    <Tile caption="Avatar raster · avatar-os-800.png (used as the site logo in structured data)"><img src={o+'avatar-os-800.png'} alt="OUTSPOKEN avatar, 800 pixel raster" width="160" height="160"/></Tile>
  </div>
  <div style={{display:'flex',gap:24,flexWrap:'wrap',alignItems:'flex-start'}}>
    <Tile caption="Favicon tile · favicon-os.svg at 64, 48 and 32"><img src={o+'favicon-os.svg'} alt="OUTSPOKEN favicon, 64 pixels" width="64" height="64"/><img src={o+'favicon-os.svg'} alt="OUTSPOKEN favicon, 48 pixels" width="48" height="48"/><img src={o+'favicon-os.svg'} alt="OUTSPOKEN favicon, 32 pixels" width="32" height="32"/></Tile>
    <Tile caption="Small build · favicon-os-16.svg at 16 and enlarged to 64"><img src={o+'favicon-os-16.svg'} alt="OUTSPOKEN favicon, small build, 16 pixels" width="16" height="16"/><img src={o+'favicon-os-16.svg'} alt="OUTSPOKEN favicon, small build, enlarged" width="64" height="64"/></Tile>
    <Tile caption="PNG fallbacks · favicon-os-16, 32, 48 and 64"><img src={o+'favicon-os-16.png'} alt="OUTSPOKEN favicon PNG, 16 pixels" width="16" height="16"/><img src={o+'favicon-os-32.png'} alt="OUTSPOKEN favicon PNG, 32 pixels" width="32" height="32"/><img src={o+'favicon-os-48.png'} alt="OUTSPOKEN favicon PNG, 48 pixels" width="48" height="48"/><img src={o+'favicon-os-64.png'} alt="OUTSPOKEN favicon PNG, 64 pixels" width="64" height="64"/></Tile>
    <Tile caption="Touch icon · apple-touch-os-180.png"><img src={o+'apple-touch-os-180.png'} alt="OUTSPOKEN touch icon" width="180" height="180"/></Tile>
  </div></div>};

export const OsAnimatedMark:Story={name:'OS stencil animated mark (reduced motion respected)',render:()=> <AnimatedMark/>};

export const Marks:Story={name:'B01 microphone marks (previous identity, replaced 2 November 2026)',render:()=> <div style={{display:'grid',gap:24}}>
 <p style={{...note,color:INK}}>Previous identity. The B01 microphone mark and lockup were replaced by the OS stencil family above. These files stay in the repository as history.</p>
 <div style={{display:'flex',gap:32,alignItems:'flex-end',flexWrap:'wrap'}}><img src={v+'mark-b01.svg'} alt="Previous OUTSPOKEN microphone mark, colour" width="160" height="212"/><div style={{background:'#162760',padding:20}}><img src={v+'mark-b01-inverse.svg'} alt="Previous OUTSPOKEN microphone mark, inverse" width="160" height="212"/></div><img src={v+'mark-b01-mono.svg'} alt="Previous OUTSPOKEN microphone mark, one colour" width="160" height="212"/></div>
 <div style={{display:'flex',gap:20,alignItems:'flex-end'}}>{[24,32,64,128].map(s=><img key={s} src={v+'mark-b01-24.svg'} alt="" width={s} height={s}/>)}</div>
 <div style={{display:'grid',gap:16,justifyItems:'start'}}><img src={v+'lockup-b01.svg'} alt="Previous OUTSPOKEN lockup" width="268" height="46"/><div style={{background:'#162760',padding:20}}><img src={v+'lockup-b01-inverse.svg'} alt="Previous OUTSPOKEN lockup, inverse" width="268" height="46"/></div></div></div>};
export const Icons:Story={render:()=> <div style={{display:'grid',gap:24}}>{[24,32,56].map(s=><div key={s} style={{display:'flex',gap:14,flexWrap:'wrap',color:'#162760'}}>{names.map(n=><Icon key={n} name={n} size={s}/>)}</div>)}<div style={{background:'#162760',color:'#F1F3F6',padding:20,display:'flex',gap:14,flexWrap:'wrap'}}>{names.map(n=><Icon key={n} name={n} size={40}/>)}</div></div>};
