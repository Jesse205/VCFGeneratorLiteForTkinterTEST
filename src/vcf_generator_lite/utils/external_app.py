import webbrowser
from tkinter import Misc

from vcf_generator_lite.ui.message_boxes.external_app_message_boxes import show_open_url_failure_message_box


def open_url_with_fallback(parent: Misc, url: str):
    result = webbrowser.open(url)
    if not result:
        show_open_url_failure_message_box(parent, url)
