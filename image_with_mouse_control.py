# encoding:utf8
# https://github.com/SmileJET/utils-for-python

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ImageWithMouseControl(QWidget):
    """
    point: 保存图片的左上角的位置
    img: 原图像
    scaled_img: 缩放后的图像
    first: 因为调用__init__函数时, 部件未渲染, 所以采取了曲线救国的方式
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.img = QPixmap()
        self.scaled_img = self.img
        self.first = True
        self.point = QPoint(0, 0)
        self.setStyleSheet('border: 1px solid')

    def adjust_image(self):
        h = self.img.height()
        w = self.img.width()
        h1 = self.size().height()
        w1 = self.size().width()

        if h < h1 and w < w1:
            self.scaled_img = self.img
        else:
            minh = min(h, h1)
            minw = min(w, w1)
            self.point = QPoint(0, 0)
            if minh < minw:
                self.scaled_img = self.img.scaledToHeight(minh)
            else:
                self.scaled_img = self.img.scaledToWidth(minw)

        self.point = QPoint(int(w1 / 2 - self.scaled_img.width() / 2), int(h1 / 2 - self.scaled_img.height() / 2))

    def paintEvent(self, e):
        # 初始化时图片为空
        if not self.img.isNull():
            painter = QPainter()
            painter.begin(self)
            # 绘制图片
            painter.drawPixmap(self.point, self.scaled_img)
            painter.end()

            if self.first:
                self.adjust_image()
                self.first = False
                self.update()

    def mouseMoveEvent(self, e):  # 重写移动事件
        if self.left_click:
            self._endPos = e.pos() - self._startPos
            self.point = self.point + self._endPos
            self._startPos = e.pos()
            self.repaint()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self._startPos = e.pos()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = False
        elif e.button() == Qt.RightButton:
            self.point = QPoint(0, 0)
            self.repaint()

    def wheelEvent(self, e):
        scale_pixel = 20
        r = int(self.scaled_img.width() / self.scaled_img.height())

        if e.angleDelta().y() < 0:
            # 放大图片, 向后滑
            # scaledToWidth只需要提供宽度, 高度在函数内完成计算
            self.scaled_img = self.img.scaledToWidth(self.scaled_img.width() - scale_pixel)
            # 图片从鼠标位置缩放
            new_w = e.x() - (self.scaled_img.width() * (e.x() - self.point.x())) / (self.scaled_img.width() + scale_pixel)
            new_h = e.y() - (self.scaled_img.height() * (e.y() - self.point.y())) / (self.scaled_img.height() + scale_pixel * r)
            self.point = QPoint(new_w, new_h)
            self.repaint()

        elif e.angleDelta().y() > 0:
            # 缩小图片, 向前滑
            self.scaled_img = self.img.scaledToWidth(self.scaled_img.width() + scale_pixel)
            new_w = e.x() - (self.scaled_img.width() * (e.x() - self.point.x())) / (self.scaled_img.width() - scale_pixel)
            new_h = e.y() - (self.scaled_img.height() * (e.y() - self.point.y())) / (self.scaled_img.height() - scale_pixel * r)
            self.point = QPoint(new_w, new_h)
            self.repaint()

    def resizeEvent(self, e):
        super().resizeEvent(e)
