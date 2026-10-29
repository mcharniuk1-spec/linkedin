"""Keyless Exa MCP discovery. Results are seeds, never performance evidence."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit
import hashlib,json,re,time
import httpx
from .contracts import AccessSuspended, CollectionError, utcnow

ENDPOINT='https://mcp.exa.ai/mcp'
OBJECTIVE=('Find public LinkedIn publication permalinks relevant to B2B AI SaaS founders, '
 'practical product/customer methods, positioning and buyer-relevant content. '
 'Exclude private profiles, login pages and unrelated posts. Keep original URLs and date evidence; '
 'search order and indexed dates do not establish publication popularity or freshness.')


def _message(response, ident):
    response.raise_for_status()
    if 'text/event-stream' in response.headers.get('content-type',''):
        messages=[]
        for event in response.text.split('\n\n'):
            data='\n'.join(line[5:].lstrip() for line in event.splitlines() if line.startswith('data:'))
            if data:
                messages.append(json.loads(data))
        message=next((m for m in messages if m.get('id')==ident),None)
    else:
        message=response.json()
    if not isinstance(message,dict) or message.get('id')!=ident or 'error' in message:
        raise CollectionError('invalid_discovery_protocol_response')
    return message.get('result',{})


def discover(config, store, approved_authors=(), *, client=None, now=None):
    if not config.get('enabled'):
        return []
    if store.get_suspension('exa-search'):
        raise AccessSuspended('discovery_backend_suspended')
    if config.get('endpoint',ENDPOINT)!=ENDPOINT:
        raise CollectionError('unapproved_discovery_endpoint')
    now=now or datetime.now(ZoneInfo('Europe/Sofia'))
    values={'since14':(now.date()-timedelta(days=14)).isoformat(),'tomorrow':(now.date()+timedelta(days=1)).isoformat()}
    def cursor(k):
        x=store.db.execute('SELECT value FROM metadata WHERE key=?',(k,)).fetchone();return int(x[0]) if x else 0
    tc,ac=cursor('topic_cursor'),cursor('author_cursor');topics=config.get('queries',[]);queries=[]
    if topics:
        queries.append(topics[tc%len(topics)].format(**values))
    author_count=min(int(config.get('author_queries_per_run',2)),len(approved_authors))
    for i in range(author_count):
        slug=approved_authors[(ac+i)%len(approved_authors)].rstrip('/').split('/')[-1]
        if re.fullmatch('[A-Za-z0-9-]+',slug):
            queries.append(f'site:linkedin.com/posts/{slug}_ after:{values["since14"]} before:{values["tomorrow"]}')
    queries=queries[:min(8,int(config.get('max_queries',3)))];urls=[]
    owned=client is None;c=client or httpx.Client(timeout=30,follow_redirects=False,trust_env=False)
    headers={'Accept':'application/json, text/event-stream','Content-Type':'application/json'}
    def request(ident,method,params):
        started=time.monotonic()
        try:
            response=c.post(ENDPOINT,headers=headers,json={'jsonrpc':'2.0','id':ident,'method':method,'params':params})
            store.log_request('exa-search',{'status_code':response.status_code,'latency_ms':(time.monotonic()-started)*1000,'bytes':len(response.content),'kind':'discovery','collected_at':utcnow()})
            if len(response.content)>2_000_000:
                raise CollectionError('discovery_response_size_cap')
            if response.status_code in (401,403,429,999):
                store.suspend('exa-search','discovery_access_or_quota_stop');raise AccessSuspended('discovery_access_or_quota_stop')
            return response,_message(response,ident)
        except httpx.HTTPError:
            raise CollectionError('discovery_transport_failure') from None
    try:
        response,init=request(1,'initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'linkedin-bounded-collector','version':'1'}})
        if response.headers.get('mcp-session-id'):
            headers['Mcp-Session-Id']=response.headers['mcp-session-id']
        c.post(ENDPOINT,headers=headers,json={'jsonrpc':'2.0','method':'notifications/initialized'})
        _,listing=request(2,'tools/list',{})
        tool=next((x for x in listing.get('tools',[]) if x.get('name')=='web_search_exa'),None)
        if not tool:
            raise CollectionError('discovery_tool_not_available')
        for i,query in enumerate(queries,3):
            arguments={'query':query,'numResults':min(10,int(config.get('max_results_per_query',8)))}
            if 'objective' in tool.get('inputSchema',{}).get('properties',{}):
                arguments['objective']=OBJECTIVE
            _,result=request(i,'tools/call',{'name':'web_search_exa','arguments':arguments})
            text='\n'.join(x.get('text','') for x in result.get('content',[]) if x.get('type')=='text')
            raw=json.dumps(result,sort_keys=True,ensure_ascii=False).encode()
            digest=hashlib.sha256(raw).hexdigest()
            import gzip
            with store.db:
                store.db.execute('CREATE TABLE IF NOT EXISTS discoveries (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
                store.db.execute('INSERT OR IGNORE INTO raw_objects VALUES (?,?)',(digest,gzip.compress(raw,mtime=0)))
                store.db.execute('INSERT OR IGNORE INTO discoveries VALUES (?,?)',(hashlib.sha256((query+'|'+digest+'|'+utcnow()).encode()).hexdigest(),json.dumps({'query':query,'collected_at':utcnow(),'raw_sha256':digest,'rank_is_not_performance':True})))
            if result.get('isError') or re.search(r'quota|rate.limit|unauthori[sz]ed|too many requests',text,re.I):
                store.suspend('exa-search','discovery_tool_quota_or_error');raise AccessSuspended('discovery_tool_quota_or_error')
            for value in re.findall(r'https://[^\s<>"\)]+',text):
                p=urlsplit(value)
                if (p.hostname=='linkedin.com' or (p.hostname or '').endswith('.linkedin.com')) and '/posts/' in p.path and re.search(r'activity-\d{19}',p.path):
                    from ..pipeline.normalizer import canonical
                    url=canonical(value)
                    if url not in urls and not store.known_url(url):urls.append(url)
        with store.db:
            store.db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('topic_cursor',str(tc+1)))
            store.db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('author_cursor',str(ac+author_count)))
        return urls
    finally:
        if owned:c.close()
