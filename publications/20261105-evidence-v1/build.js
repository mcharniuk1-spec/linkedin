/* Build original branded publication layouts from supplied, reviewable copy. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname;
const input=process.env.PUBLICATION_CONTENT || path.join(root,'content.json');
const output=process.env.PUBLICATION_OUTPUT || path.join(root,'output');
const verify=process.env.PUBLICATION_VERIFY || path.join(root,'verification');
const previous=path.join(root,'assets/source-art');
const fonts=path.join(root,'assets/source-fonts');
const logo=path.join(previous,'lockup.png');
const fontFiles=['fraunces-latin-full-normal.woff2','mona-sans-latin-wght-normal.woff2','geist-mono-latin-wght-normal.woff2','FRAUNCES-OFL.txt','MONA-OFL.txt','GEIST-OFL.txt'];
const items=JSON.parse(fs.readFileSync(input,'utf8'));
if(!Array.isArray(items)||items.length!==10)throw Error('Expected exactly 10 publication records');
const ids=new Set();
function safe(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;')}
function wrapped(value,max,maxlines){
 const source=String(value??'').trim();if(!source)throw Error('Missing required slide text');
 const rows=[];let line='';for(const word of source.split(/\s+/)){if(word.length>max+7)throw Error('Single token too long for slide: '+word.length);let candidate=(line+' '+word).trim();if(candidate.length>max&&line){rows.push(line);line=word}else line=candidate;}if(line)rows.push(line);
 if(rows.length>maxlines)throw Error(`Text exceeds ${maxlines} lines: ${source}`);return rows;
}
const text=(value,x,y,cls,width,lines,leading)=>wrapped(value,width,lines).map((t,i)=>`<text x="${x}" y="${y+i*leading}" class="${cls}">${safe(t)}</text>`).join('');
const uri=p=>'data:image/png;base64,'+fs.readFileSync(p).toString('base64');
const logoData=uri(logo), artwork={};
for(let i=1;i<=10;i++)for(const k of ['graphic','scene'])artwork[`${k}-${i}`]=uri(path.join(previous,`${k}-${String(i).padStart(2,'0')}.png`));
fs.mkdirSync(output,{recursive:true});fs.mkdirSync(verify,{recursive:true});
const svgDir=path.join(output,'source-svg');fs.mkdirSync(svgDir,{recursive:true});
const fontOut=path.join(output,'source-fonts');fs.mkdirSync(fontOut,{recursive:true});
for(const f of fontFiles)fs.copyFileSync(path.join(fonts,f),path.join(fontOut,f));
const css=`<style>.headline{font-family:Fraunces,Georgia,serif;font-size:66px;fill:#162760}.headlineLight{font-family:Fraunces,Georgia,serif;font-size:66px;fill:#fff}.body{font-family:'Mona Sans',Arial,sans-serif;font-size:31px;fill:#34466a}.bodyLight{font-family:'Mona Sans',Arial,sans-serif;font-size:31px;fill:#eef1f7}.mono{font-family:'Geist Mono',monospace;font-size:20px;letter-spacing:2px;fill:#824f19}.monoLight{font-family:'Geist Mono',monospace;font-size:20px;letter-spacing:2px;fill:#f6d591}.tag{font-family:'Mona Sans',Arial,sans-serif;font-size:24px;fill:#162760}.tagLight{font-family:'Mona Sans',Arial,sans-serif;font-size:24px;fill:#fff}.tiny{font-family:'Geist Mono',monospace;font-size:17px;letter-spacing:1px;fill:#52617f}.tinyLight{font-family:'Geist Mono',monospace;font-size:17px;letter-spacing:1px;fill:#d4dbea}.num{font-family:Fraunces,Georgia,serif;font-size:43px;fill:#162760}</style>`;
const jobs=[],documents=[],summary=[];
// Curated source-art variation across each deck; every source scene is fictional.
const scenePlan=[[1,3,4,6,10],[2,5,7,8,9],[3,1,6,10,5],[4,2,7,8,3],[5,4,2,6,10],[6],[7],[8],[9],[10]];
const graphicPlan=[[1,4,3,7,10],[2,9,8,4,1],[3,1,6,7,5],[4,2,7,8,3],[5,4,2,6,10],[6],[7],[8],[9],[10]];
const photoOffsets=[230,155,320,300,310,390,420,370,300,390];
for(let i=0;i<items.length;i++){
 const item=items[i], index=i+1, wanted=index<=5?'carousel':'single';
 if(!item||typeof item.id!=='string'||!/^\d\d-[a-z0-9-]+$/.test(item.id)||ids.has(item.id))throw Error('Invalid or duplicate id');ids.add(item.id);
 if(item.format!==wanted||!item.caption||!item.title)throw Error(`Invalid item ${item.id}`);
 const folder=path.join(output,item.id);fs.mkdirSync(folder,{recursive:true});fs.writeFileSync(path.join(folder,'caption.txt'),item.caption.trim()+'\n');
 const files={graphic:[],people:[]},source_art={graphic:[],people:[]};
 for(const variant of ['graphic','people']){
  const slides=item.variants?.[variant];const target=wanted==='carousel'?5:1;
  if(!Array.isArray(slides)||slides.length!==target)throw Error(`Expected ${target} slides: ${item.id}/${variant}`);
  for(let j=0;j<slides.length;j++){
   const slide=slides[j];if(!slide||!Array.isArray(slide.diagram)||slide.diagram.length<2||slide.diagram.length>4)throw Error(`Invalid diagram ${item.id}/${variant}/${j}`);
   const number=String(index).padStart(2,'0'), page=String(j+1).padStart(2,'0');
   const artIndex=variant==='people'?scenePlan[i][j]:graphicPlan[i][j];
   const dark=variant==='graphic'&&((index+j)%3===0);const bg=dark?'#101d42':((index+j)%3===1?'#f5f5f2':'#fffdfa');
   const h=wrapped(slide.headline,29,4), b=wrapped(slide.body,54,4);
   const artFirst=(index*7+j+(variant==='people'?1:0))%3===0&&h.length<=2&&b.length<=3;
   const headlineY=artFirst?650:245;
   const bodyY=headlineY+(h.length-1)*72+105;
   const bodyEnd=bodyY+(b.length-1)*42;if(!artFirst&&bodyEnd>690)throw Error(`Upper text overflow ${item.id}/${variant}/${j}`);
   const artY=artFirst?210:Math.max(535,bodyEnd+55), artH=350, dY=artFirst?Math.max(1000,bodyEnd+45):artY+380;
   if(dY+175>1235)throw Error(`Lower content overflow ${item.id}/${variant}/${j}`);
   const headline=dark?'headlineLight':'headline',body=dark?'bodyLight':'body',mono=dark?'monoLight':'mono',tiny=dark?'tinyLight':'tiny';
   let s=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350">${css}<defs><clipPath id="art"><rect x="65" y="${artY}" width="950" height="${artH}" rx="24"/></clipPath></defs><rect width="1080" height="1350" fill="${bg}"/>`;
   if(dark)s+=`<rect x="66" y="38" width="342" height="81" rx="16" fill="#ffffff"/>`;
   s+=`<image x="78" y="49" width="306" height="62" preserveAspectRatio="xMinYMid meet" xlink:href="${logoData}"/>`;
   s+=`<text x="70" y="172" class="${mono}">FOUNDER NOTES  /  ${number} · ${page}</text>`;
   s+=text(slide.headline,70,headlineY,headline,29,4,72);
   s+=text(slide.body,70,bodyY,body,54,4,42);
   const ornament=(index+j)%4;
   if(variant==='graphic'){
    const panel=dark?'#1a2c55':'#eef0f1';s+=`<rect x="65" y="${artY}" width="950" height="${artH}" rx="24" fill="${panel}"/>`;
    if(ornament===0)s+=`<circle cx="265" cy="${artY+155}" r="127" fill="none" stroke="#aab5cb" stroke-width="2"/><circle cx="265" cy="${artY+155}" r="98" fill="none" stroke="#eaa93c" stroke-width="2"/>`;
    if(ornament===1)s+=`<path d="M100 ${artY+220} C290 ${artY+15} 390 ${artY+300} 585 ${artY+75}" fill="none" stroke="#eaa93c" stroke-width="3"/>`;
    if(ornament===2)s+=`<rect x="115" y="${artY+55}" width="278" height="198" rx="25" fill="none" stroke="#eaa93c" stroke-width="3" transform="rotate(-8 255 ${artY+155})"/>`;
    if(ornament===3)s+=`<path d="M115 ${artY+275} H370 M115 ${artY+300} H295 M115 ${artY+325} H335" fill="none" stroke="#eaa93c" stroke-width="4"/>`;
    s+=`<image x="${(index+j)%2?445:80}" y="${artY+4}" width="540" height="${artH-8}" preserveAspectRatio="xMidYMid meet" xlink:href="${artwork[`graphic-${artIndex}`]}"/>`;
    const x=(index+j)%2?130:730;s+=`<rect x="${x-18}" y="${artY+78}" width="235" height="125" rx="12" fill="${panel}"/><text x="${x}" y="${artY+120}" class="${mono}">${j===0?'THE IDEA':'FIELD NOTE'}</text><text x="${x}" y="${artY+178}" class="${dark?'headlineLight':'headline'}">${number}.${page}</text>`;
   }else{
    s+=`<rect x="65" y="${artY}" width="950" height="${artH}" rx="24" fill="#d6dbe2"/><image x="65" y="${artY-photoOffsets[artIndex-1]}" width="950" height="1188" preserveAspectRatio="xMidYMid meet" clip-path="url(#art)" xlink:href="${artwork[`scene-${artIndex}`]}"/>`;
    s+=`<rect x="80" y="${artY+305}" width="254" height="31" rx="12" fill="#fff" fill-opacity=".96"/><text x="94" y="${artY+326}" class="tiny">ILLUSTRATIVE SCENE</text>`;
    if(ornament%2===0)s+=`<circle cx="930" cy="${artY+55}" r="23" fill="#eaa93c"/><path d="M922 ${artY+55} h16 M930 ${artY+47} v16" stroke="#162760" stroke-width="2"/>`;
   }
   const n=slide.diagram.length;const gap=14,w=(950-gap*(n-1))/n;
   for(let k=0;k<n;k++){
    const label=String(slide.diagram[k]);if(label.length>31||!label.trim())throw Error('Diagram label too long');
    const x=65+k*(w+gap),fill=k===(j% n)?'#f6d591':(dark?'#283c66':'#ffffff');
    s+=`<rect x="${x}" y="${dY}" width="${w}" height="90" rx="16" fill="${fill}"/><text x="${x+w/2}" y="${dY+36}" text-anchor="middle" class="${dark&&k!==(j%n)?'tagLight':'tag'}">`;
    const rows=wrapped(label,n===4?15:22,2);s+=rows.map((v,l)=>`<tspan x="${x+w/2}" dy="${l===0?0:28}">${safe(v)}</tspan>`).join('')+'</text>';
   }
   s+=`<text x="70" y="${dY+140}" class="${tiny}">CHECK THE CAPTION FOR CONTEXT AND EVIDENCE</text>`;
   s+=`<path d="M70 1253 H1010" stroke="${dark?'#61708e':'#c8d1df'}" stroke-width="2"/><text x="70" y="1293" class="${tiny}">OUTSPOKEN  /  FOUNDER-LED CONTENT</text><text x="1008" y="1293" text-anchor="end" class="${tiny}">POST ${number} · ${page}/${String(target).padStart(2,'0')}</text></svg>`;
   const basename=`${number}-${variant}-${page}`, svgPath=path.join(svgDir,basename+'.svg'), pngPath=path.join(folder,`${variant}-${page}.png`);
   const sourceName=`${variant==='people'?'scene':'graphic'}-${String(artIndex).padStart(2,'0')}.png`;
   fs.writeFileSync(svgPath,s);jobs.push({id:item.id,variant,svg:svgPath,png:pngPath,source_art:sourceName});files[variant].push(`${variant}-${page}.png`);source_art[variant].push(sourceName);
  }
  if(wanted==='carousel')documents.push({id:item.id,variant,images:files[variant].map(f=>path.join(folder,f)),pdf:path.join(folder,`${variant}-carousel.pdf`)});
 }
 summary.push({id:item.id,title:item.title,format:wanted,files,source_art,caption:'caption.txt',evidence:item.evidence??null,limitations:item.limitations??null});
}
fs.writeFileSync(path.join(verify,'render-jobs.json'),JSON.stringify(jobs,null,2));fs.writeFileSync(path.join(verify,'pdf-jobs.json'),JSON.stringify(documents,null,2));
const sourceAssets=Object.entries(artwork).map(([key,value])=>({id:key,sha256:crypto.createHash('sha256').update(Buffer.from(value.slice(value.indexOf(',')+1),'base64')).digest('hex'),provenance:'Earlier project-generated illustrative asset, 20261105 Outspoken personal editorial run',rights_state:'Project-generated; founder and rights review required',use:'Embedded unchanged in editable SVG; scene images depict fictional people.'}));
const hashFile=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify({status:'draft_founder_review',research_note:'No claim of 100 new posts; see evidence and limitations.',source_assets:sourceAssets,identity_asset:{sha256:hashFile(logo),provenance:'Existing project V13 lockup, inherited release; owner review required'},fonts:fontFiles.filter(f=>f.endsWith('.woff2')).map(f=>({path:'source-fonts/'+f,sha256:hashFile(path.join(fonts,f)),license:'SIL Open Font License; see adjacent license text'})),publications:summary},null,2));
const cards=summary.map(item=>`<section class="post"><div class="post-head"><div><div class="eyebrow">${safe(item.id)} · ${safe(item.format)}</div><h2>${safe(item.title)}</h2></div><a href="${encodeURIComponent(item.id)}/caption.txt">Download caption</a></div><details><summary>Read draft caption</summary><p class="caption">${safe(items.find(x=>x.id===item.id).caption)}</p></details><div class="variants">${['graphic','people'].map(v=>`<div><h3>${v==='graphic'?'Graphic direction':'People-led direction'}</h3>${v==='people'?'<p class="notice">People shown are fictional illustrative scenes.</p>':''}<div class="slides">${item.files[v].map((f,i)=>`<a href="${encodeURIComponent(item.id)}/${f}"><img loading="lazy" src="${encodeURIComponent(item.id)}/${f}" alt="${safe(item.title)}; ${v} version; page ${i+1}"></a>`).join('')}</div>${item.format==='carousel'?`<a class="download" href="${encodeURIComponent(item.id)}/${v}-carousel.pdf">Download five-page ${v} carousel</a>`:''}</div>`).join('')}</div><p class="source">Evidence: ${safe(Array.isArray(item.evidence)?item.evidence.join(' · '):item.evidence||'See source ledger')}<br>Limit: ${safe(Array.isArray(item.limitations)?item.limitations.join(' · '):item.limitations||'Founder review required.')}</p></section>`).join('');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Outspoken — publication draft board</title><style>@font-face{font-family:Fraunces;src:url('source-fonts/fraunces-latin-full-normal.woff2')}@font-face{font-family:Mona;src:url('source-fonts/mona-sans-latin-wght-normal.woff2')}*{box-sizing:border-box}body{margin:0;background:#f4f4f0;color:#162760;font-family:Mona,Arial,sans-serif}main{max-width:1400px;margin:auto;padding:48px 26px}h1,h2{font-family:Fraunces,Georgia,serif;font-weight:400}h1{font-size:clamp(42px,7vw,78px);max-width:850px;margin:.2em 0}h2{font-size:32px;margin:10px 0}h3{font-size:17px;text-transform:uppercase;letter-spacing:.07em}.eyebrow{font-size:12px;letter-spacing:.14em;color:#824f19;text-transform:uppercase}.intro{font-size:18px;max-width:830px;line-height:1.6}.notice,.source{font-size:14px;line-height:1.5;color:#566782}.post{padding:32px;margin:24px 0;background:#fff;border:1px solid #dce1e8;border-radius:20px}.post-head{display:flex;justify-content:space-between;gap:20px;align-items:center}.post-head a,.download{color:#162760;font-weight:600}summary{cursor:pointer;font-weight:600}.caption{white-space:pre-wrap;max-width:860px;line-height:1.65}.variants{display:grid;grid-template-columns:1fr 1fr;gap:24px}.slides{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory}.slides a{flex:0 0 min(300px,85%);scroll-snap-align:start}.slides img{display:block;width:100%;border-radius:8px;border:1px solid #d6dae2}.download{display:inline-block;margin-top:14px}.source{border-top:1px solid #e0e4eb;padding-top:18px}.review{border-left:4px solid #eaa93c;padding:12px 16px;background:#fff}@media(max-width:700px){main{padding:28px 14px}.variants{grid-template-columns:1fr}.post{padding:20px}.post-head{display:block}}</style></head><body><main><div class="eyebrow">OUTSPOKEN / CONTENT STUDIO</div><h1>Founder ideas, made visible.</h1><p class="intro">Ten draft publications for European B2B AI SaaS founders. Five have five-page carousels in two directions. Five are single images in two directions.</p><p class="review">DRAFT FOR FOUNDER REVIEW. Research is historical; no claim is made that 100 new LinkedIn posts were collected. Illustrative people are not customers.</p>${cards}</main></body></html>`;
fs.writeFileSync(path.join(output,'index.html'),html);
console.log(JSON.stringify({publication_count:summary.length,carousel_count:documents.length/2,png_jobs:jobs.length,pdf_jobs:documents.length}));
