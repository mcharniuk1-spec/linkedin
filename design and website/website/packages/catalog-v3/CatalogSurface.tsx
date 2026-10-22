import React from 'react';
import manifest from './manifest.json';
export type CatalogCategory = 'banner'|'poster'|'block'|'heading'|'video-frame'|'caption-emphasis'|'schema'|'publication';
export type CatalogSurfaceProps = { id: string; slots?: Record<string,string>; titleLines?: string[]; bodyLines?: string[]; eyebrow?: string; caption?: string; mediaSrc?: string; className?: string; ariaLabel?: string; style?: React.CSSProperties };
type RawGlob = (pattern:string,options:{query:string;import:string;eager:boolean})=>Record<string,string>;
const raw=(import.meta as ImportMeta & {glob:RawGlob}).glob('./masters/**/*.svg',{query:'?raw',import:'default',eager:true});
const assets:Record<string,string>={
 '05-real-human-shadow':'/assets/revisions/v3/nature/05-real-human-shadow.webp',
 '01-tidal-signal':'/assets/revisions/v3/nature/01-tidal-signal.webp',
 '02-resonance-field':'/assets/revisions/v3/nature/02-resonance-field.webp',
 '03-still-to-signal':'/assets/revisions/v3/nature/03-still-to-signal.webp'
};
const escape=(v:string)=>v.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
export const catalogEntries=manifest.entries;
export function CatalogSurface({id,slots={},titleLines,bodyLines,eyebrow,caption,mediaSrc,className,ariaLabel,style}:CatalogSurfaceProps){
 const entry=catalogEntries.find(e=>e.id===id);if(!entry)throw new Error('Unknown Outspoken catalog ID: '+id);
 let svg=raw['./'+entry.source];if(!svg)throw new Error('Missing Outspoken SVG master: '+entry.source);
 const values={...slots};titleLines?.forEach((s,i)=>values['title-'+i]=s);bodyLines?.forEach((s,i)=>values['body-'+i]=s);if(eyebrow)values.eyebrow=eyebrow;if(caption)values.caption=caption;
 svg=svg.replace(/(<text\b[^>]*data-slot="([^"]+)"[^>]*>)([\s\S]*?)(<\/text>)/g,(all,start,key,old,end)=>values[key]===undefined?all:start+escape(values[key])+end);
 svg=svg.replace(/<style>[\s\S]*?<\/style>/g,'');
 svg=svg.replace(/\.\.\/\.\.\/\.\.\/assets\/revisions\/v3\/nature\/([^"/]+)\.webp/g,(_m,key)=>assets[key]||'');
 svg=svg.replace(/\.\.\/\.\.\/\.\.\/assets\/revisions\/v2\/photos\/OS-PH205\.png/g,'/assets/revisions/v2/photos/OS-PH205.png');
 svg=svg.replace(/\.\.\/\.\.\/\.\.\/assets\/revisions\/v2\/paper\/OS-TX201\.png/g,'/assets/revisions/v2/paper/OS-TX201.png');
 if(mediaSrc){if(!/^(?:https?:\/\/|\/|\.\.\/|data:image\/(?:png|jpeg|webp);base64,)/.test(mediaSrc))throw new Error('Unsupported media URL');svg=svg.replace(/(<image\b[^>]*data-slot="media"[^>]*href=")[^"]+("[^>]*>)/g,'$1'+escape(mediaSrc)+'$2');}
 svg=svg.replace('<svg ','<svg style="width:100%;height:auto;display:block" ');
 return <div className={className} role="img" aria-label={ariaLabel||entry.use_when} data-catalog-id={id} style={{...style}} dangerouslySetInnerHTML={{__html:svg}}/>;
}
export const Banner=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
export const Poster=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
export const EditorialBlock=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
export const Heading=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
export const VideoFrame=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
export const CaptionEmphasis=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
export const Schema=(p:CatalogSurfaceProps)=><CatalogSurface {...p}/>;
