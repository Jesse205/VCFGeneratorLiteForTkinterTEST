// 探测 / 设置 macOS 主显示器的 HiDPI 模式：无参数打印当前与可用 HiDPI 模式，`set` 选择 2x 模式。
import CoreGraphics
import Foundation

let main = CGMainDisplayID()
if let mode = CGDisplayCopyDisplayMode(main) {
    print("current: points=\(mode.width)x\(mode.height) pixels=\(mode.pixelWidth)x\(mode.pixelHeight)")
}
let options = [kCGDisplayShowDuplicateLowResolutionModesOptionKey: true] as CFDictionary
let modes = (CGDisplayCopyAllDisplayModes(main, options) as? [CGDisplayMode]) ?? []
let hidpi = modes.filter { $0.pixelWidth > $0.width }
for mode in hidpi {
    print("hidpi: points=\(mode.width)x\(mode.height) pixels=\(mode.pixelWidth)x\(mode.pixelHeight)")
}
if CommandLine.arguments.count > 1 && CommandLine.arguments[1] == "set" {
    guard let target = hidpi.first(where: { $0.pixelWidth == $0.width * 2 && $0.width >= 1280 }) else {
        print("no usable 2x mode")
        exit(1)
    }
    var config: CGDisplayConfigRef?
    guard CGBeginDisplayConfiguration(&config) == .success else { exit(1) }
    guard CGConfigureDisplayWithDisplayMode(config, main, target, nil) == .success else { exit(1) }
    guard CGCompleteDisplayConfiguration(config, .permanently) == .success else { exit(1) }
    print("set: points=\(target.width)x\(target.height) pixels=\(target.pixelWidth)x\(target.pixelHeight)")
}