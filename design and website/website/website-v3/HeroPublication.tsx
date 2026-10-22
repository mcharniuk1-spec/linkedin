import {useEffect,useId,useRef,useState,type ReactNode} from 'react';
import {createPortal} from 'react-dom';
import {useReducedMotion} from 'motion/react';
import './hero-publication.css';

export function HeroPublication({post,children,onOpenChange}:{post:{body?:string;title:string};children:ReactNode;onOpenChange?:(open:boolean)=>void}){
  const [open,setOpen]=useState(false),[closing,setClosing]=useState(false),dialog=useRef<HTMLDialogElement>(null),trigger=useRef<HTMLButtonElement>(null),closeButton=useRef<HTMLButtonElement>(null),reduced=useReducedMotion(),id=useId();
  useEffect(()=>{if(!open)return;const node=dialog.current;if(!node)return;node.showModal();closeButton.current?.focus({preventScroll:true});const before=document.body.style.overflow;document.body.style.overflow='hidden';return()=>{node.close();document.body.style.overflow=before;trigger.current?.focus({preventScroll:true});};},[open]);
  const close=()=>{if(closing)return;setClosing(true);onOpenChange?.(false);const finish=()=>{dialog.current?.close();setOpen(false);setClosing(false);};if(reduced||!dialog.current)return finish();dialog.current.animate([{opacity:1,transform:'translateY(0) scale(1)'},{opacity:0,transform:'translateY(12px) scale(.98)'}],{duration:220,easing:'ease-in',fill:'forwards'}).finished.then(finish,finish);};
  return <><article className="hero-publication" aria-label="Illustrative LinkedIn publication">
    <header><img src="/assets/revisions/v5/people/avatar-b.webp" alt="Fictional founder portrait" width="32" height="32"/><span><strong>Founder perspective</strong><small>Illustrative LinkedIn post</small></span><i aria-hidden="true">•••</i></header>
    <p className="hero-publication__excerpt">{post.body}</p>
    <div className="hero-publication__art"><h3>{post.title}</h3><img src="/assets/revisions/v5/identity/selected/flat.svg" alt="" width="28" height="40"/></div>
    <p className="hero-publication__disclosure">Illustrative work · not client content</p>
    <footer><span aria-hidden="true">Like　 Comment　 Repost</span><button ref={trigger} type="button" aria-haspopup="dialog" onClick={()=>{setOpen(true);onOpenChange?.(true);}}>Read post ↗</button></footer>
  </article>{open?createPortal(<dialog ref={dialog} className="hero-post-dialog" aria-labelledby={id} onCancel={e=>{e.preventDefault();close();}} onClick={e=>{if(e.target===e.currentTarget)close();}}><div className="hero-post-reader"><header><h2 id={id}>Illustrative LinkedIn publication</h2><button ref={closeButton} type="button" onClick={close} aria-label="Close publication">Close ×</button></header>{children}</div></dialog>,document.body):null}</>;
}
