import { useState, type ReactNode } from 'react';
import { ActionButton, approvedCopy, Container, IconGlyph, illustrativeLabel, LogoLockup, SurfacePlate, TextField, TextArea, CheckboxField, StatusFeedback, TextLink, TypeRole, type ChildrenProps } from './foundations';
// Semantic compatibility for historical media inputs. IDs are chosen by meaning, not number.
// The contextual caption/alt remains the caller's responsibility; these objects are editorial metaphors.
export const baselineObjectAliases: Readonly<Record<string,string>> = {
  'OS-O201':'OS-O305', // First-hand experience
  'OS-O202':'OS-O310', // Useful follow-up
  'OS-O203':'OS-O301', // Founder voice
  'OS-O204':'OS-O319', // Buyer problem
  'OS-O205':'OS-O314', // Buying group
  'OS-O206':'OS-O302', // Point of view
  'OS-O207':'OS-O318', // Capability to value
  'OS-O208':'OS-O313', // Distinct position
  'OS-O209':'OS-O313', // Content direction
  'OS-O210':'OS-O312', // Claim evidence
  'OS-O211':'OS-O318', // Technical trade-offs
  'OS-O212':'OS-O305', // Product decision
  'OS-O213':'OS-O304', // Source to draft
  'OS-O214':'OS-O304', // Clear argument
  'OS-O215':'OS-O315', // Focused idea
  'OS-O216':'OS-O306', // Document sequence
  'OS-O217':'OS-O317', // Founder video
  'OS-O218':'OS-O324', // Format adaptation
  'OS-O219':'OS-O304', // Exact revision
  'OS-O220':'OS-O312', // Founder approval
  'OS-O221':'OS-O322', // Ready-to-post handoff
  'OS-O222':'OS-O319', // Buyer relevance
  'OS-O223':'OS-O307', // Learning review
  'OS-O224':'OS-O304', // Deliberate improvement
};
export function resolveBrandMediaSource(src?:string):string|undefined {
  if(src==='/assets/masters/OS-O010-fictional-founder.png') return '/assets/revisions/v2/photos/OS-PH205.png';
  const legacy=src?.match(/^\/assets\/revisions\/v2\/objects\/(OS-O\d{3})\.(png|webp|svg)$/);
  if(!legacy) return src;
  const current=baselineObjectAliases[legacy[1]];
  return current ? `/assets/revisions/v5/objects/${current}-front.png` : src;
}
export function SectionHeading({eyebrow,title,children}:ChildrenProps&{eyebrow?:string;title:string}){return <header className="os-section-heading">{eyebrow?<EditorialLabel>{eyebrow}</EditorialLabel>:null}<TypeRole role="h2">{title}</TypeRole>{children?<p className="os-type-lead">{children}</p>:null}</header>}
export function ServiceCard({title,number,children,steps=[]}:ChildrenProps&{title:string;number?:string;steps?:string[]}){return <article className="os-service"><span className="os-service-number">{number??'01'}</span><h3>{title}</h3><div>{children}</div>{steps.length?<ul>{steps.map(s=><li key={s}>{s}</li>)}</ul>:null}</article>}
export function PersonCard({name,role,src,fictional=true}: {name:string;role:string;src?:string;fictional?:boolean}){return <article className="os-person"><MediaShellMask src={src} alt={`${fictional?'Fictional portrait of ':''}${name}`} ratio="portrait"/><h3>{name}</h3><p>{role}</p>{fictional?<EditorialLabel>Fictional person · design specimen</EditorialLabel>:null}</article>}
export function ResourceCard({title,description,href,category='Field notes'}:{title:string;description:string;href?:string;category?:string}){return <article className="os-resource"><EditorialLabel>{category}</EditorialLabel><h3>{title}</h3><p>{description}</p><TextLink href={href}>Read the note</TextLink></article>}
export function ContactFormSpecimen(){const [sent,setSent]=useState(false);return <form className="os-form" onSubmit={e=>{e.preventDefault();setSent(true)}}><EditorialLabel>Local form specimen · no data is sent</EditorialLabel><TextField label="Your name" name="name" autoComplete="name" required/><TextField label="Work email" name="email" type="email" autoComplete="email" required/><TextArea label="What would you like buyers to understand?" name="message" required/><CheckboxField label="I understand this is a local demonstration." required/><ActionButton type="submit">Preview enquiry</ActionButton>{sent?<StatusFeedback status="success">Your local preview is complete. Nothing was sent or stored.</StatusFeedback>:null}</form>}
type BannerProps={title?:string;children?:ReactNode;action?:ReactNode;media?:ReactNode};
export function CentralHeroBanner({title=approvedCopy.hero,children=approvedCopy.vp,action,media}:BannerProps){return <section className="os-hero"><div className="os-hero-copy"><EditorialLabel>Founder branding · LinkedIn content</EditorialLabel><h1>{title}</h1><p className="os-type-lead">{children}</p>{action??<ActionButton disabled title="Booking destination pending">{approvedCopy.cta}</ActionButton>}</div>{media?<div className="os-hero-media">{media}</div>:null}</section>}
export function FullWidthSectionBanner({title='Your experience has a buyer-facing story.',children,action,media}:BannerProps){return <section className="os-banner os-banner-full os-tone-navy"><div><h2>{title}</h2>{children?<p>{children}</p>:null}{action}</div>{media}</section>}
export function InlineContextBanner({title='A useful perspective starts with a better question.',children,action}:BannerProps){return <aside className="os-banner os-banner-inline"><div><h3>{title}</h3>{children?<p>{children}</p>:null}</div>{action}</aside>}
export function SideBanner({title='Keep the buyer in the room.',children,action}:BannerProps){return <aside className="os-banner os-banner-side"><span className="os-fine-rule"/><h3>{title}</h3>{children?<p>{children}</p>:null}{action}</aside>}
export function CTABanner({title='Let’s find the story worth telling.',children,action}:BannerProps){return <section className="os-banner os-banner-cta"><div><h2>{title}</h2>{children?<p>{children}</p>:null}</div>{action??<ActionButton disabled>{approvedCopy.cta}</ActionButton>}</section>}
export function AnnouncementBanner({title='A new founder field note',children,action,dismissible=true}:BannerProps&{dismissible?:boolean}){const [visible,setVisible]=useState(true);return visible?<aside className="os-announcement" aria-label="Announcement"><div><strong>{title}</strong>{children?<span> {children}</span>:null}</div>{action}{dismissible?<button className="os-icon-button" aria-label="Dismiss announcement" onClick={()=>setVisible(false)}><IconGlyph name="close"/></button>:null}</aside>:null}
export function PublicationVideoBanner({title='Founder thinking. Buyer relevance.',children,media}:BannerProps){return <section className="os-publication-banner"><div><EditorialLabel>Founder content example</EditorialLabel><h2>{title}</h2>{children?<p>{children}</p>:null}</div>{media??<MediaShellMask alt="Video media pending"/>}</section>}
export function ProofDataCard({title,claim,source,status='hypothesis'}:{title:string;claim:string;source?:{label:string;href:string};status?:'fact'|'interpretation'|'hypothesis'|'gap'}){return <article className="os-proof"><EditorialLabel>{status}</EditorialLabel><h3>{title}</h3><p>{claim}</p><SourceFootnote label={source?.label??'Source required before use as evidence'} href={source?.href}/></article>}
export function EditorialLabel({children}:ChildrenProps){return <span className="os-editorial-label">{children}</span>}
export function QuoteAttribution({quote,name,role,fictional=true}:{quote:string;name:string;role?:string;fictional?:boolean}){return <figure className="os-quote"><blockquote>{quote}</blockquote><figcaption><strong>{name}</strong>{role?<span> · {role}</span>:null}</figcaption>{fictional?<p className="os-fiction-label">{illustrativeLabel}</p>:null}</figure>}
export function ChecklistSteps({items,current=0}:{items:string[];current?:number}){return <ol className="os-steps">{items.map((item,i)=><li key={`${i}-${item}`} aria-current={i===current?'step':undefined}><span className="os-step-marker">{i<current?<IconGlyph name="check" size={16}/>:String(i+1).padStart(2,'0')}</span><span>{item}</span></li>)}</ol>}
export function ComparisonGrid({headers,rows}:{headers:[string,string,string];rows:[string,string,string][]}){return <div className="os-table-wrap" tabIndex={0} role="region" aria-label="Comparison table"><table className="os-comparison"><thead><tr>{headers.map(h=><th scope="col" key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{r.map((c,j)=>j===0?<th scope="row" key={j}>{c}</th>:<td key={j}>{c}</td>)}</tr>)}</tbody></table></div>}
export function SourceFootnote({label,href,number=1}:{label:string;href?:string;number?:number}){return <p className="os-source"><span>[{number}]</span> {href?<a href={href}>{label}</a>:label}</p>}
export function NativePostFrame({author='Maya Reed',role='Fictional founder · B2B AI SaaS',children,artwork}:ChildrenProps&{author?:string;role?:string;artwork?:ReactNode}){return <article className="os-native-post"><header><span className="os-avatar" aria-hidden="true">{author.split(' ').map(n=>n[0]).join('')}</span><div><strong>{author}</strong><p>{role}</p></div><IconGlyph name="source" size={18}/></header><div className="os-post-copy">{children}</div>{artwork?<div className="os-post-artwork">{artwork}</div>:null}<p className="os-fiction-label">Illustrative post · fictional person</p><footer><span>Like</span><span>Comment</span><span>Repost</span><span>Send</span></footer></article>}
export function MediaShellMask({src,alt,ratio='landscape',children}:ChildrenProps&{src?:string;alt:string;ratio?:'landscape'|'portrait'|'square'}){const [failed,setFailed]=useState(false);return <figure className={`os-media os-media-${ratio}`}>{src&&!failed?<img src={resolveBrandMediaSource(src)} alt={alt} onError={()=>setFailed(true)}/>:<div className="os-media-fallback"><IconGlyph name="play" size={36}/><p>{alt}</p><span className="os-type-label">Media placeholder · no footage supplied</span></div>}{children?<figcaption>{children}</figcaption>:null}</figure>}
export function MetricWithSource({value,label,source,qualifier=''}:{value:string;label:string;source:{label:string;href?:string};qualifier?:string}){return <figure className="os-metric"><strong>{value}</strong><figcaption>{label}</figcaption>{qualifier?<p className="os-type-support">{qualifier}</p>:null}<SourceFootnote {...source}/></figure>}
export function PaginationSeries({page,total,onChange}:{page:number;total:number;onChange?:(page:number)=>void}){return <nav className="os-pagination" aria-label="Series pages"><button aria-label="Previous page" disabled={page<=1} onClick={()=>onChange?.(page-1)}>←</button><span aria-live="polite">{page} / {total}</span><button aria-label="Next page" disabled={page>=total} onClick={()=>onChange?.(page+1)}>→</button></nav>}
export function DemoFeedbackCard({kind='email',name='Alex Morgan',children='The interview helped me see the idea I wanted to explain.'}:ChildrenProps&{kind?:'email'|'comment';name?:string}){return <article className="os-feedback"><p className="os-fiction-label">{illustrativeLabel}</p><header><IconGlyph name={kind==='email'?'mail':'chat'}/><div><strong>{name} · demo identity</strong><p>{kind==='email'?'alex@example.com':'Illustrative comment'}</p></div></header><div>{children}</div><footer>Demo content · no customer outcome claimed</footer></article>}
export function OpeningTitle({eyebrow='Founder perspective',title='The customer problem behind the product.'}:{eyebrow?:string;title?:string}){return <div className="os-video-title"><EditorialLabel>{eyebrow}</EditorialLabel><h2>{title}</h2><span className="os-fine-rule"/></div>}
export function LowerThird({name='Maya Reed',role='Fictional founder · design specimen'}:{name?:string;role?:string}){return <div className="os-lower-third"><strong>{name}</strong><span>{role}</span></div>}
export function Captions({text,activeWord}:{text:string;activeWord?:string}){return <p className="os-captions">{activeWord&&text.includes(activeWord)?<>{text.slice(0,text.indexOf(activeWord))}<mark>{activeWord}</mark>{text.slice(text.indexOf(activeWord)+activeWord.length)}</>:text}</p>}
export function EmphasisWordNumber({children,variant='highlight'}:ChildrenProps&{variant?:'highlight'|'underline'|'number'}){return variant==='highlight'?<mark className="os-emphasis">{children}</mark>:<strong className={`os-emphasis-${variant}`}>{children}</strong>}
export function CitationOverlay({label,href}:{label:string;href?:string}){return <aside className="os-citation-overlay"><SourceFootnote label={label} href={href}/></aside>}
export function ChapterDivider({number='01',title}:{number?:string;title:string}){return <div className="os-chapter"><span>{number}</span><h2>{title}</h2><span className="os-fine-rule"/></div>}
export function ClosingCTA({title=approvedCopy.hero,href}:{title?:string;href?:string}){return <div className="os-closing"><LogoLockup/><h2>{title}</h2><TextLink href={href}>{approvedCopy.cta}</TextLink></div>}
export function WatermarkSignature({inverse=false}:{inverse?:boolean}){return <div className="os-watermark"><LogoLockup inverse={inverse}/></div>}
export function PresenterMediaScene({src,name='Maya Reed',caption='Make the customer problem clear.'}:{src?:string;name?:string;caption?:string}){return <section className="os-presenter"><MediaShellMask src={src} alt={`Fictional presenter ${name}`}/><div className="os-presenter-overlays"><LowerThird name={name}/><Captions text={caption}/><WatermarkSignature inverse/></div></section>}
export function ObjectProcessScene({steps=['Interview','Strategy','Drafts','Founder approval']}: {steps?:string[]}){return <section className="os-object-process"><EditorialLabel>From experience to authored content</EditorialLabel><ChecklistSteps items={steps}/><figure className="os-process-object" data-object="OS-O304"><img src="/assets/revisions/v3/objects/OS-O304.webp" alt="Satin blue and silver ink pen for professional editorial writing" width={600} height={600}/><figcaption>Professional writing · founder approval stays with you.</figcaption></figure></section>}
export function EvidenceComparisonScene(){return <section className="os-evidence-scene"><SectionHeading eyebrow="Editorial specimen" title="A claim is only as useful as its evidence."/><ComparisonGrid headers={['Question','Unclear claim','Source-led alternative']} rows={[["What changed?","The market wants this.","Three interviewees described this problem."],["What is known?","Our approach always works.","We can explain the method and its limits."]]}/><SourceFootnote label="Illustrative wording comparison; no research result is asserted."/></section>}
export function ClosingScene({href}:{href?:string}){return <section className="os-closing-scene"><ClosingCTA href={href}/><p>Founder branding. LinkedIn content.</p><span className="os-fine-rule"/></section>}
