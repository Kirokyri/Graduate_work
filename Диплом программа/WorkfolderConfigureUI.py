import sys
import os
import yadisk
from backup import Backup

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QPushButton, QTextEdit, QMainWindow, QDialog, QLabel, QLineEdit, QFileDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QHBoxLayout, QCheckBox, QVBoxLayout, QToolButton, QAbstractItemView
from PyQt5.QtCore import QSize, Qt

from config import Config

# Вызывается по кнопке 'Настройка рабочей папки' и после создания новой папки
# Принимает на вход список настроек папки.
# Содержит списки форматов файлов, которые можно выбрать для сохранения.
# Имеет кнопки "Выбрать все", ОК и Отмена. "Выбрать все" выбирает все или отменяет выбор всего.

class CheckableItem(QWidget):
    stateChangeSignal = pyqtSignal(str, bool)

    def __init__(self, label_text, parent=None):
        super().__init__(parent)

        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(QSize(15, 15))
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(50)
        self.label.setFixedHeight(15)

        self.checkbox.stateChanged.connect(self.handle_state_changed)

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.checkbox)

    def isChecked(self):
        return self.checkbox.isChecked()

    def checkItem(self):
        self.checkbox.setChecked(True)

    def uncheckItem(self):
        self.checkbox.setChecked(False)

    def setState(self, state):
        self.checkbox.setChecked(state)

    def handle_state_changed(self, state: bool):
        self.stateChangeSignal.emit(self.label.text(), state)



