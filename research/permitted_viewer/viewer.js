(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else { root.PermittedResearchViewer = api; api.start(document); }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const SCHEMA = 'outspoken-research-viewer/1';
  const MAX_BYTES = 5 * 1024 * 1024;
  const ARRAYS = ['authorized_posts', 'reference_candidates', 'external_signals', 'target_companies'];
  const isObject = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const isTimestamp = v => typeof v === 'string' && /T.*(?:Z|[+-]\d{2}:\d{2})$/i.test(v) && Number.isFinite(Date.parse(v));
  const str = value => value === null || value === undefined || value === '' ? 'Unknown' : String(value);
  const validCount = n => Number.isSafeInteger(n) && n >= 0;
  function count(value) {
    if (isObject(value)) return value.status === 'observed' && validCount(value.value) ? value.value : null;
    return validCount(value) ? value : null;
  }
  function safeUrl(value) {
    try {
      const u = new URL(value);
      return ['https:', 'http:'].includes(u.protocol) && !u.username && !u.password ? u.href : null;
    } catch (_) { return null; }
  }
  function validate(data) {
    if (!isObject(data) || data.schema !== SCHEMA) throw new Error('Unsupported snapshot schema.');
    if (!isTimestamp(data.generated_at)) throw new Error('A timezone-qualified generated_at timestamp is required.');
    if (!isObject(data.operations)) throw new Error('An operations object is required.');
    for (const name of ARRAYS) {
      if (!Array.isArray(data[name]) || data[name].length > 10000 || data[name].some(x => !isObject(x))) throw new Error('Invalid or missing ' + name + ' array.');
    }
    if (data.operations.sources !== undefined && (!Array.isArray(data.operations.sources) || data.operations.sources.some(x => !isObject(x)))) throw new Error('Invalid source status list.');
    return data;
  }
  function trendEvidence(post) {
    if (post.publication_date_status !== 'verified_source_date' || !isTimestamp(post.published_at) || Date.parse(post.published_at)>Date.now()) return {state:'not_measured', reason:'Publication date has not been verified from an authorized source.'};
    const snapshots = Array.isArray(post.snapshots) ? post.snapshots.filter(s => isObject(s) && typeof s.source_id === 'string' && s.source_id && typeof s.parser_version === 'string' && s.parser_version && isTimestamp(s.observed_at) && Date.parse(s.observed_at)<=Date.now()).sort((a,b)=>Date.parse(a.observed_at)-Date.parse(b.observed_at)) : [];
    for (let j=snapshots.length-1;j>0;j--) {
      const later=snapshots[j];
      for(let i=j-1;i>=0;i--) {
        const first=snapshots[i], hours=(Date.parse(later.observed_at)-Date.parse(first.observed_at))/3600000;
        if(hours<6 || first.source_id!==later.source_id || first.parser_version!==later.parser_version || Date.parse(first.observed_at)<Date.parse(post.published_at)) continue;
        let differences=[];
        for(const key of ['reactions','comments','reposts']) {
          const a=count(isObject(first.metrics)?first.metrics[key]:null), b=count(isObject(later.metrics)?later.metrics[key]:null);
          if(a!==null && b!==null) differences.push({metric:key, before:a, after:b, change:b-a});
        }
        if(!differences.length) continue;
        if(differences.some(x=>x.change<0)) return {state:'not_measured',reason:'Comparable counters decreased; source review is required.'};
        if(!differences.some(x=>x.change>0)) return {state:'no_increase',reason:'Two compatible observations show no increase.',hours,differences,first:first.observed_at,last:later.observed_at};
        return {state:'measured_increase',reason:'Two compatible observations show an increase. This alone does not prove a trend.',hours,differences,first:first.observed_at,last:later.observed_at};
      }
    }
    return {state:'not_measured',reason:'Two compatible observations at least six hours apart with comparable observed counters are required.'};
  }
  function start(doc) {
    const $ = id => doc.getElementById(id);
    const create = (tag, text, className) => {const el=doc.createElement(tag);if(text!==undefined)el.textContent=str(text);if(className)el.className=className;return el;};
    const set = (node, children) => node.replaceChildren(...children);
    function row(dl, label, value) {dl.append(create('dt',label),create('dd',value));}
    function title(item) {return item.title || item.name || item.company_name || item.text_summary || item.external_id || 'Untitled item';}
    function source(card, item) {
      const p=create('p');p.append(create('strong','Source: '));
      const href=safeUrl(item.source_url || item.url);
      if(href){const a=create('a','Open source');a.href=href;a.target='_blank';a.rel='noopener noreferrer';p.append(a);}
      else p.append(doc.createTextNode('Unknown or unavailable'));
      card.append(p);
    }
    function baseCard(item) {
      const card=create('article',undefined,'card');card.append(create('h4',title(item)));
      card.append(create('span','Source: '+str(item.source_id),'badge'));
      card.append(create('span','Review: '+str(item.review_status),'badge'));
      card.append(create('span','Permission: '+str(item.permission_state),'badge'));
      source(card,item);return card;
    }
    function empty(el,message){set(el,[create('p',message,'empty')]);}
    function renderHealth(op, generated) {
      $('generated').textContent='Snapshot generated: '+str(generated);
      $('status-notes').textContent=op.status_notes ? 'Status notes: '+str(op.status_notes) : '';
      const daily=isObject(op.daily_progress)?op.daily_progress:op;
      const goals=isObject(daily.goals)?daily.goals:{};
      const state=op.linkedin_status || 'Unknown';
      const summary=[['LinkedIn source',state],['New unique posts',count(daily.new_unique_posts)],
        ['Observed accounts',count(daily.distinct_observed_accounts)],['Post goal',count(goals.new_unique_posts ?? daily.post_goal)],
        ['Account goal',count(goals.distinct_observed_accounts ?? daily.account_goal)],['Duplicates',count(op.duplicates)],
        ['Missed/delayed runs',count(op.missed_or_delayed_runs)]];
      set($('health'),summary.map(([label,value])=>{const box=create('div',undefined,'metric');box.append(create('strong',value===null?'Unknown':value),create('span',label));return box;}));
      const sources=Array.isArray(op.sources)?op.sources:[];
      if(!sources.length){empty($('source-status'),'No source-level status supplied.');return;}
      set($('source-status'),sources.map(s=>{const card=create('article',undefined,'card'+(s.hold?' warning':''));card.append(create('h4',str(s.source_id)));const dl=create('dl');
        for(const [label,value] of [['Status',s.status],['Attempted requests',count(s.attempted_requests)],['Successful requests',count(s.successful_requests)],['Hold',s.hold],['Quota used',count(s.quota_used)],['Quota limit',count(s.quota_limit)],['Observed at',s.observed_at]]) row(dl,label,value);card.append(dl);return card;}));
    }
    function renderAuthorized(rows) {
      if(!rows.length){empty($('authorized-list'),'No authorized LinkedIn posts supplied.');return;}
      set($('authorized-list'),rows.map(p=>{const card=baseCard(p),dl=create('dl'),m=isObject(p.metrics)?p.metrics:{};
        for(const [label,value] of [['Author or organization',isObject(p.author)?p.author.name:(p.author||p.organization)],['Published at',p.published_at],['Publication date state',p.publication_date_status],['Latest observation',p.observed_at||p.collected_at],['Reactions',count(m.reactions)],['Comments',count(m.comments)],['Reposts',count(m.reposts)],['Impressions',count(m.impressions)]])row(dl,label,value);
        const evidence=trendEvidence(p);row(dl,'Measured change',evidence.reason);
        if(evidence.differences){row(dl,'Observation interval',evidence.hours.toFixed(1)+' hours: '+evidence.first+' to '+evidence.last);for(const d of evidence.differences)row(dl,d.metric+' change',d.before+' → '+d.after+' (+'+d.change+')');}
        if(p.trend_status==='trending'&&p.trend_review_status==='reviewed'&&evidence.state==='measured_increase')row(dl,'Trend qualification','Trending — reviewed; see evidence and reason.');
        else row(dl,'Trend qualification','Not established.');
        if(p.trend_reason)row(dl,'Reviewer reason',p.trend_reason);card.append(dl);return card;}));
    }
    function renderReferences(rows) {
      if(!rows.length){empty($('reference-list'),'No reference candidates supplied.');return;}
      set($('reference-list'),rows.map(p=>{const card=baseCard(p),dl=create('dl');for(const [label,value] of [['Topic',p.topic],['Author fit',p.author_fit],['Discovered at',p.discovered_at],['Relevance reason',p.relevance_reason],['Performance evidence',p.performance_evidence]])row(dl,label,value);card.append(dl);return card;}));
    }
    function renderExternal(rows) {
      if(!rows.length){empty($('external-list'),'No external topic signals supplied.');return;}
      set($('external-list'),rows.map(p=>{const card=baseCard(p),dl=create('dl'),m=isObject(p.metrics)?p.metrics:{};for(const [label,value] of [['Topic',p.topic],['Source type',p.source_type],['Discovered at',p.discovered_at||p.collected_at],['Source score',count(m.score)],['Source comments',count(m.comments)],['Context',p.description]])row(dl,label,value);card.append(dl);return card;}));
    }
    function renderTargets(rows) {
      if(!rows.length){empty($('targets-list'),'No target companies supplied.');return;}
      set($('targets-list'),rows.map(p=>{const card=baseCard(p),dl=create('dl');for(const [label,value] of [['Description',p.description],['Country/base',p.country],['Company size',p.employee_count],['Funding',p.funding],['Fit',p.fit_status],['Content opportunity',p.content_opportunity],['Expressed need',p.expressed_need],['Buying interest',p.buying_interest],['Discovered at',p.discovered_at]])row(dl,label,value);card.append(dl);return card;}));
    }
    function render(data) {renderHealth(data.operations,data.generated_at);renderAuthorized(data.authorized_posts);renderReferences(data.reference_candidates);renderExternal(data.external_signals);renderTargets(data.target_companies);}
    const tabs=['authorized','reference','external','targets'];
    function activate(key,focus){for(const k of tabs){const active=k===key,tab=$('tab-'+k);tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;$('pane-'+k).hidden=!active;}if(focus)$('tab-'+key).focus();}
    tabs.forEach((key,index)=>{const el=$('tab-'+key);el.addEventListener('click',()=>activate(key,false));el.addEventListener('keydown',event=>{let n;if(event.key==='ArrowRight')n=(index+1)%tabs.length;else if(event.key==='ArrowLeft')n=(index+tabs.length-1)%tabs.length;else if(event.key==='Home')n=0;else if(event.key==='End')n=tabs.length-1;else return;event.preventDefault();activate(tabs[n],true);});});
    let selection = 0;
    $('snapshot').addEventListener('change', async event=>{
      const file=event.target.files && event.target.files[0];if(!file)return;
      const current=++selection;
      $('generated').textContent='No snapshot loaded.';
      $('status-notes').textContent='';
      set($('health'),[]);
      empty($('source-status'),'No snapshot selected.');
      for(const id of ['authorized-list','reference-list','external-list','targets-list'])empty($(id),'No snapshot selected.');
      if(file.size>MAX_BYTES){$('load-status').textContent='Snapshot is too large (maximum 5 MiB).';return;}
      try{const value=validate(JSON.parse(await file.text()));if(current!==selection)return;render(value);$('load-status').textContent='Snapshot loaded in this browser only.';}
      catch(err){if(current===selection)$('load-status').textContent='Snapshot not loaded: '+(err instanceof SyntaxError?'Invalid JSON.':err.message);}
    });
    for(const id of ['authorized-list','reference-list','external-list','targets-list'])empty($(id),'No snapshot selected.');
  }
  return {SCHEMA, MAX_BYTES, validate, count, safeUrl, trendEvidence, start};
});
