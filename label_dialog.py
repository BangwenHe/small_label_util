from ui_label_dialog import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets
import sys


class LabelDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None, btn=None):
        super(LabelDialog, self).__init__(parent)
        self.setupUi(self)
        self.btn = btn
        self.text = btn.text()
        self.lineEdit.setText(self.text)

    def accept(self):
        if not self.lineEdit.text().strip():
            QtWidgets.QMessageBox.warning(self, "警告", "标签为空", QtWidgets.QMessageBox.Yes)
            self.lineEdit.setText(self.text)
            self.lineEdit.setFocus()
        else:
            self.btn.setText(self.lineEdit.text().strip())
            super(LabelDialog, self).accept()

    def reject(self):
        super(LabelDialog, self).reject()