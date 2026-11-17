// 探测 / 设置 macOS 主显示器的 HiDPI 模式：无参数打印当前与可用 HiDPI 模式，`set` 选择 2x 模式。
import CoreGraphics
import Foundation

let main = CGMainDisplayID()
if let mode = CGDisplayCopyDisplayMode(main) {
    print("current: points=\(mode.width)x\(mode.height) pixels=\(mode.pixelWidth)x\(mode.pixelHeight)")
}
let modes = (CGDisplayCopyAllDisplayModes(main, nil) as? [CGDisplayMode]) ?? []
// Swift 未 bridging 该 CFString 常量，直接用键名字符串；部分虚拟显示器仅在此选项下暴露 HiDPI 模式。
let options = ["kCGDisplayShowDuplicateLowResolutionModesOptionKey": true] as CFDictionary
let modesWithOptions = (CGDisplayCopyAllDisplayModes(main, options) as? [CGDisplayMode]) ?? []
print("mode counts: nil=\(modes.count) withOption=\(modesWithOptions.count)")
var hidpi: [CGDisplayMode] = []
for mode in modes + modesWithOptions where mode.pixelWidth > mode.width {
    hidpi.append(mode)
    print("hidpi: points=\(mode.width)x\(mode.height) pixels=\(mode.pixelWidth)x\(mode.pixelHeight)")
}
if CommandLine.arguments.count > 1 && CommandLine.arguments[1] == "set" {
    var target: CGDisplayMode? = nil
    for mode in hidpi {
        let is2x: Bool = mode.pixelWidth == mode.width * 2
        let wideEnough: Bool = mode.width >= 1280
        if is2x && wideEnough {
            target = mode
            break
        }
    }
    guard let chosen = target else {
        print("no usable 2x mode")
        exit(1)
    }
    var config: CGDisplayConfigRef?
    guard CGBeginDisplayConfiguration(&config) == .success else { exit(1) }
    guard CGConfigureDisplayWithDisplayMode(config, main, chosen, nil) == .success else { exit(1) }
    guard CGCompleteDisplayConfiguration(config, .permanently) == .success else { exit(1) }
    print("set: points=\(chosen.width)x\(chosen.height) pixels=\(chosen.pixelWidth)x\(chosen.pixelHeight)")
}