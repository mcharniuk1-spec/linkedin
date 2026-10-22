"""Local normalizer/store for captured public LinkedIn posts. No login or network calls.

Capture access is a separate agent/provider step. This tool never claims a whole profile,
complete media, or verified rights from an HTML page. Requires existing beautifulsoup4.
"""
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
from datetime import datetime,timezone
import argparse,hashlib,json,re,sqlite3
from bs4 import BeautifulSoup

VERSION='0.3.0'
def now():return datetime.now(timezone.utc).isoformat()
def digest(b):return hashlib.sha256(b).hexdigest()
def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key: '+k)
  d[k]=v
 return d
def canonical(u):
 p=urlsplit(u)
 if p.scheme!='https' or not (p.hostname=='linkedin.com' or (p.hostname or '').endswith('.linkedin.com')):raise ValueError('expected a public HTTPS LinkedIn URL')
 if p.username or p.password or p.port not in (None,443):raise ValueError('unexpected authority')
 return urlunsplit(('https','www.linkedin.com',p.path.rstrip('/'),'',''))
def values(v):return v if isinstance(v,list) else [v] if v is not None else []
def ld_candidates(soup):
 candidates=[]
 for script in soup.select('script[type="application/ld+json"]'):
  try:
   data=json.loads(script.get_text(),object_pairs_hook=unique)
   for d in values(data):
    if isinstance(d,dict):candidates.extend(values(d.get('@graph')) or [d])
  except (ValueError,TypeError):continue
 return candidates

def target_ld(soup,url):
 target=re.search(r'activity-(\d+)',canonical(url))
 if not target:return {}
 found=[]
 for d in ld_candidates(soup):
  if not isinstance(d,dict) or d.get('@type') not in ('SocialMediaPosting','VideoObject'):continue
  try:u=canonical(d.get('@id',''))
  except (ValueError,TypeError):continue
  m=re.search(r'activity-(\d+)',u)
  if m and m.group(1)==target.group(1):found.append(d)
 if len(found)!=1:return {}
 return found[0]

def post_context(soup,url):
 """Select the actual main post; never a comment, related card or whole page."""
 article=soup.select_one('article[data-activity-urn]')
 if article is not None:return article,'legacy',target_ld(soup,url)
 ld=target_ld(soup,url)
 cards=soup.select('main section[aria-label="Primary content"] [role="listitem"][componentkey^="update-card-focus"]')
 if not ld or len(cards)!=1:raise ValueError('no public post article; unsupported layout, identity missing or auth wall')
 article=cards[0];creator=ld.get('creator') or ld.get('author') or {};actor=main_actor(article,creator)
 if not actor or article.select_one('[data-testid="expandable-text-box"]') is None:raise ValueError('new guest layout lacks matching main actor/commentary')
 return article,'guest_component',ld

def main_actor(article,creator=None):
 actor=article.select_one('a[data-tracking-control-name="public_post_feed-actor-name"]')
 if actor is not None:return actor
 creator=creator or {};u=creator.get('url')
 if not u:return None
 target=urlsplit(u).path.rstrip('/').lower()
 for a in article.select('a[href]'):
  p=urlsplit(a['href'])
  if (p.hostname=='linkedin.com' or (p.hostname or '').endswith('.linkedin.com')) and p.path.rstrip('/').lower()==target and a.get_text(' ',strip=True):return a
 return None

