import type {CSSProperties} from 'react';
import {tokens} from '../tokens/generated/tokens';
import '../../website-v3/brand-r13.css';

/*
 * R13 identity section (2 November 2026, proposed, owner acceptance not recorded).
 * The OS stencil mark is rebuilt as vector from a Codex concept (LOGO-03 left).
 * The wordmark is the unchanged V5 outline. Every file below is served from /assets/identity/v13/.
 * The earlier B01 microphone identity (V10) stays listed as history.
 */
const V13='/assets/identity/v13/';
const V10='/assets/identity/v10/';
/** Mark aspect from the viewBox 184.16 x 100. */
const RATIO=184.16/100;
/** Marigold slash bounding box in mark units (measured with getBBox): 43.28 x 23.35 at (87.76, 75.58). Clear space x = 23.35 % of the mark height. */
const sizes=[16,24,32,48] as const;
export type IdentityR13View={id:string;src:string;label:string};
export type IdentityR13Props={
  /** Horizontal light lockup; the page passes the served OS lockup. */
  lockupSrc?:string;
  /** Earlier microphone model views, kept behind a disclosure as history. */
  earlierViews?:IdentityR13View[];
  /** Extruded V5 wordmark views; the wordmark itself is unchanged. */
  wordmarkViews?:IdentityR13View[];
};

type Ground='light'|'pearl'|'dark';
const markFamily:{file:string;label:string;ground:Ground;alt:string}[]=[
  {file:'mark-os.svg',label:'Colour',ground:'light',alt:'OS stencil mark in colour on a white ground'},
  {file:'mark-os-inverse.svg',label:'Inverse',ground:'dark',alt:'OS stencil mark, inverse pair on a deep navy ground'},
  {file:'mark-os-mono.svg',label:'Mono',ground:'pearl',alt:'OS stencil mark in one navy ink on a pearl ground'},
  {file:'mark-os-mono-inverse.svg',label:'Mono inverse',ground:'dark',alt:'OS stencil mark in one light ink on a deep navy ground'}
];
const sizeRows:{id:string;file:string;label:string;note:string;ground:Ground}[]=[
  {id:'stencil',file:'mark-os.svg',label:'Stencil mark',note:'Light ground',ground:'light'},
  {id:'solid',file:'mark-os-solid.svg',label:'Solid build',note:'Gaps closed · light ground',ground:'light'},
  {id:'solid-inverse',file:'mark-os-solid-inverse.svg',label:'Solid build',note:'Gaps closed · dark ground',ground:'dark'}
];
const lockups:{file:string;label:string;ground:Ground;kind:'wide'|'stacked';alt:string}[]=[
  {file:'lockup-os.svg',label:'Horizontal · light',ground:'light',kind:'wide',alt:'OUTSPOKEN horizontal lockup on a white ground'},
  {file:'lockup-os-inverse.svg',label:'Horizontal · dark',ground:'dark',kind:'wide',alt:'OUTSPOKEN horizontal lockup, inverse pair on a deep navy ground'},
  {file:'lockup-os-stacked.svg',label:'Stacked · light',ground:'light',kind:'stacked',alt:'OUTSPOKEN stacked lockup on a white ground'},
  {file:'lockup-os-stacked-inverse.svg',label:'Stacked · dark',ground:'dark',kind:'stacked',alt:'OUTSPOKEN stacked lockup, inverse pair on a deep navy ground'},
  {file:'lockup-os-mono.svg',label:'Horizontal · mono',ground:'pearl',kind:'wide',alt:'OUTSPOKEN horizontal lockup in one navy ink'},
  {file:'lockup-os-stacked-mono.svg',label:'Stacked · mono',ground:'pearl',kind:'stacked',alt:'OUTSPOKEN stacked lockup in one navy ink'}
];
const roles:{name:string;hex:string;role:string;note:string;proposed?:boolean;dark?:boolean}[]=[
  {name:'Navy',hex:tokens['palette.navy'],role:'The O and OUT on light grounds',note:'14.06:1 on white'},
  {name:'Nickel 600',hex:tokens['palette.silver-600'],role:'The S and SPOKEN on light grounds',note:'4.56:1 on pearl · 5.07:1 on white',proposed:true},
  {name:'Marigold',hex:tokens['palette.marigold-500'],role:'The slash',note:'Graphic only'},
  {name:'Inverse light',hex:tokens['palette.inverse-light'],role:'The O and OUT on dark grounds',note:'15.65:1 on deep navy',proposed:true},
  {name:'Inverse silver',hex:tokens['palette.inverse-silver'],role:'The S and SPOKEN on dark grounds',note:'9.97:1 on deep navy',proposed:true},
  {name:'Deep navy',hex:tokens['palette.navy-deep'],role:'Dark ground, not a text colour',note:'Carries the inverse pair',proposed:true,dark:true}
];

