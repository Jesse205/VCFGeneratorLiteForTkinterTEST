"""A ScrolledText widget feels like a text widget but also has a
vertical scroll bar on its right.  (Later, options may be added to
add a horizontal bar as well, to make the bars disappear
automatically when not needed, to move them to the other side of the
window, etc.)

Configuration options are passed to the Text widget.
A Frame widget is inserted between the master and the text, to hold
the Scrollbar widget.
Most methods calls are inherited from the Text widget; Pack, Grid and
Place methods are redirected to the Frame widget, however.
"""
from tkinter import Tk
from tkinter.ttk import Scrollbar

from vcf_generator_lite.widget.themed_text import ThemedText

__all__ = ['ScrolledText']


class ScrolledText(ThemedText):
    """
    带有边框、Ttk滚动条的Text组件
    """

    def __init__(
        self,
        master=None,
        **kw
    ):
        super().__init__(master, **kw)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side="right", fill="y")
        self.vbar.configure(command=self.yview)
        self.configure(yscrollcommand=self.vbar.set)

    def __str__(self):
        return str(self.frame)


def example():
    window = Tk()
    window.geometry("500x500")
    widget = ScrolledText(window, bg='white', padding=2)
    widget.insert("end", __doc__)
    widget.pack(fill="both", expand=True, padx=10, pady=10)
    window.mainloop()


if __name__ == "__main__":
    example()