def parse_post(path,url,captured_at,rights='research_only_unverified_reuse'):
 raw=Path(path).read_bytes();soup=BeautifulSoup(raw,'html.parser');url=canonical(url)
 article,layout,ld=post_context(soup,url)
 if layout=='legacy':
  p=parse_legacy_post(path,url,captured_at,rights);p['source']['normalizer_sha256']=digest(Path(__file__).read_bytes());return p
 ident=re.search(r'activity-(\d+)',url).group(1);urn='urn:li:activity:'+ident
 creator=ld.get('creator') or ld.get('author') or {};actor=main_actor(article,creator)
 commentary=article.select_one('[data-testid="expandable-text-box"]');text=commentary.get_text('\n',strip=True).strip()
 metrics={k:{'value':None,'status':'not_exposed','source_path':None} for k in ['reactions','comments','reposts','impressions','reach','views','clicks','saves']}
 for key,selector in [('reactions','a[aria-label="Reaction button state: no reaction"]'),('comments','a[aria-label="Comment"]'),('reposts','a[aria-label="Repost"]')]:
  nodes=article.select(selector)
  if len(nodes)!=1:continue
  visible=nodes[0].get_text(' ',strip=True);m=re.fullmatch(r'([0-9][0-9,]*)',visible)
  if m:metrics[key]={'value':int(m.group(1).replace(',','')),'status':'observed','source_path':'main_guest_post '+selector}
 followers=None
 for stat in values(creator.get('interactionStatistic')):
  if isinstance(stat,dict) and str(stat.get('interactionType','')).endswith('/FollowAction') and type(stat.get('userInteractionCount')) is int:followers=stat['userInteractionCount']
 media=[]
 for i,img in enumerate(article.select('img[alt="View image"]')):
  variants=[]
  for part in img.get('srcset','').split(','):
   candidate=part.strip().split()
   if len(candidate)==2 and re.fullmatch(r'\d+w',candidate[1]):variants.append((int(candidate[1][:-1]),candidate[0]))
  src=max(variants)[1] if variants else img.get('src')
  if src and urlsplit(src).hostname=='media.licdn.com' and '/dms/image/' in urlsplit(src).path:media.append({'id':f'{urn}:image:{i}','type':'image','url':src,'alt':img.get('alt'),'bytes_acquired':False,'visual_review_status':'not_viewed','rights':rights})
 warnings=['Guest component layout: only main DOM text/counters and matching source JSON-LD fields extracted; full media coverage unverified.']
 if ld.get('@type')=='VideoObject':
  media.append({'id':f'{urn}:video:0','type':'video','asset_urn':None,'renditions':[],'poster_url':ld.get('thumbnailUrl'),'caption_url':None,'duration_iso':ld.get('duration'),'bytes_acquired':False,'visual_review_status':'not_watched','audio_review_status':'not_listened','rights':rights});warnings.append('VideoObject exposed without native rendition URL; video acquisition unavailable in this layout.')
 return {'schema_version':1,'parser_version':VERSION,'id':urn,'url':url,'attributed_urn':None,'captured_at':captured_at,'source':{'method':'captured_public_guest_html','raw_path':str(Path(path).resolve()),'sha256':digest(raw),'rights':rights,'coverage':'single_public_page_subset','all_author_posts':False,'layout':'guest_component','normalizer_sha256':digest(Path(__file__).read_bytes())},'author':{'name':actor.get_text(' ',strip=True),'url':actor['href'].split('?')[0].rstrip('/'),'type':creator.get('@type'),'followers':followers},'published_at':ld.get('datePublished') or ld.get('uploadDate'),'text':text,'text_status':'captured_dom_completeness_unverified','metrics':metrics,'media':media,'transcript':{'text':None,'origin':None,'status':'not_exposed','language':None,'timing':None},'warnings':warnings}

