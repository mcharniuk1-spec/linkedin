import Foundation
import AppKit
import CoreText
let root=URL(fileURLWithPath:CommandLine.arguments[1]).standardizedFileURL
let qa=CommandLine.arguments.count>2 ? URL(fileURLWithPath:CommandLine.arguments[2]) : root
for n in ["fraunces-latin-full-normal.woff2","mona-sans-latin-wght-normal.woff2","geist-mono-latin-wght-normal.woff2"] {
 var e:Unmanaged<CFError>?
 guard CTFontManagerRegisterFontsForURL(root.appendingPathComponent("assets/fonts/"+n) as CFURL,.process,&e) else {fatalError("Font registration failed: \(n)")}
}
final class TextAudit:NSObject,XMLParserDelegate {
 var attrs:[String:String]?;var text="";var failures:[[String:Any]]=[];var count=0;var resolved:Set<String>=[];var runs:[([String:String],String)]=[]
 func parser(_ p:XMLParser,didStartElement name:String,namespaceURI:String?,qualifiedName:String?,attributes a:[String:String]){if name=="text"{attrs=a;text=""}}
 func parser(_ p:XMLParser,foundCharacters s:String){if attrs != nil{text+=s}}
 func parser(_ p:XMLParser,didEndElement name:String,namespaceURI:String?,qualifiedName:String?){
  if name=="text",let a=attrs,let family=a["data-postscript"],let size=Double(a["font-size"] ?? ""),let x=Double(a["x"] ?? ""),let y=Double(a["y"] ?? ""){
   let font=CTFontCreateWithName(family as CFString,size,nil);let actual=CTFontCopyPostScriptName(font) as String;resolved.insert(actual)
   let kern=Double(a["letter-spacing"] ?? "0") ?? 0
   let at=CFAttributedStringCreate(nil,text as CFString,[kCTFontAttributeName:font,kCTKernAttributeName:kern] as CFDictionary)!
   let line=CTLineCreateWithAttributedString(at);let width=CTLineGetTypographicBounds(line,nil,nil,nil)
   if actual != family || x<40 || x+width>1040 || y>1320 || y-CTFontGetAscent(font)<35{failures.append(["text":text,"x":x,"y":y,"width":width,"requested":family,"resolved":actual])}
   runs.append((a,text));count+=1;attrs=nil
  }
 }
}
let jobs=try JSONSerialization.jsonObject(with:Data(contentsOf:root.appendingPathComponent("render-jobs.json"))) as! [[String:Any]]
guard jobs.count==19 else{fatalError("Expected19graphics")}
let sheet=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1728,pixelsHigh:2700,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
let sheetContext=NSGraphicsContext(bitmapImageRep:sheet)!
let pdf=NSMutableData();var media=CGRect(x:0,y:0,width:1080,height:1350)
let consumer=CGDataConsumer(data:pdf as CFMutableData)!;let pdfContext=CGContext(consumer:consumer,mediaBox:&media,nil)!
var rows:[[String:Any]]=[];var errors:[[String:Any]]=[];var faces:Set<String>=[];var texts=0
for (i,j) in jobs.enumerated(){
 var xml=try String(contentsOf:root.appendingPathComponent(j["svg"] as! String),encoding:.utf8)
 let audit=TextAudit();let parser=XMLParser(data:Data(xml.utf8));parser.delegate=audit;guard parser.parse() else{fatalError("SVG XML")}
 errors += audit.failures.map{var x=$0;x["file"]=j["svg"];return x};faces.formUnion(audit.resolved);texts += audit.count
 if xml.contains("href=\"selection-context.png\""){let b=try Data(contentsOf:root.appendingPathComponent("assets/selection-context.png"));xml=xml.replacingOccurrences(of:"href=\"selection-context.png\"",with:"href=\"data:image/png;base64,"+b.base64EncodedString()+"\"")}
 xml=xml.replacingOccurrences(of:"<text[^>]*>.*?</text>",with:"",options:.regularExpression)
 guard let img=NSImage(data:Data(xml.utf8)) else{fatalError("SVG rendering")};img.size=NSSize(width:1080,height:1350)
 let rep=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1080,pixelsHigh:1350,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
 let ctx=NSGraphicsContext(bitmapImageRep:rep)!;NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=ctx;img.draw(in:NSRect(x:0,y:0,width:1080,height:1350),from:.zero,operation:.copy,fraction:1);let cg=ctx.cgContext;cg.textMatrix = .identity
 for (a,text) in audit.runs {
  let font=CTFontCreateWithName(a["data-postscript"]! as CFString,Double(a["font-size"]!)!,nil)
  let hex=a["fill"]!.replacingOccurrences(of:"#",with:"");let v=UInt64(hex,radix:16)!
  let colour=CGColor(red:CGFloat((v>>16)&255)/255,green:CGFloat((v>>8)&255)/255,blue:CGFloat(v&255)/255,alpha:1)
  let kern=Double(a["letter-spacing"] ?? "0") ?? 0
  let at=CFAttributedStringCreate(nil,text as CFString,[kCTFontAttributeName:font,kCTForegroundColorAttributeName:colour,kCTKernAttributeName:kern] as CFDictionary)!
  cg.textPosition=CGPoint(x:Double(a["x"]!)!,y:1350-Double(a["y"]!)!);CTLineDraw(CTLineCreateWithAttributedString(at),cg)
 }
 ctx.flushGraphics();NSGraphicsContext.restoreGraphicsState()
 try rep.representation(using:.png,properties:[:])!.write(to:root.appendingPathComponent(j["png"] as! String))
 if i<4{pdfContext.beginPDFPage(nil);pdfContext.draw(rep.cgImage!,in:media);pdfContext.endPDFPage()}
 NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=sheetContext;NSImage(cgImage:rep.cgImage!,size:NSSize(width:1080,height:1350)).draw(in:NSRect(x:(i%4)*432,y:2700-(i/4+1)*540,width:432,height:540),from:.zero,operation:.copy,fraction:1);sheetContext.flushGraphics();NSGraphicsContext.restoreGraphicsState()
 rows.append(["id":j["id"]!,"page":j["page"]!,"width":1080,"height":1350])
}
pdfContext.closePDF();try (pdf as Data).write(to:root.appendingPathComponent("assets/01-the-flow.pdf"))
try sheet.representation(using:.png,properties:[:])!.write(to:qa.appendingPathComponent("contact.png"))
let out:[String:Any]=["status":errors.isEmpty ? "PASS":"FAIL","renderer":"CoreText glyph drawing over native SVG geometry with embedded exact browser fonts","graphics":rows,"first_carousel_pages":4,"text_runs_checked":texts,"font_faces":faces.sorted(),"text_width_or_font_failures":errors]
try JSONSerialization.data(withJSONObject:out,options:[.prettyPrinted,.sortedKeys]).write(to:root.appendingPathComponent("render-checks.json"))
print("Rendered19graphics,4PDFpages,\(texts)text runs,\(errors.count)font/bounds failures")
if !errors.isEmpty{for x in errors{print(x)};exit(1)}
