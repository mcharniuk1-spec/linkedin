"""Descriptive public-counter assessments; no reach, sales or global trend score."""
import hashlib
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def stamp(value):
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return d if d.tzinfo else None
    except (AttributeError, ValueError, TypeError):
        return None


def age_group(age):
    if age is None or age < 0:
        return 'unknown_or_future'
    for edge in [7, 30, 90, 180]:
        if age <= edge:
            return 'up_to_%sd' % edge
    return 'over_180d'


def post_format(p, asset_kinds=()):
    kinds = {m.get('type') for m in p.get('media', [])} | set(asset_kinds)
    if 'video' in kinds:
        return 'video'
    if 'document' in kinds or 'document_preview' in kinds or p.get('_documents'):
        return 'document'
    if 'image' in kinds:
        return 'image'
    return 'text_or_external_link'


def assess(posts, snapshots, velocity, interpretations, minimum=8, assets=()):
    sem = {x['post_id']: x for x in interpretations}
    vv = {x['post_id']: x for x in velocity}
    ss = defaultdict(list)
    for s in snapshots:
        if stamp(s.get('captured_at')):
            ss[s['post_id']].append(s)
    kinds = defaultdict(set)
    for a in assets:
        kinds[a['post_id']].add(a['kind'])
    rows, groups = [], defaultdict(list)
    for p in posts:
        s = max(ss[p['id']], key=lambda x: stamp(x['captured_at'])) if ss[p['id']] else None
        captured = s['captured_at'] if s else p.get('captured_at')
        metrics = s.get('metrics', {}) if s else p['metrics']
        def observed(name):
            m = metrics.get(name, {})
            return m.get('value') if m.get('status') == 'observed' and numeric(m.get('value')) else None
        reaction = metrics.get('reactions', {})
        count = reaction.get('value') if reaction.get('status') == 'observed' and numeric(reaction.get('value')) else None
        pub = stamp(p.get('published_at'))
        at = stamp(captured)
        date_conflict = len({x.get('published_at') for x in ss[p['id']] if x.get('published_at')}) > 1
        age = (at - pub).total_seconds() / 86400 if at and pub and not date_conflict else None
        lang = sem.get(p['id'], {}).get('content_language', 'unknown')
        author = p['author'].get('url', '').split('linkedin.com')[-1].rstrip('/').lower()
        fmt = post_format(p, kinds[p['id']])
        cohort = '|'.join([author, fmt, age_group(age), lang])
        r = {'post_id': p['id'], 'metric_snapshot_id': s.get('snapshot_id') if s else None,
             'metric_source_sha256': s.get('raw_sha256') if s else p['source']['sha256'],
             'metric_captured_at': captured, 'reactions': count,
             'comments': observed('comments'), 'reposts': observed('reposts'),
             'metric_statuses': {k: metrics.get(k, {}).get('status', 'unavailable') for k in ['reactions', 'comments', 'reposts']},
             'publication_date_conflict': date_conflict,
             'format': fmt, 'content_language': lang, 'age_days_at_metric_capture': round(age, 4) if age is not None else None,
             'comparison_cohort': cohort, 'comparison_n': 0, 'comparison_median_reactions': None,
             'pattern_representative': sem.get(p['id'], {}).get('pattern_representative', True),
             'reaction_midrank_percentile': None, 'performance_status': 'insufficient_comparable_sample',
             'trend_status': 'not_established', 'causal_status': 'unknown', 'sales_effectiveness': 'unknown'}
        rows.append(r)
        if count is not None and age is not None and age >= 0 and lang != 'unknown' and r['pattern_representative']:
            groups[cohort].append(r)
    for r in rows:
        g = groups[r['comparison_cohort']]
        r['comparison_n'] = len(g)
        values = [x['reactions'] for x in g]
        if not r['pattern_representative']:
            reason = 'A retained similar-wording variant. Its counters are shown, but it does not add an independent idea or comparison record.'
        elif r['reactions'] is None:
            reason = 'The reaction counter is not observed; missing is not zero.'
        elif 'unknown_or_future' in r['comparison_cohort']:
            reason = 'The publication age is unknown or future, so comparative performance is held.'
        elif len(values) < minimum:
            reason = '%s observed reactions; only %s comparable same-author/format/age/language records (minimum %s). No relative performance label.' % (r['reactions'], len(values), minimum)
        else:
            val = r['reactions']; med = statistics.median(values)
            pct = (sum(x < val for x in values) + .5 * sum(x == val for x in values)) / len(values)
            r.update(comparison_median_reactions=med, reaction_midrank_percentile=round(pct, 4))
            high = pct >= .8 and val > med
            r['performance_status'] = 'strong_sample_reference' if high else 'ordinary_sample_reference'
            reason = '%s observed reactions versus sample median %s; midrank percentile %.1f%% in %s comparable records. %s' % (val, med, pct * 100, len(values), 'Upper sample band; a descriptive reference, not reach or sales proof.' if high else 'No upper-band advantage established. Equal counters share a midpoint rank.')
        r['performance_reason'] = reason
        v = vv.get(r['post_id'])
        if not v or not v.get('eligible'):
            r['trend_reason'] = 'A comparable six-hour second snapshot is unavailable: %s.' % ((v or {}).get('reason') or 'no measured window')
        elif v.get('counter_decreased'):
            r['trend_status'] = 'counter_decrease_review'
            r['trend_reason'] = 'The public counter decreased; preserve the change as a correction/removal signal, not negative audience reach.'
        elif v.get('reaction_delta') == 0:
            r['trend_status'] = 'flat_observed_window'
            r['trend_reason'] = 'The reaction counter did not change across %.2f hours; this window supplies no growth signal.' % v['span_hours']
        else:
            r['trend_status'] = 'growth_observed_not_trend'
            r['trend_reason'] = '+%s reactions across %.2f hours (%.4f/h). A positive counter change alone does not establish a trend; comparable fresh peers and additional intervals are still needed.' % (v['reaction_delta'], v['span_hours'], v['reactions_per_hour'])
        r['scope'] = 'Selected public-page sample. Age bins are coarse; topic, distribution and promotion remain confounders. No impressions, audience quality, causality or conversion estimate.'
    return rows


def validate_interpretations(posts, rows, contract):
    expected = {p['id']: p for p in posts}
    ids = [x.get('post_id') for x in rows]
    problems = []
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        problems.append('Interpretations must cover every corpus post exactly once, with no extras.')
    for r in rows:
        pid = r.get('post_id'); p = expected.get(pid)
        if not p:
            continue
        if r.get('text_sha256') != hashlib.sha256(p['text'].encode()).hexdigest():
            problems.append(pid + ': text hash mismatch')
        for key in contract['required_fields'] + ['content_language']:
            if key not in r or r[key] is None:
                problems.append(pid + ': missing ' + key)
        for field, choices in [('primary_topic', 'topic_ids'), ('editorial_job', 'editorial_jobs'), ('reference_value', 'reference_values')]:
            if r.get(field) not in contract[choices]:
                problems.append(pid + ': invalid ' + field)
        if not isinstance(r.get('secondary_topics'), list) or any(x not in contract['topic_ids'] for x in r.get('secondary_topics', [])):
            problems.append(pid + ': invalid secondary topics')
    return problems
