import Foundation
import AppKit
import CoreText

struct Job: Codable { let id: String; let variant: String; let page: Int; let svg: String; let png: String }
let fm=FileManager.default
let root=URL(fileURLWithPath: CommandLine.arguments.dropFirst().first(where: {$0.hasPrefix("--root=")}).map{String($0.dropFirst(7))} ?? fm.currentDirectoryPath).standardizedFileURL
let defaultAssets=root.appendingPathComponent("../20261105-evidence-v1/assets").standardizedFileURL
let assetRoot=URL(fileURLWithPath: ProcessInfo.processInfo.environment["ASSET_ROOT"] ?? defaultAssets.path).standardizedFileURL
let review=URL(fileURLWithPath:ProcessInfo.processInfo.environment["PUBLICATION_REVIEW"] ?? root.appendingPathComponent("generated-review").path)
for url in [root.appendingPathComponent("fonts/YoungSerif-Regular.ttf"), root.appendingPathComponent("fonts/mona-sans-latin-wght-normal.woff2")] {
 var error: Unmanaged<CFError>?
 guard CTFontManagerRegisterFontsForURL(url as CFURL,.process,&error) else {fputs("Font registration failed: \(url.path) \(String(describing:error))\n",stderr);exit(1)}
}
let jobs=try JSONDecoder().decode([Job].self,from:Data(contentsOf:review.appendingPathComponent("render-jobs.json")))
guard jobs.count==25 else { fputs("Expected 25 render jobs\n",stderr);exit(1) }
let limitArg=CommandLine.arguments.first(where:{$0.hasPrefix("--limit=")})
let limit=limitArg.flatMap{Int($0.dropFirst(8))} ?? jobs.count
guard limit>0 && limit<=jobs.count else {fputs("Invalid render limit\n",stderr);exit(1)}
let expression=try NSRegularExpression(pattern:"(?:xlink:)?href=\"([^\"]+)\"")
var results:[[String:Any]]=[]
for job in jobs.prefix(limit) {
    let source=root.appendingPathComponent(job.svg).standardizedFileURL
    var svg=try String(contentsOf:source,encoding:.utf8)
    let matches=expression.matches(in:svg,range:NSRange(svg.startIndex...,in:svg))
    for match in matches.reversed() {
        guard let valueRange=Range(match.range(at:1),in:svg) else {continue}
        let value=String(svg[valueRange]);if value.hasPrefix("#") || value.hasPrefix("data:") {continue}
        guard !value.contains("://") else {fputs("Remote SVG resource is not allowed\n",stderr);exit(1)}
        let file=source.deletingLastPathComponent().appendingPathComponent(value).standardizedFileURL
        let target:URL
        if file.path.hasPrefix(defaultAssets.path+"/") {
            target=assetRoot.appendingPathComponent(String(file.path.dropFirst(defaultAssets.path.count+1)))
        } else {fputs("SVG resource escaped the shared asset root\n",stderr);exit(1)}
        guard target.standardizedFileURL.path.hasPrefix(assetRoot.path+"/") && target.pathExtension.lowercased()=="png" else {fputs("Unsupported SVG resource\n",stderr);exit(1)}
        let data=try Data(contentsOf:target)
        svg.replaceSubrange(valueRange,with:"data:image/png;base64,"+data.base64EncodedString())
    }
    guard let svgData=svg.data(using:.utf8),let image=NSImage(data:svgData) else {fputs("Cannot load SVG: \(job.id)\n",stderr);exit(1)}
    image.size=NSSize(width:1080,height:1350)
    guard let rep=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1080,pixelsHigh:1350,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0),let context=NSGraphicsContext(bitmapImageRep:rep) else {exit(1)}
    NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=context
    image.draw(in:NSRect(x:0,y:0,width:1080,height:1350),from:.zero,operation:.copy,fraction:1)
    context.flushGraphics();NSGraphicsContext.restoreGraphicsState()
    guard let png=rep.representation(using:.png,properties:[:]) else {exit(1)}
    let destination=root.appendingPathComponent(job.png)
    try fm.createDirectory(at:destination.deletingLastPathComponent(),withIntermediateDirectories:true)
    try png.write(to:destination)
    results.append(["id":job.id,"variant":job.variant,"page":job.page,"png":job.png,"width":rep.pixelsWide,"height":rep.pixelsHigh,"external_images_resolved":matches.count])
}
let result:[String:Any]=["status":"PASS","rendered":results.count,"expected_total":jobs.count,"partial":limit<jobs.count,"renderer":"macOS AppKit/CoreText","images":results]
try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]).write(to:review.appendingPathComponent("native-render-result.json"))
print("Rendered \(results.count) PNGs at 1080 × 1350; shared PNG bytes resolved only in memory")
