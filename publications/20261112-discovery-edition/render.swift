import Foundation
import AppKit
import CoreText
let r=URL(fileURLWithPath:CommandLine.arguments[1]).standardizedFileURL
let p=r
for n in ["YoungSerif-Regular.ttf","mona-sans-latin-wght-normal.woff2"] {
 var e:Unmanaged<CFError>?
 guard CTFontManagerRegisterFontsForURL(p.appendingPathComponent("assets/fonts/"+n) as CFURL,.process,&e) else {fatalError("Font registration")}
}
let jobs=try JSONSerialization.jsonObject(with:Data(contentsOf:r.appendingPathComponent("render-jobs.json"))) as! [[String:Any]]
guard jobs.count==19 else {fatalError("Expected19")}
let sheet=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1440,pixelsHigh:2250,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
let sheetContext=NSGraphicsContext(bitmapImageRep:sheet)!
let pdf=NSMutableData();var mediaBox=CGRect(x:0,y:0,width:1080,height:1350)
let consumer=CGDataConsumer(data:pdf as CFMutableData)!
let pdfContext=CGContext(consumer:consumer,mediaBox:&mediaBox,nil)!
var results:[[String:Any]]=[]
for (i,j) in jobs.enumerated(){
 let data=try Data(contentsOf:p.appendingPathComponent(j["svg"] as! String));guard let image=NSImage(data:data) else {fatalError("SVG")};image.size=NSSize(width:1080,height:1350)
 let rep=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1080,pixelsHigh:1350,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
 let context=NSGraphicsContext(bitmapImageRep:rep)!
 NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=context
 image.draw(in:NSRect(x:0,y:0,width:1080,height:1350),from:.zero,operation:.copy,fraction:1);context.flushGraphics();NSGraphicsContext.restoreGraphicsState()
 try rep.representation(using:.png,properties:[:])!.write(to:p.appendingPathComponent(j["png"] as! String))
 if i<4{pdfContext.beginPDFPage(nil);pdfContext.draw(rep.cgImage!,in:mediaBox);pdfContext.endPDFPage()}
 NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=sheetContext
 image.draw(in:NSRect(x:(i%4)*360,y:2250-(i/4+1)*450,width:360,height:450),from:.zero,operation:.copy,fraction:1);sheetContext.flushGraphics();NSGraphicsContext.restoreGraphicsState()
 results.append(["id":j["id"]!,"page":j["page"]!,"width":1080,"height":1350])
}
pdfContext.closePDF();try (pdf as Data).write(to:p.appendingPathComponent("assets/01-the-flow.pdf"))
try sheet.representation(using:.png,properties:[:])!.write(to:r.appendingPathComponent("contact.png"))
try JSONSerialization.data(withJSONObject:["status":"PASS","renderer":"macOS AppKit/CoreText","pngs":results,"first_carousel_pages":4],options:[.prettyPrinted,.sortedKeys]).write(to:r.appendingPathComponent("render-checks.json"))
print("Rendered19PNGs and4pagePDF")
