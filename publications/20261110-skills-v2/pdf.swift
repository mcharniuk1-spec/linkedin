import Foundation
import AppKit
import PDFKit

struct Job:Codable {let id:String;let variant:String;let images:[String];let pdf:String}
let fm=FileManager.default
let root=URL(fileURLWithPath:CommandLine.arguments.dropFirst().first(where:{$0.hasPrefix("--root=")}).map{String($0.dropFirst(7))} ?? fm.currentDirectoryPath)
let review=root.appendingPathComponent(ProcessInfo.processInfo.environment["PUBLICATION_REVIEW"] ?? "generated-review")
let jobs=try JSONDecoder().decode([Job].self,from:Data(contentsOf:review.appendingPathComponent("pdf-jobs.json")))
guard jobs.count==10 else {fputs("Expected 10 PDF jobs\n",stderr);exit(1)}
let limitArg=CommandLine.arguments.first(where:{$0.hasPrefix("--limit=")})
let limit=limitArg.flatMap{Int($0.dropFirst(8))} ?? jobs.count
guard limit>0 && limit<=jobs.count else {fputs("Invalid PDF limit\n",stderr);exit(1)}
var results:[[String:Any]]=[]
for job in jobs.prefix(limit) {
    guard job.images.count==5 else {exit(1)}
    let document=PDFDocument()
    for (index,name) in job.images.enumerated() {
        guard let image=NSImage(contentsOf:root.appendingPathComponent(name)),let page=PDFPage(image:image) else {fputs("Missing PNG for PDF: \(name)\n",stderr);exit(1)}
        page.setBounds(CGRect(x:0,y:0,width:1080,height:1350),for:.mediaBox)
        document.insert(page,at:index)
    }
    let destination=root.appendingPathComponent(job.pdf)
    guard document.write(to:destination),let readback=PDFDocument(url:destination),readback.pageCount==5 else {fputs("PDF readback failed\n",stderr);exit(1)}
    results.append(["id":job.id,"variant":job.variant,"path":job.pdf,"pages":5])
}
let result:[String:Any]=["status":"PASS","documents":results.count,"expected_total":jobs.count,"partial":limit<jobs.count,"results":results]
try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]).write(to:review.appendingPathComponent("native-pdf-result.json"))
print("Built and read back \(results.count) five-page PDFs")
