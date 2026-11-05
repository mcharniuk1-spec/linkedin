import Foundation
import AppKit
import PDFKit

struct Job: Codable { let id: String; let variant: String; let images: [String]; let pdf: String }
let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let data = try Data(contentsOf: root.appendingPathComponent("verification/pdf-jobs.json"))
let jobs = try JSONDecoder().decode([Job].self, from: data)
guard jobs.count == 10 else { fputs("Expected 10 PDF jobs\n", stderr); exit(1) }
for job in jobs {
    guard job.images.count == 5 else { fputs("Expected five carousel slides\n", stderr); exit(1) }
    let document = PDFDocument()
    for (index, path) in job.images.enumerated() {
        guard let image = NSImage(contentsOfFile: path), let page = PDFPage(image: image) else {
            fputs("Cannot make PDF page for \(job.id) \(job.variant)\n", stderr); exit(1)
        }
        document.insert(page, at: index)
    }
    guard document.pageCount == 5 && document.write(to: URL(fileURLWithPath: job.pdf)) else {
        fputs("Cannot write PDF for \(job.id)\n", stderr); exit(1)
    }
}
print("Built \(jobs.count) five-page PDFs")
