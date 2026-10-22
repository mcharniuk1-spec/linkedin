"""Generate original synthetic parser fixtures; no captured LinkedIn source text."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
HOST = 'https://www.linkedin.com'
LINKED = 'urn:li:activity:7000000000000000007'

def url(pid, author):
    return HOST + '/posts/' + author + '_synthetic-activity-' + str(pid) + '-AbCd'


def legacy(pid, author, index):
    u = url(pid, author)
    ld = {'@context':'https://schema.org','@type':'SocialMediaPosting','@id':u,
          'datePublished':'2026-10-01T10:00:00Z',
          'creator':{'@type':'Person','name':'Synthetic Author ' + str(index),'url':HOST+'/in/'+author,
                     'interactionStatistic':{'userInteractionCount':1000}}}
    text = ('Synthetic fixture %s teaches a fictional B2B buyer research method. '
            'This original test sentence is invented for parser and identity checks; it is not a real publication.' % index)
    related = ''
    if index == 7:
        related = '<a data-tracking-control-name="link-overlay-public_post" href="'+url(7000000000000000200,author)+'">Invented same-author link</a><a data-tracking-control-name="link-overlay-public_post" href="'+url(7000000000000000201,'synthetic-other')+'">Invented related link</a>'
    return '<!doctype html><html><script type="application/ld+json">'+json.dumps(ld)+'</script><article data-activity-urn="urn:li:activity:'+str(pid)+'"><a data-tracking-control-name="public_post_feed-actor-name" href="'+HOST+'/in/'+author+'">Synthetic Author '+str(index)+'</a><div data-test-id="main-feed-activity-card__commentary">'+text+'</div><div class="main-feed-activity-card__social-actions"><span data-test-id="social-actions__reaction-count">'+str(10+index)+'</span><span data-test-id="social-actions__comments">2 Comments</span></div><div data-test-id="feed-images-content"><img alt="Synthetic original test image" src="https://media.licdn.com/dms/image/synthetic-'+str(index)+'.jpg"></div>'+related+'</article><aside><time datetime="2099-01-01">Unrelated comment date</time></aside></html>'


def generate():
    for i in range(1,9):
        pid=7000000000000000000+i;author='synthetic-link-author' if i==7 else 'synthetic-author-'+str(i)
        (HERE/('legacy-'+str(i)+'.html')).write_text(legacy(pid,author,i))
    counts=[(57,27,1),(233,53,2),(95,28,1),(26,None,None),(325,26,7)]
    for i,(reactions,comments,reposts) in enumerate(counts):
        pid=7100000000000000000+i;author='synthetic-guest-'+str(i);u=url(pid,author)
        creator={'@type':'Person','name':'Synthetic Guest '+str(i),'url':HOST+'/in/'+author}
        ld={'@type':'VideoObject' if i==4 else 'SocialMediaPosting','@id':u,'creator':creator,'datePublished':'2026-10-01T10:00:00Z'}
        if i==2:ld={'@graph':[{'@type':'SocialMediaPosting','@id':url(7999999999999999990,'noise')},ld]}
        text='Synthetic guest layout %s explains a fictional founder positioning lesson. The target paragraph is original test data and contains no scraped post text.'%i
        counters='<a aria-label="Reaction button state: no reaction">%s</a><a aria-label="Comment">%s</a><a aria-label="Repost">%s</a>'%(reactions,comments if comments is not None else 'Comment',reposts if reposts is not None else 'Repost')
        card='<div role="listitem" componentkey="update-card-focus-synthetic"><a href="'+creator['url']+'">'+creator['name']+'</a><div data-testid="expandable-text-box">'+text+'</div>'+counters+'</div>'
        html='<html><script type="application/ld+json">'+json.dumps(ld)+'</script><main><section aria-label="Primary content">'+card+'</section><section aria-label="Other content"><a aria-label="Reaction button state: no reaction">999999</a></section></main></html>'
        (HERE/('guest-'+str(i)+'.html')).write_text(html)
    (HERE/'guest-5.html').write_text('<html><main><section aria-label="Primary content">Synthetic unsupported or signed-out page; no matching actor or commentary.</section></main></html>')

if __name__ == '__main__':
    generate()
