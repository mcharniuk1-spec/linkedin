import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'release-manifest.json'),'utf8'));
const files=manifest.files;
const seen=new Set();
for(const item of files){
 if(seen.has(item.path)||path.isAbsolute(item.path)||item.path.split('/').includes('..'))throw Error('Invalid or duplicate manifest path '+item.path);
 seen.add(item.path);const b=fs.readFileSync(path.join(root,item.path));
 if(b.length!==item.bytes||crypto.createHash('sha256').update(b).digest('hex')!==item.sha256)throw Error('Hash or length differs '+item.path);
}
for(const item of manifest.rights_ledger){
 const f=files.find(x=>x.path===item.path);
 if(!f||f.sha256!==item.sha256||!['owned','licensed','permission_verified'].includes(item.rights_state))throw Error('Invalid asset rights '+item.path);
}
console.log(JSON.stringify({status:'PASS',files:files.length,rights:manifest.rights_ledger.length,owner_accepted:manifest.owner_accepted}));
