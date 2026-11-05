import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research.collector.ci_state import canonical
from research.collector.contracts import ConfigurationError
from research.collector.latest_viewer import project_latest
from research.collector.store import Store


class LatestViewerTests(unittest.TestCase):
    def test_authenticated_revision_is_projected_and_temporary_store_removed(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            output=Path(temp)/'view.json';pointer={'revision':3};digest=hashlib.sha256(canonical(pointer)).hexdigest()
            dirs=[]
            def restore(repo,state,context,bootstrap):
                dirs.append(Path(state).parent);s=Store(state);s.suspend('linkedin-public','challenge_page');s.close()
                Path(context).write_text(json.dumps({'blob_sha':'blob','checkpoint_sha256':digest,'artifact_id':42}))
                return {'restored_revision':3}
            with patch('research.collector.latest_viewer.restore',restore),patch('research.collector.latest_viewer.pointer',return_value=(pointer,'blob')):
                result=project_latest('owner/repo',output)
            self.assertEqual(result['restored_revision'],3);self.assertEqual(result['linkedin_status'],'blocked')
            self.assertEqual(json.loads(output.read_text())['checkpoint']['revision'],3)
            self.assertFalse(dirs[0].exists());self.assertEqual(output.stat().st_mode & 0o777,0o600)

    def test_changed_checkpoint_fails_closed_without_output(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as temp:
            output=Path(temp)/'view.json'
            def restore(repo,state,context,bootstrap):
                s=Store(state);s.close();Path(context).write_text(json.dumps({'blob_sha':'old','checkpoint_sha256':'a'*64,'artifact_id':42}))
                return {'restored_revision':3}
            with patch('research.collector.latest_viewer.restore',restore),patch('research.collector.latest_viewer.pointer',return_value=({'revision':4},'new')):
                with self.assertRaises(ConfigurationError):project_latest('owner/repo',output)
            self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
