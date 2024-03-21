# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --include-data-dir=./assets=assets
# nuitka-project: --windows-icon-from-ico=./assets/icon.ico
# nuitka-project: --product-name="VCF Generator"
# nuitka-project: --product-version=2.0.0.0
# nuitka-project: --copyright="Copyright (c) 2023-2024 Jesse205"
# nuitka-project: --output-dir=../build
# nuitka-project: --standalone
#
# Debugging options, controlled via environment variable at compile time.
# nuitka-project-if: os.getenv("DEBUG_COMPILATION", "no") == "yes":
#     nuitka-project: --enable-console
# nuitka-project-else:
#     nuitka-project: --disable-console

import os

import vcf_generator.ui.main

os.chdir(os.path.dirname(__file__))

if __name__ == '__main__':
    vcf_generator.ui.main.main()
