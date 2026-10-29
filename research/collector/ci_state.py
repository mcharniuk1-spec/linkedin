"""Encrypted Actions state with an explicit, compare-and-swap checkpoint.

Only the encrypted artifact and a small public checksum pointer leave the runner.
No raw records, tokens or decrypted database are Actions artifacts or Git files.
After successful first CI bootstrap, an operator must set the repository variable
COLLECTOR_BOOTSTRAP_ALLOWED=false. It is never reset automatically; lost state
requires recovery, not another bootstrap.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse, base64, hashlib, io, json, os, re, sqlite3, stat, subprocess, tempfile, threading, time, zipfile
import zlib
from cryptography.fernet import Fernet, InvalidToken
from .contracts import ConfigurationError
from .store import Store

SCHEMA='linkedin-collector-state/1'
BRANCH='collector-state'
CHECKPOINT='state/checkpoint.json'
MAX_ENCRYPTED=48*1024*1024
MAX_ZIP_DOWNLOAD=MAX_ENCRYPTED+1024*1024
MAX_GH_JSON=2*1024*1024
MAX_GH_STDERR=128*1024
MAX_DECODED=96*1024*1024
MAX_KEY_FILE=256


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def key():
    value=os.environ.get('COLLECTOR_STATE_KEY')
    if not value and os.environ.get('COLLECTOR_STATE_KEY_FILE'):
        path=Path(os.environ['COLLECTOR_STATE_KEY_FILE'])
        try:
            if path.is_symlink():
                raise ConfigurationError('invalid_state_key_file')
            fd=os.open(path,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
            info=os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or (os.name=='posix' and info.st_mode & 0o077) or info.st_size>MAX_KEY_FILE:
                os.close(fd);raise ConfigurationError('invalid_state_key_file')
            with os.fdopen(fd,'rb') as f:
                raw=f.read(MAX_KEY_FILE+1)
            if len(raw)>MAX_KEY_FILE:raise ConfigurationError('invalid_state_key_file')
            value=raw.decode('ascii').strip()
        except ConfigurationError:
            raise
        except (OSError,UnicodeError):
            raise ConfigurationError('invalid_state_key_file') from None
    if not value:
        raise ConfigurationError('missing_state_encryption_key')
    try:
        return value.encode(),Fernet(value.encode())
    except (ValueError,TypeError):
        raise ConfigurationError('invalid_state_encryption_key') from None


def _bounded_gh_run(cmd,input_bytes,response_limit,timeout=90):
    try:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                              stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except OSError:
        raise ConfigurationError('github_state_api_failed') from None
    buffers={'stdout':bytearray(),'stderr':bytearray()};limits={'stdout':response_limit,'stderr':MAX_GH_STDERR}
    too_large=threading.Event()

    def drain(name,stream):
        limit=limits[name];buf=buffers[name]
        try:
            while True:
                part=stream.read(min(65536,limit+1-len(buf)))
                if not part:break
                buf.extend(part)
                if len(buf)>limit:
                    too_large.set()
                    try:proc.kill()
                    except OSError:pass
                    break
        except OSError:
            too_large.set()

    readers=[threading.Thread(target=drain,args=('stdout',proc.stdout),daemon=True),
             threading.Thread(target=drain,args=('stderr',proc.stderr),daemon=True)]
    for thread in readers:thread.start()
    writer_error=[]
    def write_input():
        try:
            if proc.stdin:
                proc.stdin.write(input_bytes or b'');proc.stdin.close()
        except (BrokenPipeError,OSError):writer_error.append(True)
    writer=threading.Thread(target=write_input,daemon=True) if input_bytes is not None else None
    if writer:writer.start()
    deadline=time.monotonic()+timeout;timed_out=False
    while proc.poll() is None:
        if too_large.is_set():break
        if time.monotonic()>=deadline:
            timed_out=True
            try:proc.kill()
            except OSError:pass
            break
        time.sleep(.01)
    try:proc.wait(timeout=1)
    except subprocess.TimeoutExpired:
        proc.kill();proc.wait()
    for thread in readers:thread.join(timeout=1)
    if writer:writer.join(timeout=1)
    if timed_out:raise ConfigurationError('github_state_api_timeout')
    if too_large.is_set():raise ConfigurationError('github_response_too_large')
    return proc.returncode,bytes(buffers['stdout']),bytes(buffers['stderr'])


def gh(path, *, method='GET', body=None, binary=False, missing=False, response_limit=None):
    if not isinstance(path,str) or path.startswith('/') or '\n' in path or '\r' in path:
        raise ConfigurationError('invalid_github_api_path')
    if method not in {'GET','POST','PUT','DELETE'}:
        raise ConfigurationError('invalid_github_api_method')
    cmd=['gh','api',path,'--method',method]
    input_bytes=None
    if body is not None:
        cmd+=['--input','-']
        input_bytes=canonical(body)
        if len(input_bytes)>MAX_GH_JSON:raise ConfigurationError('github_request_too_large')
    limit=response_limit if response_limit is not None else (MAX_ZIP_DOWNLOAD if binary else MAX_GH_JSON)
    if not isinstance(limit,int) or not 1<=limit<=MAX_ZIP_DOWNLOAD:
        raise ConfigurationError('invalid_github_response_limit')
    code,stdout,stderr=_bounded_gh_run(cmd,input_bytes,limit)
    if code:
        if missing and b'404' in stderr:
            return None
        raise ConfigurationError('github_state_api_failed')
    if binary:return stdout
    try:return json.loads(stdout)
    except (ValueError,TypeError):raise ConfigurationError('github_response_invalid') from None


def _valid_repository(repository):
    if not isinstance(repository,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repository):
        raise ConfigurationError('invalid_github_repository')


def _validate_pointer(value,repository):
    if not isinstance(value,dict) or value.get('schema')!=SCHEMA or value.get('repository')!=repository:
        raise ConfigurationError('invalid_state_checkpoint')
    if (not isinstance(value.get('revision'),int) or isinstance(value.get('revision'),bool) or value['revision']<1
        or not isinstance(value.get('artifact_id'),int) or isinstance(value.get('artifact_id'),bool) or value['artifact_id']<1
        or not isinstance(value.get('encrypted_bytes'),int) or isinstance(value.get('encrypted_bytes'),bool) or not 1<=value['encrypted_bytes']<=MAX_ENCRYPTED
        or not isinstance(value.get('encrypted_sha256'),str) or not re.fullmatch(r'[0-9a-f]{64}',value['encrypted_sha256'])
        or not isinstance(value.get('key_id'),str) or not re.fullmatch(r'[0-9a-f]{12}',value['key_id'])):
        raise ConfigurationError('invalid_state_checkpoint')
    return value


def pointer(repository):
    _valid_repository(repository)
    x=gh(f'repos/{repository}/contents/{CHECKPOINT}?ref={BRANCH}',missing=True)
    if x is None:
        return None,None
    try:
        content=''.join(x['content'].split())
        p=json.loads(base64.b64decode(content,validate=True))
        if not isinstance(x.get('sha'),str) or not x['sha']:
            raise ValueError('missing blob revision')
        return _validate_pointer(p,repository),x['sha']
    except (ValueError,KeyError,TypeError,AttributeError):
        raise ConfigurationError('invalid_state_checkpoint') from None


def artifacts(repository, *, include_expired=False):
    _valid_repository(repository)
    out=[]
    for page in range(1,11):
        x=gh(f'repos/{repository}/actions/artifacts?per_page=100&page={page}')
        if not isinstance(x,dict) or not isinstance(x.get('artifacts'),list):
            raise ConfigurationError('invalid_artifact_listing')
        items=x['artifacts']
        for a in items:
            if (not isinstance(a,dict) or not isinstance(a.get('name'),str)
                or not isinstance(a.get('id'),int) or isinstance(a.get('id'),bool)
                or not isinstance(a.get('expired',False),bool)):
                raise ConfigurationError('invalid_artifact_listing')
            if a['name'].startswith('linkedin-private-state-') and (include_expired or not a.get('expired',False)):
                out.append(a)
        if len(items)<100:
            return out
    raise ConfigurationError('artifact_listing_page_cap')


def seal(state_dir, output, context):
    if not isinstance(context,dict) or not isinstance(context.get('repository'),str):
        raise ConfigurationError('invalid_state_context')
    revision=context.get('revision');previous=context.get('checkpoint_sha256')
    if (not isinstance(revision,int) or isinstance(revision,bool) or revision<0
        or (previous is not None and (not isinstance(previous,str) or not re.fullmatch(r'[0-9a-f]{64}',previous)))
        or (revision==0 and previous is not None) or (revision>0 and previous is None)):
        raise ConfigurationError('invalid_state_context')
    state_dir=Path(state_dir);output=Path(output);store=Store(state_dir)
    snap=state_dir/'checkpoint.sqlite'
    try:
        store.snapshot(snap)
    finally:
        store.close()
    db=snap.read_bytes();snap.unlink()
    k,cipher=key()
    envelope={'schema':SCHEMA,'repository':context['repository'],
      'revision':revision+1,'previous_checkpoint_sha256':previous,
      'database_sha256':hashlib.sha256(db).hexdigest(),'database':base64.b64encode(db).decode()}
    vault=state_dir/'tokens.enc'
    if vault.exists():
        envelope['token_vault']=base64.b64encode(vault.read_bytes()).decode()
    # Compress before authenticated encryption; bound the ciphertext before upload.
    import gzip
    encrypted=cipher.encrypt(gzip.compress(canonical(envelope),mtime=0))
    if len(encrypted)>MAX_ENCRYPTED:
        raise ConfigurationError('encrypted_state_capacity_hold')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(encrypted);os.chmod(output,0o600)
    return {'sha256':hashlib.sha256(encrypted).hexdigest(),'bytes':len(encrypted),
            'revision':envelope['revision'],'key_id':hashlib.sha256(k).hexdigest()[:12]}


def unseal(encrypted, state_dir, expected):
    if not isinstance(expected,dict):
        raise ConfigurationError('invalid_state_checkpoint')
    if not isinstance(encrypted,bytes) or len(encrypted)>MAX_ENCRYPTED or hashlib.sha256(encrypted).hexdigest()!=expected.get('encrypted_sha256'):
        raise ConfigurationError('state_artifact_hash_mismatch')
    if expected.get('encrypted_bytes') is not None and len(encrypted)!=expected['encrypted_bytes']:
        raise ConfigurationError('state_artifact_size_mismatch')
    k,cipher=key()
    if hashlib.sha256(k).hexdigest()[:12]!=expected.get('key_id'):
        raise ConfigurationError('state_key_identity_mismatch')
    try:
        import gzip
        packed=cipher.decrypt(encrypted)
        # Bounded decompression prevents a valid-but-oversized archive exhausting a runner.
        with gzip.GzipFile(fileobj=io.BytesIO(packed)) as f:
            decoded=f.read(MAX_DECODED+1)
        if len(decoded)>MAX_DECODED:
            raise ConfigurationError('decrypted_state_capacity_hold')
        value=json.loads(decoded)
        if (not isinstance(value,dict) or value.get('schema')!=SCHEMA
            or value.get('repository')!=expected.get('repository')
            or value.get('revision')!=expected.get('revision')):
            raise ConfigurationError('invalid_encrypted_state')
        if ('previous_checkpoint_sha256' in expected
            and value.get('previous_checkpoint_sha256')!=expected['previous_checkpoint_sha256']):
            raise ConfigurationError('invalid_encrypted_state')
        if not isinstance(value.get('database_sha256'),str) or not re.fullmatch(r'[0-9a-f]{64}',value['database_sha256']):
            raise ConfigurationError('invalid_encrypted_state')
        if not isinstance(value.get('database'),str):
            raise ConfigurationError('invalid_encrypted_state')
        db=base64.b64decode(value['database'],validate=True)
        if hashlib.sha256(db).hexdigest()!=value['database_sha256']:
            raise ConfigurationError('invalid_encrypted_state')
        token_vault=None
        if value.get('token_vault') is not None:
            if not isinstance(value['token_vault'],str) or len(value['token_vault'])>2*1024*1024:
                raise ConfigurationError('invalid_encrypted_state')
            token_vault=base64.b64decode(value['token_vault'],validate=True)
    except ConfigurationError:
        raise
    except (InvalidToken,ValueError,KeyError,TypeError,OSError):
        raise ConfigurationError('invalid_encrypted_state') from None
    state_dir=Path(state_dir);state_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(state_dir,0o700)
    db_path=state_dir/'collector.sqlite';tmp=state_dir/'restore.tmp';vault_path=state_dir/'tokens.enc'
    if any(p.exists() or p.is_symlink() for p in (db_path,tmp,vault_path)):
        raise ConfigurationError('restore_requires_empty_state_directory')
    try:
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'wb') as f:
            f.write(db);f.flush();os.fsync(f.fileno())
        con=sqlite3.connect(tmp)
        try:
            integrity=con.execute('pragma integrity_check').fetchone()
            if not integrity or integrity[0]!='ok':
                raise ConfigurationError('invalid_state_database')
            marker=con.execute("select count(*) from metadata where key='bootstrap_sha256'").fetchone()
            if not marker or marker[0]!=1:
                raise ConfigurationError('invalid_state_database')
        finally:
            con.close()
        tmp.replace(db_path);os.chmod(db_path,0o600)
        if token_vault is not None:
            fd=os.open(vault_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
            with os.fdopen(fd,'wb') as f:
                f.write(token_vault);f.flush();os.fsync(f.fileno())
    except ConfigurationError:
        try:tmp.unlink()
        except FileNotFoundError:pass
        raise
    except (sqlite3.Error,OSError,ValueError):
        try:tmp.unlink()
        except FileNotFoundError:pass
        raise ConfigurationError('invalid_state_database') from None
    return {'restored':True,'revision':value['revision']}


def restore(repository, state_dir, context_path, bootstrap=False):
    _valid_repository(repository)
    p,blob=pointer(repository)
    available=artifacts(repository,include_expired=True)
    if p is None:
        is_ci=os.environ.get('GITHUB_ACTIONS','').lower()=='true'
        if not bootstrap or available:
            raise ConfigurationError('missing_state_checkpoint_requires_explicit_first_bootstrap_or_recovery')
        if is_ci:
            if (os.environ.get('GITHUB_EVENT_NAME')!='workflow_dispatch'
                or os.environ.get('COLLECTOR_BOOTSTRAP_ALLOWED','').lower()!='true'):
                raise ConfigurationError('missing_state_checkpoint_requires_explicit_first_bootstrap_or_recovery')
        if gh(f'repos/{repository}/git/ref/heads/{BRANCH}',missing=True) is not None:
            raise ConfigurationError('state_branch_exists_without_checkpoint_requires_recovery')
        context={'repository':repository,'revision':0,'checkpoint_sha256':None,'blob_sha':None,'artifact_id':None}
        key()  # Missing key must fail before any source request, including bootstrap.
    else:
        # A newer orphan might contain observations not yet referenced by the checkpoint.
        if any(a['id']>p['artifact_id'] for a in available):
            raise ConfigurationError('orphan_state_artifact_requires_recovery')
        artifact=next((a for a in available if a['id']==p['artifact_id'] and not a.get('expired',False)),None)
        if not artifact:
            raise ConfigurationError('state_artifact_missing_or_oversized')
        encrypted=_read_state_artifact(repository,artifact)
        unseal(encrypted,state_dir,p)
        context={'repository':repository,'revision':p['revision'],
            'checkpoint_sha256':hashlib.sha256(canonical(p)).hexdigest(),'blob_sha':blob,'artifact_id':p['artifact_id']}
    Path(context_path).parent.mkdir(parents=True,exist_ok=True)
    Path(context_path).write_text(json.dumps(context,indent=2)+'\n')
    return {'restored_revision':context['revision'],'bootstrap':p is None}


def _read_state_artifact(repository,artifact):
    artifact_id=artifact.get('id')
    size=artifact.get('size_in_bytes')
    if (not isinstance(artifact_id,int) or isinstance(artifact_id,bool) or artifact_id<1
        or not isinstance(size,int) or isinstance(size,bool) or size<1 or size>MAX_ZIP_DOWNLOAD):
        raise ConfigurationError('state_artifact_missing_or_oversized')
    body=gh(f'repos/{repository}/actions/artifacts/{artifact_id}/zip',binary=True,response_limit=MAX_ZIP_DOWNLOAD)
    if not isinstance(body,bytes) or len(body)>MAX_ZIP_DOWNLOAD or len(body)!=size:
        raise ConfigurationError('state_archive_size_mismatch')
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            infos=archive.infolist()
            if len(infos)!=1 or infos[0].filename!='state.enc':
                raise ConfigurationError('unexpected_state_archive_members')
            info=infos[0]
            if info.file_size<1 or info.file_size>MAX_ENCRYPTED or info.compress_size>MAX_ZIP_DOWNLOAD:
                raise ConfigurationError('unexpected_state_archive_members')
            with archive.open(info,'r') as member:
                encrypted=member.read(MAX_ENCRYPTED+1)
                if len(encrypted)>MAX_ENCRYPTED or len(encrypted)!=info.file_size or member.read(1):
                    raise ConfigurationError('state_archive_member_size_mismatch')
            return encrypted
    except ConfigurationError:
        raise
    except (zipfile.BadZipFile,zipfile.LargeZipFile,RuntimeError,OSError,EOFError,ValueError,zlib.error):
        raise ConfigurationError('invalid_state_archive') from None


def publish(repository, artifact_id, seal_report, context):
    _valid_repository(repository)
    if not isinstance(context,dict) or context.get('repository')!=repository:
        raise ConfigurationError('invalid_state_context')
    context_revision=context.get('revision')
    if not isinstance(context_revision,int) or isinstance(context_revision,bool) or context_revision<0:
        raise ConfigurationError('invalid_state_context')
    if ('blob_sha' not in context or 'checkpoint_sha256' not in context
        or (context['blob_sha'] is not None and not isinstance(context['blob_sha'],str))):
        raise ConfigurationError('invalid_state_context')
    previous=context.get('checkpoint_sha256')
    if (previous is not None and (not isinstance(previous,str) or not re.fullmatch(r'[0-9a-f]{64}',previous))) or (context_revision==0 and previous is not None) or (context_revision>0 and previous is None):
        raise ConfigurationError('invalid_state_context')
    if not isinstance(seal_report,dict):raise ConfigurationError('invalid_seal_report')
    report_revision=seal_report.get('revision');report_bytes=seal_report.get('bytes')
    report_sha=seal_report.get('sha256');report_key_id=seal_report.get('key_id')
    if (not isinstance(report_revision,int) or isinstance(report_revision,bool)
        or report_revision!=context_revision+1 or not isinstance(report_bytes,int)
        or isinstance(seal_report.get('bytes'),bool) or not 1<=report_bytes<=MAX_ENCRYPTED
        or not isinstance(report_sha,str) or not re.fullmatch(r'[0-9a-f]{64}',report_sha)
        or not isinstance(report_key_id,str) or not re.fullmatch(r'[0-9a-f]{12}',report_key_id)):
        raise ConfigurationError('invalid_seal_report')
    if isinstance(artifact_id,bool):raise ConfigurationError('state_artifact_missing_or_oversized')
    try:artifact_id=int(artifact_id)
    except (TypeError,ValueError):raise ConfigurationError('state_artifact_missing_or_oversized') from None
    if artifact_id<1:raise ConfigurationError('state_artifact_missing_or_oversized')
    current,blob=pointer(repository)
    digest=hashlib.sha256(canonical(current)).hexdigest() if current else None
    if digest!=context['checkpoint_sha256'] or blob!=context['blob_sha']:
        raise ConfigurationError('concurrent_checkpoint_change')
    if current and current['revision']!=context_revision:
        raise ConfigurationError('concurrent_checkpoint_change')
    if current is None and context_revision!=0:
        raise ConfigurationError('invalid_state_context')

    artifact=next((a for a in artifacts(repository,include_expired=True) if a.get('id')==artifact_id),None)
    if (not artifact or artifact.get('expired',False)
        or not isinstance(artifact.get('name'),str) or not artifact['name'].startswith('linkedin-private-state-')):
        raise ConfigurationError('state_artifact_missing_or_oversized')
    encrypted=_read_state_artifact(repository,artifact)
    if len(encrypted)!=report_bytes or hashlib.sha256(encrypted).hexdigest()!=report_sha:
        raise ConfigurationError('seal_report_artifact_mismatch')
    expected={'repository':repository,'revision':report_revision,'encrypted_sha256':report_sha,
              'encrypted_bytes':report_bytes,'key_id':report_key_id,
              'previous_checkpoint_sha256':context['checkpoint_sha256']}
    with tempfile.TemporaryDirectory(prefix='linkedin-state-verify-') as td:
        unseal(encrypted,td,expected)
    if current is None:
        base=gh(f'repos/{repository}/git/ref/heads/main')['object']['sha']
        if gh(f'repos/{repository}/git/ref/heads/{BRANCH}',missing=True) is not None:
            raise ConfigurationError('state_branch_exists_without_checkpoint_requires_recovery')
        gh(f'repos/{repository}/git/refs',method='POST',body={'ref':'refs/heads/'+BRANCH,'sha':base})
    value={'schema':SCHEMA,'repository':repository,'revision':seal_report['revision'],
        'artifact_id':artifact_id,'encrypted_sha256':report_sha,
        'encrypted_bytes':report_bytes,'key_id':report_key_id,
        'updated_at':datetime.now(timezone.utc).isoformat(),
        'privacy':'Encrypted bounded state only; no raw data or token is public plaintext.'}
    body={'message':'Advance encrypted collection checkpoint','branch':BRANCH,'content':base64.b64encode(canonical(value)+b'\n').decode()}
    if blob:
        body['sha']=blob
    gh(f'repos/{repository}/contents/{CHECKPOINT}',method='PUT',body=body)
    actual,_=pointer(repository)
    if actual!=value:
        raise ConfigurationError('checkpoint_readback_failed')
    # Delete older ciphertext only after successful CAS and readback; retain two checkpoints.
    older=sorted(artifacts(repository),key=lambda a:a['id'],reverse=True)
    for a in older[2:]:
        gh(f'repos/{repository}/actions/artifacts/{a["id"]}',method='DELETE',binary=True)
    return {'checkpoint_revision':value['revision'],'artifact_id':value['artifact_id'],'verified':True}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['restore','seal','publish'])
    ap.add_argument('--repository',default=os.environ.get('GITHUB_REPOSITORY'))
    ap.add_argument('--state-dir',default='research/work/collector');ap.add_argument('--context',default='research/work/context.json')
    ap.add_argument('--output',default='research/work/state.enc');ap.add_argument('--report',default='research/work/seal.json')
    ap.add_argument('--artifact-id');ap.add_argument('--bootstrap',action='store_true');a=ap.parse_args()
    try:
        if a.command=='restore':
            result=restore(a.repository,a.state_dir,a.context,a.bootstrap)
        elif a.command=='seal':
            result=seal(a.state_dir,a.output,json.loads(Path(a.context).read_text()));Path(a.report).write_text(json.dumps(result)+'\n')
        else:
            result=publish(a.repository,a.artifact_id,json.loads(Path(a.report).read_text()),json.loads(Path(a.context).read_text()))
        print(json.dumps(result))
    except ConfigurationError as e:
        print(json.dumps({'status':'FAILED_CLOSED','error_code':str(e)}));return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
