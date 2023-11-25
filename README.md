# VCF Generator Lite

![license：MIT](https://img.shields.io/badge/license-MIT-green)

VCF Generator, enter your name and cell phone number to automatically generate VCF files for batch import.

## Screenshots

![Screenshot](./screenshots/Snipaste_2023-11-25_23-57-38.png)

## Usage

Run `vcf生成器.pyw` with a Python parser or `启动vcf生成器.bat` in the distribution root directory to start the program.

1. Copy the name and phone number in the format below into the edit box.
   ```text
   Name1	13345367789
   Name2	13245467890
   Name3	13154678907
   Name4	13145436748
   ```
2. Click "Generate" and the software will create a file named `phones.vcf`.
3. Copy `phones.vcf` to your cell phone, open the file and select "Contacts", then select "OK".
4. Wait for the import to complete.

> [!TIP]
>
> - Tabs will be automatically converted to spaces. 
> - The program will automatically remove extra spaces in the input box. 
> - If there is more than one space in a line, all characters before the last space will be treated as names.\
>   For example, `Wang lei 1333333333333` will be recognized as
>   ```text
>   Name: Wang lei
>   Phone: 1333333333333
>   ```

## Architecture

- `vcf生成器.pyw`: entry file.

## Build

Run `build.bat` directly.

> [!WARNING]\
> For unknown reasons, packaging as a single file can result in a very slow runtime. It is therefore recommended not to package as a single file.
