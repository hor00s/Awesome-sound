import sys
from window.window import (
    QApplication,
    MainWindow,
)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wn = MainWindow()
    wn.show()
    sys.exit(app.exec_())
