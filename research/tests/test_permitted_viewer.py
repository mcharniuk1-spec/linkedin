"""Offline checks for the standalone, source-separated snapshot viewer."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path


VIEWER = Path(__file__).resolve().parents[1] / "permitted_viewer"


class ViewerTests(unittest.TestCase):
    def test_fixture_and_static_boundaries(self):
        data = json.loads((VIEWER / "fixture.json").read_text())
        self.assertEqual(data["schema"], "outspoken-research-viewer/1")
        for name in ("authorized_posts", "reference_candidates", "external_signals", "target_companies"):
            self.assertTrue(data[name])
            self.assertTrue(all("synthetic" in x["source_id"] for x in data[name]))
        html = (VIEWER / "index.html").read_text()
        self.assertIn("connect-src 'none'", html)
        self.assertIn('type="file"', html)
        self.assertEqual(html.count('role="tab"'), 4)
        js = (VIEWER / "viewer.js").read_text()
        for forbidden in ("innerHTML", "fetch(", "XMLHttpRequest", "localStorage", "eval("):
            self.assertNotIn(forbidden, js)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for JavaScript behavior tests")
    def test_javascript_contract_and_observation_boundaries(self):
        script = r'''
const assert=require('assert');
const fs=require('fs');
const viewer=require(process.argv[1]);
const data=JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
assert.equal(viewer.validate(data).schema, viewer.SCHEMA);
assert.throws(()=>viewer.validate({...data, external_signals:null}));
assert.throws(()=>viewer.validate({...data, generated_at:'2020-01-01'}));
assert.throws(()=>viewer.validate({...data, schema:'wrong'}));
assert.equal(viewer.count(0),0);
for (const value of [null,-1,3.5,'2',{status:'unknown',value:2}]) assert.equal(viewer.count(value),null);
assert.equal(viewer.count({status:'observed',value:2}),2);
for (const url of ['javascript:alert(1)','data:text/html,x','https://user:pass@example.test/']) assert.equal(viewer.safeUrl(url),null);
assert.equal(viewer.safeUrl('https://example.test/x'),'https://example.test/x');
const snapshot=(time,n,source='s',parser='p')=>({source_id:source,parser_version:parser,observed_at:time,metrics:{reactions:n}});
const base={publication_date_status:'verified_source_date',published_at:'2020-01-01T00:00:00Z',snapshots:[]};
const run=(a,b,overrides={})=>viewer.trendEvidence({...base,...overrides,snapshots:[a,b]}).state;
const first=snapshot('2020-01-01T01:00:00Z',3);
assert.equal(run(first,snapshot('2020-01-01T06:59:59Z',4)),'not_measured');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',4)),'measured_increase');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',4,'other')),'not_measured');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',4,'s','other')),'not_measured');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',null)),'not_measured');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',2)),'not_measured');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',3)),'no_increase');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',4),{publication_date_status:'unverified'}),'not_measured');
assert.equal(run(first,snapshot('2020-01-01T07:00:00Z',4),{published_at:'2020-01-02T00:00:00Z'}),'not_measured');
'''
        subprocess.run(["node", "-e", script, str(VIEWER / "viewer.js"), str(VIEWER / "fixture.json")], check=True)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for JavaScript behavior tests")
    def test_loading_tabs_and_untrusted_text_with_fake_dom(self):
        script = r'''
const assert=require('assert'),fs=require('fs'),viewer=require(process.argv[1]);
class Element {
  constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.attrs={};this.textContent='';this.hidden=false;}
  append(...nodes){this.children.push(...nodes)}
  replaceChildren(...nodes){this.children=nodes}
  setAttribute(k,v){this.attrs[k]=v}
  addEventListener(k,f){this.listeners[k]=f}
  focus(){this.focused=true}
}
const elements={};
const doc={getElementById(id){return elements[id]||(elements[id]=new Element('div'))},createElement(tag){return new Element(tag)},createTextNode(t){const n=new Element('#text');n.textContent=t;return n}};
viewer.start(doc);
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
data.authorized_posts[0].title='<img src=x onerror=alert(1)>';
const change=elements.snapshot.listeners.change;
const file={size:100,text:async()=>JSON.stringify(data)};
(async()=>{
 await change({target:{files:[file]}});
 assert.equal(elements['load-status'].textContent,'Snapshot loaded in this browser only.');
 const card=elements['authorized-list'].children[0];
 assert.equal(card.children[0].tag,'h4');
 assert.equal(card.children[0].textContent,'<img src=x onerror=alert(1)>');
 elements['tab-external'].listeners.click();
 assert.equal(elements['pane-external'].hidden,false);
 assert.equal(elements['pane-authorized'].hidden,true);
 await change({target:{files:[{size:3,text:async()=>'bad'}]}});
 assert.match(elements['load-status'].textContent,/not loaded/);
 assert.equal(elements['authorized-list'].children[0].textContent,'No snapshot selected.');
})().catch(error=>{console.error(error);process.exitCode=1});
'''
        subprocess.run(["node", "-e", script, str(VIEWER / "viewer.js"), str(VIEWER / "fixture.json")], check=True)


if __name__ == "__main__":
    unittest.main()
