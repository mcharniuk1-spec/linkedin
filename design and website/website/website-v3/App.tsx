import {useEffect,useRef,useState,type FormEvent,type ReactNode} from 'react';
import {AnimatePresence,motion,useReducedMotion,useScroll,useTransform,type MotionValue} from 'motion/react';
import {createPortal} from 'react-dom';
import {BrandStudio} from '../packages/showcase-v5';
import {NeuronField,PerspectiveVideo,ThreeTiltButton} from '../packages/experience-v3';
import copyData from './content.json';
import opinionData from './reviews.json';
import priceData from './pricing.json';
import {MobileHome} from './mobile/MobileHome';
import {useMobileLayout} from './mobile/MobileChapter';
import {useHeroPhases,useShortHeroViewport} from './hero-phases';
import {HeroPublication} from './HeroPublication';
import {ServicesOverview} from './ServicesOverview';
import {BuyerStory} from './BuyerStory';
import './opening-v7.css';

const copy=copyData as any, opinions=opinionData as any[], pricing=priceData as any;
const asset='/assets/revisions/v3/', media='/assets/revisions/v5/people/founder-blue.webp';
const avatars=['/assets/revisions/v5/people/avatar-a.webp','/assets/revisions/v5/people/avatar-b.webp'];
const sampleAvatar=(key:string)=>avatars[Array.from(key).reduce((sum,c)=>sum+c.charCodeAt(0),0)%avatars.length];
const identity='/assets/revisions/v5/identity/selected/';
const film='/video/revisions/v5/Outspoken-v5-style-proof-landscape.mp4';

