import sys

script_path = sys.path[0]

frozen = getattr(sys, 'frozen', False)

is_windows = sys.platform == "win32"
