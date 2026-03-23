from vcf_generator_lite.entries.cli import main_cli
from vcf_generator_lite.entries.gui import main_gui
from vcf_generator_lite.entries.union import main

__all__ = ["main", "main_gui", "main_cli"]

if __name__ == "__main__":
    main()
