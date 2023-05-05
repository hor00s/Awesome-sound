import sys
from window.uiactions import log_error
from PyQt5.QtWidgets import QApplication
from window.window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    wn = MainWindow()
    wn.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log_error(err)
