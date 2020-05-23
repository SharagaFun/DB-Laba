from DBApp import DBApp
from PyQt5.QtWidgets import *
import sys

def main():
    app = QApplication(sys.argv)
    window = DBApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
