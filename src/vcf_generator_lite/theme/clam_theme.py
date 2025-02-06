from vcf_generator_lite.util.style.theme.config import ThemeConfig, ThemeTtkConfig, ThemeColors

clam_theme = ThemeConfig(
    name="Clam theme",
    ttk=ThemeTtkConfig(
        name="clam",
        overrides={
            "TButton": dict(
                padding="3p"
            ),
            "Frame": dict(
                background="$color:window_background"
            ),
            "Toplevel": dict(
                background="$color:window_background"
            ),
            "TScrollbar": dict(
                width="12p",
            ),
            "ScrolledText.TFrame": dict(
                highlightthickness=1,
                highlightbackground="gray"
            )
        }
    ),
    colors=ThemeColors(
        window_background="$lookup:.:background",
    ),
    widgets={
        "Frame": dict(
            background="$color:window_background"
        ),
        "Toplevel": dict(
            background="$color:window_background"
        ),
        "Text": dict(
            borderWidth=1,
            background="white",
            insertWidth="$lookup:TEntry:insertwidth",
            highlightBackground="$lookup:TEntry:bordercolor",
            highlightColor="$lookup:TEntry:bordercolor:focus",
            highlightThickness="1p",
            selectBackground="$lookup:TEntry:selectbackground:focus",
            selectForeground="$lookup:TEntry:selectforeground:focus",
            inactiveSelectBackground="$lookup:TEntry:selectbackground",
        ),
        "ScrolledTextFrame": dict(
            background="white",
            insertWidth="$lookup:TEntry:insertwidth",
            highlightBackground="$lookup:TEntry:bordercolor",
            highlightColor="$lookup:TEntry:bordercolor:focus",
            highlightThickness="1p",
            selectBackground="$lookup:TEntry:selectbackground:focus",
            selectForeground="$lookup:TEntry:selectforeground:focus",
            inactiveSelectBackground="$lookup:TEntry:selectbackground",
        ),
    }
)
