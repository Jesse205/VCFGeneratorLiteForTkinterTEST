from tkinter import Misc, messagebox

from vcf_generator_lite.utils.locales import t


def show_open_url_failure_message_box(parent: Misc, url: str):
    messagebox.showinfo(
        parent=parent,
        title=t("open_url_failure_message_box.title"),
        message=t("open_url_failure_message_box.message"),
        detail=t("open_url_failure_message_box.detail").format(url=url),
    )
