// Usage: swift pdf_to_png.swift <pdf> <out folder> [longest side in px, default 1600]
// Writes page001.png, page002.png … (first PDF page = page001)
import PDFKit; import AppKit
let a = CommandLine.arguments
let maks = a.count > 3 ? CGFloat(Double(a[3]) ?? 1600) : 1600
guard let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else { print("cannot open PDF"); exit(1) }
print("pages:", doc.pageCount)
for i in 0..<doc.pageCount {
  let p = doc.page(at: i)!
  let img = p.thumbnail(of: NSSize(width: maks, height: maks), for: .mediaBox)
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  let navn = String(format: "%@/page%03d.png", a[2], i + 1)
  try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: navn))
}
