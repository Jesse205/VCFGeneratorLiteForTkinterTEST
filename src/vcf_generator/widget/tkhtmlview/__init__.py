"""
tkinter HTML text widgets

修改自 https://github.com/bauripalash/tkhtmlview，去除了字体设置和图片加载，修复无法选择
"""
from tkinter import *
from tkinter.font import Font

from vcf_generator.widget.scrolledtext import ScrolledText
from vcf_generator.widget.tkhtmlview import html_parser
from vcf_generator.widget.tkhtmlview.utils import RenderHTML

VERSION = "0.3.0"

__all__ = ['HTMLText', 'HTMLScrolledText']


class HTMLText(Text):
    """
    HTML text widget
    """

    def __init__(self, master=None, html=None, wrap="word", default_font: Font = None, **kw):
        super().__init__(master=master, wrap=wrap, **kw)
        self.html_parser = html_parser.HTMLTextParser()
        self.html_parser.default_font = default_font
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


def example():
    root = Tk()
    root.title("HTMLText")
    html = """
    <html>
    <head>
        <title>HTMLText</title>
    </head>
    <body>
        <h1>H1 标题1</h1>
        <h2>H2 标题2</h1>
        <h3>H3 标题3</h1>
        <h4>H4 标题4</h1>
        <h5>H5 标题5</h1>
        <p>
            HTMLText is a widget that displays HTML formatted text.
        </p>
    </body>
    </html>
    """
    html_text = HTMLText(root, html=html, default_font=Font(family="微软雅黑"))
    html_text.pack(fill=BOTH, expand=True)
    # html_text.fit_height()
    html_scrolled_text = HTMLScrolledText(root, html=html)
    html_scrolled_text.pack(fill=BOTH, expand=True)
    # html_scrolled_text.fit_height()
    root.mainloop()


if __name__ == "__main__":
    example()
