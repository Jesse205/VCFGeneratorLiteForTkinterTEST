from tkinter import Tk, Toplevel

from vcf_generator_lite.core.vcf_generator import InvalidLine
from vcf_generator_lite.dialogs.invalid_items.controller import InvalidItemsController
from vcf_generator_lite.dialogs.invalid_items.dialog import InvalidItemsDialog


def create_invalid_items_dialog(
    master: Tk | Toplevel,
    display_path: str,
    invalid_lines: list[InvalidLine],
) -> tuple[InvalidItemsDialog, InvalidItemsController]:
    invalid_items_dialog = InvalidItemsDialog(master)
    invalid_items_controller = InvalidItemsController(invalid_items_dialog, display_path, invalid_lines)
    return invalid_items_dialog, invalid_items_controller
