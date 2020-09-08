import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import *


# 创建mainWin类并传入Ui_MainWindow
class MainWin(QMainWindow, UiSmallLabelTool):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)


if __name__ == '__main__':
    # 下面是使用PyQt5的固定用法
    app = QApplication(sys.argv)
    main_win = MainWin()
    main_win.show()
    sys.exit(app.exec_())
