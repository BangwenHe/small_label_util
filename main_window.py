from PyQt5 import QtCore, QtGui, QtWidgets
from image_with_mouse_control import ImageWithMouseControl
import os
import shutil


__appname__ = u'图片标注小工具'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username=None, parent=None):
        self.img_dir = None     # 切割后的图片路径
        self.save_dir = None    # 打好标签的图片保存路径, 会在该路径下建立三个文件夹:person_cheat, person_not_cheat, blur
        self.img_list = None    # 图片路径下的所有图片名称数组
        self.img_name = None    # 当前显示图片的名称
        self.labels = None      # 所有图片的标签
        self.username = username
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
    def setupUi(self, SmallLabelTool):
        SmallLabelTool.setObjectName("SmallLabelTool")
        SmallLabelTool.resize(837, 617)
        self.centralwidget = QtWidgets.QWidget(SmallLabelTool)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(493, 305))
        self.centralwidget.setMaximumSize(QtCore.QSize(1920, 1080))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.next_prev = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.next_prev.sizePolicy().hasHeightForWidth())
        self.next_prev.setSizePolicy(sizePolicy)
        self.next_prev.setStyleSheet("")
        self.next_prev.setLineWidth(1)
        self.next_prev.setObjectName("next_prev")
        self.prev_next = QtWidgets.QHBoxLayout(self.next_prev)
        self.prev_next.setContentsMargins(0, 0, 0, 0)
        self.prev_next.setSpacing(6)
        self.prev_next.setObjectName("prev_next")
        self.prev_button = QtWidgets.QPushButton(self.next_prev)
        self.prev_button.setObjectName("prev_button")
        self.prev_next.addWidget(self.prev_button)
        self.next_button = QtWidgets.QPushButton(self.next_prev)
        self.next_button.setObjectName("next_button")
        self.prev_next.addWidget(self.next_button)
        self.gridLayout.addWidget(self.next_prev, 1, 2, 1, 1)
        self.labels = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.labels.sizePolicy().hasHeightForWidth())
        self.labels.setSizePolicy(sizePolicy)
        self.labels.setMaximumSize(QtCore.QSize(159, 16777215))
        self.labels.setStyleSheet("QGroupBox#labels{border:1px solid #828790}")
        self.labels.setObjectName("labels")
        self.label = QtWidgets.QVBoxLayout(self.labels)
        self.label.setObjectName("label")
        self.person_not_cheat_radio = QtWidgets.QRadioButton(self.labels)
        self.person_not_cheat_radio.setObjectName("person_not_cheat_radio")
        self.blur_radio = QtWidgets.QRadioButton(self.labels)
        self.blur_radio.setObjectName("blur_radio")
        self.person_cheat_radio = QtWidgets.QRadioButton(self.labels)
        self.person_cheat_radio.setObjectName("person_cheat_radio")
        
        # 调整标签位置
        self.label.addWidget(self.person_not_cheat_radio)
        self.label.addWidget(self.person_cheat_radio)
        self.label.addWidget(self.blur_radio)
        
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.label.addItem(spacerItem)
        self.label.setStretch(1, 2)
        self.gridLayout.addWidget(self.labels, 0, 2, 1, 1)

        self.img_preview_list = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.img_preview_list.sizePolicy().hasHeightForWidth())
        self.img_preview_list.setSizePolicy(sizePolicy)
        self.img_preview_list.setMaximumSize(QtCore.QSize(159, 16777215))
        self.img_preview_list.setStyleSheet("QListWidget#img_preview_list{border:1px solid #828790; background: #f0f0f0}")
        self.img_preview_list.setFrameShape(QtWidgets.QFrame.Box)
        self.img_preview_list.setObjectName("img_preview_list")
        self.gridLayout.addWidget(self.img_preview_list, 0, 3, 2, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setStyleSheet("QFrame#frame{border:1px solid #828790}")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 这里换成image_with_mouse_control的对象
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
        self.gridLayout.addWidget(self.frame, 0, 0, 2, 1)
        SmallLabelTool.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(SmallLabelTool)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 837, 23))
        self.menubar.setObjectName("menubar")
        self.menuopen = QtWidgets.QMenu(self.menubar)
        self.menuopen.setObjectName("menuopen")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        SmallLabelTool.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(SmallLabelTool)
        self.statusBar.setObjectName("statusBar")
        SmallLabelTool.setStatusBar(self.statusBar)
        self.action_open_img_dir = QtWidgets.QAction(SmallLabelTool)
        self.action_open_img_dir.setObjectName("action_open_img_dir")
        self.action_change_img_save_path = QtWidgets.QAction(SmallLabelTool)
        self.action_change_img_save_path.setObjectName("action_change_img_save_path")
        self.action_help = QtWidgets.QAction(SmallLabelTool)
        self.action_help.setObjectName("action_help")
        self.menuopen.addAction(self.action_open_img_dir)
        self.menuopen.addAction(self.action_change_img_save_path)
        self.menu.addAction(self.action_help)
        self.menubar.addAction(self.menuopen.menuAction())
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(SmallLabelTool)
        QtCore.QMetaObject.connectSlotsByName(SmallLabelTool)
        SmallLabelTool.setTabOrder(self.person_not_cheat_radio, self.blur_radio)
        SmallLabelTool.setTabOrder(self.blur_radio, self.person_cheat_radio)
        SmallLabelTool.setTabOrder(self.person_cheat_radio, self.prev_button)
        SmallLabelTool.setTabOrder(self.prev_button, self.next_button)
        SmallLabelTool.setTabOrder(self.next_button, self.img_preview_list)

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

        # 关闭标签按钮
        self.person_cheat_radio.setDisabled(True)
        self.person_not_cheat_radio.setDisabled(True)
        self.blur_radio.setDisabled(True)

    def retranslateUi(self, SmallLabelTool):
        _translate = QtCore.QCoreApplication.translate
        SmallLabelTool.setWindowTitle(_translate("SmallLabelTool", __appname__))
        self.prev_button.setText(_translate("SmallLabelTool", "上一张"))
        self.next_button.setText(_translate("SmallLabelTool", "下一张"))
        self.person_not_cheat_radio.setText(_translate("SmallLabelTool", "person_not_cheat"))
        self.blur_radio.setText(_translate("SmallLabelTool", "blur"))
        self.person_cheat_radio.setText(_translate("SmallLabelTool", "person_cheat"))
        self.menuopen.setTitle(_translate("SmallLabelTool", "文件"))
        self.menu.setTitle(_translate("SmallLabelTool", "帮助"))
        self.action_open_img_dir.setText(_translate("SmallLabelTool", "打开文件路径"))
        self.action_change_img_save_path.setText(_translate("SmallLabelTool", "改变图像保存路径"))
        self.action_help.setText(_translate("SmallLabelTool", "打开帮助窗口"))

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
        print('上一张')
        if self.img_dir is not None:
            index = self.img_list.index(self.img_name)
            if self.save_img() and index != 0:
                self.img_name = self.img_list[index - 1]
                self.set_img()

    def next_button_listener(self):
        print('下一张')
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
                    shutil.move(os.path.join(self.save_dir, labels[old_label], self.img_name),
                                os.path.join(self.save_dir, labels[label], self.img_name))
                except FileNotFoundError as e:
                    shutil.copy(os.path.join(self.img_dir, self.img_name), os.path.join(self.save_dir, labels[label]))
            # 如果一致, 但是没有图片, 也需要修改
            elif self.img_name not in os.listdir(os.path.join(self.save_dir, labels[label])):
                shutil.copy(os.path.join(self.img_dir, self.img_name), os.path.join(self.save_dir, labels[label]))
            return True
        return False

    def open_img_dir_listener(self):
        # 在当前窗口内打开文件对话窗口
        directory = QtWidgets.QFileDialog.getExistingDirectory(self.centralwidget, '请选择图片所在文件夹')
        print('打开文件夹:', directory)
        if directory != '':
            self.img_dir = directory
            self.person_cheat_radio.setDisabled(False)
            self.person_not_cheat_radio.setDisabled(False)
            self.blur_radio.setDisabled(False)

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
