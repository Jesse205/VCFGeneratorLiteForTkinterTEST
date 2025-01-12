<div align="center">
<img src="./docs/images/icon.png" width="192"/>

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

<img src="./docs/images/screenshots/Snipaste_2025-01-13_06-08-40.png" width="600" alt="Snipaste_2025-01-13_06-08-40.png" />

## Environment Requirements

- Operating System
    - Windows: Windows 8+ or Windows 7+ (with patches)
    - Linux: Not supported (contributions welcome)
    - macOS: Not supported (contributions welcome)
- CPU: x86 64-bit
- Python Version: No requirement

For some systems, you can enable running this APP by patching software. If you need to run this APP on these systems, please refer to the [Patch APP](#patch-app) section.

### Patch APP

<details>
<summary>Support Running on Windows 7</summary>

1. Download `python313.dll` and `api-ms-win-core-path-l1-1-0.dll` compatible with Windows 7;
    - You can choose to download these two files from the [PythonWin7](https://github.com/adang1345/PythonWin7) repository.
2. Install the software, go to the `_internal` directory in the installation folder, and overwrite the above two DLLs.

</details>

## Usage

1. Go to the [Release][ReleaseInGitee] to download and run the installation program (file name is usually
   `VCFGenerator_<Version>_<PythonVersion>_<Architecture>_64bit_setup.exe`).
2. Open APP;
3. Copy the name and phone number in the format of `Name  PhoneNumber` on each line into the editing box below;
    ```text
    Hardy Buck 13445467890
    Alva Mackintosh 13554678907
    Hobart Baker 13645436748
    ```
4. Click "生成" (Generate), select a path to save the file;
5. Copy the generated VCF file to your phone, select "Contacts" when opening the file, and then follow the prompts;
6. Wait for import to complete.

> [!TIP]
>
> - Tabs will be automatically converted to spaces for processing.
> - The program will automatically remove excess spaces from the input box.
> - If there are multiple spaces in each line, all characters before the last space will be treated as names.
>
> For example, ` Hardy Buck   13333333333   ` will be recognized as
> ```text
> Name: Hardy Buck
> Phone: 13333333333
> ```

## Project Structure

- `src`：Source code directory
    - `vcf_generator/ui`： GUI
    - `vcf_generator/util`：Utilities
    - `vcf_generator/widget`：Tkinter widget
    - `vcf_generator/constants.py`：Constants
    - `vcf_generator/assets`：Resource file directory
    - `__main__.py`：Program entry
- `scripts`：Script directory

## Developing

> [!TIP]
>
> You can view all the commands defined in this project by running pdm run --list.

### Pre-development

1. Install [Python 3.11+](https://www.python.org/), [PDM](https://pdm-project.org/zh-cn/latest/), [UPX](https://upx.github.io/), [InnoSetup 6.3](https://jrsoftware.org/isinfo.php);
2. Install dependencies: `pdm install`;
3. Install the PDM plugins: `pdm install --plugins`;
4. Download the InnoSetup file: `pdm run prepare_innosetup_extensions`.

### Building

1. Generate app binary: `poetry run build_app`;
2. Generate installer：`poetry run build_setup`.

### Change version

Run `poetry run change-version <Version>`.

## License

This project is open source under the [MIT license](./LICENSE)

- [Fluent Emoji](https://github.com/microsoft/fluentui-emoji)(used as application icon): MIT license
- [Python](https://www.python.org/): [Python license](https://docs.python.org/3/license.html)
- [UPX](https://upx.github.io/)(for compressing code): GPL-2.0 license
- [PyInstaller](https://pyinstaller.org/en/stable/)(for packaging as an APP)：[GPL-2.0 license](https://pyinstaller.org/en/stable/license.html)
- [tkhtmlview](https://github.com/bauripalash/tkhtmlview): MIT License

## Contribute

See [Contribution Guidelines (Chinese)](./CONTRIBUTING.zh.md).

[ReleaseInGitee]: https://gitee.com/HelloTool/VCFGeneratorLiteForTkinter/releases/latest
