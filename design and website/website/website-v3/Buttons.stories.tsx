import type {Meta,StoryObj} from '@storybook/react-vite';
import './website.css';
import './button.css';
const arrow=<svg viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M3 11 11 3M5 3h6v6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const tones=['','marigold','silver','outline'] as const;
const meta={title:'V10/Buttons',parameters:{layout:'padded'},tags:['autodocs']} satisfies Meta;export default meta;type Story=StoryObj<typeof meta>;
export const OnLight:Story={render:()=> <div style={{display:'grid',gap:16,justifyItems:'start'}}>{tones.map(t=><div key={t||'navy'} style={{display:'flex',gap:12,flexWrap:'wrap'}}>
 <button className={'os-btn'+(t?' os-btn--'+t:'')}>Book an intro call{arrow}</button>
 <button className={'os-btn'+(t?' os-btn--'+t:'')} disabled>Disabled</button>
 <button className={'os-btn is-loading'+(t?' os-btn--'+t:'')}>Sending{arrow}</button></div>)}</div>};
export const OnDark:Story={render:()=> <div className="dark-surface" style={{background:'#0E1A47',padding:32,display:'flex',gap:12,flexWrap:'wrap'}}><button className="os-btn os-btn--marigold">Book an intro call{arrow}</button><button className="os-btn os-btn--on-dark">Explore the services{arrow}</button></div>};
