import {useEffect,useRef,useState,type ReactNode} from 'react';
import {motion,useReducedMotion} from 'motion/react';
import content from './content.json';
import details from './service-details.json';
import {Icon,type IconName} from './Icon';
import {Sel} from './HeroPeople';
import './service-details.css';

/** Service parts for the one-page site (V10, proposed): each service has a reason (argument), a check the reader can run, deliverables and a scope. */
const ease=[.16,1,.3,1] as const;
const modules=content.services.modules as Array<{id:string;number:string;title:string;short:string;body:string;deliverables:string[];boundary:string}>;
const argsById=details.arguments as Record<string,{headline:string;why:string;check:string;image?:string}>;
const pad=(n:number)=>String(n).padStart(2,'0');

/** "A *word* here": the starred word becomes the selected-text accent. */
function Accent({text}:{text:string}){
  return <>{text.split(/(\*[^*]+\*)/).filter(Boolean).map((part,i)=>part.startsWith('*')?<Sel key={i}>{part.replace(/\*/g,'')}</Sel>:<span key={i}>{part}</span>)}</>;
}

function Stage({id,image}:{id:string;image?:string}){
  if(image)return <figure className="svc__stage svc__stage--image"><img src={image} alt="" loading="lazy" decoding="async"/></figure>;
  return <figure className="svc__stage" aria-hidden="true"><i/><i/><i/><Icon name={id as IconName} size={104}/></figure>;
}

export function ServiceDetails({extras}:{extras?:ReactNode}){
  const reduced=useReducedMotion(),still=reduced||new URLSearchParams(location.search).has('design');
  const [active,setActive]=useState(0),cards=useRef<Array<HTMLElement|null>>([]);
  useEffect(()=>{
    const els=cards.current.filter(Boolean) as HTMLElement[];if(!els.length||!('IntersectionObserver' in window))return;
    const io=new IntersectionObserver(entries=>{
      const hit=entries.filter(e=>e.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];
      if(hit)setActive(els.indexOf(hit.target as HTMLElement));
    },{rootMargin:'-30% 0px -50% 0px',threshold:[0,.15,.5,1]});
    els.forEach(el=>io.observe(el));
    const seen=new IntersectionObserver(entries=>{for(const e of entries)if(e.isIntersecting){e.target.classList.add('is-seen');seen.unobserve(e.target)}},{threshold:.2});
    document.querySelectorAll('.svc-head,.svc').forEach(el=>seen.observe(el));
    return()=>{io.disconnect();seen.disconnect()};
  },[]);
  const open=(e:React.MouseEvent<HTMLAnchorElement>,id:string)=>{
    if(e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();
    document.getElementById('svc-'+id)?.scrollIntoView({behavior:still?'instant':'smooth',block:'start'});
  };
  return <section id="services" className="svc-section section" data-block="service-details" tabIndex={-1} aria-labelledby="svc-heading">
    <header className="svc-head">
      <p className="eyebrow hero-pill">{details.kicker}</p>
      <h2 id="svc-heading"><Accent text={details.title}/></h2>
      <p>{details.intro}</p>
      <aside className="svc-def" aria-labelledby="svc-def-q"><p className="eyebrow">{details.definition.label}</p><h3 id="svc-def-q">{details.definition.question}</h3><p>{details.definition.answer}</p></aside>
    </header>
    <div className="svc-layout">
      <nav className="svc-index" aria-label={details.indexLabel}>
        <ol>{modules.map((m,i)=><li key={m.id}><a href={'#svc-'+m.id} aria-label={m.number+' '+m.title.replace(/,\s+/g,', ')} aria-current={active===i?'true':undefined} onClick={e=>open(e,m.id)}><span>{m.number}</span><Icon name={m.id as IconName} size={20}/><b>{m.title.replace(/,\s+/g,', ')}</b></a></li>)}</ol>
      </nav>
      <div className="svc-list">
        {modules.map((m,i)=>{
          const a=argsById[m.id];if(!a)return null;
          return <motion.article key={m.id} id={'svc-'+m.id} ref={el=>{cards.current[i]=el}} className="svc is-animated" data-service={m.id} aria-labelledby={'svc-t-'+m.id}
            initial={still?false:{opacity:0,y:40}} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.12}} transition={{duration:.8,ease}}>
            <div className="svc__top"><span className="svc__count">{m.number}<i> / {pad(modules.length)}</i></span><span className="svc__tag"><Icon name={m.id as IconName} size={20}/><h3 id={'svc-t-'+m.id}>{m.title.replace(/,\s+/g,', ')}</h3></span></div>
            <p className="svc__argument"><Accent text={a.headline}/></p>
            <div className="svc__grid">
              <div className="svc__copy">
                <h4>{details.whyLabel}</h4><p>{a.why}</p>
                <p className="svc__check"><strong>{details.checkLabel}</strong>{a.check}</p>
              </div>
              <div className="svc__side">
                <Stage id={m.id} image={a.image}/>
                <h4>{details.getLabel}</h4>
                <ul>{m.deliverables.map(d=><li key={d}>{d}</li>)}</ul>
              </div>
            </div>
            <details className="svc__scope"><summary>{details.scopeLabel}</summary><p>{m.boundary}</p></details>
          </motion.article>;
        })}
      </div>
    </div>
    {extras}
  </section>;
}
