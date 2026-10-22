"""Runtime records for the original synthetic HTML fixture corpus."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import normalizer

FIXTURES=Path(__file__).resolve().parent/'fixtures/cycle'
LINKED='urn:li:activity:7000000000000000007'

def records():
    captured=(datetime.now(timezone.utc)-timedelta(hours=1)).isoformat()
    posts=[]
    for i in range(1,9):
        pid=7000000000000000000+i;author='synthetic-link-author' if i==7 else 'synthetic-author-'+str(i)
        u='https://www.linkedin.com/posts/'+author+'_synthetic-activity-'+str(pid)+'-AbCd'
        posts.append(normalizer.parse_post(FIXTURES/('legacy-'+str(i)+'.html'),u,captured,rights='original_synthetic_test_fixture'))
    guests=[]
    for i in range(6):
        u='https://www.linkedin.com/posts/synthetic-guest-'+str(i)+'_synthetic-activity-'+str(7100000000000000000+i)+'-AbCd'
        guests.append({'url':u,'path':str(FIXTURES/('guest-'+str(i)+'.html'))})
    return posts[:7],posts[7:],guests
