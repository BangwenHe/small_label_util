import sys
from PyQt5.QtWidgets import *
import main_window


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        usr = QLabel("用户：")
        self.usrLineEdit = QLineEdit()
        self.user = None

        gridLayout = QGridLayout()
        gridLayout.addWidget(usr, 0, 0, 1, 1)
        gridLayout.addWidget(self.usrLineEdit, 0, 1, 1, 3)

        okBtn = QPushButton("确定")
        cancelBtn = QPushButton("取消")
        btnLayout = QHBoxLayout()

        btnLayout.setSpacing(60)
        btnLayout.addWidget(okBtn)
        btnLayout.addWidget(cancelBtn)

        dlgLayout = QVBoxLayout()
        dlgLayout.addLayout(gridLayout)
        dlgLayout.addLayout(btnLayout)

        self.setLayout(dlgLayout)
        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.reject)
        self.setWindowTitle("登录")
        self.setFixedSize(240, 118)

    def accept(self):
        if not self.usrLineEdit.text().strip():
            QMessageBox.warning(self, "警告", "用户名为空！", QMessageBox.Yes)
            self.usrLineEdit.setFocus()
        else:
            self.user = self.usrLineEdit.text().strip()
            super(LoginDialog, self).accept()

    def reject(self):
        QMessageBox.warning(self, "退出", "确定退出？", QMessageBox.Yes)
        sys.exit(0)