class CheckBoxListWidget(QListWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

    def addItem(self, label_text):
        item = QListWidgetItem(self)
        widget = CheckableItem(label_text)
        #item.setSizeHint(widget.sizeHint())
        item.setSizeHint(QSize(40, 25))
        self.setItemWidget(item, widget)
        super().addItem(item)
        #widget.stateChangeSignal.connect(self.handle_checkbox_state_changed)

    #def handle_checkbox_state_changed(self, label, state):
    #    print("Checkbox state changed:", label, state)
    def get_last_item(self) -> CheckableItem:
        count = self.count()
        if count > 0:
            return self.itemWidget(self.item(count - 1))

    def check_last_item(self):
        count = self.count()
        if count > 0:
            self.itemWidget(self.item(count - 1)).checkItem()
            


class ConfigureWorkfolderUI(QDialog):
    def __init__(self, config: Config, found_formats: list, parent=None) -> None:
        super(ConfigureWorkfolderUI, self).__init__(parent)
        self.config = config
        
        audio_formats = ['mp3', 'wma', 'wav', 'flac', 'aa', 'aac']
        video_formats = ['avi', 'mp4', 'wmv', 'webm', 'mkv', 'mov']
        image_formats = ['jpeg', 'jpg', 'png', 'webp', 'gif', 'bmp']
        text_formats = ['doc', 'docx', 'xls', 'xlsx', 'txt', 'pdf', 'odt']

        self.titles = []
        self.formats_checkbox_list = []
        self.formats_checkbox_list = self.init_lists(audio_formats, video_formats, image_formats, text_formats, found_formats)
        
        #self.select_all_list = []

        self.init_ui()


    def init_lists(self, audio, video, image, text, found):
        audio_checkbox = CheckBoxListWidget('Аудио-форматы')
        self.titles.append(audio_checkbox.title)
        audio_checkbox.addItem(audio_checkbox.title)
        audio_checkbox.get_last_item().stateChangeSignal.connect(self.select_all_changed)
        #self.select_all_list.append(audio_checkbox.get_last_item())
        for ext in audio:
            audio_checkbox.addItem(ext)
            if ext in self.config.get_formats():
                audio_checkbox.check_last_item()

        video_checkbox = CheckBoxListWidget('Видео-форматы')
        self.titles.append(video_checkbox.title)
        video_checkbox.addItem(video_checkbox.title)
        video_checkbox.get_last_item().stateChangeSignal.connect(self.select_all_changed)
        #self.select_all_list.append(video_checkbox.get_last_item())
        for ext in video:
            video_checkbox.addItem(ext)
            if ext in self.config.get_formats():
                video_checkbox.check_last_item()

        image_checkbox = CheckBoxListWidget('Форматы изображений')
        self.titles.append(image_checkbox.title)
        image_checkbox.addItem(image_checkbox.title)
        image_checkbox.get_last_item().stateChangeSignal.connect(self.select_all_changed)
        #self.select_all_list.append(image_checkbox.get_last_item())
        for ext in image:
            image_checkbox.addItem(ext)
            if ext in self.config.get_formats():
                image_checkbox.check_last_item()

        text_checkbox = CheckBoxListWidget('Текстовые форматы')
        self.titles.append(text_checkbox.title)
        text_checkbox.addItem(text_checkbox.title)
        text_checkbox.get_last_item().stateChangeSignal.connect(self.select_all_changed)
        #self.select_all_list.append(text_checkbox.get_last_item())
        for ext in text:
            text_checkbox.addItem(ext)
            if ext in self.config.get_formats():
                text_checkbox.check_last_item()

        found_checkbox = CheckBoxListWidget('Неизвестные форматы')
        self.titles.append(found_checkbox.title)
        found_checkbox.addItem(found_checkbox.title)
        found_checkbox.get_last_item().stateChangeSignal.connect(self.select_all_changed)
        #self.select_all_list.append(found_checkbox.get_last_item())
        for ext in found:
            if not ext in audio and not ext in video and not ext in image and not ext in text:
                found_checkbox.addItem(ext)
                if ext in self.config.get_formats():
                    found_checkbox.check_last_item()
        
        for ext in self.config.get_formats():
            if not ext in audio and not ext in video and not ext in image and not ext in text and not ext in found:
                found_checkbox.addItem(ext)
                found_checkbox.check_last_item()

        return([audio_checkbox, video_checkbox, image_checkbox, text_checkbox, found_checkbox])


    def init_ui(self):
        self.resize(1024, 400)
        #self.centralwidget = QtWidgets.QWidget(self)
        #self.centralwidget.setObjectName("centralwidget")

        main_layout = QVBoxLayout(self)
        upper_layout = QHBoxLayout()
        lower_layout = QHBoxLayout()
        lower_layout.setAlignment(Qt.AlignRight)

        main_layout.addLayout(upper_layout)
        main_layout.addLayout(lower_layout)
        
        for checkbox in self.formats_checkbox_list:
            upper_layout.addWidget(checkbox)
            #for item in checkbox:
            #    item.

        button1 = QToolButton()
        button1.setText('ОК')
        button1.setFixedSize(QSize(80, 25))
        button1.clicked.connect(self.confirm)
        button2 = QToolButton()
        button2.setText('Отмена')
        button2.setFixedSize(QSize(80, 25))
        button2.clicked.connect(self.cancel)

        lower_layout.addWidget(button1)
        lower_layout.addWidget(button2)

        self.show()
    
    def confirm(self):
        self.accept()

    def cancel(self):
        self.reject()

    def select_all_changed(self, title, state):
        print(f'Title {title} selected.')
        if title in self.titles:
            for checkbox in self.formats_checkbox_list:
                if title == checkbox.title:
                    count = checkbox.count()
                    for index in range(0, count):
                        widget = checkbox.itemWidget(checkbox.item(index))
                        widget.setState(state)


    def get_data(self) -> Config:
        new_config = Config()
        for checkbox in self.formats_checkbox_list:
            count = checkbox.count()
            for index in range(0, count):
                widget = checkbox.itemWidget(checkbox.item(index))
                if widget.isChecked() and not widget.label.text() in self.titles:
                    new_config.add_format(widget.label.text())
                    #print(f'{checkbox.title} {widget.label.text()}')
        return new_config
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #ex = ConfigureWorkfolderUI(Config())
    conf = Config()
    conf.add_format('wav')
    conf.add_format('txt')
    conf.add_format('unknwn')
    ex = ConfigureWorkfolderUI(conf, ['ppp', 'rrr', 'ddd'])
    sys.exit(app.exec_())