from abc import ABC, abstractmethod
from tkinter import Misc, Widget

from vcf_generator_lite.utils.tkinter.window import WindowExtension


class VerticalDialogLayout(WindowExtension, ABC):
    def _create_widgets(self, parent: Misc):
        header = self._create_header(parent)
        if header is not None:
            header.pack(fill="x")

        content = self._create_content(parent)
        if content is not None:
            content.pack(fill="both", expand=True)

        footer = self._create_footer(parent)
        if footer is not None:
            footer.pack(fill="x", side="bottom")

    @abstractmethod
    def _create_header(self, parent: Misc) -> Widget | None: ...

    @abstractmethod
    def _create_content(self, parent: Misc) -> Widget | None: ...

    @abstractmethod
    def _create_footer(self, parent: Misc) -> Widget | None: ...
