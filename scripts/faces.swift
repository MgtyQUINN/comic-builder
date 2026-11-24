// Finner ansikter og personer i bilder med Apple Vision. Skriver JSON til stdout.
// Bruk: ansikter bilde1.jpg bilde2.png ...
// Koordinater er brøker (0–1) med origo øverst til venstre: [x, y, b, h].
import Foundation
import Vision
import AppKit

func boks(_ r: CGRect) -> [Double] {
    return [Double(r.minX), Double(1 - r.maxY), Double(r.width), Double(r.height)].map { ($0 * 10000).rounded() / 10000 }
}
var ut: [String: Any] = [:]
for sti in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: sti),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let fr = VNDetectFaceRectanglesRequest()
    let mr = VNDetectHumanRectanglesRequest()
    mr.upperBodyOnly = false
    let h = VNImageRequestHandler(cgImage: cg, options: [:])
    try? h.perform([fr, mr])
    let ans = (fr.results ?? []).filter { $0.confidence > 0.5 }.map { boks($0.boundingBox) }
    let men = (mr.results ?? []).filter { $0.confidence > 0.3 }.map { boks($0.boundingBox) }
    ut[sti] = ["b": cg.width, "h": cg.height, "ansikter": ans, "personer": men]
}
let d = try! JSONSerialization.data(withJSONObject: ut, options: [.sortedKeys])
FileHandle.standardOutput.write(d)
