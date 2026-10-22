import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {motionAliases} from '../scripts/motion-aliases';
const site=path.dirname(fileURLToPath(import.meta.url));
export default defineConfig({resolve:{alias:motionAliases},root:site,publicDir:path.resolve(site,'../../assets/public'),appType:'spa',server:{host:'127.0.0.1',port:6046,strictPort:true},build:{outDir:path.resolve(site,'../dist'),emptyOutDir:true,sourcemap:false}});
