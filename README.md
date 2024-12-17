<div align="center">
<img src="./vcf_generator/assets/images/icon.png" width="192"/>

# VCF Generator Lite

[![Gitee repository](https://img.shields.io/badge/Gitee-repository-C71D23?logo=gitee)](https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter)

[![Windows](https://img.shields.io/badge/Windows-exe-%232863C5?logo=windows)][ReleaseInGitee]

[中文](./README.zh.md) |
**English** |
<small>More translations are welcome!</small>

_The application currently only supports Chinese language_

</div>

VCF generator, input name and phone number to automatically generate VCF files for batch import into the address book.

[![License：MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](./CODE_OF_CONDUCT.md)

## Screenshot

<img src="./screenshots/Snipaste_2024-06-17_04-06-51.png" width="600" alt="Snipaste_2024-06-17_04-06-51.png" />

## Usage

Go to the [Release][ReleaseInGitee] to download and run the installation program (file name is usually `VCFGenerator_<Version>_<PythonVersion>_<Architecture>_64bit_setup.exe`).

1. Copy the name and phone number in the format of "name and phone number" on each line into the editing box below;
   ```text
   Hardy Buck 13445467890
   Alva Mackintosh 13554678907
   Hobart Baker 13645436748
   ```
2. Click "Generate", select a path to save the file;
3. Copy the generated VCF file to your phone, select "Address Book" when opening the file, and then follow the prompts.
4. Wait for import to complete

> [!TIP]
>
> - Tabs will be automatically converted to spaces for processing.
> - The program will automatically remove excess spaces from the input box.
> - If there are multiple spaces in each line, all characters before the last space will be treated as names.\
>   For example, `Hardy Buck 13333333333` will be recognized as
>   ```text
>   Name: Hardy Buck
>   Phone: 13333333333
>   ```

> [!NOTE]
> 
> If you need to use this software on Windows 7, please add or overwrite the `python313.dll` and `api-ms-win-core-path-l1-1-0.dll` files compatible with Windows 7 in the `_internal` folder of the software installation directory. You can download these two files from the [PythonWin7](https://github.com/adang1345/PythonWin7) repository.


## Project Structure

- `vcf_generator`: Source code directory
    - `console`: Developing CLI
    - `ui`: GUI
    - `util`: Tool classes
    - `widget`: Tkinter widget
    - `constants.py`: Constants
- `assets`: Resource file directory
- `main.py`: Program entry

## Developing

> [!NOTE]
>
> The development environment currently only supports 64 bits Windows 8+ and does not currently support macOS and Linux.

### Building

1. Install [Python 3.8+](https://www.python.org/), [Poetry](https://python-poetry.org/), [UPX](https://upx.github.io/), [InnoSetup](https://jrsoftware.org/isinfo.php)
2. Download and install `ChineseSimplified.isl` from [Inno Setup Translations](https://jrsoftware.org/files/istrans/).
3. Install project: `poetry install`
4. Generate `file_version_info.txt`：`poetry run generate-version-file`
5. Generate app binary: `poetry run build-app`
6. Generate installer：`poetry run build-setup`

### Change version

Run `poetry run change-version <Version>`

## License

This project is open source under the [MIT license](./LICENSE)

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)(used as application icon): MIT license
- [Python](https://www.python.org/): [Python license](https://docs.python.org/3/license.html)
- [UPX](https://upx.github.io/): GPL-2.0 licenses
- [PyInstaller](https://pyinstaller.org/en/stable/)：[PyInstaller license](https://pyinstaller.org/en/stable/license.html)
- [Nuitka](https://nuitka.net/): Apache-2.0 license
- [tkhtmlview](https://github.com/bauripalash/tkhtmlview): MIT License

[ReleaseInGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest

## Contribute

See [Contribution Guidelines](./CONTRIBUTING.zh.md).
