from tkinter import Label, Event
from tkinter.ttk import Label as TtkLabel


def auto_wrap_configure_event(event: Event):
    widget = event.widget
    if isinstance(widget, Label) or isinstance(widget, TtkLabel):
        widget.configure(wraplength=event.width)
