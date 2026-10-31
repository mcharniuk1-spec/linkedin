#!/usr/bin/env python3
"""Verify the complete scoped report export without network or dependencies."""
from pathlib import Path
from collections import Counter
import json, statistics, hashlib
ROOT=Path(__file__).resolve().parent

def pairs(items):
    out={}
    for key,value in items:
        if key in out:raise ValueError('duplicate JSON key: '+key)
        out[key]=value
    return out

def load(name):return json.loads((ROOT/name).read_text(),object_pairs_hook=pairs)
def require(ok,reason):
    if not ok:raise ValueError(reason)

d=load('data.json');q=d['queries'];posts=q['posts']['rows'];stats=load('sample-statistics.json')
require(d['buildStatus']=='complete','report incomplete')
require(d['report']['asOf']=='2026-10-22','wrong evidence cutoff')
require(len(posts)==279,'wrong post count')
for key in ['post_id','url']:require(len({r[key] for r in posts})==279,'duplicate '+key)
require(len({r['author_name'] for r in posts})==61,'wrong author count')
for metric,n,total,median in [('reactions',276,115216,107.5),('comments',256,39930,36.5)]:
    xs=[r[metric] for r in posts if r[metric] is not None]
    require(all(type(x) is int and x>=0 for x in xs),'invalid counter')
    require((len(xs),sum(xs),statistics.median(xs))==(n,total,median),'counter mismatch '+metric)
for key,med,n in [('text',94,135),('image',186.5,111),('video',30,24),('document',178,9)]:
    rows=[r for r in posts if r['media_class']==key]
    require(len(rows)==n,'format n '+key)
    require(statistics.median(r['reactions'] for r in rows if r['reactions'] is not None)==med,'format median '+key)
for key in ['formats','topics','jobs','author_types','qualification','performance','age']:
    require(sum(r['posts'] for r in q[key]['rows'])==279,'group total '+key)
authors=q['authors']['rows'];require(len(authors)==61 and sum(r['posts'] for r in authors)==279,'author table')
require(sum(r['prospects'] for r in q['funding']['rows'])==20,'prospect table')
for row in q['availability']['rows']:require(row['observed']+row['missing']==279,'missingness total')
for field in ['experience','message_origin','messenger_role']:
    require(all(r[field]=='not_coded_in_source' for r in posts),'uncoded field changed')
require(Counter(r['media_class'] for r in posts)==Counter({'text':135,'image':111,'video':24,'document':9}),'format coverage')
require({r['post_id'] for r in load('report-rows.json')['rows']}=={r['post_id'] for r in posts},'row identity mismatch')
media=load('media-evidence.json');tags=media['post_level_feature_tags']['post_tags'];require(len(tags)==36,'feature coverage')
require(all(('/'+'Users/') not in p.read_text() for p in ROOT.rglob('*.json')),'private path')
print(json.dumps({'status':'PASS','posts':279,'authors':61,'queries':len(q),'feature_tagged_posts':36,'prospects_separate':20,'html_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()},indent=2))
