import React from 'react';
import type {Meta,StoryObj} from '@storybook/react-vite';
import {CatalogSurface,catalogEntries} from './CatalogSurface';
const meta={title:'Outspoken/V3/Editable Catalog',component:CatalogSurface,args:{id:'OS-BA3-01'},parameters:{layout:'padded'},argTypes:{id:{control:'select',options:catalogEntries.map(x=>x.id)}}} satisfies Meta<typeof CatalogSurface>;
export default meta;type Story=StoryObj<typeof meta>;
export const Editable:Story={args:{id:'OS-BA3-01',eyebrow:'Buyer context',titleLines:['Make the buyer’s','question visible.'],bodyLines:['Start with the task. Name the decision.']}};
function Gallery({category}:{category:string}){return <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(320px,1fr))',gap:24}}>{catalogEntries.filter(x=>x.category===category).map(x=><section key={x.id}><CatalogSurface id={x.id}/><p>{x.id} · {x.layout}</p><p>{x.use_when}</p></section>)}</div>}
export const Banners:Story={render:()=> <Gallery category="banner"/>};
export const Posters:Story={render:()=> <Gallery category="poster"/>};
export const Blocks:Story={render:()=> <Gallery category="block"/>};
export const Headings:Story={render:()=> <Gallery category="heading"/>};
export const VideoFrames:Story={render:()=> <Gallery category="video-frame"/>};
export const CaptionsAndEmphasis:Story={render:()=> <Gallery category="caption-emphasis"/>};
export const Schemas:Story={render:()=> <Gallery category="schema"/>};
export const Publications:Story={render:()=> <Gallery category="publication"/>};
