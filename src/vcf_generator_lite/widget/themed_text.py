"""
A themed Text widget that integrates with ttk styles for consistent appearance.

This widget wraps the standard Text widget within a ttk Frame, enabling full
compatibility with ttk's theming engine. Visual styling should be configured
through ttk style definitions rather than direct widget parameters.

ttk Style Configuration:
Style Name: "TextFrame.TEntry" (default)
Class: "TextFrame" (default class for all ThemedText instances)
States:
- "hover" (mouse over)
- "focus" (widget focused)
Options:
- borderwidth
- padding

"""
from tkinter import Text, Pack, Grid, Place, Event, EventType, Tk
from tkinter.ttk import Frame, Style


class ThemedText(Text):
    def __init__(
        self,
        master=None,
        relief=None,
        style="TextFrame.TEntry",
        class_="TextFrame",
        width=0,
        height=0,
        **kw
    ):
        style_obj = Style(master)
        border_width = style_obj.lookup(style, "borderwidth", None, 1)
        padding = style_obj.lookup(style, "padding", None, 1)
        highlightcolor=style_obj.lookup(style, "bordercolor", ["focus"], "blue")
        del style_obj
        self.frame = Frame(
            master,
            padding=padding,
            borderwidth=border_width,
            relief=relief,
            style=style,
            class_=class_
        )
        Text.__init__(
            self,
            self.frame,
            width=width,
            height=height,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            highlightcolor=highlightcolor,
            **kw
        )
        self.pack(side="left", fill="both", expand=True)
        for sequence in ("<FocusIn>", "<FocusOut>", "<Enter>", "<Leave>", "<ButtonPress>", "<ButtonRelease>"):
            self.bind(sequence, self.__on_state_event, "+")

        # Copy geometry methods of self.frame without overriding Text methods -- hack!
        for m in (vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()).difference(vars(Text).keys()):
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __on_state_event(self, event: Event):
        match event.type:
            case EventType.FocusIn:
                self.frame.state(["focus"])
            case EventType.FocusOut:
                self.frame.state(["!focus"])
            case EventType.Enter:
                self.frame.state(["hover"])
            case EventType.Leave:
                self.frame.state(["!hover"])
            case EventType.ButtonPress:
                self.frame.state(["pressed"])
            case EventType.ButtonRelease:
                self.frame.state(["!pressed"])

    def __str__(self):
        return str(self.frame)


def example():
    window = Tk()
    window.geometry("500x500")
    widget = ThemedText(window, bg='white')
    widget.insert("end", __doc__)
    widget.pack(fill="both", expand=True, padx=10, pady=10)
    window.mainloop()


if __name__ == "__main__":
    example()
