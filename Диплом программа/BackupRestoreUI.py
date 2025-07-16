import sys
import os
import yadisk
from backup import Backup

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QTextEdit, QMainWindow, QDialog, QLabel, QLineEdit, QFileDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal

# Вызывается по кнопке "Восстановить данные"
# Получает список бэкапов выбранной рабочей папки. 
# Предоставляет выбор бэкапа для восстановления.
# Отображает имеющиеся бэкапы
# Имеет кнопка ОК и Отмена.

class BackupResotoreUI(QDialog):
    sendDataSignal = pyqtSignal(Backup)
    def __init__(self, backups_list: list, parent=None) -> None:
        super(BackupResotoreUI, self).__init__(parent)
        self.backups = backups_list
        self.full_backup = Backup('Full backup', '', 0, '')
        self.backups.append(self.full_backup)
        self.init_ui()

    def init_ui(self):
        self.resize(500, 600)
        #self.centralwidget = QtWidgets.QWidget(self)
        #self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        # Кнопка ОК
        self.confirmButton = QtWidgets.QPushButton(self)
        self.confirmButton.setObjectName("confirmButton")
        self.confirmButton.setText('ОК')
        self.confirmButton.clicked.connect(self.confirm)
        self.gridLayout.addWidget(self.confirmButton, 3, 3, 1, 1)

        # Кнопка Отмена
        self.cancelButton = QtWidgets.QPushButton(self)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setText('Отмена')
        self.cancelButton.clicked.connect(self.cancel)
        self.gridLayout.addWidget(self.cancelButton, 4, 3, 1, 1)
    
        # Панель информации
        self.backupList = QtWidgets.QListWidget(self)
        self.backupList.setObjectName("backupList")
        self.gridLayout.addWidget(self.backupList, 1, 1, 4, 1)
        self.backupList.addItems([x.get_name() for x in self.backups])
        


        # Label
        self.label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 3)
        self.label.setText("Список резервных копий")

        #self.menubar = QtWidgets.QMenuBar(self)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        #self.menubar.setObjectName("menubar")
        #self.setMenuBar(self.menubar)
        #self.statusbar = QtWidgets.QStatusBar(self)
        #self.statusbar.setObjectName("statusbar")
        #self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.show()
    
    def confirm(self):
        self.accept()

    def cancel(self):
        self.reject()

    def get_input_value(self) -> Backup:
        for backup in self.backups:
            if backup.get_name() == self.backupList.currentItem().text():
                return backup
        #return self.backups[self.backups.index(self.backupList.currentItem().text())]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BackupResotoreUI([])
    sys.exit(app.exec_())