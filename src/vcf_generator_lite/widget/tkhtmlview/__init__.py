"""
tkinter HTML text widgets

修改自 https://github.com/bauripalash/tkhtmlview，去除了字体设置和图片加载，修复无法选择
"""

from tkinter.constants import NORMAL, END
from tkinter.ttk import Style

from ttk_text import ThemedText
from ttk_text.scrolled_text import ScrolledText

from vcf_generator_lite.widget.tkhtmlview import html_parser
from vcf_generator_lite.widget.tkhtmlview.utils import RenderHTML

VERSION = "0.3.0"

__all__ = ["HTMLText", "HTMLScrolledText"]


class HTMLText(ThemedText):
    """
    HTML text widget
    """

    def __init__(self, master=None, html=None, wrap="word", **kw):
        super().__init__(master=master, wrap=wrap, **kw)
        style: str = self.frame.cget("style")
        style_obj = Style(self)
        highlight_color = style_obj.lookup(style, "bordercolor", ["focus"], "blue")
        self.configure(highlightcolor=highlight_color)
        self.html_parser = html_parser.HTMLTextParser()
        if isinstance(html, str):
            self.set_html(html)
        elif isinstance(html, RenderHTML):
            self.set_html(html.get_html())

    def set_html(self, html, strip=True):
        """
        Set HTML widget text. If strip is enabled (default) it ignores spaces and new lines.
        """
        prev_state = self.cget("state")
        self.config(state=NORMAL)
        self.delete("1.0", END)
        for tag in self.tag_names():
            self.tag_delete(tag)

        self.html_parser.w_set_html(self, html, strip=strip)
        self.config(state=prev_state)

    def fit_height(self):
        """
        Fit widget height to wrapped lines
        """
        for h in range(1, 4):
            self.config(height=h)
            self.master.update()
            if self.yview()[1] >= 1:
                break
        else:
            self.config(height=0.5 + 3 / self.yview()[1])


class HTMLScrolledText(HTMLText, ScrolledText):
    pass