def parse_legacy_post(path,url,captured_at,rights='research_only_unverified_reuse'):
 raw=Path(path).read_bytes(); soup=BeautifulSoup(raw,'html.parser');url=canonical(url)
 article=soup.select_one('article[data-activity-urn]')
 if article is None:raise ValueError('no public post article; auth wall, unsupported layout or wrong page')
 urn=article.get('data-activity-urn');match=re.search(r'activity[:\-](\d+)',url+' '+urn)
 if not match or not urn.endswith(match.group(1)):raise ValueError('post identity does not match URL')
 candidates=[]
 for script in soup.select('script[type="application/ld+json"]'):
  try:
   data=json.loads(script.get_text(),object_pairs_hook=unique)
   for d in values(data):
    if isinstance(d,dict):candidates.extend(values(d.get('@graph')) or [d])
  except (ValueError,TypeError):continue
 ld=next((d for d in candidates if isinstance(d,dict) and str(d.get('@id','')).split('?')[0].rstrip('/')==url),{})
 commentary=article.select_one('[data-test-id="main-feed-activity-card__commentary"]')
 if commentary is None:raise ValueError('post commentary selector absent; refuse unrelated page text')
 text=commentary.get_text('',strip=False).strip();creator=ld.get('creator') or ld.get('author') or {}
 if not isinstance(creator,dict):creator={}
 actor=article.select_one('a[data-tracking-control-name="public_post_feed-actor-name"]')
 if actor and (not creator.get('name') or not creator.get('url')):
  creator={**creator,'name':creator.get('name') or actor.get_text(' ',strip=True),'url':creator.get('url') or actor.get('href','').split('?')[0]}
 metrics={k:{'value':None,'status':'not_exposed','source_path':None} for k in ['reactions','comments','reposts','impressions','reach','views','clicks','saves']}
 # JSON-LD may contain a default zero when no visible post total is exposed.
 # Promote only the actual main-post counters, keeping the raw HTML for reconciliation.
 totals=article.select_one('.main-feed-activity-card__social-actions')
 for key,selector in [('reactions','[data-test-id="social-actions__reaction-count"]'),('comments','[data-test-id="social-actions__comments"]'),('reposts','[data-test-id="social-actions__reposts"]')]:
  node=totals.select_one(selector) if totals else None
  visible=node.get_text(' ',strip=True) if node else ''
  count_match=re.fullmatch(r'([0-9][0-9,]*)\s*(?:Comments?|Reactions?|Reposts?)?',visible,re.I)
  metrics[key]={'value':int(count_match.group(1).replace(',','')),'status':'observed','source_path':selector} if count_match else {'value':None,'status':'not_exposed','source_path':None}
 media=[]
 for i,v in enumerate(article.select(':scope > [data-test-id="feed-native-video-content"] video')):
  try:sources=json.loads(v.get('data-sources','[]'),object_pairs_hook=unique)
  except ValueError:sources=[]
  media.append({'id':f'{urn}:video:{i}','type':'video','asset_urn':v.get('data-digitalmedia-asset-urn'),'renditions':sources,'poster_url':v.get('data-poster-url'),'caption_url':v.get('data-captions-url'),'duration_iso':ld.get('duration'),'bytes_acquired':False,'visual_review_status':'not_watched','audio_review_status':'not_listened','rights':rights})
 for i,img in enumerate(article.select(':scope > [data-test-id="feed-images-content"] img, :scope > .feed-images-content img')):
  src=img.get('data-delayed-url') or img.get('src')
  if src and urlsplit(src).hostname=='media.licdn.com' and '/dms/image/' in urlsplit(src).path:media.append({'id':f'{urn}:image:{i}','type':'image','url':src,'alt':img.get('alt'),'bytes_acquired':False,'visual_review_status':'not_viewed','rights':rights})
 # Profile portraits and background banners are intentionally excluded from post media.
 transcript=ld.get('transcript')
 if transcript is not None and not isinstance(transcript,str):transcript=None
 warning=[]
 if not ld:warning.append('matching JSON-LD absent; creator/date/metrics may be unavailable')
 if 'truncated' in ' '.join(commentary.get('class',[])):warning.append('CSS truncated marker present; DOM text completeness is not proven')
 return {'schema_version':1,'parser_version':VERSION,'id':urn,'url':url,'attributed_urn':article.get('data-attributed-urn'),'captured_at':captured_at,'source':{'method':'captured_public_guest_html','raw_path':str(Path(path).resolve()),'sha256':digest(raw),'rights':rights,'coverage':'single_public_page_subset','all_author_posts':False},'author':{'name':creator.get('name'),'url':creator.get('url'),'type':creator.get('@type'),'followers':(creator.get('interactionStatistic') or {}).get('userInteractionCount') if isinstance(creator.get('interactionStatistic'),dict) else None},'published_at':ld.get('datePublished') or ld.get('uploadDate'),'text':text,'text_status':'captured_dom_completeness_unverified','metrics':metrics,'media':media,'transcript':{'text':transcript,'origin':'public_page_jsonld' if transcript else None,'status':'available_not_audio_verified' if transcript else 'not_exposed','language':article.select_one('video').get('data-language') if article.select_one('video') else None,'timing':None},'warnings':warning}
