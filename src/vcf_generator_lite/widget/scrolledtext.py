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

from tkinter import Text, Pack, Grid, Place, Frame
from tkinter.constants import RIGHT, LEFT, Y, BOTH, FLAT
from tkinter.ttk import Scrollbar

from vcf_generator_lite.util.resource import get_default_color

__all__ = ['ScrolledText']


class ScrolledText(Text):
    """
    带有边框、Ttk滚动条的Text组件
    """

    def __init__(
        self,
        master=None,
        borderwidth=1,
        relief=FLAT,
        highlightthickness=1,
        highlightbackground="gray",
        highlightcolor=get_default_color(),
        **kw
    ):
        self.frame = Frame(
            master,
            relief=relief,
            highlightthickness=highlightthickness,
            highlightbackground=highlightbackground,
            highlightcolor=highlightcolor,
        )
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(
            self,
            self.frame,
            borderwidth=borderwidth,
            relief="flat",
            **kw
        )
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


def example():
    from tkinter.constants import END

    stext = ScrolledText(bg='white', height=10)
    stext.insert(END, __doc__)
    stext.pack(fill=BOTH, side=LEFT, expand=True)
    stext.focus_set()
    stext.mainloop()


if __name__ == "__main__":
    example()
