__author__ = 'hor00s'
__email__ = 'hor00s199@gmail.com'
__status__ = 'alpha'
__license__ = 'MIT'
__credits__ = ''
__maintainers__ = (
    'hor00s',
)


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
