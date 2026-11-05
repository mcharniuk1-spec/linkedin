import Foundation
import AppKit
import CoreText

struct Job: Codable { let id: String; let variant: String; let svg: String; let png: String }
let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let fontRoot = root.appendingPathComponent("output/source-fonts")
for name in ["fraunces-latin-full-normal.woff2", "mona-sans-latin-wght-normal.woff2", "geist-mono-latin-wght-normal.woff2"] {
    var error: Unmanaged<CFError>?
    guard CTFontManagerRegisterFontsForURL(fontRoot.appendingPathComponent(name) as CFURL, .process, &error) else {
        fputs("Font registration failed: \(name)\n", stderr); exit(1)
    }
}
let data = try Data(contentsOf: root.appendingPathComponent("verification/render-jobs.json"))
let jobs = try JSONDecoder().decode([Job].self, from: data)
guard jobs.count == 60 else { fputs("Expected 60 render jobs\n", stderr); exit(1) }
for job in jobs {
    guard let image = NSImage(contentsOfFile: job.svg), let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff), rep.pixelsWide == 1080, rep.pixelsHigh == 1350,
          let png = rep.representation(using: .png, properties: [:]) else {
        fputs("Cannot render SVG or incorrect output dimensions: \(job.id) \(job.variant)\n", stderr); exit(1)
    }
    try png.write(to: URL(fileURLWithPath: job.png))
}
print("Rendered \(jobs.count) PNGs at 1080 × 1350")
