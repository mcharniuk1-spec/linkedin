import Foundation
import AppKit
import CoreText
let fm=FileManager.default
let r=URL(fileURLWithPath:CommandLine.arguments[1]).standardizedFileURL
let p=r
for n in ["YoungSerif-Regular.ttf","mona-sans-latin-wght-normal.woff2"] {
 var e:Unmanaged<CFError>?
 guard CTFontManagerRegisterFontsForURL(p.appendingPathComponent("assets/fonts/"+n) as CFURL,.process,&e) else {fatalError("Font registration failed")}
}
let jobs=try JSONSerialization.jsonObject(with:Data(contentsOf:r.appendingPathComponent("render-jobs.json"))) as! [[String:String]]
guard jobs.count==10 else {fatalError("Expected10")}
var records:[[String:Any]]=[]
let contact=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1080,pixelsHigh:1800,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
let contactContext=NSGraphicsContext(bitmapImageRep:contact)!
for (i,j) in jobs.enumerated() {
 let bytes=try Data(contentsOf:p.appendingPathComponent(j["svg"]!))
 guard let image=NSImage(data:bytes) else {fatalError("SVG decode")}
 image.size=NSSize(width:1080,height:1350)
 let rep=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1080,pixelsHigh:1350,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
 let context=NSGraphicsContext(bitmapImageRep:rep)!
 NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=context
 image.draw(in:NSRect(x:0,y:0,width:1080,height:1350),from:.zero,operation:.copy,fraction:1)
 context.flushGraphics();NSGraphicsContext.restoreGraphicsState()
 try rep.representation(using:.png,properties:[:])!.write(to:p.appendingPathComponent(j["png"]!))
 NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=contactContext
 image.draw(in:NSRect(x:(i%3)*360,y:1800-(i/3+1)*450,width:360,height:450),from:.zero,operation:.copy,fraction:1)
 contactContext.flushGraphics();NSGraphicsContext.restoreGraphicsState()
 records.append(["id":j["id"]!,"rendered":true,"width":1080,"height":1350])
}
try contact.representation(using:.png,properties:[:])!.write(to:r.appendingPathComponent("contact.png"))
try JSONSerialization.data(withJSONObject:["renderer":"macOS AppKit/CoreText","records":records],options:[.prettyPrinted,.sortedKeys]).write(to:r.appendingPathComponent("render-checks.json"))
print("Rendered10publicationPNGs and contact sheet")
