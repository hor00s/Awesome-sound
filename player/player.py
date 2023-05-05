import sys
from PyQt5.QtWidgets import QApplication
from window.window import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wn = MainWindow()
    wn.show()
    sys.exit(app.exec_())
