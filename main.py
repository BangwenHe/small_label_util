import sys
from PyQt5 import QtWidgets
import login_dialog
import main_window


if __name__ == '__main__':
    # 打开登录窗口并运行
    app = QtWidgets.QApplication(sys.argv)
    login = login_dialog.LoginDialog()
    login.show()

    if login.exec_() == QtWidgets.QDialog.Accepted:
        main_window = main_window.MainWindow(username=login.user)
        main_window.show()
        sys.exit(app.exec_())
