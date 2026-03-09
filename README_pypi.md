# VCF Generator Lite ![with Tkinter](https://img.shields.io/badge/with-Tkinter-00319C)

VCF Generator Lite is a lightweight tool that quickly converts name and phone number lists into vCard files for batch import to mobile contacts.

## Features

- **Smart Parsing**: Batch contacts in `Name Phone Note` format (note optional), automatically handles tabs and spaces.
- **Batch Generation**: Combines all contacts into a single `.vcf` file.
- **Number Validation**: Automatically skips invalid numbers and quickly locates error rows.
- **Editing Assistance**: Displays line numbers in text area, supports one-click quote removal.

## Usage

1. Copy the name and phone number in the format of `Name Phone Note` on each line into the text field below. The note can be omitted.
   ```text
   Isaac Newton	13445467890	British mathematician
   Muhammad		13554678907
   Confucius		13645436748
   ```
2. Click **Generate**, select a path to save the file.
3. You can use the generated vCard file wherever you need it.

> [!NOTE]
>
> - Tabs will be automatically converted to spaces, and you can use both tabs and spaces to separate the name and phone number.
> - The program will automatically remove extra spaces from the text field.
>
> For example, ` Han Meimei   13333333333   A   well-known girl` will be recognized as
>
>
> > - Name: Han Meimei
> > - Phone: 13333333333
> > - Note: A well-known girl
>

## License

This project is licensed under the Apache 2.0 license. For details, please refer to the [LICENSE file](https://github.com/hellotool/VCFGeneratorLiteWithTkinter/blob/master/LICENSE).