export function useStaticExperience(){
  const reduced=useReducedMotion(),[small,setSmall]=useState(()=>matchMedia('(max-width:800px)').matches);
  useEffect(()=>{const m=matchMedia('(max-width:800px)'),f=()=>setSmall(m.matches);m.addEventListener('change',f);return()=>m.removeEventListener('change',f)},[]);
  return !!reduced||small||new URLSearchParams(location.search).has('design');
}
export function Wordmark({inverse=false}:{inverse?:boolean}){
  return <img className="brand-wordmark" src={identity+'lockup-'+(inverse?'inverse':'gradient')+'.svg'} alt="OUTSPOKEN" width="268" height="46"/>;
}
export function CallButton({children=copy.protected.cta,tone='navy'}:{children?:ReactNode;tone?:'navy'|'citron'|'silver'}){
  return <ThreeTiltButton tone={tone} aria-disabled="true" onClick={e=>e.preventDefault()} title="Booking is not connected in this review version">{children}</ThreeTiltButton>;
}
export function RevealHeading({children,as='h2',className=''}:{children:ReactNode;as?:'h1'|'h2'|'h3';className?:string}){
  const still=useStaticExperience(),mobile=useMobileLayout(),reduced=useReducedMotion(),Tag=as;
  const mobileMotion=mobile&&!reduced&&!new URLSearchParams(location.search).has('design');
  return <Tag className={'reveal-heading '+className}><motion.span initial={mobileMotion?{y:24,opacity:0}:still?false:{y:42,opacity:0,filter:'blur(5px)'}} whileInView={{y:0,opacity:1,filter:'blur(0px)'}} viewport={{once:true,amount:.35}} transition={{duration:mobileMotion?.6:.85,ease:[.16,1,.3,1]}}>{children}</motion.span></Tag>;
}
export function SoundWaves({className=''}:{className?:string}){
  return <svg className={'sound-waves '+className} viewBox="0 0 1000 800" fill="none" aria-hidden="true"><defs><linearGradient id="sound-gradient" x1="100" y1="0" x2="850" y2="800"><stop stopColor="#162760" stopOpacity=".02"/><stop offset=".45" stopColor="#A9AFBA" stopOpacity=".68"/><stop offset=".72" stopColor="#3157D5" stopOpacity=".45"/><stop offset="1" stopColor="#D4DD67" stopOpacity=".08"/></linearGradient></defs>{Array.from({length:15},(_,i)=><path key={i} d={'M '+(-110+i*23)+' 820 C '+(150+i*38)+' '+(700-i*6)+', '+(130+i*35)+' '+(100+i*8)+', '+(910+i*18)+' -80'} stroke="url(#sound-gradient)" strokeWidth={i%4===0?2.4:1}/>)}</svg>;
}
export function AtmosphereHero(){
  const host=useRef<HTMLElement>(null),baseStill=useStaticExperience(),short=useShortHeroViewport(),still=baseStill||short,[focused,setFocused]=useState(false);
  const{scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  const phase=useHeroPhases(p,still);
  return <section ref={host} className={'atmosphere-hero hero-v7 '+(still?'is-static ':'')+(focused?'video-focused':'')} data-block="atmosphere-hero" data-hero-phase={phase.phase}>
    <div className="v7-opening-stage">
      <div className="v7-opening-waves"><SoundWaves/></div>
      <motion.div className="v7-human-shadow" data-shadow-figure="" style={still?undefined:{opacity:phase.shadowOpacity,scale:phase.shadowScale}}><img src={asset+'nature/05-real-human-shadow.webp'} alt="Photographic shadow of a fictional person speaking"/></motion.div>
      <motion.div className="v7-opening-copy" inert={!phase.copyReady} style={still?undefined:{opacity:phase.copyOpacity,y:phase.copyY}}><p className="eyebrow">{copy.home.eyebrow}</p><RevealHeading as="h1">Make the <span className="highlight">right buyers</span> care about you and what you’re building.</RevealHeading><p className="hero-value">{copy.protected.vp}</p><CallButton/><p className="audience-line">Europe-based B2B AI SaaS · Seed to Series B</p></motion.div>
      {!still?<motion.div className="v7-shadow-cover" data-shadow-cover="" aria-hidden="true" style={{clipPath:phase.cover}}/>:null}
      <motion.div className="v7-film-scene" data-hero-media="" inert={!phase.ready} style={still?undefined:{opacity:phase.mediaOpacity,y:phase.mediaY,scale:phase.mediaScale}}>
        <div className="v7-film-heading"><p className="eyebrow">A point of view worth hearing.</p><h2>Founder thinking.<br/><span className="highlight">Buyer relevance.</span></h2></div>
        <div className="v7-film-composition"><PerspectiveVideo poster={media} src={film} title="Founder thinking. Buyer relevance." description="An original silent visual study. The people and publications shown are illustrative, not customers or client results." caption="Fictional interview image · silent visual study" onOpenChange={setFocused}/><div className="v7-publication-overlap" data-hero-post=""><HeroPublication post={copy.posts[0]} onOpenChange={setFocused}><PostCard post={copy.posts[0]}/></HeroPublication></div></div>
      </motion.div>
      {!still?<motion.div className="v7-opening-cue" style={{opacity:phase.cueOpacity}} aria-hidden="true"><span>Scroll to bring the story into focus</span><span>↓</span></motion.div>:null}
    </div>
  </section>;
}
export function ExpertiseChapter(){
  const host=useRef<HTMLElement>(null),still=useStaticExperience();
  const{scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  const copyOpacity=useTransform(p,[0,.46,.60],[1,1,0]),resultOpacity=useTransform(p,[.59,.73,1],[0,1,1]);
  return <section id="approach" ref={host} className={'expertise-chapter '+(still?'is-static':'')} data-block="expertise-chapter"><div className="expertise-stage chapter-stage">
    <div className="expertise-halo"/><motion.div className="expertise-copy" style={still?undefined:{opacity:copyOpacity}}><p className="eyebrow">From what you know to what buyers understand</p><RevealHeading>Your experience.<br/>Your <span className="highlight">edge.</span></RevealHeading><p>We uncover the experience, methods, tools and product judgment inside your business. Then we connect the evidence to the customer’s question.</p></motion.div>
    <motion.div className="brain-field"><NeuronField modelSrc={asset+'neural/human-reference-brain-web.glb'} imageSrc={asset+'nature/04-neural-constellation.webp'} progress={p} staticOnly={still}/></motion.div>
    <motion.div className="expertise-result" data-positioning="combined" style={still?undefined:{opacity:resultOpacity}}><p className="eyebrow">Five perspectives. One coherent direction.</p><h3>Your personal<br/>brand positioning.</h3><div className="positioning-card-space" aria-hidden="true"/><p className="positioning-outcome">A clear position. A story buyers can follow.<br/>Built from the substance of your company.</p><div className="result-terms"><span>Positioning</span><span>Profile</span><span>Content</span><span>Distribution</span></div></motion.div>
    <p className="chapter-footnote">An artistic metaphor for expertise. The five categories describe our editorial process.</p>
  </div></section>;
}
export function PostCard({post,index=0,small=false}:{post:any;index?:number;small?:boolean}){
  const[slide,setSlide]=useState(0),slides=post.slides;
  return <article className={'publication-card '+(small?'is-small':'')}><header><div className="founder-avatar"><img src={avatars[1]} alt="Fictional founder portrait"/></div><div><strong>Founder perspective</strong><span>B2B AI SaaS · illustrative publication</span></div><span className="post-more" aria-hidden="true">•••</span></header><p className="post-copy">{post.body||'A useful idea deserves a clear point of view. Start with the buyer’s question, then explain the decision.'}</p><div className={'post-art post-art-'+index}>
    {slides?<><span className="art-kicker">A decision, explained</span><h3>{slides[slide]}</h3><div className="carousel-pagination"><button type="button" aria-label="Previous carousel slide" onClick={()=>setSlide((slide+slides.length-1)%slides.length)}>←</button><span>{slide+1} / {slides.length}</span><button type="button" aria-label="Next carousel slide" onClick={()=>setSlide((slide+1)%slides.length)}>→</button></div></>:<><span className="art-kicker">{post.format}</span><h3>{post.title}</h3>{index===4?<div className="mini-architecture"><span>Experience</span><i>→</i><span>Judgment</span><i>→</i><span>Buyer value</span></div>:<img className="post-mark" src={identity+'flat.svg'} onError={e=>{e.currentTarget.style.display='none'}} alt=""/>}</>}
    <div className="art-signature"><img src="/assets/revisions/v5/identity/wordmark-mono.svg" alt="OUTSPOKEN"/><span>Editorial study</span></div></div><p className="specimen-note">Illustrative work · not published client content</p><footer><span>Like</span><span>Comment</span><span>Repost</span><span>Send</span></footer></article>;
}
function StackedPublication({post,index,total,progress}:{post:any;index:number;total:number;progress:MotionValue<number>}){
  const start=index/(total+1),end=(index+1)/(total+1),direction=index%2?1:-1;
  const x=useTransform(progress,[Math.max(0,start-.08),end],[direction*950,0]);
  const rotateY=useTransform(progress,[Math.max(0,start-.08),end],[direction*20,0]);
  const rotateZ=useTransform(progress,[Math.max(0,start-.08),end],[direction*7,(index-(total-1)/2)*.7]);
  const y=useTransform(progress,[Math.max(0,start-.08),end],[80,(index-(total-1))*14]);
  return <motion.div className="stacked-publication" style={{x,rotateY,rotateZ,y,zIndex:index+1}}><PostCard post={post} index={index}/></motion.div>;
}
export function PublicationStack(){
  const host=useRef<HTMLElement>(null),still=useStaticExperience(),[all,setAll]=useState(false),posts=copy.posts;
  const{scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  const wash=useTransform(p,[0,.5,1],[.02,.11,.03]),headingOpacity=useTransform(p,[0,.06,.16],[1,1,0]),sceneLeft=useTransform(p,[0,.3],['70%','50%']);
  return <section ref={host} id="work" className={'publication-stack '+(still||all?'is-static':'')} data-block="publication-stack"><div className="post-stack-stage chapter-stage"><motion.div className="stack-atmosphere" style={still?undefined:{opacity:wash}}/><motion.div className="stack-heading" style={still||all?undefined:{opacity:headingOpacity}}><p className="eyebrow">A recognizable point of view</p><RevealHeading>One strong idea.<br/><span className="highlight">Many ways</span> to tell it.</RevealHeading><p>Professional posts. Personal stories. Carousels, product walkthroughs and architecture explainers. Every format starts with something worth saying.</p><button type="button" className="text-control" onClick={()=>setAll(!all)}>{all?'Return to scroll story':'Browse the examples'}</button></motion.div><motion.div className="publication-stage" style={still||all?undefined:{left:sceneLeft}} aria-label="Illustrative publication formats">{posts.map((post:any,i:number)=>still||all?<div key={post.id}><PostCard post={post} index={i}/></div>:<StackedPublication key={post.id} post={post} index={i} total={posts.length} progress={p}/>)}</motion.div><button className="stack-browse text-control" type="button" onClick={()=>setAll(!all)}>{all?'Return to scroll story':'Browse all publication examples'}</button><div className="stack-index">{posts.map((post:any,i:number)=><span key={post.id}>{String(i+1).padStart(2,'0')} {post.format}</span>)}</div></div></section>;
}
export function ServiceStack({full=false}:{full?:boolean}){
  const services=copy.services.modules;
  return <section id="services" className={'service-section section '+(full?'services-page':'')} data-block="service-stack"><div className="service-introduction"><p className="eyebrow">The offer</p><RevealHeading>A clear position.<br/>A presence<br/><span className="highlight">built around it.</span></RevealHeading><p>From regular founder interviews to content strategy, professional writing, LinkedIn search visibility, outreach planning and campaigns. One connected approach to the person and the company.</p><a href="/services" className="text-link">Explore the complete service ↗</a></div><div className="service-cards">{services.map((s:any,i:number)=><article className={'service-plate service-plate-'+i} key={s.id} style={{top:96+(i%4)*12}}><div className="service-number">{s.number}</div><div className="service-plate-content"><h3>{s.title}</h3><p className="service-short">{s.short}</p><p>{s.body}</p>{full?<ul>{s.deliverables.map((v:string)=><li key={v}>{v}</li>)}</ul>:null}{full?<details><summary>Scope and permissions</summary><p>{s.boundary}</p></details>:null}</div></article>)}</div></section>;
}
export function PricePlans(){
  const plans=pricing.packages||pricing.proposals||[];
  return <section className="pricing-section section" data-block="price-plans"><div className="section-heading"><p className="eyebrow">A starting point for the conversation</p><RevealHeading>Choose the support<br/>your next stage needs.</RevealHeading><p>Indicative packages. We agree the scope, deliverables and permissions before an engagement. Media spend, paid tools and third-party costs are separate.</p></div><div className="price-plans">{plans.map((p:any,i:number)=><article className={'price-plan '+(i===1?'is-featured':'')} key={p.name||p.id}><span className="plan-number">0{i+1}</span><h3>{p.name||p.title}</h3><p className="plan-price">{p.price_display||p.display_price||(p.currency==='EUR'?'€':'')+(p.price||p.amount_eur||p.price_eur||'')}<span>{p.period==='one-off'?'one-off':p.display_price?'':p.billing_label||p.period||''}</span></p><p>{p.descriptor||p.positioning||p.summary||p.description||p.best_for}</p><ul>{(p.includes||p.deliverables||p.scope||[]).map((v:any,j:number)=><li key={j}>{typeof v==='string'?v:v.title||v.text}</li>)}</ul><CallButton tone={i===1?'citron':'navy'}/></article>)}</div></section>;
}
export function MailCard({email,onOpen}:{email:any;onOpen:()=>void}){
  return <button type="button" className="mail-card" onClick={onOpen} aria-label={'Read sample email: '+email.subject}><div className="mail-toolbar"><span className="mail-m" aria-hidden="true">M</span><span>Inbox</span><span className="mail-toolbar-right" aria-hidden="true">⌑　⋮</span></div><div className="mail-subject">{email.subject}</div><div className="mail-sender"><span className="mail-avatar">{Number(String(email.id).match(/\d+/)?.[0]||0)%3===0?<img src={sampleAvatar(email.sender)} alt="Fictional sender portrait"/>:email.sender.replace('Sample ','').slice(0,1)}</span><div><strong>{email.sender}</strong><span>to OUTSPOKEN team</span></div><span className="sample-badge">Sample</span></div><p>{email.body}</p><footer>Fictional correspondence · open to read</footer></button>;
}
function OpinionReader({index,onIndex,onClose}:{index:number;onIndex:(v:number)=>void;onClose:()=>void}){
  const dialog=useRef<HTMLDialogElement>(null),close=useRef<HTMLButtonElement>(null),email=opinions[index],last=useRef(document.activeElement as HTMLElement);
  useEffect(()=>{dialog.current?.showModal();close.current?.focus();const before=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{document.body.style.overflow=before;last.current?.focus()}},[]);
  return createPortal(<dialog ref={dialog} className="opinion-dialog" onCancel={e=>{e.preventDefault();onClose()}} onClick={e=>{if(e.target===e.currentTarget)onClose()}} onKeyDown={e=>{if(e.key==='ArrowRight'){e.preventDefault();onIndex((index+1)%opinions.length)}if(e.key==='ArrowLeft'){e.preventDefault();onIndex((index+opinions.length-1)%opinions.length)}}} aria-labelledby="opinion-reader-heading"><div className="opinion-reader"><header><div><p className="eyebrow">Customer Opinion · sample library</p><h2 id="opinion-reader-heading">{email.subject}</h2></div><button ref={close} className="reader-close" onClick={onClose} type="button" aria-label="Close email">×</button></header><div className="reader-navigation"><button type="button" onClick={()=>onIndex((index+opinions.length-1)%opinions.length)}>← Previous</button><span>{index+1} / {opinions.length}</span><button type="button" onClick={()=>onIndex((index+1)%opinions.length)}>Next →</button></div><div className="reader-sender"><span className="reader-avatar"><img src={sampleAvatar(email.sender)} alt="Fictional sender portrait"/></span><strong>{email.sender}</strong><span>&lt;{email.email}&gt;</span><span>to {email.recipient||'OUTSPOKEN team'}</span></div><div className="reader-body">{email.body.split('\n').filter(Boolean).map((s:string,i:number)=><p key={i}>{s}</p>)}</div>{email.reply?<div className="reader-reply"><strong>Sample reply</strong><p>{typeof email.reply==='string'?email.reply:email.reply.body}</p></div>:null}<p className="reader-disclosure">Illustrative example — not a customer testimonial. No actual customer, correspondence or result is claimed.</p><div className="reader-thumbnails" aria-label="Browse all sample emails">{opinions.map((e:any,i:number)=><button key={e.id} type="button" aria-current={i===index} onClick={()=>onIndex(i)}>{String(i+1).padStart(2,'0')}　{e.subject}</button>)}</div></div></dialog>,document.body);
}
export function CustomerOpinion(){
  const host=useRef<HTMLElement>(null),still=useStaticExperience(),[reader,setReader]=useState<number|null>(null);
  const{scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  const xA=useTransform(p,[0,.35,.7,1],['35%','2%','-20%','-40%']),xB=useTransform(p,[0,.35,.7,1],['-45%','-10%','12%','30%']);
  const rows=[opinions.filter((_,i)=>i%2===0),opinions.filter((_,i)=>i%2!==0)];
  return <section ref={host} className={'opinion-section '+(still?'is-static':'')} id="opinions" data-block="customer-opinion"><div className="opinion-stage chapter-stage"><SoundWaves/><div className="opinion-heading"><p className="eyebrow">The human side of the work</p><RevealHeading>Customer <span className="highlight">Opinion.</span></RevealHeading><p>Fifteen sample conversations about a clearer profile, better stories and a more useful content process. Fictional examples, shown as a design study.</p><button type="button" className="text-control" onClick={()=>setReader(0)}>Browse all 15 emails ↗</button></div><div className="opinion-rails">{rows.map((row,r)=><motion.div className={'opinion-rail rail-'+r} key={r} style={still?undefined:{x:r?xB:xA}}>{row.map(e=><MailCard key={e.id} email={e} onOpen={()=>setReader(opinions.indexOf(e))}/>)}</motion.div>)}</div></div>{reader!==null?<OpinionReader index={reader} onIndex={setReader} onClose={()=>setReader(null)}/>:null}</section>;
}
export function ProcessRail(){
  return <section className="process-section section" data-block="process-rail"><div className="section-heading"><p className="eyebrow">A considered process</p><RevealHeading>Built from your experience.<br/><span className="highlight">Reviewed with you.</span></RevealHeading></div><ol>{copy.services.steps.map((s:any,i:number)=><li key={s.title}><span>0{i+1}</span><div><h3>{s.title}</h3><p>{s.body}</p></div></li>)}</ol></section>;
}
export function ClosingPanel(){
  return <section className="closing-panel" data-block="closing-panel"><SoundWaves/><div><p className="eyebrow">OUTSPOKEN</p><RevealHeading>Make your next<br/><span className="highlight">point count.</span></RevealHeading><p>Bring the product. The decisions. The story only you can tell.</p><CallButton tone="citron"/></div><img src={'/assets/revisions/v5/identity/selected/model-front.png'} alt="OUTSPOKEN solid capsule microphone with silver crossbands, original generated material artwork"/></section>;
}
function Contact(){
  const form=useRef<HTMLFormElement>(null),status='This static preview does not submit data.';
  const submit=(e:FormEvent<HTMLFormElement>)=>e.preventDefault();
  return <section className="contact-page section"><div><p className="eyebrow">Keep the conversation ready</p><RevealHeading as="h1">What are<br/>you <span className="highlight">building?</span></RevealHeading><p>Tell us about the product, the people it helps and the part that is hard to explain.</p><p className="contact-mode">Public preview · submissions are disabled.</p></div><form ref={form} onSubmit={submit}><label>Name<input name="name" required autoComplete="name"/></label><label>Email<input name="email" type="email" required autoComplete="email"/></label><label>Company<input name="company" autoComplete="organization"/></label><label>Where would you like to start?<select name="service"><option>Positioning and profile</option><option>Content and founder stories</option><option>Company marketing and outreach</option><option>LinkedIn advertising</option><option>A broader program</option></select></label><label>Your context<textarea name="context" required rows={5}/></label><ThreeTiltButton type="submit" disabled>Form preview</ThreeTiltButton><p className="form-status" role="status">{status}</p><small>This form does not send email, book a call or submit to an external service.</small></form></section>;
}
function FAQ(){
  return <section className="faq-section section"><RevealHeading>Before we begin.</RevealHeading><div>{copy.services.faq.map((f:any)=><details key={f.question}><summary>{f.question}</summary><p>{f.answer}</p></details>)}</div></section>;
}
export default function App(){
  const[path,setPath]=useState(location.pathname.replace(/\/$/,'')||'/'),[menu,setMenu]=useState(false),main=useRef<HTMLElement>(null);
  const mobile=useMobileLayout();
  useEffect(()=>{const f=()=>{setPath(location.pathname.replace(/\/$/,'')||'/');setMenu(false)};addEventListener('popstate',f);return()=>removeEventListener('popstate',f)},[]);
  useEffect(()=>{
    const pages:Record<string,{title:string;description:string}>={
      '/':copy.home.seo,'/services':copy.services.seo,
      '/contact':{title:'Discuss your LinkedIn presence | OUTSPOKEN',description:'Share your product and founder-content context. This review edition does not book calls or send email.'},
      '/credits':{title:'Materials and credits | OUTSPOKEN',description:'Sources, licenses and disclosures for OUTSPOKEN’s typography, brain geometry and illustrative media.'},
      '/design-system':{title:'Brand Studio and editable components | OUTSPOKEN',description:'Explore OUTSPOKEN’s selected identity, editorial objects, frames, buttons and disclosed illustrative content.'},
      '/confirmation':{title:'Local enquiry status | OUTSPOKEN',description:'Check the current browser’s local enquiry status. No email is sent and no call is booked.'}
    };
    const meta=pages[path]||{title:'Page not found | OUTSPOKEN',description:'Return to OUTSPOKEN’s founder-led LinkedIn services.'},url='https://outspoken-voice-7c4e2.vercel.app'+(path==='/'?'/':path);
    document.title=meta.title;document.querySelector('meta[name="description"]')?.setAttribute('content',meta.description);
    for(const [property,content] of Object.entries({'og:title':meta.title,'og:description':meta.description,'og:url':url})){let node=document.querySelector<HTMLMetaElement>(`meta[property="${property}"]`);if(!node){node=document.createElement('meta');node.setAttribute('property',property);document.head.append(node)}node.content=content}
    let canonical=document.querySelector<HTMLLinkElement>('link[rel="canonical"]');if(!canonical){canonical=document.createElement('link');canonical.rel='canonical';document.head.append(canonical)}canonical.href=url;
    let schema=document.querySelector<HTMLScriptElement>('#page-schema');if(!schema){schema=document.createElement('script');schema.id='page-schema';schema.type='application/ld+json';document.head.append(schema)}schema.textContent=JSON.stringify({'@context':'https://schema.org','@type':'WebPage',name:meta.title,description:meta.description,url,inLanguage:'en'});
  },[path]);
  useEffect(()=>{if(!menu)return;const close=(e:KeyboardEvent)=>{if(e.key==='Escape'){setMenu(false);document.querySelector<HTMLButtonElement>('.menu-toggle')?.focus()}};addEventListener('keydown',close);return()=>removeEventListener('keydown',close)},[menu]);
  useEffect(()=>{if(!menu||!mobile)return;const previous=document.body.style.overflow;document.body.style.overflow='hidden';const contain=(event:KeyboardEvent)=>{if(event.key!=='Tab')return;const controls=Array.from(document.querySelectorAll<HTMLElement>('.menu-toggle,#main-navigation a,#main-navigation button:not([disabled])')),first=controls[0],last=controls.at(-1);if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}};addEventListener('keydown',contain);return()=>{document.body.style.overflow=previous;removeEventListener('keydown',contain);};},[menu,mobile]);
  const navigate=(event:React.MouseEvent<HTMLAnchorElement>,href:string)=>{if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();history.pushState({},'',href);setPath(href);setMenu(false);scrollTo({top:0,behavior:'instant'});requestAnimationFrame(()=>main.current?.focus({preventScroll:true}))};
  return <><a className="skip-link" href="#main">Skip to content</a><header className="site-header"><a href="/" onClick={e=>navigate(e,'/')} aria-label="OUTSPOKEN home"><Wordmark/></a><button className="menu-toggle" type="button" aria-expanded={menu} aria-controls="main-navigation" onClick={()=>setMenu(!menu)}>Menu {menu?'−':'+'}</button><nav id="main-navigation" className={menu?'is-open':''} aria-label="Main navigation"><a href="/" aria-current={path==='/'?'page':undefined} onClick={e=>navigate(e,'/')}>Approach</a><a href="/services" aria-current={path==='/services'?'page':undefined} onClick={e=>navigate(e,'/services')}>Services</a><a href="/contact" aria-current={path==='/contact'?'page':undefined} onClick={e=>navigate(e,'/contact')}>Contact</a><CallButton/></nav></header><main ref={main} id="main" tabIndex={-1}>
    {path==='/design-system'?<BrandStudio wordmarkSrc={identity+'lockup-gradient.svg'} videoSrc={film}/>:path==='/'?mobile?<MobileHome PostCard={PostCard} MailCard={MailCard} CallButton={CallButton} SoundWaves={SoundWaves} OpinionReader={OpinionReader} services={<BuyerStory/>} process={null} pricing={<PricePlans/>} faq={<FAQ/>} closing={<ClosingPanel/>}/>:<><AtmosphereHero/><ExpertiseChapter/><PublicationStack/><BuyerStory/><CustomerOpinion/><PricePlans/><FAQ/><ClosingPanel/></>:path==='/services'?<ServicesOverview><PricePlans/></ServicesOverview>:path==='/contact'?<Contact/>:path==='/credits'?<section className="section credits-page"><p className="eyebrow">Materials and acknowledgements</p><h1>Credits.</h1><p>Brain geometry: HuBMAP / Human Reference Atlas, Allen brain reference atlas (Ding et al., 2016). Materials, lighting and star rendering adapted by Outspoken. <a href="https://3d.nih.gov/entries/20960?version=1">Original reference</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p><p>The anatomical model is used as an artistic metaphor for expertise.</p><p>The shadow portrait, editorial interview specimen and resonance images are original generated illustrations. People, publications and emails are fictional examples. No client relationship or customer result is claimed.</p><p>Typography: Archivo and Inter, distributed under the SIL Open Font License.</p></section>:path==='/confirmation'?<section className="confirmation-page section"><p className="eyebrow">Local enquiry</p><RevealHeading as="h1">Your next step,<br/><span className="highlight">kept ready.</span></RevealHeading><p>{'This static preview does not save submissions.'}</p><p>No call was booked. No email was sent.</p><a href="/contact" onClick={e=>navigate(e,'/contact')}>Return to the form ↗</a></section>:<section className="section"><h1>Page not found</h1><a href="/">Return home</a></section>}
  </main><footer className="site-footer"><Wordmark/><p>Founder expertise. Buyer relevance.</p><div><a href="/services" onClick={e=>navigate(e,'/services')}>Services</a><a href="/contact" onClick={e=>navigate(e,'/contact')}>Contact</a><a href="/credits" onClick={e=>navigate(e,'/credits')}>Credits</a><a href="/design-system" onClick={e=>navigate(e,'/design-system')}>Design system</a></div><small>OUTSPOKEN · Design review edition. Example publications, people and emails are illustrative.</small></footer></>;
}
