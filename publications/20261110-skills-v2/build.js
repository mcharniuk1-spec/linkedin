/* Original editable publication composition. Shared artwork bytes stay unchanged. */
'use strict';
const fs=require('fs'), path=require('path'), crypto=require('crypto');
const root=__dirname, config=JSON.parse(fs.readFileSync(path.join(root,'build-config.json'),'utf8'));
const input=path.resolve(process.env.PUBLICATION_CONTENT||path.join(root,'content.json'));
const output=path.resolve(process.env.PUBLICATION_OUTPUT||path.join(root,config.output));
const review=path.resolve(process.env.PUBLICATION_REVIEW||path.join(root,config.review_output));
const assetRoot=path.resolve(process.env.ASSET_ROOT||path.join(root,config.shared_asset_root));
const canonicalAssetRoot=path.resolve(root,config.shared_asset_root);
const items=JSON.parse(fs.readFileSync(input,'utf8')), C=config.palette;
const W=1080,H=1350, margin=66, contentWidth=948;
const fonts=['fraunces-latin-full-normal.woff2','mona-sans-latin-wght-normal.woff2','geist-mono-latin-wght-normal.woff2'];
const scenePlan=[[1,3,4,6,10],[2,5,7,8,9],[3,1,6,10,5],[4,2,7,8,3],[5,4,2,6,10],[6],[7],[8],[9],[10]];
const graphicPlan=[[1,4,3,7,10],[2,9,8,4,1],[3,1,6,7,5],[4,2,7,8,3],[5,4,2,6,10],[6],[7],[8],[9],[10]];
const photoOffsets=[230,155,320,300,310,390,420,370,300,390];
function escape(v){return String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');}
function write(p,value){const temporary=p+'.writing-'+process.pid;fs.writeFileSync(temporary,value);fs.renameSync(temporary,p);}
function sha(p){return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');}
function relative(p){return path.relative(root,p).split(path.sep).join('/');}
function href(from,name){return path.relative(from,path.join(canonicalAssetRoot,name)).split(path.sep).join('/');}
// Conservative typographic estimate. The render/visual pass remains necessary.
function estimate(s,size){return [...s].reduce((n,c)=>n+(/[MW@%]/.test(c)?0.9:/[ilI.,'’ :;]/.test(c)?0.28:/[A-Z0-9]/.test(c)?0.64:0.53),0)*size;}
function wrap(value,size,width,maxLines,label){
 const valueString=String(value??'').trim();if(!valueString)throw Error('Missing '+label);
 const result=[];let current='';
 for(const word of valueString.split(/\s+/)){
  if(estimate(word,size)>width)throw Error('Unbreakable word exceeds '+label);
  const candidate=(current+' '+word).trim();if(current&&estimate(candidate,size)>width){result.push(current);current=word;}else current=candidate;
 }
 if(current)result.push(current);if(result.length>maxLines)throw Error(`${label} exceeds ${maxLines} lines: ${valueString}`);return result;
}
function text(lines,x,y,size,fill,family,leading,anchor='start'){
 return lines.map((s,i)=>`<text x="${x}" y="${y+i*leading}" font-family="${family}" font-size="${size}" font-weight="400" fill="${fill}" text-anchor="${anchor}">${escape(s)}</text>`).join('');
}
if(!Array.isArray(items)||items.length!==10)throw Error('Exactly ten publication records required');
fs.mkdirSync(output,{recursive:true});fs.mkdirSync(review,{recursive:true});const svgDir=path.join(output,'source-svg');fs.mkdirSync(svgDir,{recursive:true});
for(const f of fonts)if(!fs.existsSync(path.join(assetRoot,'source-fonts',f)))throw Error('Missing shared font '+f);
for(let i=1;i<=10;i++)for(const type of ['graphic','scene'])if(!fs.existsSync(path.join(assetRoot,'source-art',`${type}-${String(i).padStart(2,'0')}.png`)))throw Error('Missing shared source art');
if(!fs.existsSync(path.join(assetRoot,'source-art/lockup.png')))throw Error('Missing shared R13 lockup');
const jobs=[],pdfJobs=[],layout=[],publications=[],usedAssets=new Map(),ids=new Set();
for(let index=0;index<items.length;index++){
 const item=items[index],number=String(index+1).padStart(2,'0'),expected=index<5?5:1;
 if(!item.id||!/^\d\d-[a-z0-9-]+$/.test(item.id)||ids.has(item.id))throw Error('Invalid publication identity');ids.add(item.id);
 if(item.format!==(index<5?'carousel':'single')||!item.caption||!item.title)throw Error('Publication format/copy incomplete: '+item.id);
 const folder=path.join(output,item.id);fs.mkdirSync(folder,{recursive:true});write(path.join(folder,'caption.txt'),item.caption.trim()+'\n');
 const summary={id:item.id,title:item.title,format:item.format,caption:`${item.id}/caption.txt`,variants:{},evidence:item.evidence,limitations:item.limitations};
 for(const variant of ['graphic','people']){
  const panels=item.variants?.[variant];if(!Array.isArray(panels)||panels.length!==expected)throw Error('Panel count mismatch: '+item.id+'/'+variant);summary.variants[variant]=[];
  for(let panelIndex=0;panelIndex<panels.length;panelIndex++){
   const panel=panels[panelIndex],page=String(panelIndex+1).padStart(2,'0');
   if(!Array.isArray(panel.diagram)||panel.diagram.length<2||panel.diagram.length>4)throw Error('Two to four meaningful diagram labels required');
   const diagramType=panel.diagram_type||'comparison';if(!['sequence','comparison','checklist','unknown','mapping'].includes(diagramType))throw Error('Unknown diagram type');
   const dark=variant==='graphic'&&panelIndex>0&&(index+panelIndex)%3===0;
   const bg=dark?C.deep:((index+panelIndex)%2?C.warm:C.paper),ink=dark?C.white:C.navy,bodyInk=dark?'#EEF1F7':C.body;
   const headline=wrap(panel.headline,70,930,3,'headline'),body=wrap(panel.body,42,930,3,'body');
   const headlineY=225,bodyY=headlineY+(headline.length-1)*78+86,bodyEnd=bodyY+(body.length-1)*55;
   const artY=Math.max(535,bodyEnd+42),artH=350,artEnd=artY+artH;
   const diagramY=artEnd+34,diagramH=['checklist','mapping'].includes(diagramType)?170:126;
   const contextY=diagramY+diagramH+47;
   let context=String(panel.context||'Draft for founder review');
   if(item.id==='05-proof'&&!/hypothetical/i.test(context))throw Error('Every proof panel must retain its hypothetical context');
   const contextLines=wrap(context,32,930,2,'essential context');
   const contextEnd=contextY+(contextLines.length-1)*40;
   const cta=panel.cta?String(panel.cta):null;
   if(cta&&cta!=='Book an intro call')throw Error('Offer CTA must preserve approved wording');
   const ctaY=contextEnd+55,finalEnd=cta?ctaY+12:contextEnd+12;if(finalEnd>1228)throw Error('Content collides with footer: '+item.id+'/'+variant+'/'+page);
   const artNumber=variant==='people'?scenePlan[index][panelIndex]:graphicPlan[index][panelIndex];
   const sourceName=`${variant==='people'?'scene':'graphic'}-${String(artNumber).padStart(2,'0')}.png`;
   const sourceArt='source-art/'+sourceName,artHref=href(svgDir,sourceArt),logoHref=href(svgDir,'source-art/lockup.png');
   usedAssets.set(sourceArt,sha(path.join(assetRoot,sourceArt)));usedAssets.set('source-art/lockup.png',sha(path.join(assetRoot,'source-art/lockup.png')));
   const fontCSS=fonts.map((f,i)=>`@font-face{font-family:'${['Fraunces','Mona Sans','Geist Mono'][i]}';src:url('${href(svgDir,'source-fonts/'+f)}');font-weight:100 900;}`).join('');
   let svg=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350"><title>${escape(item.title)} — ${variant}, page ${panelIndex+1}</title><desc>${escape(panel.headline+' '+panel.body+' '+context+(variant==='people'?' People shown are fictional.':''))}</desc><style>${fontCSS}</style><defs><clipPath id="art"><rect x="66" y="${artY}" width="948" height="350" rx="22"/></clipPath><marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="5" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="${dark?C.pale:C.navy}" stroke-width="2"/></marker></defs><rect width="1080" height="1350" fill="${bg}"/>`;
   if(dark)svg+='<rect x="66" y="38" width="342" height="81" rx="14" fill="#FFFFFF"/>';
   svg+=`<image x="78" y="49" width="306" height="62" preserveAspectRatio="xMinYMid meet" xlink:href="${logoHref}"/>`;
   svg+=text([`FOUNDER NOTES / ${number} · ${page}`],70,161,24,dark?C.pale:'#824F19','Geist Mono',30);
   svg+=text(headline,70,headlineY,70,ink,'Fraunces',78)+text(body,70,bodyY,42,bodyInk,'Mona Sans',55);
   if(variant==='graphic'){
    const plate=dark?'#1A2C55':'#E9EEF1';svg+=`<rect x="66" y="${artY}" width="948" height="350" rx="22" fill="${plate}"/><path d="M110 ${artY+205} C245 ${artY+40} 365 ${artY+220} 520 ${artY+80}" fill="none" stroke="${C.marigold}" stroke-width="3"/><image x="${(index+panelIndex)%2?535:76}" y="${artY+4}" width="460" height="342" preserveAspectRatio="xMidYMid meet" xlink:href="${artHref}"/>`;
    const x=(index+panelIndex)%2?110:650;svg+=text([panelIndex===0?'THE IDEA':'FIELD NOTE'],x,artY+94,24,dark?C.pale:'#824F19','Geist Mono',28)+text([`${number}.${page}`],x,artY+158,58,ink,'Fraunces',65);
   }else{
    svg+=`<rect x="66" y="${artY}" width="948" height="350" rx="22" fill="#DAE0E6"/><image x="66" y="${artY-photoOffsets[artNumber-1]}" width="948" height="1188" preserveAspectRatio="xMidYMid meet" clip-path="url(#art)" xlink:href="${artHref}"/><rect x="80" y="${artY+298}" width="405" height="42" rx="10" fill="#FFFFFF" fill-opacity=".97"/>`;
    svg+=text(['ILLUSTRATIVE SCENE'],94,artY+329,30,C.navy,'Geist Mono',34);
   }
   const labels=panel.diagram.map(String),n=labels.length;
   if(diagramType==='mapping'){
    if(n!==2)throw Error('Mapping requires exactly two independent source-to-target rows');
    const arrowGap=54,boxW=(contentWidth-arrowGap)/2,boxH=74,rowGap=18;
    for(let row=0;row<labels.length;row++){
     const pair=labels[row].split(/\s*(?:→|->)\s*/);if(pair.length!==2||pair.some(x=>!x.trim()))throw Error('Mapping row must contain one source → target pair');
     const y=diagramY+row*(boxH+rowGap),neutralFill=dark?'#283C66':C.white;
     for(let col=0;col<2;col++){
      const x=margin+col*(boxW+arrowGap),isUnknown=/\bUNKNOWN\b/i.test(pair[col]);
      svg+=`<rect x="${x}" y="${y}" width="${boxW}" height="${boxH}" rx="13" fill="${neutralFill}" stroke="${isUnknown?C.marigold:'none'}" stroke-width="3" ${isUnknown?'stroke-dasharray="10 7"':''}/>`;
      const ls=wrap(pair[col],32,boxW-28,2,'mapping label'),labelY=y+boxH/2-(ls.length-1)*18+11;
      svg+=text(ls,x+boxW/2,labelY,32,ink,'Mona Sans',36,'middle');
     }
     const begin=margin+boxW+8,end=margin+boxW+arrowGap-10,arrowY=y+boxH/2,arrowInk=dark?C.pale:C.navy;
     svg+=`<path d="M${begin} ${arrowY} H${end}" stroke="${arrowInk}" stroke-width="3"/><path d="M${end-8} ${arrowY-6} L${end} ${arrowY} L${end-8} ${arrowY+6}" fill="none" stroke="${arrowInk}" stroke-width="3"/>`;
    }
   }else{
    const gap=diagramType==='sequence'?38:18,columns=diagramType==='checklist'?2:n,boxW=(contentWidth-gap*(columns-1))/columns,boxH=diagramType==='checklist'?74:126;
    const neutral=['comparison','checklist'].includes(diagramType);
    for(let k=0;k<n;k++){
     const x=margin+(k%columns)*(boxW+gap),y=diagramY+Math.floor(k/columns)*(boxH+18);
     const unknown=diagramType==='unknown'&&k===n-1;
     const fill=neutral?(dark?'#283C66':C.white):(unknown?(dark?'#1A2C55':C.white):(k===0?C.pale:(dark?'#283C66':C.white)));
     const labelInk=neutral||unknown?ink:(k===0?C.navy:ink);
     svg+=`<rect x="${x}" y="${y}" width="${boxW}" height="${boxH}" rx="13" fill="${fill}" stroke="${unknown?C.marigold:'none'}" stroke-width="3" ${unknown?'stroke-dasharray="10 7"':''}/>`;
     const ls=wrap(labels[k],32,boxW-24,3,'diagram label'),labelY=y+boxH/2-(ls.length-1)*20+11;
     svg+=text(ls,x+boxW/2,labelY,32,labelInk,'Mona Sans',40,'middle');
     if(diagramType==='sequence'&&k<n-1){
      const arrowEnd=x+boxW+gap-8,arrowY=y+boxH/2,arrowInk=dark?C.pale:C.navy;
      svg+=`<path d="M${x+boxW+5} ${arrowY} H${arrowEnd}" stroke="${arrowInk}" stroke-width="3"/><path d="M${arrowEnd-8} ${arrowY-6} L${arrowEnd} ${arrowY} L${arrowEnd-8} ${arrowY+6}" fill="none" stroke="${arrowInk}" stroke-width="3"/>`;
     }
     if(diagramType==='checklist')svg+=`<circle cx="${x+18}" cy="${y+17}" r="5" fill="${C.marigold}"/>`;
    }
   }
   svg+=text(contextLines,70,contextY,32,bodyInk,'Mona Sans',40);
   if(cta)svg+=text([cta],70,ctaY,40,ink,'Mona Sans',46);
   svg+=`<path d="M70 1251 H1010" stroke="${dark?'#61708E':C.line}" stroke-width="2"/>`+text(['OUTSPOKEN / DRAFT FOR FOUNDER REVIEW'],70,1293,22,dark?'#D4DBEA':'#52617F','Geist Mono',26)+text([`${number} · ${page}/${String(expected).padStart(2,'0')}`],1008,1293,22,dark?'#D4DBEA':'#52617F','Geist Mono',26,'end')+'</svg>';
   const svgPath=path.join(svgDir,`${number}-${variant}-${page}.svg`),pngPath=path.join(folder,`${variant}-${page}.png`);write(svgPath,svg);
   jobs.push({id:item.id,variant,page:panelIndex+1,svg:relative(svgPath),png:relative(pngPath)});
   summary.variants[variant].push({image:`${item.id}/${variant}-${page}.png`,svg:`source-svg/${number}-${variant}-${page}.svg`,source_art:`${config.shared_asset_root}/${sourceArt}`,headline:panel.headline,body:panel.body,diagram:labels,diagram_type:diagramType,context,cta});
   layout.push({id:item.id,variant,page:panelIndex+1,headline_lines:headline.length,body_lines:body.length,art_y:artY,diagram_y:diagramY,context_end:contextEnd,final_content_end:finalEnd,footer_y:1251,min_essential_font_px:30,illustrative:variant==='people'});
  }
  if(expected===5)pdfJobs.push({id:item.id,variant,images:summary.variants[variant].map(x=>relative(path.join(output,x.image))),pdf:relative(path.join(folder,`${variant}-carousel.pdf`))});
 }
 publications.push(summary);
}
if(jobs.length!==60||pdfJobs.length!==10)throw Error('Incomplete export job set');
write(path.join(review,'render-jobs.json'),JSON.stringify(jobs,null,2)+'\n');write(path.join(review,'pdf-jobs.json'),JSON.stringify(pdfJobs,null,2)+'\n');write(path.join(review,'layout-checks.json'),JSON.stringify({status:'PASS',scope:'Conservative line/layout arithmetic; actual render/visual review required',panels:layout},null,2)+'\n');
write(path.join(output,'manifest.json'),JSON.stringify({schema:'outspoken-publication-layout/2',status:'draft_founder_review',canvas:{width:W,height:H},source_content_sha256:sha(input),shared_asset_root:config.shared_asset_root,source_assets:[...usedAssets].map(([name,sha256])=>({path:`${config.shared_asset_root}/${name}`,sha256,reuse:'Unchanged earlier project-owned pixels; prior release ledger controls rights.'})),fonts:fonts.map(name=>({path:`${config.shared_asset_root}/source-fonts/${name}`,sha256:sha(path.join(assetRoot,'source-fonts',name))})),publications},null,2)+'\n');
function detailHTML(value){
 if(value===null||value===undefined)return '';
 if(Array.isArray(value))return '<ul>'+value.map(x=>'<li>'+detailHTML(x)+'</li>').join('')+'</ul>';
 if(typeof value==='object')return '<dl>'+Object.entries(value).map(([key,v])=>'<dt><strong>'+escape(key.replaceAll('_',' '))+'</strong></dt><dd>'+detailHTML(v)+'</dd>').join('')+'</dl>';
 return escape(value);
}
// Text alternatives are a source-bound handoff, not a tagged-PDF claim.
const alternativePath=path.join(root,'accessibility/alt-text.json');
const alternativePackage=fs.existsSync(alternativePath)?JSON.parse(fs.readFileSync(alternativePath,'utf8')):null;
const alternativesCurrent=alternativePackage?.source_content_sha256===sha(input)&&alternativePackage.records?.length===jobs.length&&alternativePackage.records.every(x=>fs.existsSync(path.join(root,x.asset))&&fs.existsSync(path.join(root,x.source_svg))&&sha(path.join(root,x.asset))===x.asset_sha256&&sha(path.join(root,x.source_svg))===x.source_svg_sha256);
const alternativeMap=new Map(alternativesCurrent?alternativePackage.records.map(x=>[x.asset.replace(/^assets\//,''),x.alt_text]):[]);
function imageAlternative(panel){return alternativeMap.get(panel.image)||panel.headline+' '+panel.body+' '+panel.context;}
const cards=publications.map(x=>`<article><p class="label">${escape(x.id)} · ${escape(x.format)}</p><h2>${escape(x.title)}</h2>${alternativesCurrent?`<p><a href="../accessibility/transcripts.html#${x.id}">Read full text for ${escape(x.title)}</a></p>`:''}<details><summary>Caption and source limits</summary><p class="caption">${escape(items.find(y=>y.id===x.id).caption)}</p><h3>Claims and sources</h3>${detailHTML(x.evidence)}<h3>Limits</h3>${detailHTML(x.limitations)}</details><div class="variants">${['graphic','people'].map(v=>`<section><h3>${v==='graphic'?'Graphic direction':'People-led direction'}</h3>${v==='people'?'<p>Illustrative people; not customers or founders.</p>':''}<div class="slides">${x.variants[v].map((p,i)=>`<a href="${escape(p.image)}"><img src="${escape(p.image)}" alt="${escape(imageAlternative(p))}" loading="lazy" width="1080" height="1350"></a>`).join('')}</div>${x.format==='carousel'?`<a href="${x.id}/${v}-carousel.pdf">Five-page PDF</a>`:''}</section>`).join('')}</div></article>`).join('');
write(path.join(output,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Outspoken publication review</title><style>@font-face{font-family:Mona;src:url('${path.relative(output,path.join(canonicalAssetRoot,'source-fonts/'+fonts[1])).split(path.sep).join('/')}')}body{margin:0;background:#f6f7f9;color:#162760;font:17px/1.6 Mona,Arial,sans-serif}main{max-width:1350px;margin:auto;padding:35px 22px}h1,h2{font-family:Georgia,serif;line-height:1.2}h1{font-size:48px}article{background:white;border:1px solid #d6dde7;border-radius:20px;margin:30px 0;padding:28px}.label{font-size:13px;text-transform:uppercase;letter-spacing:.1em}summary{cursor:pointer}.caption{white-space:pre-wrap;max-width:850px}.variants{display:grid;grid-template-columns:1fr 1fr;gap:25px}.slides{display:flex;gap:10px;overflow:auto}.slides a{flex:0 0 min(390px,90%)}img{display:block;width:100%;height:auto;border:1px solid #d6dde7;border-radius:8px}a{color:#162760}@media(max-width:700px){.variants{grid-template-columns:1fr}article{padding:16px}main{padding:20px 12px}}</style><main><p class="label">OUTSPOKEN / REVIEW EDITION</p><h1>Founder ideas, made visible.</h1><p>Ten draft publications. Existing R13 art and typography, clearer evidence and larger supporting text. Founder approval remains pending; fictional people remain labelled. No promise of viral reach.</p>${cards}</main></html>`);
console.log(JSON.stringify({publications:publications.length,panels:jobs.length,pdfs:pdfJobs.length,source_svg:'light relative references',content_sha256:sha(input)}));
