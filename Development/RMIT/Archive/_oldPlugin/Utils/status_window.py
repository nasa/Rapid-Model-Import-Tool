import sys
sys.path.append('c:\\Python37-32\\Lib\\site-packages')
from PyQt5.QtWidgets import QApplication, QLabel


def show_status():

    app = QApplication([])

    label = QLabel('Hello World!')
    label.show()
    app.exec_()

if __name__ == "__main__":
    show_status()