from vcf_generator_lite.ui.windows.main_window.controller import MainController
from vcf_generator_lite.ui.windows.main_window.window import VCFGeneratorLiteApp


def create_app() -> tuple[VCFGeneratorLiteApp, MainController]:
    main_window = VCFGeneratorLiteApp()
    main_controller = MainController(main_window)
    return main_window, main_controller
