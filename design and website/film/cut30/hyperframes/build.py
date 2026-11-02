#!/usr/bin/env python3
"""Generates index.html and compositions/*.html of the Outspoken 30-second film (HyperFrames).
Run from this folder: python3 build.py. Edit the templates here, then re-run; the generated HTML is plain HyperFrames source."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SPRITE = (ROOT / "assets/brand/icons-d05.svg").read_text()

# ---- timing (seconds), see ../SPEC-30S.md and VOICEOVER-30S.md
T = dict(cut1=3.30, cut2=5.70, cut3=10.90, cut4=13.85, cut5=17.50, cut6=21.30, end=30.0)
HOSTS = [  # id, start, duration
    ("s1", 0.00, 3.60), ("s2", 3.30, 2.60), ("s3", 5.70, 5.50), ("s4", 10.90, 3.30),
    ("s5", 13.60, 4.15), ("s6", 17.20, 4.30), ("s7", 21.30, 8.70),
]
# caption chunks: text, start, end, hidden (True = the picture already shows the words)
CAPTIONS = [
    ("You know your product better than anyone.", 0.30, 3.00, False),
    ("Your buyers decide in seconds.", 3.40, 5.40, False),
    ("We start with your experience,", 5.80, 7.72, False),
    ("then find the question your buyer already asks.", 7.72, 10.80, False),
    ("We write it in your voice.", 11.20, 13.60, False),
    ("Then show it clearly: posts, stories, carousels, video.", 14.00, 17.20, False),
    ("Profile, content and campaigns.", 17.60, 19.54, False),
    ("One connected message.", 19.54, 21.00, False),
]


def icon(name, size):
    m = re.search(r'<symbol id="%s" viewBox="0 0 24 24">(.*?)</symbol>' % name, SPRITE, re.S)
    inner = re.sub(r"<title>.*?</title>", "", m.group(1))
    return '<svg class="ico" width="%d" height="%d" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (size, size, inner)


PRELUDE = r"""
@font-face{font-family:'Fraunces';src:url('assets/fonts/fraunces.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Mona Sans';src:url('assets/fonts/mona-sans.woff2') format('woff2');font-weight:200 900}
@font-face{font-family:'Geist Mono';src:url('assets/fonts/geist-mono.woff2') format('woff2');font-weight:100 900}
#root{position:absolute;inset:0;overflow:hidden;font-family:'Mona Sans',sans-serif;color:#162760}
#root *{box-sizing:border-box}
.pearl{position:absolute;inset:0;background:linear-gradient(160deg,#fff 6%,#F1F3F6 58%,#E4EAF0)}
.deep{position:absolute;inset:0;background:radial-gradient(900px 900px at 80% 10%,rgba(49,87,213,.30),transparent 62%),radial-gradient(760px 760px at 8% 92%,rgba(234,169,60,.13),transparent 60%),#0D1A3B}
.dots{position:absolute;inset:0;background:radial-gradient(rgba(22,39,96,.15) 2.5px,transparent 3.5px) 0 0/48px 48px}
.dots.lt{background:radial-gradient(rgba(241,243,246,.13) 2.5px,transparent 3.5px) 0 0/48px 48px}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.09em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.03}
.pill{position:absolute;display:inline-flex;align-items:center;gap:16px;padding:15px 30px 15px 24px;border:2px solid #D9DEE7;border-radius:999px;background:rgba(255,255,255,.94);box-shadow:0 16px 34px -20px rgba(22,39,96,.45);font-size:28px;white-space:nowrap}
.pill::before{content:"";width:15px;height:15px;border-radius:50%;background:#EAA93C;flex:none}
.sel{position:relative;display:inline-block;padding:0 .12em;border-radius:10px;color:#162760;background:linear-gradient(#F6D591,#F6D591) left center/0% 100% no-repeat;outline:3px dashed rgba(22,39,96,0);outline-offset:10px}
.sel i{position:absolute;width:20px;height:20px;background:#fff;border:3px solid #162760;border-radius:3px;opacity:0;transform:scale(.3)}
.sel i:nth-of-type(1){left:-20px;top:-20px}.sel i:nth-of-type(2){right:-20px;top:-20px}.sel i:nth-of-type(3){left:-20px;bottom:-20px}.sel i:nth-of-type(4){right:-20px;bottom:-20px}
.ico{overflow:visible;flex:none;--icon-marker:#EAA93C}
.card{position:absolute;background:#fff;border:2px solid rgba(22,39,96,.12);border-radius:44px;box-shadow:0 44px 80px -46px rgba(22,39,96,.55)}
.bar{height:24px;border-radius:12px;background:#DDE3EC}
.bar.m{background:#C8D0DD}
.tag{font-family:'Geist Mono',monospace;font-weight:500;font-size:28px;letter-spacing:.09em;text-transform:uppercase;color:#475477}
.w{display:inline-block;will-change:transform,opacity}
.ln{display:block;white-space:nowrap}
"""

SEL_JS = r"""
function selIn(tl, el, t){
  tl.fromTo(el,{backgroundSize:'0% 100%',outlineColor:'rgba(22,39,96,0)'},{backgroundSize:'100% 100%',outlineColor:'rgba(22,39,96,.6)',duration:.7,ease:'power3.out'},t);
  tl.fromTo(el.querySelectorAll('i'),{opacity:0,scale:.3},{opacity:1,scale:1,duration:.35,ease:'back.out(2.4)',stagger:.06},t+.42);
}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
"""


def scene(sid, dur, body_html, css, js):
    return """<template>
  <style>%s
%s</style>
  <div id="root" data-composition-id="%s" data-width="1080" data-height="1920">
%s
  </div>
  <script>
  (function(){
    %s
    const tl = gsap.timeline({ paused: true });
%s
    window.__timelines["%s"] = tl;
  })();
  </script>
</template>
""" % (PRELUDE, css, sid, body_html, SEL_JS, js, sid)


def SEL(word):
    return '<span class="sel">%s<i></i><i></i><i></i><i></i></span>' % word


# ------------------------------------------------------------------ S1 hook
S1_HTML = """
    <div class="pearl"></div><div class="dots"></div>
    <div id="s1-stage" style="position:absolute;inset:0;transform-origin:70%% 70%%">
      <img id="s1-fig" src="assets/heroes/h1-shadow.webp" alt="" style="position:absolute;left:150px;top:690px;width:1260px;height:auto">
      <div id="s1-pill" class="pill mono" style="left:70px;top:290px">Founder-led LinkedIn marketing</div>
      <div id="s1-head" class="disp" style="position:absolute;left:70px;top:380px;font-size:176px;color:#162760">
        <span class="ln"><span class="w s1w">You</span> <span class="w s1w">know</span></span>
        <span class="ln"><span class="w s1w">your</span></span>
        <span class="ln"><span class="w s1w" id="s1-pw">%s</span></span>
      </div>
    </div>""" % SEL("product.")
S1_CSS = ""
S1_JS = r"""
    const w = document.querySelectorAll('.s1w');
    tl.fromTo('#s1-stage',{scale:1},{scale:1.07,duration:3.6,ease:'none'},0);
    tl.fromTo('#s1-fig',{x:110,opacity:1},{x:0,opacity:1,duration:1.4,ease:'power3.out'},0);
    tl.fromTo('#s1-pill',{opacity:1},{opacity:1,duration:.1},0);
    // the first word is already on screen at frame 0 (the thumbnail is the hook)
    [2,3].forEach((i,k)=>tl.fromTo(w[i],{y:70,opacity:0,filter:'blur(14px)'},{y:0,opacity:1,filter:'blur(0px)',duration:.6,ease:'power4.out'},0.08+k*0.22));
    selIn(tl, document.querySelector('#s1-pw .sel'), 0.95);
"""

# ------------------------------------------------------------------ S2 decision
def profile_card(i, avatar, name_w, pos):
    return """
      <div class="card pc" id="s2-pc%d" style="left:150px;top:660px;width:780px;height:470px;padding:44px;z-index:%d">
        <div style="display:flex;gap:34px;align-items:center">
          <img src="assets/heroes/%s" alt="" style="width:150px;height:150px;border-radius:50%%;object-fit:cover;%s">
          <div style="flex:1;display:grid;gap:18px"><div class="bar m" style="width:%dpx;height:30px"></div><div class="bar" style="width:%dpx"></div></div>
        </div>
        <div style="margin-top:44px;display:grid;gap:18px"><div class="bar m" style="width:92%%;height:28px"></div><div class="bar" style="width:78%%"></div><div class="bar" style="width:64%%"></div></div>
        <div style="margin-top:36px;display:flex;gap:16px"><div class="bar m" style="width:150px;height:44px;border-radius:22px"></div><div class="bar" style="width:190px;height:44px;border-radius:22px"></div></div>
      </div>""" % (i, 10 - i, avatar, pos, name_w, name_w - 120)


S2_HTML = """
    <div class="deep"></div><div class="dots lt"></div>
    <div id="s2-head" class="disp" style="position:absolute;left:70px;top:290px;font-size:140px;color:#F1F3F6">
      <span class="ln"><span class="w s2w">Buyers</span> <span class="w s2w">decide</span></span>
      <span class="ln"><span class="w s2w">in</span> <span class="w s2w" id="s2-pw">%s</span></span>
    </div>
    %s%s%s
    <svg id="s2-ring" width="190" height="190" viewBox="0 0 190 190" style="position:absolute;left:770px;top:560px;z-index:20">
      <circle cx="95" cy="95" r="80" fill="#0D1A3B" stroke="rgba(241,243,246,.22)" stroke-width="8"/>
      <circle id="s2-arc" cx="95" cy="95" r="80" fill="none" stroke="#EAA93C" stroke-width="12" stroke-linecap="round" stroke-dasharray="502.7" stroke-dashoffset="502.7" transform="rotate(-90 95 95)"/>
      <text x="95" y="108" text-anchor="middle" font-family="Geist Mono" font-weight="500" font-size="40" fill="#F1F3F6">2s</text>
    </svg>
    <div id="s2-tag" class="tag" style="position:absolute;left:150px;top:1150px;color:#A9AFBA">Illustrative profiles</div>""" % (
    SEL("seconds."),
    profile_card(0, "h3-avatar-a.webp", 330, ""),
    profile_card(1, "h4-avatar-b.webp", 300, ""),
    profile_card(2, "h2-founder.webp", 360, "object-position:56% 22%;"))
S2_CSS = ".pc{transform-origin:20% 80%}"
S2_JS = r"""
    const w = document.querySelectorAll('.s2w');
    tl.fromTo(w,{y:60,opacity:0},{y:0,opacity:1,duration:.55,ease:'power4.out',stagger:.1},0.28);
    selIn(tl, document.querySelector('#s2-pw .sel'), 0.9);
    tl.fromTo('#s2-pc0',{y:90,opacity:0,scale:.96},{y:0,opacity:1,scale:1,duration:.6,ease:'power4.out'},0.25);
    tl.fromTo('#s2-pc1',{y:70,opacity:.0,scale:.94},{y:34,opacity:1,scale:.965,duration:.6,ease:'power4.out'},0.35);
    tl.fromTo('#s2-pc2',{y:60,opacity:.0,scale:.92},{y:68,opacity:1,scale:.93,duration:.6,ease:'power4.out'},0.45);
    tl.fromTo('#s2-arc',{strokeDashoffset:502.7},{strokeDashoffset:0,duration:2.0,ease:'none'},0.35);
    tl.fromTo('#s2-ring',{scale:.5,opacity:0},{scale:1,opacity:1,duration:.5,ease:'back.out(2)'},0.3);
    tl.to('#s2-pc0',{x:-1300,rotation:-16,duration:.42,ease:'power3.in'},0.95);
    tl.to('#s2-pc1',{scale:1,y:0,duration:.3,ease:'power2.out'},0.95);
    tl.to('#s2-pc1',{x:-1300,rotation:-14,duration:.42,ease:'power3.in'},1.52);
    tl.to('#s2-pc2',{scale:1,y:0,duration:.3,ease:'power2.out'},1.52);
    tl.fromTo('#s2-tag',{opacity:0},{opacity:1,duration:.4},0.9);
"""

# ------------------------------------------------------------------ S3 experience -> question
CHIPS = [("Experience", "mic"), ("Methods", "strategy"), ("Tools", "automation"), ("Product judgment", "usefulness")]
chip_html = ""
for i, (label, ic) in enumerate(CHIPS):
    chip_html += """
      <div class="chip" id="s3-chip%d" style="position:absolute;left:60px;top:%dpx;width:490px;height:104px;border-radius:52px;background:#fff;border:2px solid rgba(22,39,96,.14);box-shadow:0 22px 40px -28px rgba(22,39,96,.5);display:flex;align-items:center;gap:20px;padding:0 28px;font-size:36px;font-weight:600;white-space:nowrap">%s<span>%s</span></div>""" % (
        i, 330 + i * 134, icon(ic, 54), label)
S3_HTML = """
    <div class="pearl"></div><div class="dots"></div>
    <div id="s3-k1" class="tag" style="position:absolute;left:70px;top:262px">From your experience</div>
    <div id="s3-k2" class="tag" style="position:absolute;left:70px;top:262px;opacity:0;color:#162760">to the buyer&rsquo;s question</div>
    %s
    <svg id="s3-paths" width="1080" height="1000" viewBox="0 0 1080 1000" style="position:absolute;left:0;top:0;overflow:visible">
      <g fill="none" stroke="#A9AFBA" stroke-width="4" stroke-linecap="round">
        <path id="s3-p0" d="M550 382 C 640 382, 600 560, 650 600"/>
        <path id="s3-p1" d="M550 516 C 640 516, 610 580, 650 600"/>
        <path id="s3-p2" d="M550 650 C 640 650, 610 620, 650 600"/>
        <path id="s3-p3" d="M550 784 C 640 784, 600 650, 650 600"/>
      </g>
      <circle id="s3-node" cx="650" cy="600" r="30" fill="#EAA93C"/>
      <circle id="s3-halo" cx="650" cy="600" r="30" fill="none" stroke="#EAA93C" stroke-width="5" opacity="0"/>
    </svg>
    <div id="s3-card" class="card" style="left:560px;top:640px;width:470px;height:470px;padding:40px;transform-origin:15%% 10%%">
      <div style="display:flex;gap:22px;align-items:center"><img src="assets/heroes/h4-avatar-b.webp" alt="" style="width:92px;height:92px;border-radius:50%%;object-fit:cover"><div style="display:grid;gap:14px;flex:1"><div class="bar m" style="width:200px"></div><div class="bar" style="width:140px;height:18px"></div></div></div>
      <div class="disp" style="font-size:210px;line-height:1;margin:14px 0 0 6px;color:#162760">%s</div>
      <div style="display:grid;gap:14px;margin-top:8px"><div class="bar" style="width:90%%"></div><div class="bar" style="width:68%%"></div></div>
    </div>
    <div id="s3-cap" class="tag" style="position:absolute;left:560px;top:1130px">Illustrative post</div>""" % (chip_html, SEL("?"))
S3_CSS = ""
S3_JS = r"""
    document.querySelectorAll('#s3-paths path').forEach(p=>{const l=p.getTotalLength();p.style.strokeDasharray=l;p.dataset.l=l});
    tl.fromTo('#s3-k1',{opacity:0,y:16},{opacity:1,y:0,duration:.5,ease:'power4.out'},0.1);
    [0,1,2,3].forEach(i=>{
      tl.fromTo('#s3-chip'+i,{x:-620,opacity:0},{x:0,opacity:1,duration:.7,ease:'power4.out'},0.15+i*0.14);
      const p=document.querySelector('#s3-p'+i),l=+p.dataset.l;
      tl.fromTo(p,{strokeDashoffset:l},{strokeDashoffset:0,duration:.65,ease:'power2.inOut'},0.95+i*0.12);
    });
    tl.fromTo('#s3-node',{scale:0,transformOrigin:'650px 600px'},{scale:1,duration:.5,ease:'back.out(3)'},1.35);
    tl.fromTo('#s3-halo',{scale:1,opacity:.8,transformOrigin:'650px 600px'},{scale:3.2,opacity:0,duration:.9,ease:'power2.out'},1.9);
    tl.to('#s3-k1',{opacity:0,y:-14,duration:.3},2.3);
    tl.fromTo('#s3-k2',{opacity:0,y:16},{opacity:1,y:0,duration:.5,ease:'power4.out'},2.4);
    tl.fromTo('#s3-card',{scale:.2,opacity:0,rotation:-4},{scale:1,opacity:1,rotation:0,duration:.75,ease:'back.out(1.8)'},2.5);
    selIn(tl, document.querySelector('#s3-card .sel'), 3.1);
    tl.fromTo('#s3-cap',{opacity:0},{opacity:1,duration:.4},3.0);
    tl.fromTo('#s3-paths',{opacity:1},{opacity:.35,duration:.6},3.0);
    tl.fromTo('#s3-card',{y:0},{y:-18,duration:2.2,ease:'sine.inOut'},3.4);
"""

# ------------------------------------------------------------------ S4 voice
S4_HTML = """
    <div class="pearl"></div><div class="dots"></div>
    <div id="s4-head" class="disp" style="position:absolute;left:70px;top:270px;font-size:158px">
      <span class="ln"><span class="w s4w">In</span> <span class="w s4w">your</span> <span class="w s4w" id="s4-pw">%s</span></span>
    </div>
    <svg id="s4-wave" width="1080" height="440" viewBox="0 0 1080 440" style="position:absolute;left:0;top:520px"></svg>
    <div id="s4-card" class="card" style="left:70px;top:700px;width:940px;height:420px;padding:44px 50px;transform-origin:50%% 50%%">
      <div style="display:flex;gap:26px;align-items:center"><img src="assets/heroes/h3-avatar-a.webp" alt="" style="width:100px;height:100px;border-radius:50%%;object-fit:cover"><div style="display:grid;gap:14px;flex:1"><div class="bar m" style="width:260px"></div><div class="bar" style="width:180px;height:18px"></div></div></div>
      <div id="s4-type" class="disp" style="font-size:78px;margin-top:34px;height:96px;white-space:nowrap"><span id="s4-txt"></span><span id="s4-caret" style="display:inline-block;width:6px;height:70px;margin-left:6px;background:#EAA93C;vertical-align:-6px"></span></div>
      <div style="display:grid;gap:16px;margin-top:20px"><div class="bar" style="width:94%%"></div><div class="bar" style="width:76%%"></div></div>
    </div>
    <div id="s4-mark" style="position:absolute;left:840px;top:250px;width:170px;height:225px">
      <i class="rg" style="position:absolute;left:-20px;top:20px;width:210px;height:210px;border:3px solid #EAA93C;border-radius:50%%;opacity:0"></i>
      <i class="rg" style="position:absolute;left:-20px;top:20px;width:210px;height:210px;border:3px solid #EAA93C;border-radius:50%%;opacity:0"></i>
      <i class="rg" style="position:absolute;left:-20px;top:20px;width:210px;height:210px;border:3px solid #EAA93C;border-radius:50%%;opacity:0"></i>
      <img src="assets/brand/mark-b01.svg" alt="" style="position:absolute;inset:0;width:170px;height:225px">
    </div>""" % SEL("voice.")
S4_CSS = ""
S4_JS = r"""
    const w = document.querySelectorAll('.s4w');
    tl.fromTo(w,{y:30,opacity:0},{y:0,opacity:1,duration:.35,ease:'power4.out',stagger:.06},0.0);
    selIn(tl, document.querySelector('#s4-pw .sel'), 0.45);
    // waveform ribbon: 15 sine lines, a function of time only
    const svg=document.querySelector('#s4-wave'),N=15,paths=[];
    for(let i=0;i<N;i++){const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('fill','none');p.setAttribute('stroke',i%5===2?'#3157D5':(i===7?'#EAA93C':'#A9AFBA'));p.setAttribute('stroke-width',i===7?5:(i%5===2?3.4:2.4));p.setAttribute('opacity',i===7?1:(i%5===2?.7:.85));svg.appendChild(p);paths.push(p)}
    const state={amp:0,t:0};
    function draw(){
      const t=state.t,a=state.amp;
      paths.forEach((p,i)=>{let d='';const ph=i*.42,fr=.0105+i*.00065;for(let x=0;x<=1080;x+=12){const env=Math.exp(-Math.pow((x-540)/330,2));const y=220+Math.sin(x*fr*6.28+ph+t*5.2)*(26+i*6)*env*a+Math.sin(x*.004+i+t*2.1)*14*a;d+=(x?'L':'M')+x+' '+y.toFixed(1)}p.setAttribute('d',d)})
    }
    draw();
    tl.to(state,{amp:1,duration:.5,ease:'power2.out',onUpdate:draw},0.2);
    tl.to(state,{t:3.2,duration:3.2,ease:'none',onUpdate:draw},0);
    tl.to(state,{amp:0,duration:.55,ease:'power3.in',onUpdate:draw},1.45);
    tl.fromTo('#s4-card',{scaleX:.05,scaleY:.5,opacity:0},{scaleX:1,scaleY:1,opacity:1,duration:.6,ease:'power4.out'},1.5);
    const msg='A decision, explained',txt=document.querySelector('#s4-txt');
    const typer={n:0};tl.to(typer,{n:msg.length,duration:1.0,ease:'none',onUpdate:()=>{txt.textContent=msg.slice(0,Math.round(typer.n))}},1.95);
    tl.fromTo('#s4-mark',{y:-40,opacity:0},{y:0,opacity:1,duration:.6,ease:'power4.out'},0.1);
    document.querySelectorAll('#s4-mark .rg').forEach((r,i)=>tl.fromTo(r,{scale:.7,opacity:.7},{scale:1.9,opacity:0,duration:1.4,ease:'power2.out'},0.25+i*.35));
    tl.fromTo('#s4-card',{y:0},{y:-14,duration:1.2,ease:'sine.inOut'},1.9);
"""

# ------------------------------------------------------------------ S5 show it clearly
def fmt_card(i, label, art):
    return """
      <div class="card fc" id="s5-c%d" style="left:150px;top:590px;width:780px;height:560px;padding:34px 40px;border-radius:44px">
        <div class="tag">%s</div>%s
      </div>""" % (i, label, art)

ART_POST = """<div style="margin-top:22px;display:flex;gap:22px;align-items:center"><img src="assets/heroes/h3-avatar-a.webp" alt="" style="width:84px;height:84px;border-radius:50%;object-fit:cover"><div style="display:grid;gap:12px;flex:1"><div class="bar m" style="width:240px"></div><div class="bar" style="width:170px;height:16px"></div></div></div>
<div class="disp" style="font-size:84px;margin-top:30px;color:#162760">A decision, explained.</div><div style="display:grid;gap:14px;margin-top:30px"><div class="bar" style="width:92%"></div><div class="bar" style="width:70%"></div></div>"""
ART_STORY = """<div style="position:absolute;left:250px;top:44px;width:280px;height:470px;border-radius:34px;background:linear-gradient(170deg,#1B2F78,#0D1A3B);overflow:hidden;box-shadow:0 30px 50px -30px rgba(22,39,96,.7)"><div style="position:absolute;left:50%;top:44%;width:170px;height:170px;margin:-85px 0 0 -85px;border:4px solid #EAA93C;border-radius:50%"></div><div style="position:absolute;left:50%;top:44%;width:90px;height:90px;margin:-45px 0 0 -45px;background:#F6D591;border-radius:50%"></div><div style="position:absolute;left:26px;right:26px;bottom:30px;display:grid;gap:12px"><div class="bar" style="background:rgba(241,243,246,.75);width:80%"></div><div class="bar" style="background:rgba(241,243,246,.4);width:55%"></div></div></div>"""
ART_CAR = """<div style="position:absolute;left:150px;top:70px;width:480px;height:400px"><div style="position:absolute;left:120px;top:30px;width:340px;height:360px;border-radius:30px;background:#DDE3EC"></div><div style="position:absolute;left:60px;top:15px;width:340px;height:360px;border-radius:30px;background:#C8D0DD"></div><div style="position:absolute;left:0;top:0;width:340px;height:360px;border-radius:30px;background:#fff;border:2px solid rgba(22,39,96,.14);padding:30px"><div class="disp" style="font-size:64px">Slide 1</div><div style="display:grid;gap:14px;margin-top:26px"><div class="bar" style="width:90%"></div><div class="bar" style="width:62%"></div></div></div></div><div style="position:absolute;left:0;right:0;bottom:30px;display:flex;gap:14px;justify-content:center"><i style="width:20px;height:20px;border-radius:50%;background:#EAA93C"></i><i style="width:20px;height:20px;border-radius:50%;background:#C8D0DD"></i><i style="width:20px;height:20px;border-radius:50%;background:#C8D0DD"></i></div>"""
ART_VID = """<div style="margin-top:20px;height:400px;border-radius:30px;position:relative;overflow:hidden"><img src="assets/heroes/h2-founder.webp" alt="" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:60% 30%"><div style="position:absolute;left:50%;top:50%;width:132px;height:132px;margin:-66px 0 0 -66px;border-radius:50%;background:#EAA93C;display:grid;place-items:center"><svg width="48" height="54" viewBox="0 0 46 52"><path d="M6 4l36 22L6 48z" fill="#162760"/></svg></div></div>"""
TABS = ["Post", "Story", "Carousel", "Video"]
tabs_html = "".join('<div class="tabx mono" id="s5-t%d" style="padding:12px 26px;border-radius:999px;font-size:28px;background:rgba(255,255,255,.9);border:2px solid #D9DEE7;color:#475477">%s</div>' % (i, n) for i, n in enumerate(TABS))
S5_HTML = """
    <div class="pearl"></div><div class="dots"></div>
    <div id="s5-head" class="disp" style="position:absolute;left:70px;top:270px;font-size:158px">
      <span class="ln"><span class="w s5w">Show</span> <span class="w s5w">it</span> <span class="w s5w" id="s5-pw">%s</span></span>
    </div>
    <div id="s5-tabs" style="position:absolute;left:70px;top:478px;display:flex;gap:14px;font-family:'Geist Mono',monospace">%s</div>%s%s%s%s
    <div id="s5-cap" class="tag" style="position:absolute;left:150px;top:1160px;color:#475477;font-size:28px">Illustrative formats</div>""" % (
    SEL("clearly."), tabs_html, fmt_card(0, "Post", ART_POST), fmt_card(1, "Story", ART_STORY), fmt_card(2, "Carousel", ART_CAR), fmt_card(3, "Video", ART_VID))
S5_CSS = ".fc{transform-origin:50% 100%}"
S5_JS = r"""
    const w = document.querySelectorAll('.s5w');
    tl.fromTo(w,{y:60,opacity:0,filter:'blur(12px)'},{y:0,opacity:1,filter:'blur(0px)',duration:.5,ease:'power4.out',stagger:.09},0.30);
    selIn(tl, document.querySelector('#s5-pw .sel'), 0.85);
    tl.fromTo('#s5-tabs',{opacity:0,y:16},{opacity:1,y:0,duration:.4,ease:'power3.out'},0.65);
    // one deck slot; the four formats take turns on the spoken words (global times 15.15 / 15.6 / 16.05 / 16.7)
    const at=[0.80,1.95,2.40,3.00];
    [0,1,2,3].forEach(i=>{
      tl.fromTo('#s5-c'+i,{x:i?900:0,y:i?0:90,rotation:i?7:0,opacity:i?0:0,scale:i?.96:.96},{x:0,y:0,rotation:0,opacity:1,scale:1,duration:i?.55:.6,ease:'power4.out'},at[i]);
      if(i<3) tl.to('#s5-c'+i,{x:-900,rotation:-8,opacity:0,duration:.4,ease:'power3.in'},at[i+1]);
      tl.to('#s5-t'+i,{backgroundColor:'#162760',color:'#F1F3F6',borderColor:'#162760',duration:.2},at[i]);
      if(i<3) tl.to('#s5-t'+i,{backgroundColor:'rgba(255,255,255,.9)',color:'#475477',borderColor:'#D9DEE7',duration:.25},at[i+1]);
    });
    tl.fromTo('#s5-cap',{opacity:0},{opacity:1,duration:.4},1.2);
"""

# ------------------------------------------------------------------ S6 system
NODES = [("Profile", "profile", 190), ("Content", "writing", 540), ("Campaigns", "advertising", 890)]
nodes_html = ""
for i, (lab, ic, cx) in enumerate(NODES):
    nodes_html += """
    <div class="nd" id="s6-n%d" style="position:absolute;left:%dpx;top:660px;width:170px;height:170px;border-radius:50%%;background:rgba(241,243,246,.07);border:3px solid rgba(241,243,246,.35);display:grid;place-items:center;color:#F1F3F6;--icon-marker:#F3C15D">%s</div>
    <div class="nl" id="s6-l%d" style="position:absolute;left:%dpx;top:850px;width:300px;text-align:center;font-size:44px;font-weight:600;color:#F1F3F6">%s</div>""" % (
        i, cx - 85, icon(ic, 84), i, cx - 150, lab)
S6_HTML = """
    <div class="deep"></div><div class="dots lt"></div>
    <div id="s6-title" class="disp" style="position:absolute;left:70px;top:270px;font-size:136px;color:#F1F3F6">
      <span class="ln"><span class="w s6w">One</span> <span class="w s6w" id="s6-pw">%s</span></span>
      <span class="ln"><span class="w s6w">message.</span></span>
    </div>
    <svg width="1080" height="1300" viewBox="0 0 1080 1300" style="position:absolute;left:0;top:0;overflow:visible">
      <g fill="none" stroke="rgba(169,175,186,.7)" stroke-width="4" stroke-linecap="round">
        <path id="s6-h0" d="M285 745 L 455 745"/><path id="s6-h1" d="M625 745 L 795 745"/>
        <path id="s6-v0" d="M190 930 C 190 1010, 540 990, 540 1066"/><path id="s6-v1" d="M540 930 L 540 1066"/><path id="s6-v2" d="M890 930 C 890 1010, 540 990, 540 1066"/>
      </g>
      <circle id="s6-ring" cx="540" cy="1080" r="26" fill="none" stroke="#EAA93C" stroke-width="4" opacity="0"/><circle id="s6-dot" cx="540" cy="1080" r="26" fill="#EAA93C"/>
    </svg>%s""" % (SEL("connected"), nodes_html)
S6_CSS = ""
S6_JS = r"""
    document.querySelectorAll('svg path').forEach(p=>{const l=p.getTotalLength();p.style.strokeDasharray=l;p.dataset.l=l});
    const names=['0','1','2'],at=[0.45,1.05,1.55];
    names.forEach((n,i)=>{
      tl.fromTo('#s6-n'+n,{scale:.2,opacity:0},{scale:1,opacity:1,duration:.55,ease:'back.out(2)'},at[i]-0.3);
      tl.fromTo('#s6-l'+n,{y:20,opacity:0},{y:0,opacity:1,duration:.5,ease:'power4.out'},at[i]);
    });
    ['#s6-h0','#s6-h1'].forEach((id,i)=>{const p=document.querySelector(id),l=+p.dataset.l;tl.fromTo(p,{strokeDashoffset:l},{strokeDashoffset:0,duration:.5,ease:'power2.inOut'},.9+i*.45)});
    ['#s6-v0','#s6-v1','#s6-v2'].forEach((id,i)=>{const p=document.querySelector(id),l=+p.dataset.l;tl.fromTo(p,{strokeDashoffset:l},{strokeDashoffset:0,duration:.6,ease:'power2.inOut'},1.6+i*.12)});
    tl.fromTo('#s6-dot',{scale:0,transformOrigin:'540px 1080px'},{scale:1,duration:.5,ease:'back.out(3)'},2.0);
    tl.fromTo('.s6w',{y:70,opacity:0,filter:'blur(14px)'},{y:0,opacity:1,filter:'blur(0px)',duration:.6,ease:'power4.out',stagger:.12},2.15);
    selIn(tl, document.querySelector('#s6-pw .sel'), 2.7);
    tl.fromTo('.deep',{scale:1},{scale:1.06,duration:4.3,ease:'none'},0);
    tl.fromTo('.dots',{y:0},{y:-70,duration:4.3,ease:'none'},0);
    tl.fromTo('.nd',{y:0},{y:-9,duration:1.1,ease:'sine.inOut',yoyo:true,repeat:1,stagger:.12},2.1);
    [2.6,3.3].forEach(tt=>tl.fromTo('#s6-ring',{scale:1,opacity:.9,transformOrigin:'540px 1080px'},{scale:4.2,opacity:0,duration:.8,ease:'power2.out'},tt));
"""

# ------------------------------------------------------------------ S7 close
S7_HTML = """
    <div class="deep"></div><div class="dots lt"></div>
    <svg id="s7-wave" width="1080" height="560" viewBox="0 0 1080 560" style="position:absolute;left:0;top:1380px;overflow:visible"></svg>
    <div id="s7-mark" style="position:absolute;left:440px;top:230px;width:200px;height:265px">
      <i class="rg" style="position:absolute;left:-60px;top:10px;width:320px;height:320px;border:4px solid #F3C15D;border-radius:50%%;opacity:0"></i>
      <i class="rg" style="position:absolute;left:-60px;top:10px;width:320px;height:320px;border:4px solid #F3C15D;border-radius:50%%;opacity:0"></i>
      <i class="rg" style="position:absolute;left:-60px;top:10px;width:320px;height:320px;border:4px solid #F3C15D;border-radius:50%%;opacity:0"></i>
      <img src="assets/brand/mark-b01-inverse.svg" alt="" style="position:absolute;inset:0;width:200px;height:265px">
    </div>
    <div id="s7-head" class="disp" style="position:absolute;left:70px;top:560px;width:940px;font-size:92px;line-height:1.22;color:#F1F3F6;text-align:center">
      <span class="ln"><span class="w s7w">Make</span> <span class="w s7w">the</span> <span class="w s7w">right</span></span>
      <span class="ln"><span class="w s7w">buyers</span> <span class="w s7w" id="s7-pw">%s</span> <span class="w s7w">about</span></span>
      <span class="ln"><span class="w s7w">you</span> <span class="w s7w">and</span> <span class="w s7w">what</span></span>
      <span class="ln"><span class="w s7w">you&rsquo;re</span> <span class="w s7w">building.</span></span>
    </div>
    <div id="s7-cta" style="position:absolute;left:260px;top:1040px;width:560px;height:116px;border-radius:58px;background:#F1F3F6;color:#162760;display:flex;align-items:center;justify-content:center;gap:18px;font-size:40px;font-weight:600">Book an intro call
      <svg width="30" height="30" viewBox="0 0 14 14" fill="none"><path d="M3 11 11 3M5 3h6v6" stroke="#162760" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
    <img id="s7-lock" src="assets/brand/lockup-b01-inverse.svg" alt="OUTSPOKEN" style="position:absolute;left:270px;top:1215px;width:540px;height:auto">
    <div id="s7-note" class="tag" style="position:absolute;left:0;right:0;top:1300px;text-align:center;font-size:28px;color:#A9AFBA;text-transform:none;letter-spacing:.02em">Illustrative film. People and posts are fictional.</div>""" % SEL("care")
S7_CSS = ".s7w{will-change:transform,opacity}#s7-pw .sel{color:#162760}"
S7_JS = r"""
    tl.fromTo('#s7-mark',{scale:.6,opacity:0,y:30},{scale:1,opacity:1,y:0,duration:.7,ease:'back.out(1.7)'},0.35);
    document.querySelectorAll('#s7-mark .rg').forEach((r,i)=>tl.fromTo(r,{scale:.55,opacity:.8},{scale:1.3,opacity:0,duration:1.9,ease:'power2.out'},0.5+i*.55));
    const w=document.querySelectorAll('.s7w');
    tl.fromTo('.deep',{scale:1},{scale:1.07,duration:8.7,ease:'none'},0);
    tl.fromTo('.dots',{y:0},{y:-110,duration:8.7,ease:'none'},0);
    tl.fromTo('#s7-head',{y:0},{y:-12,duration:8.0,ease:'sine.inOut'},1.6);
    const sv=document.querySelector('#s7-wave'),ps=[];
    for(let i=0;i<11;i++){const q=document.createElementNS('http://www.w3.org/2000/svg','path');q.setAttribute('fill','none');q.setAttribute('stroke',i===5?'#EAA93C':(i%4===1?'#3157D5':'#A9AFBA'));q.setAttribute('stroke-width',i===5?4:2.4);q.setAttribute('opacity',i===5?.85:.42);sv.appendChild(q);ps.push(q)}
    const ws={t:0,a:0};
    function drawW(){ps.forEach((q,i)=>{let d='';for(let x=-20;x<=1100;x+=14){const env=0.55+0.45*Math.sin(x*.004+ws.t*.6);const y=280+Math.sin(x*(.0058+i*.00035)+i*.55+ws.t*1.4)*(34+i*9)*env*ws.a+Math.sin(x*.0021+i*.8+ws.t*.7)*22*ws.a+(i-5)*14;d+=(d?'L':'M')+x+' '+y.toFixed(1)}q.setAttribute('d',d)})}
    drawW();
    tl.to(ws,{a:1,duration:1.2,ease:'power2.out',onUpdate:drawW},0.9);
    tl.to(ws,{t:8.7,duration:8.7,ease:'none',onUpdate:drawW},0);
    tl.fromTo(w,{y:60,opacity:0,filter:'blur(12px)'},{y:0,opacity:1,filter:'blur(0px)',duration:.55,ease:'power4.out',stagger:.15},0.9);
    selIn(tl, document.querySelector('#s7-pw .sel'), 2.55);
    tl.fromTo('#s7-cta',{y:40,opacity:0,scale:.9},{y:0,opacity:1,scale:1,duration:.7,ease:'back.out(1.8)'},4.0);
    tl.fromTo('#s7-lock',{opacity:0,y:20},{opacity:1,y:0,duration:.7,ease:'power4.out'},4.4);
    tl.fromTo('#s7-note',{opacity:0},{opacity:1,duration:.6},5.2);
    document.querySelectorAll('#s7-mark .rg').forEach((r,i)=>tl.fromTo(r,{scale:.55,opacity:.7},{scale:1.3,opacity:0,duration:1.9,ease:'power2.out'},6.6+i*.5));
    tl.fromTo('#s7-cta',{boxShadow:'0 0 0 0 rgba(234,169,60,0)'},{boxShadow:'0 0 0 14px rgba(234,169,60,.35)',duration:.6,ease:'power2.out'},5.4);
    tl.to('#s7-cta',{boxShadow:'0 0 0 0 rgba(234,169,60,0)',duration:.7,ease:'power2.in'},6.0);
"""

SCENES = {"s1": (S1_HTML, S1_CSS, S1_JS), "s2": (S2_HTML, S2_CSS, S2_JS), "s3": (S3_HTML, S3_CSS, S3_JS), "s4": (S4_HTML, S4_CSS, S4_JS),
          "s5": (S5_HTML, S5_CSS, S5_JS), "s6": (S6_HTML, S6_CSS, S6_JS), "s7": (S7_HTML, S7_CSS, S7_JS)}

# ------------------------------------------------------------------ captions + chrome
def captions():
    items, js = "", ""
    for i, (text, a, b, hidden) in enumerate(CAPTIONS):
        words = text.split()
        total = sum(len(w) + 1 for w in words)
        span = (b - a) * 0.92
        t = a
        spans = ""
        starts = []
        for w in words:
            starts.append(t)
            t += span * (len(w) + 1) / total
            spans += '<span class="cw" style="display:inline-block;padding:0 .1em;border-radius:12px;color:#667190;background-color:rgba(246,213,145,0)">%s</span> ' % w
        items += '<div class="cap" id="cap%d" style="position:absolute;left:0;right:0;top:1196px;display:flex;justify-content:center;opacity:0"><div style="max-width:960px;text-align:center;padding:20px 34px;border-radius:40px;background:rgba(241,243,246,.96);box-shadow:0 18px 40px -22px rgba(22,39,96,.55);font-size:56px;line-height:1.18;font-weight:600;color:#162760">%s</div></div>\n' % (i, spans.strip())
        js += "    tl.fromTo('#cap%d',{opacity:0,y:18},{opacity:1,y:0,duration:.18,ease:'power3.out'},%.2f);\n" % (i, a)
        for k, s in enumerate(starts):
            nxt = starts[k + 1] if k + 1 < len(starts) else b
            js += "    tl.to('#cap%d .cw:nth-child(%d)',{color:'#162760',backgroundColor:'#F6D591',duration:.08},%.2f);\n" % (i, k + 1, s)
            js += "    tl.to('#cap%d .cw:nth-child(%d)',{backgroundColor:'rgba(246,213,145,0)',duration:.1},%.2f);\n" % (i, k + 1, max(nxt - 0.02, s + 0.1))
        js += "    tl.to('#cap%d',{opacity:0,y:-10,duration:.16,ease:'power2.in'},%.2f);\n" % (i, b - 0.02)
    return """<template>
  <style>%s</style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
%s  </div>
  <script>
  (function(){
    const tl = gsap.timeline({ paused: true });
%s    window.__timelines["captions"] = tl;
  })();
  </script>
</template>
""" % (PRELUDE, items, js)


def chrome():
    chips = ""
    for i in range(5):
        chips += '<div class="chip" id="ch%d" style="width:92px;height:56px;border-radius:28px;display:grid;place-items:center;font-size:28px;background:rgba(255,255,255,.92);border:2px solid #D9DEE7;color:#475477;box-shadow:0 12px 26px -18px rgba(22,39,96,.5)">0%d</div>' % (i, i + 1)
    spans = [(0.0, 5.7), (5.7, 10.9), (10.9, 13.85), (13.85, 17.5), (17.5, 21.3)]
    js = ""
    for i, (a, b) in enumerate(spans):
        js += "    tl.to('#ch%d',{backgroundColor:'#EAA93C',color:'#162760',borderColor:'#EAA93C',scale:1.1,duration:.25,ease:'power3.out'},%.2f);\n" % (i, a)
        js += "    tl.to('#ch%d',{backgroundColor:'rgba(255,255,255,.92)',color:'#475477',borderColor:'#D9DEE7',scale:1,duration:.3},%.2f);\n" % (i, b - 0.05)
    return """<template>
  <style>%s</style>
  <div id="root" data-composition-id="chrome" data-width="1080" data-height="1920">
    <div id="chips" class="mono" style="position:absolute;left:0;right:0;top:182px;display:flex;justify-content:center;gap:12px;font-family:'Geist Mono',monospace;font-weight:500">%s</div>
  </div>
  <script>
  (function(){
    const tl = gsap.timeline({ paused: true });
    tl.fromTo('#chips',{opacity:0,y:-14},{opacity:1,y:0,duration:.5,ease:'power3.out'},0.25);
%s    tl.to('#chips',{opacity:0,y:-14,duration:.35,ease:'power2.in'},21.2);
    window.__timelines["chrome"] = tl;
  })();
  </script>
</template>
""" % (PRELUDE, chips, js)


# ------------------------------------------------------------------ root index.html (transitions, ink, sparks, band, iris, selection)
def index_html():
    hosts = ""
    for z, (sid, start, dur) in enumerate(HOSTS, start=2):
        hosts += '    <div id="%s" data-composition-id="%s" data-composition-src="compositions/%s.html" data-start="%.2f" data-duration="%.2f" data-track-index="%d" data-width="1080" data-height="1920" data-track-kind="graphics" style="position:absolute;inset:0;z-index:%d"></div>\n' % (sid, sid, sid, start, dur, z, z)
    return open(ROOT / "src/root.template.txt").read().replace("@@HOSTS@@", hosts)


def main():
    comp = ROOT / "compositions"
    comp.mkdir(exist_ok=True)
    for sid, (h, c, j) in SCENES.items():
        dur = [d for s, a, d in HOSTS if s == sid][0]
        (comp / (sid + ".html")).write_text(scene(sid, dur, h, c, j))
    (comp / "captions.html").write_text(captions())
    (comp / "chrome.html").write_text(chrome())
    (ROOT / "index.html").write_text(index_html())
    print("built", len(SCENES) + 2, "compositions and index.html")


if __name__ == "__main__":
    main()
