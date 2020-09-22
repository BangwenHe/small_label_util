from PyQt5 import QtCore, QtGui, QtWidgets
from image_with_mouse_control import ImageWithMouseControl
import sys
import os
import shutil
import ui_main_window
import label_dialog
import json


__appname__ = u'图片标注小工具'
__max_label_num__ = 10
__profile__ = 'profile.json'


class MainWindow(QtWidgets.QMainWindow, ui_main_window.Ui_MainWindow):
    def __init__(self, username=None, parent=None):
        self.img_dir = None     # 切割后的图片路径
        self.save_dir = None    # 打好标签的图片保存路径, 会在该路径下建立三个文件夹:person_cheat, person_not_cheat, blur
        self.img_list = None    # 图片路径下的所有图片名称数组
        self.img_name = None    # 当前显示图片的名称
        self.labels = None      # 所有图片的标签
        self.labeled_img = 0    # 已打标签数量
        self.edited_img = 0     # 修改标签数量
        self.username = username # 用户名
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(__appname__)
        self.setupUi(self)
        self.setListener()
        self.username_label.setText(self.username)
        self.read_user_profile()

    def setupUi(self, MainWindow):
        # 继承ui, 添加图片展示
        super().setupUi(self)
        self.photo = ImageWithMouseControl(self.frame)
        self.photo.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.photo.sizePolicy().hasHeightForWidth())
        self.photo.setSizePolicy(sizePolicy)
        self.photo.setTabletTracking(False)
        self.photo.setObjectName("photo")
        self.horizontalLayout.addWidget(self.photo)

        # 必须从int强转成string
        self.labeled_number_label.setText(str(self.labeled_img))
        self.edit_number_label.setText(str(self.edited_img))

    def setListener(self):
        # 设置强焦点事件, 只能通过TAB和鼠标获取焦点, 保证能使用空格切换图片
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # 上面都是qt designer 自动生成的, 监听函数放在下面绑定
        self.prev_button.clicked.connect(self.prev_button_listener)
        self.next_button.clicked.connect(self.next_button_listener)
        self.action_open_img_dir.triggered.connect(self.open_img_dir_listener)
        self.action_change_img_save_path.triggered.connect(self.change_img_save_path_listener)
        self.action_help.triggered.connect(self.help_listener)
        self.person_cheat_radio.clicked.connect(self.label_choose_listener)
        self.person_not_cheat_radio.clicked.connect(self.label_choose_listener)
        self.blur_radio.clicked.connect(self.label_choose_listener)
        self.add_button.clicked.connect(self.add_label_radio_button_listener)
        self.delete_button.clicked.connect(self.delete_label_radio_button_listener)
        self.edit_button.clicked.connect(self.edit_label_radio_button_listener)

    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_Left:
            self.prev_button.click()
        if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_Space:
            self.next_button.click()
        if e.key() == QtCore.Qt.Key_1:
            self.person_not_cheat_radio.click()
        if e.key() == QtCore.Qt.Key_2:
            self.person_cheat_radio.click()
        if e.key() == QtCore.Qt.Key_3:
            self.blur_radio.click()

    def set_img(self, path=None):
        # 绘制图像
        path = os.path.join(self.img_dir, self.img_name) if path is None else path
        self.photo.img = QtGui.QPixmap(path)
        self.photo.adjust_image()
        self.photo.update()
        self.img_preview_list.setCurrentRow(self.img_list.index(self.img_name))

        # 绘制标签
        label = self.labels[self.img_list.index(self.img_name)]
        if label == 0:
            self.person_not_cheat_radio.toggle()
        elif label == 1:
            self.person_cheat_radio.toggle()
        elif label == 2:
            self.blur_radio.toggle()

    def prev_button_listener(self):
        print(u'上一张')
        if self.img_dir is not None:
            index = self.img_list.index(self.img_name)
            if self.save_img() and index != 0:
                self.img_name = self.img_list[index - 1]
                self.set_img()

    def next_button_listener(self):
        print(u'下一张')
        if self.img_dir is not None:
            index = self.img_list.index(self.img_name)
            if self.save_img() and index != len(self.img_list) - 1:
                self.img_name = self.img_list[index + 1]
                self.set_img()

    def save_img(self):
        if self.save_dir is None:
            QtWidgets.QMessageBox.information(self.centralwidget, '注意', '尚未选择图像保存路径')
            self.action_change_img_save_path.trigger()

        if self.save_dir is not None:
            # 复制这张图片到对应的文件夹, 还要注意返回时后需要修改标签
            # 应该是点击前后图片时保存图片, 而不是点击标签就保存
            label = 0
            labels = ['person_not_cheat', 'person_cheat', 'blur']
            if self.person_cheat_radio.isChecked():
                label = 1
            elif self.blur_radio.isChecked():
                label = 2
            old_label = self.labels[self.img_list.index(self.img_name)]
            self.labels[self.img_list.index(self.img_name)] = label

            # 如果前后的标签不一致
            if label != old_label:
                try:
                    # 图片存在, 说明标签被修改
                    shutil.move(os.path.join(self.save_dir, labels[old_label], self.img_name),
                                os.path.join(self.save_dir, labels[label], self.img_name))
                    self.edited_img += 1
                    self.edit_number_label.setText(f'{self.edited_img}')
                except FileNotFoundError as e:
                    # 图片不存在, 说明新打了这张图片
                    shutil.copy(os.path.join(self.img_dir, self.img_name), os.path.join(self.save_dir, labels[label]))
                    self.labeled_img += 1
                    self.labeled_number_label.setText(f'{self.labeled_img}')

            # 如果一致, 但是没有图片, 也需要修改
            elif self.img_name not in os.listdir(os.path.join(self.save_dir, labels[label])):
                shutil.copy(os.path.join(self.img_dir, self.img_name), os.path.join(self.save_dir, labels[label]))

                self.labeled_img += 1
                self.labeled_number_label.setText(f'{self.labeled_img}')
            return True
        return False

    def open_img_dir_listener(self):
        # 在当前窗口内打开文件对话窗口
        directory = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget, '请选择图片所在文件夹')
        print('打开文件夹:', directory)
        if directory != '':
            self.img_dir = directory

        # 打开图片文件夹
        suffix = ['jpg', 'jpeg', 'bmp', 'png']
        if self.img_dir is not None:
            self.img_list = [fn for fn in os.listdir(self.img_dir) if any(fn.endswith(ext) for ext in suffix)]
            self.img_name = self.img_list[0]
            self.labels = [1 for n in range(0, len(self.img_list))]
            self.img_preview_list.clear()
            self.img_preview_list.addItems(self.img_list)
            self.img_preview_list.itemActivated.connect(self.item_activated)

    def change_img_save_path_listener(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget, '请选择图片保存的路径')
        print('打开文件夹:', directory)
        if directory != '':
            self.save_dir = directory

        if self.save_dir is not None:
            dirs = [name for name in os.listdir(self.save_dir) if os.path.isdir(os.path.join(self.save_dir, name))]
            labels = ['person_not_cheat', 'person_cheat', 'blur']

            for label in labels:
                if label not in dirs:
                    os.mkdir(os.path.join(self.save_dir, label))

            suffix = ['jpg', 'jpeg', 'bmp', 'png']
            for label in labels:
                imgs = [fn for fn in os.listdir(os.path.join(self.save_dir, label)) if any(fn.endswith(ext) for ext in suffix)]
                for img in imgs:
                    if img in self.img_list:
                        self.labels[self.img_list.index(img)] = labels.index(label)

            print(self.labels)
            self.set_img()

    def help_listener(self):
        QtWidgets.QMessageBox.information(self.centralwidget, '帮助', """1. 快捷键: 左方向键(上一张), 右方向键(下一张,空格), person_not_cheat(数字键1), person_cheat(数字键2), blur(数字键3)
2. 流程: 选择打开文件路径->选择改变图像保存路径->显示图片后可以开始打标签""")

    def label_choose_listener(self):
        if self.save_dir is None:
            QtWidgets.QMessageBox.information(self.centralwidget, '注意', '尚未选择图像保存路径')
            self.action_change_img_save_path.trigger()
            print(self.save_dir)

    def item_activated(self, item):
        print('item text:', item.text())
        if self.save_img():
            self.img_name = item.text()
            self.set_img()

    def get_checked_button(self):
        radio_buttons = self.all_label.findChildren(QtWidgets.QRadioButton)
        for item in radio_buttons:
            if item.isChecked():
                return item

    def add_label_radio_button_listener(self):
        # TODO: add button listener
        if len(self.all_label.findChildren(QtWidgets.QRadioButton)) >= __max_label_num__:
            QtWidgets.QMessageBox.information(self, "信息", f"最大添加量为{__max_label_num__}", QtWidgets.QMessageBox.Yes)
        else:
            btn = QtWidgets.QRadioButton(self.all_label)
            self.verticalLayout_2.addWidget(btn)
            dialog = label_dialog.LabelDialog(btn=btn)
            dialog.exec_()

    def delete_label_radio_button_listener(self):
        # TODO: delete button listner
        print('按下了删除按钮', self.get_checked_button().text())
        btn = self.get_checked_button()
        if btn is None:
            QtWidgets.QMessageBox.warning(self, "警告", "尚未选择标签", QtWidgets.QMessageBox.Yes)
        else:
            btn.deleteLater()

    def edit_label_radio_button_listener(self):
        btn = self.get_checked_button()
        if btn is not None:
            dialog = label_dialog.LabelDialog(btn=btn)
            dialog.exec_()

    def read_user_profile(self):
        # 读取配置文件
        if os.path.exists(os.path.join('.', __profile__)):
            with open(os.path.join('.', __profile__), 'r') as f:
                dic = json.loads(" ".join(f.readlines()))
                print(dic)

if __name__ == '__main__':
    # 测试主窗口
    # 直接打开主窗口是可行的, 但是通过登录窗口打开失败了
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(username='test')
    window.show()
    sys.exit(app.exec_())