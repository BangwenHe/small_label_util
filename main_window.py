from PyQt5 import QtCore, QtGui, QtWidgets
from util.image_with_mouse_control import ImageWithMouseControl
import sys
import os
import shutil
from ui import ui_main_window
from dialog import label_dialog
import json
import config


class MainWindow(QtWidgets.QMainWindow, ui_main_window.Ui_MainWindow):
    def __init__(self, username=None, parent=None):
        self.img_dir = None     # 切割后的图片路径
        self.save_dir = None    # 打好标签的图片保存路径, 会在该路径下建立三个文件夹:person_cheat, person_not_cheat, blur
        self.img_list = None    # 图片路径下的所有图片名称数组
        self.img_name = None    # 当前显示图片的名称
        self.labels = None      # 所有图片的标签
        self.label_name = []    # 所有标签名
        self.labeled_img = 0    # 已打标签数量
        self.edited_img = 0     # 修改标签数量
        self.username = username # 用户名
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(config.app_name)
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
        self.add_button.clicked.connect(self.add_label_radio_button_listener)
        self.delete_button.clicked.connect(self.delete_label_radio_button_listener)
        self.edit_button.clicked.connect(self.edit_label_radio_button_listener)

    def update_from_profile(self):
        # 更新img_dir
        suffix = ['jpg', 'jpeg', 'bmp', 'png']
        if self.img_dir is not None:
            try:
                self.img_list = [fn for fn in os.listdir(self.img_dir) if any(fn.endswith(ext) for ext in suffix)]
                self.labels = [0 for n in range(0, len(self.img_list))]
                self.img_preview_list.clear()
                self.img_preview_list.addItems(self.img_list)
                self.img_preview_list.itemActivated.connect(self.item_activated)
            except FileNotFoundError as e:
                print(e)
                QtWidgets.QMessageBox.warning(self, "警告", "要打开图像的路径不存在", QtWidgets.QMessageBox.Yes)

        # 更新save_dir
        if self.save_dir is not None:
            dirs = [name for name in os.listdir(self.save_dir) if os.path.isdir(os.path.join(self.save_dir, name))]

            for label in self.label_name:
                if label not in dirs:
                    os.mkdir(os.path.join(self.save_dir, label))

            for label in self.label_name:
                imgs = [fn for fn in os.listdir(os.path.join(self.save_dir, label)) if any(fn.endswith(ext) for ext in suffix)]
                for img in imgs:
                    if img in self.img_list:
                        self.labels[self.img_list.index(img)] = self.label_name.index(label)

        # 绘制标签
        if len(self.label_name) > 0:
            for name in self.label_name:
                btn = QtWidgets.QRadioButton(self.all_label, text=name)
                self.verticalLayout_2.addWidget(btn)
                btn.clicked.connect(self.label_choose_listener)

    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_Left:
            self.prev_button.click()
        if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_Space:
            self.next_button.click()

        buttons = self.all_label.findChildren(QtWidgets.QRadioButton)
        for i in range(config.max_label_num):
            if e.key() == QtCore.Qt.Key_1 + i and len(buttons) >= 1 + i:
                buttons[i].click()

    def set_img(self, path=None):
        # 绘制图像
        path = os.path.join(self.img_dir, self.img_name) if path is None else path
        self.photo.img = QtGui.QPixmap(path)
        self.photo.adjust_image()
        self.photo.update()
        self.img_preview_list.setCurrentRow(self.img_list.index(self.img_name))

        # 绘制标签
        label = self.labels[self.img_list.index(self.img_name)]
        if label >= 0 and len(self.label_name) > 0:
            buttons = self.all_label.findChildren(QtWidgets.QRadioButton)
            buttons[label].toggle()

    def prev_button_listener(self):
        print(u'上一张')
        if self.img_dir is not None:
            index = self.img_list.index(self.img_name)
            if self.get_checked_button() is not None and\
                    self.save_img() and\
                    index != 0:
                self.img_name = self.img_list[index - 1]
                self.set_img()
            else:
                QtWidgets.QMessageBox.warning(self, "警告", "该图片尚未选择标签", QtWidgets.QMessageBox.Yes)

    def next_button_listener(self):
        print(u'下一张')
        if self.img_dir is not None:
            index = self.img_list.index(self.img_name)
            if self.get_checked_button() is not None and \
                    self.save_img() and \
                    index != len(self.img_list) - 1:
                self.img_name = self.img_list[index + 1]
                self.set_img()
            else:
                QtWidgets.QMessageBox.warning(self, "警告", "该图片尚未选择标签", QtWidgets.QMessageBox.Yes)

    def save_img(self):
        if self.save_dir is None:
            QtWidgets.QMessageBox.information(self.centralwidget, '注意', '尚未选择图像保存路径')
            self.action_change_img_save_path.trigger()

        if self.save_dir is not None:
            # 复制这张图片到对应的文件夹, 还要注意返回时后需要修改标签
            # 应该是点击前后图片时保存图片, 而不是点击标签就保存
            label = self.label_name.index(self.get_checked_button().text())
            old_label = self.labels[self.img_list.index(self.img_name)]
            self.labels[self.img_list.index(self.img_name)] = label

            # 如果前后的标签不一致
            if label != old_label:
                try:
                    # 图片存在, 说明标签被修改
                    shutil.move(os.path.join(self.save_dir, self.label_name[old_label], self.img_name),
                                os.path.join(self.save_dir, self.label_name[label], self.img_name))
                    self.edited_img += 1
                    self.edit_number_label.setText(f'{self.edited_img}')
                except FileNotFoundError as e:
                    # 图片不存在, 说明新打了这张图片
                    shutil.copy(os.path.join(self.img_dir, self.img_name), os.path.join(self.save_dir, self.label_name[label]))
                    self.labeled_img += 1
                    self.labeled_number_label.setText(f'{self.labeled_img}')

            # 如果一致, 但是没有图片, 也需要修改
            elif self.img_name not in os.listdir(os.path.join(self.save_dir, self.label_name[label])):
                shutil.copy(os.path.join(self.img_dir, self.img_name), os.path.join(self.save_dir, self.label_name[label]))

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
            # 初始化所有标签默认选项
            self.labels = [0 for n in range(0, len(self.img_list))]
            self.img_preview_list.clear()
            self.img_preview_list.addItems(self.img_list)
            self.img_preview_list.itemActivated.connect(self.item_activated)
            self.set_img()

    def change_img_save_path_listener(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget, '请选择图片保存的路径')
        print('打开文件夹:', directory)
        if directory != '':
            self.save_dir = directory

        if self.save_dir is not None:
            dirs = [name for name in os.listdir(self.save_dir) if os.path.isdir(os.path.join(self.save_dir, name))]

            for label in self.label_name:
                if label not in dirs:
                    os.mkdir(os.path.join(self.save_dir, label))

            suffix = ['jpg', 'jpeg', 'bmp', 'png']
            for label in self.label_name:
                imgs = [fn for fn in os.listdir(os.path.join(self.save_dir, label)) if any(fn.endswith(ext) for ext in suffix)]
                for img in imgs:
                    if img in self.img_list:
                        self.labels[self.img_list.index(img)] = self.label_name.index(label)

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
        if len(self.all_label.findChildren(QtWidgets.QRadioButton)) >= config.max_label_num:
            QtWidgets.QMessageBox.information(self, "信息", f"最大添加量为{config.max_label_num}", QtWidgets.QMessageBox.Yes)
        elif self.save_dir is None:
            QtWidgets.QMessageBox.warning(self, "警告", "尚未选择保存图片路径", QtWidgets.QMessageBox.Yes)
        else:
            btn = QtWidgets.QRadioButton(self.all_label)
            dialog = label_dialog.LabelDialog(btn=btn)

            # 确认说明标签添加成功
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                    text= btn.text()
                    self.label_name.append(text)

                    if not os.path.exists(os.path.join(self.save_dir, text)):
                        os.mkdir(os.path.join(self.save_dir, text))
                    else:
                        # 读取该文件夹的所有文件并刷新标签
                        suffix = ['jpg', 'jpeg', 'bmp', 'png']
                        for label in self.label_name:
                            imgs = [fn for fn in os.listdir(os.path.join(self.save_dir, label)) if
                                    any(fn.endswith(ext) for ext in suffix)]
                            for img in imgs:
                                if img in self.img_list:
                                    self.labels[self.img_list.index(img)] = self.label_name.index(label)

                        # 更新标签
                        label = self.labels[self.img_list.index(self.img_name)]
                        if label >= 0 and len(self.label_name) > 0:
                            buttons = self.all_label.findChildren(QtWidgets.QRadioButton)
                            buttons[label].toggle()

                    self.verticalLayout_2.addWidget(btn)

    def delete_label_radio_button_listener(self):
        # TODO: delete button listner
        print('按下了删除按钮', self.get_checked_button().text())
        btn = self.get_checked_button()
        text = btn.text()
        if btn is None:
            QtWidgets.QMessageBox.warning(self, "警告", "尚未选择标签", QtWidgets.QMessageBox.Yes)
        elif self.save_dir is None:
            QtWidgets.QMessageBox.warning(self, "警告", "尚未选择保存图片路径", QtWidgets.QMessageBox.Yes)
        else:
            index = self.label_name.index(text)
            for i in range(len(self.labels)):
                if self.labels[i] >= index:
                    self.labels[i] -= 1

            self.label_name.remove(text)
            shutil.rmtree(os.path.join(self.save_dir, text))
            btn.deleteLater()

    def edit_label_radio_button_listener(self):
        btn = self.get_checked_button()
        if self.save_dir is None:
            QtWidgets.QMessageBox.warning(self, "警告", "尚未选择保存图片路径", QtWidgets.QMessageBox.Yes)
        elif btn is None:
            QtWidgets.QMessageBox.warning(self, "警告", "尚未选择标签", QtWidgets.QMessageBox.Yes)
        else:
            text = btn.text()
            dialog = label_dialog.LabelDialog(btn=btn)

            # 若修改成功,则修改文件夹名称
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                self.label_name[self.label_name.index(text)] = btn.text()
                os.rename(os.path.join(self.save_dir, text), os.path.join(self.save_dir, btn.text()))

    def index_of_current_user(self, dic):
        try:
            return [d['username'] for d in dic['user']].index(self.username)
        except ValueError as e:
            return -1

    def read_user_profile(self):
        # 读取配置文件
        if os.path.exists(os.path.join('.', config.profile)):
            with open(os.path.join('.', config.profile), 'r') as f:
                dic = json.load(f)
                index = self.index_of_current_user(dic)

                if index >= 0:
                    self.img_dir = dic['user'][index]['img_dir']
                    self.save_dir = dic['user'][index]['save_dir']
                    self.img_name = dic['user'][index]['img_name']
                    self.label_name = dic['user'][index]['label_name']
                    self.update_from_profile()
                    self.set_img()
        else:
            with open(os.path.join('.', config.profile), 'w') as f:
                # 写入初始json构造
                dic = {'user': []}
                json.dump(dic, f, indent=4, separators=[',', ':'])

    def closeEvent(self, e):
        # 关闭窗口时保存配置文件
        reply = QtWidgets.QMessageBox.question(self, '本程序', "是否要退出程序？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if os.path.exists(os.path.join('.', config.profile)):
                with open(os.path.join('.', config.profile), 'r') as f:
                    dic = json.load(f)
                    index = self.index_of_current_user(dic)

                    # 存在
                    if index >= 0:
                        dic['user'][index]['img_dir'] = self.img_dir
                        dic['user'][index]['save_dir'] = self.save_dir
                        dic['user'][index]['img_name'] = self.img_name
                        dic['user'][index]['label_name'] = self.label_name
                    else:
                        dic['user'].append({'username': self.username, 'img_dir': self.img_dir, 'save_dir':self.save_dir, 'img_name': self.img_name, 'label_name':self.label_name})

                with open(os.path.join('.', config.profile), 'w') as f:
                    json.dump(dic, f, indent=4, separators=[',', ':'])
            e.accept()
        else:
            e.ignore()


if __name__ == '__main__':
    # 测试主窗口
    # 直接打开主窗口是可行的, 但是通过登录窗口打开失败了
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(username='test')
    window.show()
    sys.exit(app.exec_())