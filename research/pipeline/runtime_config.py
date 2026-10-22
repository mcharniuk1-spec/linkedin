"""Portable local configuration. No installation, authentication or provider calls."""
from pathlib import Path
import json
import os
import shutil
import sys


def resolve_path(value, base):
    path = Path(os.path.expandvars(os.path.expanduser(str(value))))
    return str((path if path.is_absolute() else base / path).resolve())


def load_config(path, object_pairs_hook=None):
    path = Path(path).resolve()
    config = json.loads(path.read_text(), object_pairs_hook=object_pairs_hook)
    base = path.parent
    config['run_root'] = resolve_path(config['run_root'], base)
    for key in ('corpus_posts', 'corpus_snapshots'):
        config[key] = [resolve_path(p, base) for p in config.get(key, [])]
    if config.get('baseline_posts'):
        config['baseline_posts'] = resolve_path(config['baseline_posts'], base)
    qa = config.setdefault('transcript_qa', {})
    qa['corpus_datasets'] = [resolve_path(p, base) for p in qa.get('corpus_datasets', [])]
    whisper = config.setdefault('whisper', {})
    whisper['model'] = resolve_path(os.environ.get('LINKEDIN_WHISPER_MODEL') or whisper.get('model') or '~/.cache/whisper/large-v3-turbo.pt', base)
    python = os.environ.get('LINKEDIN_WHISPER_PYTHON') or whisper.get('python') or sys.executable
    whisper['python'] = resolve_path(python, base) if os.sep in python else python
    # Overrides are local runtime inputs. They are never written into source config.
    config['_config_directory'] = str(base)
    return config


def tool_command(config, name):
    """Resolve an explicitly configured binary or an existing PATH binary."""
    value = config.get('tools', {}).get(name) or name
    if os.sep in value:
        value = resolve_path(value, Path(config['_config_directory']))
    found = shutil.which(value)
    if not found:
        raise RuntimeError('Required existing tool unavailable: ' + name + '; configure tools.' + name + ' or PATH. No installation attempted.')
    return found
