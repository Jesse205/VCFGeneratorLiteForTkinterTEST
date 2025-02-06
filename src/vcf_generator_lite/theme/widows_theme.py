from vcf_generator_lite.util.style.theme.config import ThemeColors, ThemeTtkConfig, ThemeConfig

windows_theme = ThemeConfig(
    name="Windows vista theme",
    ttk=ThemeTtkConfig(
        name="vista",
        overrides={
            "TButton": dict(
                padding="2p",
            )
        }
    ),
    colors=ThemeColors(
        window_background="systemButtonFace",
        highlight_background="systemHighlight",
        highlight_foreground="systemHighlightText",
        tooltip_background="systemInfoBackground",
        tooltip_foreground="systemInfoText",
        client_background="systemWindow",
        client_foreground="systemWindowText",
    ),
    widgets={
        "Text": dict(
            borderWidth=1,
            highlightBackground="gray",
            highlightColor="systemHighlight",
            highlightThickness=1,
            selectBackground="systemHighlight",
            selectForeground="systemHighlightText",
        ),
        "ScrolledTextFrame": dict(
            highlightBackground="gray",
            highlightColor="systemHighlight",
            highlightThickness=1,
        ),
    }
)
