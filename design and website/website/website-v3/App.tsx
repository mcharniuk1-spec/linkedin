import {useEffect,useRef,useState,type FormEvent,type ReactNode} from 'react';
import {AnimatePresence,motion,useReducedMotion,useScroll,useTransform,type MotionValue} from 'motion/react';
import {createPortal} from 'react-dom';
import {BrandStudio} from '../packages/showcase-v5';
import {PerspectiveVideo} from '../packages/experience-v3';
import copyData from './content.json';
import {opinions,opinionCount} from './opinions';
import priceData from './pricing.json';
import {MobileHome} from './mobile/MobileHome';
import {useMobileLayout} from './mobile/MobileChapter';
import {useHeroPhases,useShortHeroViewport} from './hero-phases';
import {HeroPublication} from './HeroPublication';
import {ServiceDetails} from './ServiceDetails';
import {ExperienceStory} from './ExperienceStory';
import {WhyOutspoken} from './WhyOutspoken';
import './opening-v7.css';
import './button.css';
import './identity-v10.css';
import './hero-v10.css';
import './contact-block.css';
import {HeroPeople,Sel} from './HeroPeople';

const copy=copyData as any, pricing=priceData as any;
const asset='/assets/revisions/v3/', media='/assets/identity/v10/heroes/h2-founder.webp';
const avatars=['/assets/library-r12/thumbs/thumb-06.webp','/assets/library-r12/thumbs/thumb-02.webp'];
const countWord=(n:number)=>['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten'][n]??String(n);
const identity='/assets/revisions/v5/identity/selected/';
const film='/video/revisions/v5/Outspoken-v5-style-proof-landscape.mp4';
const inquiryIsLocal=()=>/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
export function useStaticExperience(){
  const reduced=useReducedMotion(),[small,setSmall]=useState(()=>matchMedia('(max-width:800px)').matches);
  useEffect(()=>{const m=matchMedia('(max-width:800px)'),f=()=>setSmall(m.matches);m.addEventListener('change',f);return()=>m.removeEventListener('change',f)},[]);
  return !!reduced||small||new URLSearchParams(location.search).has('design');
}
export function Wordmark({inverse=false}:{inverse?:boolean}){
  return <img className="brand-wordmark" src={'/assets/identity/v10/lockup-b01'+(inverse?'-inverse':'')+'.svg'} alt="OUTSPOKEN" width="268" height="46"/>;
}
const ArrowIcon=()=> <svg viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M3 11 11 3M5 3h6v6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>;
export function CallButton({children=copy.protected.cta,tone='navy'}:{children?:ReactNode;tone?:'navy'|'marigold'|'silver'}){
  return <button type="button" className={'os-btn'+(tone==='navy'?'':' os-btn--'+tone)} aria-disabled="true" onClick={e=>e.preventDefault()} title="Booking is not connected in this review version">{children}<ArrowIcon/></button>;
}
export function RevealHeading({children,as='h2',className='',id}:{children:ReactNode;as?:'h1'|'h2'|'h3';className?:string;id?:string}){
  const still=useStaticExperience(),mobile=useMobileLayout(),reduced=useReducedMotion(),Tag=as;
  const mobileMotion=mobile&&!reduced&&!new URLSearchParams(location.search).has('design');
  return <Tag id={id} className={'reveal-heading '+className}><motion.span initial={mobileMotion?{y:24,opacity:0}:still?false:{y:42,opacity:0,filter:'blur(5px)'}} whileInView={{y:0,opacity:1,filter:'blur(0px)'}} viewport={{once:true,amount:.35}} transition={{duration:mobileMotion?.6:.85,ease:[.16,1,.3,1]}}>{children}</motion.span></Tag>;
}
export function SoundWaves({className=''}:{className?:string}){
  return <svg className={'sound-waves '+className} viewBox="0 0 1000 800" fill="none" aria-hidden="true"><defs><linearGradient id="sound-gradient" x1="100" y1="0" x2="850" y2="800"><stop stopColor="#162760" stopOpacity=".02"/><stop offset=".45" stopColor="#A9AFBA" stopOpacity=".68"/><stop offset=".72" stopColor="#3157D5" stopOpacity=".45"/><stop offset="1" stopColor="#EAA93C" stopOpacity=".08"/></linearGradient></defs>{Array.from({length:15},(_,i)=><path key={i} d={'M '+(-110+i*23)+' 820 C '+(150+i*38)+' '+(700-i*6)+', '+(130+i*35)+' '+(100+i*8)+', '+(910+i*18)+' -80'} stroke="url(#sound-gradient)" strokeWidth={i%4===0?2.4:1}/>)}</svg>;
}
export function AtmosphereHero(){
  const host=useRef<HTMLElement>(null),baseStill=useStaticExperience(),short=useShortHeroViewport(),still=baseStill||short,[focused,setFocused]=useState(false);
  const{scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  const phase=useHeroPhases(p,still);
  return <section ref={host} className={'atmosphere-hero hero-v7 '+(still?'is-static ':'')+(focused?'video-focused':'')} data-block="atmosphere-hero" data-hero-phase={phase.phase}>
    <div className="v7-opening-stage">
      <div className="v7-opening-waves"><SoundWaves/></div>
      <motion.div className="v7-human-shadow" data-shadow-figure="" style={still?undefined:{opacity:phase.shadowOpacity,scale:phase.shadowScale}}><img src="/assets/identity/v10/heroes/h1-shadow.webp" alt="Photographic shadow of a fictional person speaking"/></motion.div>
      <motion.div className="v7-opening-copy" inert={!phase.copyReady} style={still?undefined:{opacity:phase.copyOpacity,y:phase.copyY}}><p className="eyebrow hero-pill">{copy.home.eyebrow}</p><RevealHeading as="h1">Make the right buyers <Sel>care</Sel> about you and what you’re building.</RevealHeading><p className="hero-value">{copy.protected.vp}</p><CallButton/><HeroPeople/></motion.div>
      {!still?<motion.div className="v7-shadow-cover" data-shadow-cover="" aria-hidden="true" style={{clipPath:phase.cover}}/>:null}
      <motion.div className="v7-film-scene" data-hero-media="" style={still?undefined:{opacity:phase.statementOpacity}}>
        <motion.div className="v7-film-heading" style={still?undefined:{y:phase.statementY}}><p className="eyebrow">A point of view worth hearing.</p><h2>Founder thinking.<br/><span className="highlight">Buyer relevance.</span></h2></motion.div>
        <motion.div className="v7-film-composition" inert={!phase.ready} style={still?undefined:{opacity:phase.mediaOpacity,y:phase.mediaY,scale:phase.mediaScale}}><PerspectiveVideo poster={media} src={film} title="Founder thinking. Buyer relevance." description="An original silent visual study. The people and publications shown are illustrative, not customers or client results." caption="Fictional interview image · silent visual study" onOpenChange={setFocused}/><div className="v7-publication-overlap" data-hero-post=""><HeroPublication post={copy.posts[0]} onOpenChange={setFocused}><PostCard post={copy.posts[0]}/></HeroPublication></div></motion.div>
      </motion.div>
      {!still?<motion.div className="v7-opening-cue" style={{opacity:phase.cueOpacity}} aria-hidden="true"><span>Scroll to bring the story into focus</span><span>↓</span></motion.div>:null}
    </div>
  </section>;
}
export function PostCard({post,index=0,small=false}:{post:any;index?:number;small?:boolean}){
  const[slide,setSlide]=useState(0),slides=post.slides;
  return <article className={'publication-card '+(small?'is-small':'')}><header><div className="founder-avatar"><img src={avatars[1]} alt="Fictional founder portrait"/></div><div><strong>Founder perspective</strong><span>B2B AI SaaS · illustrative publication</span></div><span className="post-more" aria-hidden="true">•••</span></header><p className="post-copy">{post.body||'A useful idea deserves a clear point of view. Start with the buyer’s question, then explain the decision.'}</p><div className={'post-art post-art-'+index}>
    {slides?<><span className="art-kicker">A decision, explained</span><h3>{slides[slide]}</h3><div className="carousel-pagination"><button type="button" aria-label="Previous carousel slide" onClick={()=>setSlide((slide+slides.length-1)%slides.length)}>←</button><span>{slide+1} / {slides.length}</span><button type="button" aria-label="Next carousel slide" onClick={()=>setSlide((slide+1)%slides.length)}>→</button></div></>:<><span className="art-kicker">{post.format}</span><h3>{post.title}</h3>{index===4?<div className="mini-architecture"><span>Experience</span><i>→</i><span>Judgment</span><i>→</i><span>Buyer value</span></div>:<img className="post-mark" src={identity+'flat.svg'} onError={e=>{e.currentTarget.style.display='none'}} alt=""/>}</>}
    <div className="art-signature"><img src="/assets/revisions/v5/identity/wordmark-mono.svg" alt="OUTSPOKEN"/><span>Editorial study</span></div></div><p className="specimen-note">Illustrative work · not published client content</p><footer><span>Like</span><span>Comment</span><span>Repost</span><span>Send</span></footer></article>;
}
export function PricePlans(){
  const plans=pricing.packages||pricing.proposals||[];
  return <section id="pricing" className="pricing-section section" data-block="price-plans" tabIndex={-1}><div className="section-heading"><p className="eyebrow">A starting point for the conversation</p><RevealHeading>Choose the support<br/>your next stage needs.</RevealHeading><p>Indicative packages. We agree the scope, deliverables and permissions before an engagement. Media spend, paid tools and third-party costs are separate.</p></div><div className="price-plans">{plans.map((p:any,i:number)=><article className={'price-plan '+(i===1?'is-featured':'')} key={p.name||p.id}><span className="plan-number">0{i+1}</span><img className="plan-art" src={['/assets/library-r12/elements/element-02-1.webp','/assets/library-r12/elements/element-05-3.webp','/assets/library-r12/elements/element-03-5.webp'][i]||''} alt="" width="160" height="120" loading="lazy" decoding="async"/><h3>{p.name||p.title}</h3><p className="plan-price">{p.price_display||p.display_price||(p.currency==='EUR'?'€':'')+(p.price||p.amount_eur||p.price_eur||'')}<span>{p.period==='one-off'?'one-off':p.display_price?'':p.billing_label||p.period||''}</span></p><p>{p.descriptor||p.positioning||p.summary||p.description||p.best_for}</p><ul>{(p.includes||p.deliverables||p.scope||[]).map((v:any,j:number)=><li key={j}>{typeof v==='string'?v:v.title||v.text}</li>)}</ul><CallButton tone={i===1?'marigold':'navy'}/></article>)}</div></section>;
}
export function MailCard({email,onOpen}:{email:any;onOpen:()=>void}){
  return <button type="button" className="mail-card" onClick={onOpen} ><div className="mail-toolbar" aria-hidden="true"><span className="mail-m" aria-hidden="true">M</span><span>Inbox</span><span className="mail-toolbar-right" aria-hidden="true">⌑　⋮</span></div><div className="mail-subject">{email.subject}</div><div className="mail-sender"><span className="mail-avatar" aria-hidden="true">{email.sender.replace('Sample ','').slice(0,1)}</span><div><strong>{email.sender}</strong><span>to OUTSPOKEN team</span></div><span className="sample-badge">Sample</span></div><p>{email.body}</p><footer>Fictional correspondence · open to read</footer></button>;
}
function OpinionReader({index,onIndex,onClose}:{index:number;onIndex:(v:number)=>void;onClose:()=>void}){
  const dialog=useRef<HTMLDialogElement>(null),close=useRef<HTMLButtonElement>(null),email=opinions[index],last=useRef(document.activeElement as HTMLElement);
  useEffect(()=>{dialog.current?.showModal();close.current?.focus();const before=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{document.body.style.overflow=before;last.current?.focus()}},[]);
  return createPortal(<dialog ref={dialog} className="opinion-dialog" onCancel={e=>{e.preventDefault();onClose()}} onClick={e=>{if(e.target===e.currentTarget)onClose()}} onKeyDown={e=>{if(e.key==='ArrowRight'){e.preventDefault();onIndex((index+1)%opinions.length)}if(e.key==='ArrowLeft'){e.preventDefault();onIndex((index+opinions.length-1)%opinions.length)}}} aria-labelledby="opinion-reader-heading"><div className="opinion-reader"><header><div><p className="eyebrow">Customer Opinion · sample library</p><h2 id="opinion-reader-heading">{email.subject}</h2></div><button ref={close} className="reader-close" onClick={onClose} type="button" aria-label="Close email">×</button></header><div className="reader-navigation"><button type="button" onClick={()=>onIndex((index+opinions.length-1)%opinions.length)}>← Previous</button><span>{index+1} / {opinions.length}</span><button type="button" onClick={()=>onIndex((index+1)%opinions.length)}>Next →</button></div><div className="reader-sender"><span className="reader-avatar" aria-hidden="true">{email.sender.replace('Sample ','').slice(0,1)}</span><strong>{email.sender}</strong><span>&lt;{email.email}&gt;</span><span>to {email.recipient||'OUTSPOKEN team'}</span></div><div className="reader-body">{email.body.split('\n').filter(Boolean).map((s:string,i:number)=><p key={i}>{s}</p>)}</div>{email.reply?<div className="reader-reply"><strong>Sample reply</strong><p>{typeof email.reply==='string'?email.reply:email.reply.body}</p></div>:null}<p className="reader-disclosure">Illustrative example — not a customer testimonial. No actual customer, correspondence or result is claimed.</p><div className="reader-thumbnails" aria-label="Browse all sample emails">{opinions.map((e:any,i:number)=><button key={e.id} type="button" aria-current={i===index} onClick={()=>onIndex(i)}>{String(i+1).padStart(2,'0')}　{e.subject}</button>)}</div></div></dialog>,document.body);
}
export function CustomerOpinion(){
  const host=useRef<HTMLElement>(null),still=useStaticExperience(),[reader,setReader]=useState<number|null>(null);
  const{scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  const xA=useTransform(p,[0,.35,.7,1],['35%','2%','-20%','-40%']),xB=useTransform(p,[0,.35,.7,1],['-45%','-10%','12%','30%']);
  const rows=[opinions.filter((_,i)=>i%2===0),opinions.filter((_,i)=>i%2!==0)];
  return <section ref={host} className={'opinion-section '+(still?'is-static':'')} id="opinions" data-block="customer-opinion"><div className="opinion-stage chapter-stage"><SoundWaves/><div className="opinion-heading"><p className="eyebrow">The human side of the work</p><RevealHeading>Customer <span className="highlight">Opinion.</span></RevealHeading><p>{countWord(opinionCount)} sample conversations about a clearer profile, better stories and a more useful content process. Fictional examples, shown as a design study, not customer testimonials.</p><button type="button" className="text-control" onClick={()=>setReader(0)}>Read all {opinionCount} samples ↗</button></div><div className="opinion-rails">{rows.map((row,r)=><motion.div className={'opinion-rail rail-'+r} key={r} style={still?undefined:{x:r?xB:xA}}>{row.map(e=><MailCard key={e.id} email={e} onOpen={()=>setReader(opinions.indexOf(e))}/>)}</motion.div>)}</div></div>{reader!==null?<OpinionReader index={reader} onIndex={setReader} onClose={()=>setReader(null)}/>:null}</section>;
}
export function ProcessRail(){
  return <section className="process-section section" data-block="process-rail"><div className="section-heading"><p className="eyebrow">A considered process</p><RevealHeading>Built from your experience.<br/><span className="highlight">Reviewed with you.</span></RevealHeading></div><ol>{copy.services.steps.map((s:any,i:number)=><li key={s.title}><span>0{i+1}</span><div><h3>{s.title}</h3><p>{s.body}</p></div></li>)}</ol></section>;
}
export function ContactBlock(){
  const form=useRef<HTMLFormElement>(null),[busy,setBusy]=useState(false),[status,setStatus]=useState<{ok:boolean;text:string}|null>(null),local=inquiryIsLocal();
  const submit=async(e:FormEvent<HTMLFormElement>)=>{e.preventDefault();setBusy(true);setStatus(null);const fd=new FormData(e.currentTarget);const data:Record<string,unknown>=Object.fromEntries(fd);data.consent=fd.get('consent')==='on';data.source='website one-pager';
    try{
      const res=await fetch(local?'/api/enquiries':'/api/lead',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
      const result=await res.json().catch(()=>({}));
      if(!res.ok)throw Error(result.error||'The message could not be saved. Please try again.');
      form.current?.reset();if(result.id)sessionStorage.setItem('outspoken-local-save',String(result.id));
      setStatus({ok:true,text:local?'Saved to the local Excel workbook. No email was sent and no call was booked.':'Thank you. Your message was received. We reply by email; no call is booked automatically.'});
    }catch(error){setStatus({ok:false,text:error instanceof Error?error.message:'The message could not be saved. Please try again.'})}
    finally{setBusy(false)}
  };
  return <section id="contact" className="contact-block" data-block="contact" tabIndex={-1} aria-labelledby="contact-heading"><SoundWaves/>
    <div className="contact-block__arch" aria-hidden="true"><i/></div>
    <div className="contact-block__intro"><p className="eyebrow hero-pill">Contact</p><RevealHeading id="contact-heading" className="contact-block__title">What are you <span className="highlight">building?</span></RevealHeading><p>Tell us about the product, the people it helps and the part that is hard to explain. Bring the decisions and the story only you can tell.</p><p className="contact-mode">Replies come by email from a person. This review edition books no calls automatically.</p>
      <div className="closing-mark"><i aria-hidden="true"/><i aria-hidden="true"/><i aria-hidden="true"/><img src="/assets/identity/v10/mark-b01-inverse.svg" alt="OUTSPOKEN microphone mark: a matte capsule microphone with a marigold ring" width="160" height="212"/></div></div>
    <form ref={form} onSubmit={submit}><label>Name<input name="name" required maxLength={120} autoComplete="name"/></label><label>Email<input name="email" type="email" required maxLength={200} autoComplete="email"/></label><label>Company<input name="company" maxLength={160} autoComplete="organization"/></label><label>Where would you like to start?<select name="service"><option>Positioning and profile</option><option>Content and founder stories</option><option>Company marketing and outreach</option><option>LinkedIn advertising</option><option>A broader program</option></select></label><label>Your context<textarea name="context" required minLength={10} maxLength={4000} rows={5}/></label>
      <label className="contact-hp" aria-hidden="true">Leave this field empty<input name="website" tabIndex={-1} autoComplete="off"/></label>
      <label className="contact-consent"><input type="checkbox" name="consent" required/><span>I agree that OUTSPOKEN stores these details to reply to my enquiry.</span></label>
      <button type="submit" className={'os-btn'+(busy?' is-loading':'')} disabled={busy}>{busy?'Sending…':'Send message'}</button>
      <p className={'form-status'+(status?(status.ok?' is-ok':' is-error'):'')} role="status" aria-live="polite">{status?status.text:''}</p>
      <small>Details are kept in a private database and are not shared. Ask us to delete them at any time.</small></form>
  </section>;
}
function FAQ(){
  return <section id="faq" className="faq-section section"><RevealHeading>Before we begin.</RevealHeading><div>{copy.services.faq.map((f:any)=><details key={f.question}><summary>{f.question}</summary><p>{f.answer}</p></details>)}</div></section>;
}
export default function App(){
  const norm=(p:string)=>{const q=p.replace(/\/$/,'')||'/';return q==='/services'||q==='/contact'?'/':q};
  const[path,setPath]=useState(()=>norm(location.pathname)),[menu,setMenu]=useState(false),[spy,setSpy]=useState(''),main=useRef<HTMLElement>(null);
  const mobile=useMobileLayout();
  useEffect(()=>{const f=()=>{setPath(norm(location.pathname));setMenu(false);if(location.hash)setTimeout(()=>scrollToId(location.hash.slice(1),true),80)};addEventListener('popstate',f);return()=>removeEventListener('popstate',f)},[]);
  // One page: the former /services and /contact addresses open the matching block of the landing page.
  useEffect(()=>{const old=location.pathname.replace(/\/$/,'');const id=old==='/services'?'services':old==='/contact'?'contact':location.hash.slice(1);if(old==='/services'||old==='/contact')history.replaceState({},'','/#'+id);if(id&&(path==='/'))setTimeout(()=>scrollToId(id,true),350)},[]);
  // Header state: the block currently in view.
  useEffect(()=>{if(path!=='/')return;const ids=['approach','pricing','services','contact'];let tick:number|undefined;const f=()=>{tick=undefined;let current='';for(const id of ids){const el=document.getElementById(id);if(el&&el.getBoundingClientRect().top<=innerHeight*.4)current=id}setSpy(current)};const on=()=>{if(tick===undefined)tick=window.setTimeout(f,60)};f();addEventListener('scroll',on,{passive:true});addEventListener('resize',on);return()=>{removeEventListener('scroll',on);removeEventListener('resize',on);if(tick!==undefined)clearTimeout(tick)}},[path]);
  useEffect(()=>{
    const pages:Record<string,{title:string;description:string}>={
      '/':copy.home.seo,
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
  const scrollToId=(id:string,instant=false)=>{const el=document.getElementById(id);if(!el)return;el.scrollIntoView({behavior:instant||matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});el.focus({preventScroll:true})};
  const jump=(event:React.MouseEvent<HTMLAnchorElement>,id:string)=>{if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();setMenu(false);if(path!=='/'){history.pushState({},'','/#'+id);setPath('/');setTimeout(()=>scrollToId(id,true),120)}else{history.replaceState({},'','/#'+id);scrollToId(id)}};
  const navigate=(event:React.MouseEvent<HTMLAnchorElement>,href:string)=>{if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();history.pushState({},'',href);setPath(href);setMenu(false);scrollTo({top:0,behavior:'instant'});requestAnimationFrame(()=>main.current?.focus({preventScroll:true}))};
  return <><a className="skip-link" href="#main">Skip to content</a><header className="site-header"><a href="/" onClick={e=>navigate(e,'/')} aria-label="OUTSPOKEN home"><Wordmark/></a><button className="menu-toggle" type="button" aria-expanded={menu} aria-controls="main-navigation" onClick={()=>setMenu(!menu)}>Menu {menu?'−':'+'}</button><nav id="main-navigation" className={menu?'is-open':''} aria-label="Main navigation"><a href="/#approach" aria-current={path==='/'&&spy==='approach'?'location':undefined} onClick={e=>jump(e,'approach')}>Approach</a><a href="/#pricing" aria-current={path==='/'&&spy==='pricing'?'location':undefined} onClick={e=>jump(e,'pricing')}>Pricing</a><a href="/#services" aria-current={path==='/'&&spy==='services'?'location':undefined} onClick={e=>jump(e,'services')}>Services</a><a href="/#contact" aria-current={path==='/'&&spy==='contact'?'location':undefined} onClick={e=>jump(e,'contact')}>Contact</a><CallButton/></nav></header><main ref={main} id="main" tabIndex={-1}>
    {path==='/design-system'?<BrandStudio wordmarkSrc={'/assets/identity/v10/lockup-b01.svg'} videoSrc={film}/>:path==='/'?mobile?<MobileHome PostCard={PostCard} MailCard={MailCard} CallButton={CallButton} SoundWaves={SoundWaves} OpinionReader={OpinionReader} story={<ExperienceStory/>} why={<WhyOutspoken/>} pricing={<PricePlans/>} services={<ServiceDetails extras={<><ProcessRail/><FAQ/></>}/>} contact={<ContactBlock/>}/>:<><AtmosphereHero/><ExperienceStory/><WhyOutspoken/><CustomerOpinion/><PricePlans/><ServiceDetails extras={<><ProcessRail/><FAQ/></>}/><ContactBlock/></>:path==='/credits'?<section className="section credits-page"><p className="eyebrow">Materials and acknowledgements</p><h1>Credits.</h1><p>Brain geometry: HuBMAP / Human Reference Atlas, Allen brain reference atlas (Ding et al., 2016). Materials, lighting and star rendering adapted by Outspoken. <a href="https://3d.nih.gov/entries/20960?version=1">Original reference</a> · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p><p>The anatomical model is used as an artistic metaphor for expertise.</p><p>The shadow portrait, editorial interview specimen and resonance images are original generated illustrations. People, publications and emails are fictional examples. No client relationship or customer result is claimed.</p><p>Typography: Archivo and Inter, distributed under the SIL Open Font License.</p></section>:path==='/confirmation'?<section className="confirmation-page section"><p className="eyebrow">Local enquiry</p><RevealHeading as="h1">Your next step,<br/><span className="highlight">kept ready.</span></RevealHeading><p>{sessionStorage.getItem('outspoken-local-save')?'A submission was saved to the local Excel workbook in this browser session.':'No submission has been saved in this browser session.'}</p><p>No call was booked. No email was sent.</p><a href="/#contact" onClick={e=>jump(e,'contact')}>Return to the form ↗</a></section>:<section className="section"><h1>Page not found</h1><a href="/">Return home</a></section>}
  </main><footer className="site-footer"><Wordmark/><p>Founder expertise. Buyer relevance.</p><div><a href="/#services" onClick={e=>jump(e,'services')}>Services</a><a href="/#contact" onClick={e=>jump(e,'contact')}>Contact</a><a href="/credits" onClick={e=>navigate(e,'/credits')}>Credits</a><a href="/design-system" onClick={e=>navigate(e,'/design-system')}>Design system</a></div><small>OUTSPOKEN · Design review edition. Example publications, people and emails are illustrative.</small></footer></>;
}
