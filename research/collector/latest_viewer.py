"""Restore an authenticated production checkpoint into a local-only viewer snapshot."""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from .ci_state import canonical, pointer, restore
from .contracts import ConfigurationError
from .store import Store
from .viewer_projection import build


def project_latest(repository, output):
    output=Path(output).expanduser().absolute()
    if output.parent.resolve()!=output.parent or any((p/'.git').exists() for p in (output.parent,*output.parents)):
        raise ConfigurationError('private_non_git_output_required')
    if not output.parent.is_dir():raise ConfigurationError('output_parent_missing')
    with tempfile.TemporaryDirectory(prefix='linkedin-checkpoint-') as tmp:
        root=Path(tmp); os.chmod(root,0o700)
        info=restore(repository,root/'state',root/'context.json',False)
        ctx=json.loads((root/'context.json').read_text())
        store=Store(root/'state')
        try:
            with store.lock(): data=build(store)
        finally:store.close()
        current,blob=pointer(repository)
        if current is None or blob!=ctx['blob_sha'] or hashlib.sha256(canonical(current)).hexdigest()!=ctx['checkpoint_sha256']:
            raise ConfigurationError('checkpoint_changed_during_projection_retry')
        data['operations']['status_notes']+=' Authenticated production checkpoint revision '+str(info['restored_revision'])+'.'
        data['checkpoint']={'revision':info['restored_revision'],'artifact_id':ctx['artifact_id'],
                            'checkpoint_sha256':ctx['checkpoint_sha256']}
        fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    return {'restored_revision':info['restored_revision'],'snapshot_written':True,
            'reference_candidates':len(data['reference_candidates']),
            'external_signals':len(data['external_signals']),
            'target_companies':len(data['target_companies']),
            'linkedin_status':data['operations']['linkedin_status']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();print(json.dumps(project_latest(args.repository,args.output)))


if __name__=='__main__':main()
