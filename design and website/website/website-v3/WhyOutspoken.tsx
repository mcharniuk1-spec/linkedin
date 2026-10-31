import {motion,useReducedMotion} from 'motion/react';
import data from './founders.json';
import './why-outspoken.css';

/** OS-WEB-V10-002. Founder quote and cards: names, photos, roles and links are verified on arch-flow.dev; the quote is a proposed edit. */
const ease=[.2,.8,.2,1] as const;
const words=data.quote.split(/(\*[^*]+\*)/).filter(Boolean).flatMap(part=>{const accent=part.startsWith('*');return (part.replace(/\*/g,'').match(/\S+\s*/g)||[]).map(w=>({w,accent}))});

export function WhyOutspoken(){
  const reduced=useReducedMotion(),still=reduced||new URLSearchParams(location.search).has('design');
  return <section className="why" id="why" data-block="why-outspoken" aria-labelledby="why-heading">
    <div className="why__inner">
      <p className="eyebrow">{data.kicker}</p>
      <h2 id="why-heading">{data.title}</h2>
      <figure className="why__quote">
        {still
          ?<blockquote>{words.map((x,i)=><span key={i} className={'word'+(x.accent?' is-accent':'')}>{x.w}</span>)}</blockquote>
          :<motion.blockquote initial="hidden" whileInView="show" viewport={{once:true,amount:.6}} variants={{show:{transition:{staggerChildren:.042}}}}>{words.map((x,i)=><motion.span key={i} className={'word'+(x.accent?' is-accent':'')} variants={{hidden:{opacity:.3,y:'.12em'},show:{opacity:1,y:0}}} transition={{duration:.65,ease}}>{x.w}</motion.span>)}</motion.blockquote>}
        <figcaption><span className="why__tag">Proposed wording · awaiting founder approval</span></figcaption>
      </figure>
      <ul className="why__cards" aria-label="Outspoken co-founders">
        {data.founders.map((f,i)=><motion.li key={f.name} initial={still?false:{opacity:0,y:28}} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.5}} transition={{duration:.7,delay:i*.12,ease}}>
          <a className="why__card" href={f.href} target="_blank" rel="me noopener noreferrer" aria-label={`Open ${f.name}’s LinkedIn profile, opens in a new tab`}>
            <img src={f.photo} width="72" height="72" loading="lazy" decoding="async" alt=""/>
            <span className="why__copy"><strong>{f.name}</strong><span>{f.role}</span><small>{f.bio}</small></span>
            <span className="why__link" aria-hidden="true">LinkedIn ↗</span>
          </a>
        </motion.li>)}
      </ul>
      <p className="why__note">{data.note}</p>
    </div>
  </section>;
}
