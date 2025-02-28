from vcf_generator_lite.window.main.controller import MainController
from vcf_generator_lite.window.main.window import MainWindow


def create_main_window() -> tuple[MainWindow, MainController]:
    main_window = MainWindow()
    main_controller = MainController(main_window)
    return main_window, main_controller