function Swatch({name,hex,role,note,proposed,dark}:typeof roles[number]){
  return <li className="os13-swatch" data-proposed={proposed?'true':undefined}>
    <span className="os13-swatch__chip" data-dark={dark?'true':undefined} style={{background:hex}} aria-hidden="true"/>
    <span className="os13-swatch__text"><strong>{name}{proposed?<em className="os13-tag">Proposed</em>:null}</strong><code>{hex}</code><span>{role}</span><small>{note}</small></span>
  </li>;
}

export function IdentityR13({lockupSrc=V13+'lockup-os.svg',earlierViews=[],wordmarkViews=[]}:IdentityR13Props){
  const x=`calc(var(--w) * ${(100/184.16).toFixed(5)} * 0.2335)`;
  return <div className="os13 os13-root" data-release="r13-proposed">
    <div className="os13-hero">
      <div className="os13-hero__copy">
        <p className="os13-status"><span className="os13-chip">Proposed · R13 · 2 November 2026</span><span>Not yet accepted by the owner</span></p>
        <img className="os13-hero__lockup" src={lockupSrc} alt="OUTSPOKEN lockup: OS stencil mark with the V5 outlined wordmark" width="437" height="72"/>
        <p className="os13-p">A stencil <b>O</b> in navy, a Nickel <b>S</b> and one marigold slash. The letters are the logo, cut as a stencil, with the V5 outlined wordmark beside them.</p>
        <p className="os13-p os13-p--quiet">Everything below is a served vector master. The rules at the end say how to use it.</p>
      </div>
      <figure className="os13-fig os13-stage" aria-label="OS stencil mark, large">
        <div className="os13-stage__art"><img src={V13+'mark-os.svg'} alt="OS stencil mark in colour, large" width="737" height="400"/></div>
        <figcaption><strong>The mark</strong><code>mark-os.svg</code><span>Animated entrance: mark-os-animated.svg</span></figcaption>
      </figure>
    </div>

    <div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">01 / Mark family</p><h3 className="os13-h">Colour, inverse, mono.</h3></div>
      <div className="os13-grid os13-grid--4">
        {markFamily.map(m=><figure className="os13-fig os13-tile" data-ground={m.ground} key={m.file}>
          <div className="os13-tile__art"><img src={V13+m.file} alt={m.alt} width="184" height="100" style={{width:'min(100%,168px)',height:'auto'}}/></div>
          <figcaption><strong>{m.label}</strong><code>{m.file}</code></figcaption>
        </figure>)}
      </div>
    </div>

    <div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">02 / Small sizes</p><h3 className="os13-h">The solid build for small sizes.</h3>
        <p className="os13-p">Shown at real size in CSS pixels. Sizes are the height of the mark. The solid build closes the stencil gaps so they do not fill in or turn grey.</p></div>
      <div className="os13-sizes" role="group" aria-label="Mark at 16, 24, 32 and 48 pixels high">
        {sizeRows.map(r=><div className="os13-sizes__row" data-ground={r.ground} key={r.id}>
          <p className="os13-sizes__name"><strong>{r.label}</strong><span>{r.note}</span></p>
          <div className="os13-sizes__run">
            {sizes.map(s=><figure className="os13-fig os13-size" key={s}>
              <img src={V13+r.file} alt={`${r.label} at ${s} pixels high, ${r.note.toLowerCase()}`} height={s} width={Math.round(s*RATIO*10)/10} style={{height:s,width:'auto'}} data-size={s}/>
              <figcaption>{s} px</figcaption>
            </figure>)}
          </div>
        </div>)}
      </div>
    </div>

    <div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">03 / Lockups</p><h3 className="os13-h">Horizontal and stacked.</h3></div>
      <div className="os13-grid os13-grid--2">
        {lockups.map(l=><figure className="os13-fig os13-tile os13-tile--lockup" data-ground={l.ground} data-kind={l.kind} key={l.file}>
          <div className="os13-tile__art"><img src={l.file==='lockup-os.svg'?lockupSrc:V13+l.file} alt={l.alt} style={{width:l.kind==='wide'?'min(100%,380px)':'min(100%,240px)',height:'auto'}}/></div>
          <figcaption><strong>{l.label}</strong><code>{l.file}</code></figcaption>
        </figure>)}
      </div>
    </div>

    <div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">04 / Avatar and favicon</p><h3 className="os13-h">Small formats.</h3></div>
      <div className="os13-grid os13-grid--2">
        <figure className="os13-fig os13-tile os13-tile--small" data-ground="pearl">
          <div className="os13-tile__art os13-tile__art--row">
            {([[144,'avatar-os.svg'],[64,'avatar-os.svg'],[32,'avatar-os.svg'],[24,'avatar-os-24.svg']] as const).map(([s,f])=><span className="os13-pick" key={s+f}>
              <span className="os13-avatar" style={{'--s':s+'px'} as CSSProperties}><img src={V13+f} alt={`OS avatar, circle crop at ${s} pixels`} width={s} height={s}/></span>
              <small>{s} px</small>
            </span>)}
          </div>
          <figcaption><strong>Avatar · circle crop</strong><code>avatar-os.svg · avatar-os-24.svg</code></figcaption>
        </figure>
        <figure className="os13-fig os13-tile os13-tile--small" data-ground="pearl">
          <div className="os13-tile__art os13-tile__art--row">
            {([[64,'favicon-os.svg','tile'],[32,'favicon-os.svg','tile'],[16,'favicon-os-16.svg','tile'],[80,'apple-touch-os.svg','touch']] as const).map(([s,f,k])=><span className="os13-pick" key={s+f}>
              <img className={k==='touch'?'os13-touch':'os13-tile-icon'} src={V13+f} alt={k==='touch'?'Apple touch icon':`Favicon tile at ${s} pixels`} width={s} height={s} style={{width:s,height:s}}/>
              <small>{k==='touch'?'Touch 180':s+' px'}</small>
            </span>)}
          </div>
          <figcaption><strong>Favicon tile</strong><code>favicon-os.svg · favicon-os-16.svg · apple-touch-os.svg</code></figcaption>
        </figure>
      </div>
    </div>

    <div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">05 / Usage</p><h3 className="os13-h">Six rules for the mark.</h3></div>
      <div className="os13-usage">
        <figure className="os13-fig os13-clear" style={{'--w':'clamp(170px,56vw,268px)'} as CSSProperties}>
          <div className="os13-clear__box" style={{'--xs':x} as CSSProperties}>
            <div className="os13-clear__mark">
              <img src={V13+'mark-os.svg'} alt="OS stencil mark with its clear space marked" width="184" height="100"/>
              <span className="os13-clear__slash" aria-hidden="true"/>
            </div>
            {(['t','r','b','l'] as const).map(s=><i className="os13-clear__x" data-side={s} key={s} aria-hidden="true">x</i>)}
          </div>
          <figcaption><strong>Clear space</strong><span>x is the height of the marigold slash. Keep x free on every side.</span></figcaption>
        </figure>
        <ol className="os13-rules" aria-label="Usage rules">
          <li><strong>Size.</strong> Use the stencil mark at 48 px and above. Below 48 px, use the solid build.</li>
          <li><strong>Wordmark.</strong> The wordmark stays the unchanged V5 outline. Never re-typeset it.</li>
          <li><strong>Colour.</strong> Nickel 600 sets the S and SPOKEN on light grounds. On dark grounds use the inverse pair, #F2F5FA and #B9C7DA.</li>
          <li><strong>Clear space.</strong> Keep clear space equal to the height of the marigold slash on every side.</li>
          <li><strong>Origin.</strong> Rebuilt as vector from a Codex concept (LOGO-03 left). Proposed. Not yet accepted by the owner.</li>
          <li><strong>Earlier version.</strong> The previous B01 microphone identity is the earlier version. It is listed below.</li>
        </ol>
      </div>
      <ul className="os13-roles" aria-label="Colour roles">{roles.map(r=><Swatch key={r.name} {...r}/>)}</ul>
    </div>

    <div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">06 / Earlier version</p><h3 className="os13-h">The B01 microphone identity.</h3>
        <p className="os13-p">The microphone mark with the same V5 outlined wordmark. Replaced in this proposal. It stays in the repository as history and is not removed.</p></div>
      <div className="os13-earlier">
        <figure className="os13-fig os13-tile os13-earlier__lockup" data-ground="light"><div className="os13-tile__art"><img src={V10+'lockup-b01.svg'} alt="Earlier OUTSPOKEN lockup with the B01 microphone mark" style={{width:'min(100%,360px)',height:'auto'}}/></div><figcaption><strong>B01 lockup · V10</strong><code>identity/v10/lockup-b01.svg</code></figcaption></figure>
        <figure className="os13-fig os13-tile os13-earlier__mark" data-ground="light"><div className="os13-tile__art"><img src={V10+'mark-b01.svg'} alt="Earlier B01 microphone mark" style={{height:'110px',width:'auto'}}/></div><figcaption><strong>B01 mark · V10</strong><code>identity/v10/mark-b01.svg</code></figcaption></figure>
      </div>
      {earlierViews.length?<details className="os13-details"><summary>Earlier microphone model views ({earlierViews.length})</summary>
        <div className="os13-views">{earlierViews.map(v=><figure className="os13-fig" key={v.id}><img src={v.src} alt={v.label} loading="lazy"/><figcaption>{v.label}</figcaption></figure>)}</div></details>:null}
    </div>

    {wordmarkViews.length?<div className="os13-block">
      <div className="os13-block__head"><p className="os13-label">07 / Wordmark views</p><h3 className="os13-h">Lettering with substance.</h3>
        <p className="os13-p">Actual extruded wordmark views. The V5 outline is unchanged. Keep the vector master and native text separate for editing.</p></div>
      <div className="os13-views os13-views--word">{wordmarkViews.map(v=><figure className="os13-fig" key={v.id}><img src={v.src} alt={v.label} loading="lazy"/><figcaption>{v.label}</figcaption></figure>)}</div>
    </div>:null}
  </div>;
}
