import sys
from PyQt5 import QtWidgets
import login_dialog


if __name__ == '__main__':
    # 打开登录窗口并运行
    app = QtWidgets.QApplication(sys.argv)
    login = login_dialog.LoginDialog()
    login.show()
    sys.exit(app.exec_())
