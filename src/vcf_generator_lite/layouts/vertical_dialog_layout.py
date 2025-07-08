from abc import abstractmethod, ABC
from tkinter import Misc, Widget
from tkinter.constants import X, BOTH, BOTTOM
from typing import Optional

from vcf_generator_lite.utils.tkinter.window import WindowExtension


class VerticalDialogLayout(WindowExtension, ABC):

    def _create_widgets(self, parent: Misc):
        header = self._create_header(parent)
        if header is not None:
            header.pack(fill=X)

        content = self._create_content(parent)
        if content is not None:
            content.pack(fill=BOTH, expand=True)

        footer = self._create_actions(parent)
        if footer is not None:
            footer.pack(fill=X, side=BOTTOM)

    @abstractmethod
    def _create_header(self, parent: Misc) -> Optional[Widget]: ...

    @abstractmethod
    def _create_content(self, parent: Misc) -> Optional[Widget]: ...

    @abstractmethod
    def _create_actions(self, parent: Misc) -> Optional[Widget]: ...
