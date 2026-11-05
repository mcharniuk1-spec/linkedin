"""Conservative single-snapshot review ordering; never a trend detector."""
from datetime import datetime, timezone


def _aware(value):
    try:
        parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except (AttributeError,TypeError,ValueError):
        return None


def prioritize(rows, *, now=None):
    """Rank only recent, source-dated records with fresh observed counters.

    Search order and missing counters are never scores. Reactions and comments
    remain separate. This is a queue for actual source/editorial review; without
    same-parser repeated snapshots it cannot identify trending or velocity.
    """
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError('aware_datetime_required')
    now=now.astimezone(timezone.utc)
    result=[]
    for row in rows:
        if row.get('content_type')!='linkedin_post':continue
        item={k:row.get(k) for k in ('record_id','source_id','external_id','source_url','published_at','collected_at')}
        item.update(reactions=None,comments=None,age_bucket=None,priority=None,
                    review_status='pending_source_and_author_review',trend_status='not_measured_single_snapshot')
        published=_aware(row.get('published_at'));observed=_aware(row.get('collected_at'))
        legacy=row.get('legacy_record') if isinstance(row.get('legacy_record'),dict) else {}
        metrics=legacy.get('metrics') if isinstance(legacy.get('metrics'),dict) else {}
        def observed_count(key):
            v=metrics.get(key)
            return v.get('value') if isinstance(v,dict) and v.get('status')=='observed' and type(v.get('value')) is int and v['value']>=0 else None
        item['reactions']=observed_count('reactions');item['comments']=observed_count('comments')
        if row.get('publication_date_status')!='verified_source_date' or not published:
            item['qualification']='source_date_unverified'
        elif not observed or published>observed or observed>now:
            item['qualification']='invalid_or_future_observation'
        elif (now-observed).total_seconds()>24*3600:
            item['qualification']='observation_older_than_24h'
        elif item['reactions'] is None or item['comments'] is None:
            item['qualification']='reaction_or_comment_count_unavailable'
        else:
            age=(now-published).total_seconds()/3600
            item['age_bucket']=('under_24h' if age<24 else '24_to_72h' if age<72 else
                                '3_to_14_days' if age<=14*24 else 'older_than_14_days')
            item['qualification']='review_candidate' if age<=14*24 else 'older_than_14_days'
        result.append(item)
    buckets={'under_24h':0,'24_to_72h':1,'3_to_14_days':2}
    ranked=sorted((r for r in result if r['qualification']=='review_candidate'),
                  key=lambda r:(buckets[r['age_bucket']],-r['reactions'],-r['comments'],r['external_id'] or ''))
    for i,r in enumerate(ranked,1):r['priority']=i
    unranked=[r for r in result if r['qualification']!='review_candidate']
    return ranked+unranked