def validate_record(r):
 if not isinstance(r,dict):raise ValueError('record must be an object')
 required={'schema_version','parser_version','id','url','attributed_urn','captured_at','source','author','published_at','text','text_status','metrics','media','transcript','warnings'}
 if set(r)!=required:raise ValueError('post fields differ: '+str(set(r)^required))
 if canonical(r['url'])!=r['url']:raise ValueError('noncanonical URL')
 if not re.fullmatch(r'urn:li:activity:\d+',r['id']):raise ValueError('invalid post ID')
 url_id=re.search(r'activity-(\d+)',r['url'])
 if url_id is None or r['id']!='urn:li:activity:'+url_id.group(1):raise ValueError('URL/post identity mismatch')
 captured=datetime.fromisoformat(r['captured_at'].replace('Z','+00:00'))
 if captured.tzinfo is None:raise ValueError('captured_at must include UTC/offset timezone')
 if not isinstance(r['source'],dict) or not re.fullmatch('[0-9a-f]{64}',r['source'].get('sha256','')):raise ValueError('missing source hash')
 keys={'reactions','comments','reposts','impressions','reach','views','clicks','saves'}
 if set(r['metrics'])!=keys:raise ValueError('missing/extra metric')
 for key,m in r['metrics'].items():
  if set(m)!={'value','status','source_path'} or m['status'] not in ['observed','not_exposed','unavailable','conflict']:raise ValueError('invalid metric '+key)
  if m['value'] is not None and (type(m['value']) is not int or m['value']<0):raise ValueError('metric must be null or nonnegative integer')
  if (m['status']=='observed')!=(m['value'] is not None):raise ValueError('missing/zero metric state mismatch')
 if not isinstance(r['text'],str) or not isinstance(r['media'],list):raise ValueError('bad text/media type')
 if r['source'].get('all_author_posts') is not False:raise ValueError('single page cannot prove whole-author coverage')
 return r
def store(records,db):
 # Validate the whole input before opening a transaction; a malformed batch cannot partly commit.
 for r in records:validate_record(r)
 db=Path(db);db.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect(db) as c:
  c.execute('CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY,url TEXT NOT NULL)')
  c.execute('CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY,post_id TEXT NOT NULL,captured_at TEXT NOT NULL,raw_sha256 TEXT NOT NULL,payload TEXT NOT NULL)')
  for r in records:
   payload=json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(',',':'));sid=digest((r['id']+'|'+r['captured_at']+'|'+r['source']['sha256']).encode())
   existing=c.execute('SELECT payload FROM snapshots WHERE id=?',(sid,)).fetchone()
   if existing and existing[0]!=payload:raise ValueError('conflicting payload for immutable capture identity')
   c.execute('INSERT OR IGNORE INTO posts VALUES(?,?)',(r['id'],r['url']))
   c.execute('INSERT OR IGNORE INTO snapshots VALUES(?,?,?,?,?)',(sid,r['id'],r['captured_at'],r['source']['sha256'],payload))
 return {'posts':len({r['id'] for r in records}),'input_records':len(records),'db':str(db)}
def main():
 p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
 q=s.add_parser('parse');q.add_argument('--html',required=True,type=Path);q.add_argument('--url',required=True);q.add_argument('--captured-at',required=True);q.add_argument('--out',required=True,type=Path)
 q=s.add_parser('ingest');q.add_argument('--input',required=True,type=Path);q.add_argument('--db',required=True,type=Path)
 a=p.parse_args()
 if a.command=='parse':
  r=validate_record(parse_post(a.html,a.url,a.captured_at));a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'post_id':r['id'],'media':len(r['media']),'transcript_status':r['transcript']['status'],'output':str(a.out)}))
 else:
  raw=a.input.read_text();records=[json.loads(line,object_pairs_hook=unique) for line in raw.splitlines() if line.strip()];print(json.dumps(store(records,a.db)))
if __name__=='__main__':main()
