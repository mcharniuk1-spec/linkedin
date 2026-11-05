"""Privacy-preserving daily collection progress; never a trend or quality score."""
from datetime import datetime, time, timedelta, timezone
import json
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo


def daily_progress(store, *, now=None, posts_goal=100, accounts_goal=10):
    """Count newly stored LinkedIn posts and distinct observable actor URLs.

    The local day uses actual Sofia DST boundaries. Baseline aliases, snapshots,
    unrelated record types and unknown actors are not counted as publications
    or accounts. This is collection progress, not an analytical release.
    """
    zone = ZoneInfo('Europe/Sofia')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('aware_datetime_required')
    day = now.astimezone(zone).date()
    start = datetime.combine(day, time.min, tzinfo=zone).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone).astimezone(timezone.utc)
    posts = unknown_authors = malformed = future = 0
    actors = set()
    for collected_at, payload in store.db.execute('SELECT collected_at,payload FROM records'):
        try:
            value = json.loads(payload)
            if not isinstance(value, dict):
                raise ValueError('invalid_payload')
            if value.get('content_type') != 'linkedin_post':
                continue
            stamp = datetime.fromisoformat(collected_at.replace('Z', '+00:00'))
            if stamp.tzinfo is None:
                raise ValueError('timestamp_without_timezone')
        except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
            malformed += 1
            continue
        if not start <= stamp.astimezone(timezone.utc) < end:
            continue
        if stamp.astimezone(timezone.utc) > now.astimezone(timezone.utc):
            future += 1
            continue
        posts += 1
        author = value.get('author')
        url = author.get('url') if isinstance(author,dict) else None
        try:
            parsed = urlsplit(url) if isinstance(url,str) else None
            if not parsed or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError('missing_actor')
            host = parsed.hostname.lower()
            if not (host == 'linkedin.com' or host.endswith('.linkedin.com')):
                raise ValueError('not_linkedin_actor')
            parts = [p for p in parsed.path.split('/') if p]
            if len(parts) != 2 or parts[0].lower() not in {'in','company'}:
                raise ValueError('not_actor_path')
            actors.add('/'+parts[0].lower()+'/'+parts[1].lower())
        except ValueError:
            unknown_authors += 1
    return {
        'local_date': day.isoformat(), 'timezone': 'Europe/Sofia',
        'window_start_utc': start.isoformat(), 'window_end_utc': end.isoformat(),
        'new_unique_posts': posts, 'distinct_observed_accounts': len(actors),
        'posts_without_usable_actor': unknown_authors, 'malformed_records_excluded': malformed,
        'future_records_excluded': future,
        'goals': {'new_unique_posts': posts_goal, 'distinct_observed_accounts': accounts_goal},
        'posts_goal_met': posts >= posts_goal, 'accounts_goal_met': len(actors) >= accounts_goal,
        'interpretation': 'newly stored observations; pending review, not a trend or outcome measure',
    }
