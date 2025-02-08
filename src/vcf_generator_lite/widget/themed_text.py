"""
Themed tkinter text
"""
from tkinter import Text, Pack, Grid, Place, Event, EventType, Tk
from tkinter.ttk import Frame


class ThemedText(Text):
    def __init__(
        self,
        master=None,
        padding=None,
        relief=None,
        borderwidth=None,
        style="TextFrame.TEntry",
        class_="TextFrame",
        width=0,
        height=0,
        **kw
    ):
        self.frame = Frame(
            master,
            padding=padding,
            relief=relief,
            borderwidth=borderwidth,
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
            **kw
        )
        self.pack(side="left", fill="both", expand=True)
        self.bind("<FocusIn>", self.__on_state_event, "+")
        self.bind("<FocusOut>", self.__on_state_event, "+")
        self.bind("<Enter>", self.__on_state_event, "+")
        self.bind("<Leave>", self.__on_state_event, "+")
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

    def __str__(self):
        return str(self.frame)


def example():
    window = Tk()
    window.geometry("500x500")
    widget = ThemedText(window, bg='white', padding=2)
    widget.insert("end", __doc__)
    widget.pack(fill="both", expand=True, padx=10, pady=10)
    window.mainloop()


if __name__ == "__main__":
    example()
