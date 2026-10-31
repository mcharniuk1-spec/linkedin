from pathlib import Path
import re,unittest,yaml
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[2]
class WorkflowTests(unittest.TestCase):
 def test_collection_schedule_and_no_analysis_boundary(self):
  p=ROOT/'.github/workflows/linkedin-collect.yml';text=p.read_text();w=yaml.load(text,Loader=yaml.BaseLoader)
  self.assertEqual(w['on']['schedule'],[{'cron':'*/30 * * * *','timezone':'Europe/Sofia'}])
  self.assertEqual(w['concurrency']['cancel-in-progress'],'false');steps=w['jobs']['collect']['steps']
  runs='\n'.join(x.get('run','') for x in steps)
  self.assertIn('research.collector.cli collect',runs)
  for forbidden in ('cycle.py','transcribe',' refresh','update-run','ffmpeg','ollama'):
   self.assertNotIn(forbidden,runs)
  for x in steps:
   if 'uses' in x:self.assertRegex(x['uses'],r'@[0-9a-f]{40}$')
  upload=next(x for x in steps if x.get('uses','').startswith('actions/upload-artifact@'))
  self.assertEqual(upload['with']['path'],'research/work/state.enc')
 def test_timezone_retains_local_noon_and_evening_across_dst(self):
  for month,offset in ((1,2),(7,3),(10,2)):
   for hour in (12,20):
    local=datetime(2026,month,29,hour,tzinfo=ZoneInfo('Europe/Sofia'))
    self.assertEqual(local.utcoffset().total_seconds()/3600,offset)
    self.assertEqual(local.astimezone(ZoneInfo('UTC')).hour,hour-offset)
 def test_test_workflow_commands_exist(self):
  w=yaml.load((ROOT/'.github/workflows/collector-tests.yml').read_text(),Loader=yaml.BaseLoader)
  checkout=next(x for x in w['jobs']['synthetic-tests']['steps'] if x.get('uses','').startswith('actions/checkout@'))
  self.assertIn('.github',checkout['with']['sparse-checkout'].split())
  for x in w['jobs']['synthetic-tests']['steps']:
   run=x.get('run','')
   if run.startswith('python scripts/'):self.assertTrue((ROOT/run.split()[1]).is_file())
if __name__=='__main__':unittest.main()
