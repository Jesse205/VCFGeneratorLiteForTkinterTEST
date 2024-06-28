import os
import sys
from typing import Optional, List, Dict
import pkgutil
import constants
import json


def get_path_in_assets(file_name: str) -> str:
    """
    Get the path to the file in the assets' folder.
    :param file_name: The name of the file.
    :return: The path to the file.
    """
    return os.path.join(os.path.dirname(sys.modules["vcf_generator"].__file__), "assets", file_name)


def get_window_icon() -> Optional[str]:
    if sys.platform == "win32":
        return get_path_in_assets("images/icon.ico")
    return None


def get_default_color() -> str:
    if sys.platform == "win32":
        return "SystemHighlight"
    return "blue"


def get_licenses() -> List[Dict[str, str]]:
    return json.loads(pkgutil.get_data('vcf_generator', 'assets/data/licenses.json'))


def get_about_html() -> str:
    licenses_html = "".join([
        f"<a href=\"{_license['url']}\">{_license['name']}</a> - {_license['license']}<br />" for _license in
        get_licenses()
    ])
    about_html = pkgutil.get_data('vcf_generator', 'assets/texts/about.html').decode('UTF-8', 'ignore')
    about_html = about_html.format(source_url=constants.URL_SOURCE, release_url=constants.URL_RELEASES,
                                   jesse205_email=constants.EMAIL_JESSE205, licenses_html=licenses_html)
    return about_html
