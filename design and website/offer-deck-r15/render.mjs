// Needs Playwright with Chromium installed (npm i playwright; npx playwright install chromium).
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { mkdir } from 'node:fs/promises';
const folder=process.argv[2];const out=process.argv[3]||folder;await mkdir(out+'/slides',{recursive:true});
const browser=await chromium.launch({headless:true,channel:'chrome',chromiumSandbox:true});
const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
await page.goto(pathToFileURL(folder+'/index.html').href,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
const slides=page.locator('.slide');const count=await slides.count();if(count!==11)throw Error('Expected 11 slides');
for(let i=0;i<count;i++)await slides.nth(i).screenshot({path:out+'/slides/'+String(i+1).padStart(2,'0')+'.png',animations:'disabled'});
await page.pdf({path:out+'/offer-deck.pdf',printBackground:true,width:'1920px',height:'1080px',preferCSSPageSize:true});console.log(JSON.stringify({slides:count,fonts:await page.evaluate(()=>({fraunces:document.fonts.check('400 16px Fraunces'),mona:document.fonts.check('400 16px "Mona Sans"')}))}));await browser.close();
