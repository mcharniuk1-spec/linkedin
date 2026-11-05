"""Private, explicitly consented owner-export analytics. No network or API input.

Manual exports are independent of API data. This module deliberately refuses API
ingestion: separate agreement review and an API-specific store are required.
The caller is responsible for safeguarding and deleting the source export itself.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import sqlite3
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

MAX_FILE = 20_000_000
MAX_EXPANDED = 30_000_000
MAX_ROWS = 20_000
MAX_COLUMNS = 200
MISSING = {'', '-', '—', '–', 'n/a', 'na', 'null', 'none'}
METRICS = {'reactions','likes','comments','reposts','impressions','clicks','views','saves','engagements','followers'}
ALIASES = {
    'date':'date', 'day':'date', 'publicationdate':'date', 'publishedat':'date', 'postdate':'date',
    'postid':'post_id','publicationid':'post_id','shareid':'post_id',
    'posturl':'post_url','url':'post_url','permalink':'post_url','postlink':'post_url',
    'reactions':'reactions','reaction':'reactions','likes':'likes','like':'likes',
    'comments':'comments','comment':'comments','reposts':'reposts','repost':'reposts',
    'shares':'reposts','share':'reposts','impressions':'impressions','clicks':'clicks',
    'views':'views','videoviews':'views','saves':'saves','engagements':'engagements',
    'followers':'followers',
}


class ExportError(ValueError):
    """Safe error code: never includes content, account identity or source path."""


def _utc(value):
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ExportError('timezone_aware_timestamp_required')
    return value.astimezone(timezone.utc)


def _key(value):
    if not isinstance(value,str) or not 1 <= len(value.strip()) <= 256:
        raise ExportError('opaque_account_identifier_required')
    return hashlib.sha256(('consented-account-v1|'+value.strip()).encode()).hexdigest()


def _head(value):
    return re.sub(r'[^a-z0-9]','',str(value).lower())


def _read_source(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE:
        raise ExportError('source_file_missing_symlink_or_too_large')
    if path.suffix.lower() == '.xls':
        raise ExportError('binary_xls_unsupported_export_as_xlsx_or_csv')
    if path.suffix.lower() not in {'.csv','.xlsx'}:
        raise ExportError('only_csv_and_xlsx_supported')
    raw=path.read_bytes()
    return path.suffix.lower(),raw,hashlib.sha256(raw).hexdigest()


def _xml(data):
    if b'\x00' in data or b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ExportError('xml_dtd_or_entity_forbidden')
    try:return ET.fromstring(data)
    except ET.ParseError:raise ExportError('malformed_xml') from None


def _xlsx(raw, sheet_name):
    try: z=zipfile.ZipFile(io.BytesIO(raw))
    except (zipfile.BadZipFile, OSError):raise ExportError('invalid_xlsx_archive') from None
    with z:
        infos=z.infolist(); names=[x.filename for x in infos]
        if len(infos)>3000 or len(names)!=len(set(names)) or sum(x.file_size for x in infos)>MAX_EXPANDED:
            raise ExportError('xlsx_archive_limits_or_duplicate_entries')
        for info in infos:
            parts=PurePosixPath(info.filename).parts
            if info.filename.startswith('/') or '..' in parts or info.file_size>MAX_EXPANDED or info.flag_bits & 1:
                raise ExportError('xlsx_unsafe_archive_entry')
        def read(name):
            try:return z.read(name)
            except (KeyError,RuntimeError,zipfile.BadZipFile):raise ExportError('xlsx_required_entry_missing_or_corrupt') from None
        ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            'p':'http://schemas.openxmlformats.org/package/2006/relationships'}
        book=_xml(read('xl/workbook.xml'))
        props=book.find('m:workbookPr',ns)
        date1904=props is not None and props.get('date1904','0').lower() in {'1','true'}
        rels=_xml(read('xl/_rels/workbook.xml.rels'))
        targets={r.get('Id'):r.get('Target') for r in rels.findall('p:Relationship',ns)
                 if r.get('TargetMode')!='External'}
        sheets=[]
        for s in book.findall('m:sheets/m:sheet',ns):
            target=targets.get(s.get('{%s}id'%ns['r']));name=s.get('name')
            if not target or not name:continue
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            target=PurePosixPath(target)
            if '..' in target.parts or not str(target).startswith('xl/worksheets/'):
                raise ExportError('xlsx_unsafe_worksheet_path')
            sheets.append((name,str(target)))
        if sheet_name is None:
            if len(sheets)!=1:raise ExportError('xlsx_sheet_name_required')
            chosen=sheets[0]
        else:
            matches=[s for s in sheets if s[0]==sheet_name]
            if len(matches)!=1:raise ExportError('xlsx_sheet_not_found')
            chosen=matches[0]
        shared=[]
        if 'xl/sharedStrings.xml' in names:
            for node in _xml(read('xl/sharedStrings.xml')).findall('m:si',ns):
                shared.append(''.join(t.text or '' for t in node.iter('{%s}t'%ns['m'])))
        tree=_xml(read(chosen[1])); rows=[]
        for row in tree.findall('m:sheetData/m:row',ns):
            values={}
            for c in row.findall('m:c',ns):
                ref=c.get('r','');match=re.fullmatch(r'([A-Z]{1,3})[1-9][0-9]*',ref)
                if not match:raise ExportError('xlsx_bad_cell_reference')
                col=0
                for char in match.group(1):col=col*26+ord(char)-64
                if col>MAX_COLUMNS or col in values:raise ExportError('xlsx_column_limit_or_duplicate')
                if c.find('m:f',ns) is not None:raise ExportError('xlsx_formula_cells_not_supported')
                typ=c.get('t','n'); v=c.find('m:v',ns)
                text=(v.text or '') if v is not None else ''
                if typ=='s':
                    try:
                        index=int(text)
                        if index<0:raise IndexError()
                        text=shared[index]
                    except (ValueError,IndexError):raise ExportError('xlsx_invalid_shared_string') from None
                elif typ=='inlineStr':text=''.join(t.text or '' for t in c.iter('{%s}t'%ns['m']))
                elif typ not in {'n','str','b','d'}:raise ExportError('xlsx_cell_type_not_supported')
                values[col]=text
            if values:rows.append([values.get(i,'') for i in range(1,max(values)+1)])
            if len(rows)>MAX_ROWS+1:raise ExportError('xlsx_row_limit')
        return rows, chosen[0],date1904


def _csv(raw):
    try:
        text=raw.decode('utf-8-sig')
        rows=list(csv.reader(io.StringIO(text,newline=''),strict=True))
    except (UnicodeDecodeError,csv.Error):raise ExportError('invalid_utf8_csv') from None
    if len(rows)>MAX_ROWS+1 or any(len(r)>MAX_COLUMNS for r in rows):raise ExportError('csv_limits')
    return rows, None,False


def _day(value, date_format):
    if not isinstance(value,str):value=str(value)
    value=value.strip()
    if not value:return None
    if date_format == 'excel1900':
        if not re.fullmatch(r'[0-9]{1,5}',value):raise ExportError('date_does_not_match_declared_format')
        serial=int(value)
        if serial < 1 or serial == 60:raise ExportError('invalid_excel_date_serial')
        return (date(1899,12,31)+timedelta(days=serial-(1 if serial>60 else 0))).isoformat()
    formats={'iso':'%Y-%m-%d','dmy':'%d/%m/%Y','mdy':'%m/%d/%Y'}
    if date_format not in formats:raise ExportError('explicit_date_format_required')
    try:return datetime.strptime(value,formats[date_format]).date().isoformat()
    except ValueError:raise ExportError('date_does_not_match_declared_format') from None


def _url(value):
    if not value:return None
    try:
        p=urlsplit(value.strip());host=(p.hostname or '').lower()
        if p.scheme!='https' or p.username or p.password or not (host=='linkedin.com' or host.endswith('.linkedin.com')):
            raise ValueError()
        if not p.path.strip('/') or any(ord(c)<32 for c in p.path):raise ValueError()
        return 'https://www.linkedin.com'+p.path.rstrip('/')
    except (AttributeError,ValueError):raise ExportError('invalid_linkedin_post_url') from None


def _number(value):
    value=str(value).strip()
    if value.lower() in MISSING:return None
    # Only properly grouped thousands separators; no decimals or compact units.
    if ',' in value or ' ' in value:
        if not re.fullmatch(r'\d{1,3}(?:,\d{3})+|\d{1,3}(?: \d{3})+',value):
            raise ExportError('invalid_nonnegative_count')
        value=value.replace(',','').replace(' ','')
    if not re.fullmatch(r'\d{1,15}',value):raise ExportError('invalid_nonnegative_count')
    return int(value)


def parse_export(path, *, granularity, sheet_name=None, date_format='iso'):
    """Return normalized facts and raw-file hash, never the raw export itself.

    Explicit granularity avoids turning portfolio/date summaries into posts.
    Each supported table has one header row; unknown columns are not retained.
    """
    if granularity not in {'post','daily_aggregate'}:raise ExportError('explicit_granularity_required')
    extension,raw,digest=_read_source(path)
    rows,sheet,date1904=_csv(raw) if extension=='.csv' else _xlsx(raw,sheet_name)
    if date1904 and date_format=='excel1900':raise ExportError('xlsx_1904_dates_not_supported')
    if not rows:raise ExportError('empty_export')
    headers={}
    for index,name in enumerate(rows[0]):
        field=ALIASES.get(_head(name))
        if field:
            if field in headers:raise ExportError('ambiguous_duplicate_header')
            headers[field]=index
    if not (METRICS & headers.keys()):raise ExportError('no_supported_metric_columns')
    if granularity=='post' and not ({'post_id','post_url'} & headers.keys()):raise ExportError('post_identity_column_required')
    if granularity=='daily_aggregate' and 'date' not in headers:raise ExportError('aggregate_date_column_required')
    parsed=[];identities=set()
    for row in rows[1:]:
        if not any(str(x).strip() for x in row):continue
        def get(field):return str(row[headers[field]]).strip() if field in headers and headers[field]<len(row) else ''
        day=_day(get('date'),date_format) if get('date') else None
        url=_url(get('post_url')) if get('post_url') else None
        post_id=get('post_id') or None
        if post_id and (len(post_id)>512 or any(ord(c)<32 for c in post_id)):raise ExportError('invalid_post_id')
        if granularity=='post':
            if not (post_id or url):raise ExportError('post_identity_required_per_row')
            subject='id:'+post_id if post_id else 'url:'+url
        else:
            if not day:raise ExportError('aggregate_date_required_per_row')
            subject='day:'+day
        if subject in identities:raise ExportError('duplicate_identity_in_export')
        identities.add(subject)
        metrics={m:_number(get(m)) if m in headers else None for m in sorted(METRICS)}
        if all(v is None for v in metrics.values()):raise ExportError('row_has_no_observed_metrics')
        parsed.append({'subject_id':subject,'post_id':post_id,'post_url':url,'date':day,'metrics':metrics,
                       'date_precision':'day_only' if day else 'not_exposed'})
    if not parsed:raise ExportError('no_data_rows')
    return {'source_kind':'owner_provided_export','granularity':granularity,'source_sha256':digest,
            'sheet':sheet,'rows':parsed}


class ConsentedStore:
    """A separate, local-only SQLite store; no raw export or LinkedIn credentials."""
    def __init__(self, root):
        root=Path(root).expanduser().absolute()
        if root.is_symlink() or root.resolve()!=root or any((p/'collector.sqlite').exists() or (p/'.git').exists() for p in (root,*root.parents)):
            raise ExportError('separate_private_store_required')
        if root.exists() and (not root.is_dir() or any(p.name not in {'consented-data.sqlite'} for p in root.iterdir())):
            raise ExportError('dedicated_private_store_directory_required')
        root.mkdir(parents=True,exist_ok=True,mode=0o700)
        if root.is_symlink():raise ExportError('separate_private_store_required')
        os.chmod(root,0o700);self.root=root;self.path=root/'consented-data.sqlite'
        if self.path.is_symlink():raise ExportError('store_symlink_forbidden')
        self.db=sqlite3.connect(self.path);os.chmod(self.path,0o600)
        self.db.execute('PRAGMA foreign_keys=ON');self.db.execute('PRAGMA secure_delete=ON')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS consent (account_hash TEXT PRIMARY KEY, consent_ref_hash TEXT NOT NULL,
            purpose TEXT NOT NULL, expires_at TEXT NOT NULL, retention_days INTEGER NOT NULL, status TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS snapshots (id TEXT PRIMARY KEY, account_hash TEXT NOT NULL REFERENCES consent(account_hash),
            subject_id TEXT NOT NULL, granularity TEXT NOT NULL, observed_at TEXT NOT NULL, expires_at TEXT NOT NULL,
            payload TEXT NOT NULL, source_sha256 TEXT NOT NULL, UNIQUE(account_hash,granularity,subject_id,observed_at));
          CREATE TABLE IF NOT EXISTS aliases (account_hash TEXT NOT NULL REFERENCES consent(account_hash),
            alias TEXT NOT NULL, subject_id TEXT NOT NULL, PRIMARY KEY(account_hash,alias));
          CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, action TEXT NOT NULL,
            account_hash TEXT, row_count INTEGER NOT NULL);
        ''')
    def close(self):self.db.close()
    def _audit(self,now,action,key,count):
        self.db.execute('INSERT INTO audit(timestamp,action,account_hash,row_count) VALUES (?,?,?,?)',
                        (now.isoformat(),action,key,count))
    def grant(self,account_id,*,consent_reference,purpose,expires_at,retention_days=30,now=None):
        now=_utc(now or datetime.now(timezone.utc));expires_at=_utc(expires_at)
        if not isinstance(consent_reference,str) or not 1<=len(consent_reference.strip())<=512:
            raise ExportError('explicit_consent_reference_required')
        if purpose not in {'owned_account_analytics','consented_account_analytics'}:
            raise ExportError('explicit_allowed_purpose_required')
        if type(retention_days) is not int or not 1<=retention_days<=365 or expires_at<=now:
            raise ExportError('invalid_consent_expiry_or_retention')
        key=_key(account_id);ref=hashlib.sha256(consent_reference.strip().encode()).hexdigest()
        with self.db:
            existing=self.db.execute('SELECT status FROM consent WHERE account_hash=?',(key,)).fetchone()
            if existing:raise ExportError('existing_or_revoked_consent_cannot_be_overwritten')
            self.db.execute('INSERT INTO consent VALUES (?,?,?,?,?,?)',(key,ref,purpose,expires_at.isoformat(),retention_days,'active'))
            self._audit(now,'consent_recorded',key,0)
        return {'status':'consent_recorded','account_hash':key,'expires_at':expires_at.isoformat()}
    def import_file(self,account_id,path,*,observed_at,granularity,sheet_name=None,date_format='iso',now=None,source_kind='owner_provided_export'):
        now=_utc(now or datetime.now(timezone.utc));observed_at=_utc(observed_at)
        if source_kind!='owner_provided_export':raise ExportError('api_ingestion_not_enabled')
        if observed_at>now:raise ExportError('future_observation_not_allowed')
        key=_key(account_id);self.purge_expired(now=now)
        consent=self.db.execute('SELECT expires_at,retention_days,status FROM consent WHERE account_hash=?',(key,)).fetchone()
        if not consent or consent[2]!='active' or datetime.fromisoformat(consent[0])<=now:
            raise ExportError('active_consent_required')
        parsed=parse_export(path,granularity=granularity,sheet_name=sheet_name,date_format=date_format)
        if any(row['date'] and date.fromisoformat(row['date'])>now.date() for row in parsed['rows']):
            raise ExportError('future_publication_or_aggregate_date')
        expiry=min(datetime.fromisoformat(consent[0]),now+timedelta(days=consent[1]))
        inserted=duplicates=0
        with self.db:
            for row in parsed['rows']:
                if granularity=='post':
                    aliases=([('id:'+row['post_id'])] if row['post_id'] else [])+([('url:'+row['post_url'])] if row['post_url'] else [])
                    subjects={found[0] for alias in aliases for found in self.db.execute('SELECT subject_id FROM aliases WHERE account_hash=? AND alias=?',(key,alias))}
                    if len(subjects)>1:raise ExportError('conflicting_post_aliases')
                    row['subject_id']=next(iter(subjects)) if subjects else row['subject_id']
                    for alias in aliases:
                        self.db.execute('INSERT OR IGNORE INTO aliases VALUES (?,?,?)',(key,alias,row['subject_id']))
                payload=json.dumps(row,sort_keys=True,separators=(',',':'))
                sid=hashlib.sha256((key+'|'+granularity+'|'+row['subject_id']+'|'+observed_at.isoformat()).encode()).hexdigest()
                prior=self.db.execute('SELECT payload FROM snapshots WHERE id=?',(sid,)).fetchone()
                if prior:
                    earlier=json.loads(prior[0])
                    if any(earlier[k]!=row[k] for k in ('metrics','date','date_precision')):raise ExportError('conflicting_same_observation')
                    duplicates+=1;continue
                self.db.execute('INSERT INTO snapshots VALUES (?,?,?,?,?,?,?,?)',
                    (sid,key,row['subject_id'],granularity,observed_at.isoformat(),expiry.isoformat(),payload,parsed['source_sha256']))
                inserted+=1
            self._audit(now,'owner_export_imported',key,inserted)
        return {'status':'imported','granularity':granularity,'inserted':inserted,'duplicates':duplicates,
                'source_sha256':parsed['source_sha256'],'expires_at':expiry.isoformat()}
    def get_snapshots(self,account_id,*,now=None):
        now=_utc(now or datetime.now(timezone.utc));self.purge_expired(now=now);key=_key(account_id)
        consent=self.db.execute('SELECT expires_at,status FROM consent WHERE account_hash=?',(key,)).fetchone()
        if not consent or consent[1]!='active' or datetime.fromisoformat(consent[0])<=now:raise ExportError('active_consent_required')
        return [{'granularity':g,'observed_at':at,'expires_at':ex,'source_sha256':h,**json.loads(p)}
                for g,at,ex,h,p in self.db.execute('SELECT granularity,observed_at,expires_at,source_sha256,payload FROM snapshots WHERE account_hash=? ORDER BY observed_at,id',(key,))]
    def purge_expired(self,*,now=None):
        now=_utc(now or datetime.now(timezone.utc))
        with self.db:
            count=self.db.execute('SELECT count(*) FROM snapshots WHERE expires_at<=?',(now.isoformat(),)).fetchone()[0]
            self.db.execute('DELETE FROM snapshots WHERE expires_at<=?',(now.isoformat(),))
            self.db.execute("UPDATE consent SET status='expired' WHERE status='active' AND expires_at<=?",(now.isoformat(),))
            self.db.execute("DELETE FROM aliases WHERE NOT EXISTS (SELECT 1 FROM snapshots WHERE snapshots.account_hash=aliases.account_hash AND snapshots.subject_id=aliases.subject_id AND snapshots.granularity='post')")
            if count:self._audit(now,'expired_data_deleted',None,count)
        return {'expired_rows_deleted':count}
    def revoke(self,account_id,*,now=None):
        now=_utc(now or datetime.now(timezone.utc));key=_key(account_id)
        with self.db:
            if not self.db.execute('SELECT 1 FROM consent WHERE account_hash=?',(key,)).fetchone():raise ExportError('consent_not_found')
            count=self.db.execute('SELECT count(*) FROM snapshots WHERE account_hash=?',(key,)).fetchone()[0]
            self.db.execute('DELETE FROM snapshots WHERE account_hash=?',(key,))
            self.db.execute('DELETE FROM aliases WHERE account_hash=?',(key,))
            self.db.execute("UPDATE consent SET status='revoked' WHERE account_hash=?",(key,))
            self._audit(now,'consent_revoked_and_rows_deleted',key,count)
        return {'status':'revoked','rows_deleted':count,'source_file_deleted':False,'external_backups_deleted':False}
