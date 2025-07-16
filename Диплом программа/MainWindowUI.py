# Разные библиотеки
import sys
import tempfile
import os
import yadisk
from zipfile import ZipFile
from hashlib import sha256
from datetime import datetime

# PyQt
from PyQt5.QtGui import QIcon, QFont, QCloseEvent
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QModelIndex, Qt, QDir
from PyQt5.QtWidgets import (QAbstractItemView, QTreeView, QApplication, QMainWindow,
                             QHeaderView, QDialog, QPushButton, QLineEdit, QComboBox,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                             QWidget, QToolButton, QLabel, QHBoxLayout, QFileSystemModel, QSpacerItem)

# Мои файлы
from myTreeItem import TreeItem
from workFolder import WorkFolder, WorkFolderFile, load_workfolders_from_xml, save_workfolders_to_xml
from workFolderTree import WorkFolderTree
from errorHandler import ErrorHandler
from WorkFolderUI2 import WorkFolderUI, ChangeList
from AuthenticationScreen import Authenticate
from backup import Backup
from BackupRestoreUI import BackupResotoreUI
from WorkfolderConfigureUI import ConfigureWorkfolderUI

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self):
        super(QFileSystemModel, self).__init__()
 
        self.horizontalHeaders = [''] * 4
        self.setHeaderData(0, Qt.Horizontal, "Column 0")
        self.setHeaderData(1, Qt.Horizontal, "Column 1")

    def data(self, index, role):
        if role == Qt.DisplayRole and index.column() == 2:  # Предполагаем, что размер в байтах
            file_info = self.fileInfo(index)
            return file_info.size()
        return super().data(index, role)
 
    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)
 
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except:
                pass
        return super().headerData(section, orientation, role)


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomDialog, self).__init__(parent)
        layout = QVBoxLayout()

        buttonLayout = QHBoxLayout()

        label = QLabel(text="Имя новой папки:")
        self.main_font = QFont('Times New Roman', 14)
        self.setStyleSheet("QLabel { background-color: white }")
        label.setFont(self.main_font)

        self.line_edit = QLineEdit(self)
        self.line_edit.setFont(self.main_font)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)

        okButton = QPushButton("ОК", self)
        cancelButton = QPushButton("Отмена", self)

        okButton.clicked.connect(self.okButtonClicked)
        cancelButton.clicked.connect(self.cancelButtonClicked)

        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def okButtonClicked(self):
        self.accept()

    def cancelButtonClicked(self):
        self.reject()
    
    def get_input_value(self):
        return self.line_edit.text()


class FileTreeViewer(QMainWindow):
    item_selected_signal = pyqtSignal()
    update_view_signal = pyqtSignal()
    update_on_upload_signal = pyqtSignal(str)
    errorHandler = ErrorHandler()
    workfolder_deleted_signal = pyqtSignal()
    #cloud_path_root = '/Folder'
    cloud_path_root = ''
    app_folder = 'disk:/App'
    work_folder_list_file = 'data/WorkFolders.xml'

    def __init__(self, y: yadisk.YaDisk):# root: TreeItem, y: yadisk.YaDisk):
        super().__init__()
        self.show()
        self.y = y

        self.root = TreeItem(y.get_meta(self.cloud_path_root, limit=0))
        build_hierarchy(self.root, self.app_folder)
        self.app_folder_root = TreeItem(y.get_meta(self.app_folder, limit=0))
        self.root_work_folder_tree = WorkFolderTree(WorkFolder(self.cloud_path_root, self.root.get_name()), self.root)
        self.work_folder_tree_map = {}       # Соответствие между пунктами списка папок и объектами папок.
        self.work_folder_tree_map[self.root_work_folder_tree.get_name()] = self.root_work_folder_tree
        self.work_folder_tree_list = []                                                                                     
        self.current_selected_work_folder_tree = self.root_work_folder_tree
        self.item_map = {}
        #self.root = root
        #self.current_selected_cloud_item = self.root
        #self.current_selected_treeWidget = self.tree_widget_right.item
        #self.current_selected_local_item = 
        
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Две панели файловой системы')
        self.setGeometry(100, 100, 1600, 800)

        # Левое дерево
        
        self.tree_widget_left = QTreeWidget(self)
        self.tree_widget_left.setHeaderLabels(['Имя', 'Тип', 'Размер', 'Дата создания', 'Дата изменения'])
        self.tree_widget_left.setRootIsDecorated(True)
        self.tree_widget_left.setAlternatingRowColors(True)
        self.tree_widget_left.setStyleSheet("QTreeWidget::item { border-bottom: 1px solid black; border-right: 1px dark grey; }")
        self.tree_widget_left.itemSelectionChanged.connect(self.handle_item_selection_left)
        self.item_selected_signal.connect(self.handle_item_selected_signal)                                       ## При выборе строки в дереве возвращается объект TreeItem
        #self.update_view_signal.connect(self.handle_update_view_signal)
        self.update_on_upload_signal.connect(self.handle_update_on_upload_signal)
        #self.workfolder_deleted_signal.connect(self.reload_app_folder)
        
        
        self.tree_widget_left.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree_widget_left.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree_widget_left.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree_widget_left.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        left_scroll_bar = self.tree_widget_left.horizontalScrollBar()
        #left_scroll_bar.setStyleSheet("QScrollBar:horizontal { border: 2px solid grey; background: lightgray; height: 15px; margin: 0px 15px 0 15px; }")
        left_scroll_bar.setSingleStep(20)
        self.tree_widget_left.setAnimated(True)
        self.tree_widget_left.setAllColumnsShowFocus(False)

        self.tree_widget_left.setStyleSheet("""
            QTreeWidget::item:selected {
                background-color: lightblue;
                color: black; 
            }
        """)
        
        # Настройка ширины столбцов
        for column in range(self.tree_widget_left.columnCount()):
            #self.tree_widget_left.resizeColumnToContents(column)
            self.tree_widget_left.setColumnWidth(column, 300)
        
        # Построение дерева
        self.build_tree(self.tree_widget_left, self.root)

        '''
        # Правое дерево
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath('')
        self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

        self.tree_widget_right = QTreeWidget(self)
        self.tree_widget_right.setHeaderLabels(['Имя', 'Тип'])
        self.tree_widget_right.setRootIsDecorated(True)
        self.tree_widget_right.setAlternatingRowColors(True)
        self.tree_widget_right.setStyleSheet("QTreeWidget::item { border-bottom: 1px solid black; }")
        self.tree_widget_right.itemSelectionChanged.connect(self.on_item_selected_right)
        self.tree_widget_right.setAllColumnsShowFocus(False)

        self.tree_widget_right.setModel(self.file_model)
        self.tree_widget_right.setRootIndex(self.file_model.index(''))
        self.tree_widget_right.setStyleSheet("""
            QTreeWidget::item:selected {
                background-color: lightblue;
                color: black; 
            }
        """)
        '''
        # Правое дерево
        self.file_model = QFileSystemModel()
        #self.file_model = CustomFileSystemModel()
        #self.file_model.setRootPath('')
        file_model_root_index = self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setHeaderData(4, Qt.Horizontal, "Новый столбец")
        self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        
        self.tree_widget_right = QTreeView(self)
        self.tree_widget_right.setModel(self.file_model)

        

        columns_to_show = [
            (0, "Имя файла"),
            (1, "Размер"),
            (2, "Тип"),
            (3, "Дата модификации"),
        ]

        header = QHeaderView(Qt.Orientation.Vertical, self.tree_widget_left)

        self.tree_widget_right.header().selectAll()

        #for column, header_text in columns_to_show:
            #self.file_model.setHeaderData(column, Qt.Orientation.Vertical, str(header_text).format("0"))
            #self.tree_widget_right.setHeader(header)
            #self.tree_widget_right.showColumn(column)


        #self.tree_widget_right.header().hideSection(1)
        #self.tree_widget_right.header().hideSection(2)
        #self.tree_widget_right.header().hideSection(3)
        #self.file_model.setHeaderData(0, Qt.Orientation.Horizontal, "Имя")
        #self.file_model.setHeaderData(1, Qt.Orientation.Horizontal, "Тип")
        #for i in range(1, 2):
        #    self.tree_widget_right.setColumnWidth(i, 500)
        #    self.file_model.setHeaderData(i, Qt.Orientation.Horizontal, 'Column {}'.format(i))
        #self.file_model.setHeaderData(0, Qt.Orientation.Horizontal, 'Column {}'.format("0"))
        #self.tree_widget_right.setHeader()
        #self.tree_widget_right.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        #self.tree_widget_right.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        
        self.tree_widget_right.setRootIndex(self.file_model.index(''))  # Установка корневой директории
        self.tree_widget_right.setRootIsDecorated(True)
        self.tree_widget_right.setAlternatingRowColors(True)
        self.tree_widget_right.setStyleSheet("QTreeWidget::item { border-bottom: 1px solid black; }")
        #self.tree_widget_right.selectionChanged.connect(self.on_item_selected_right)
        self.tree_widget_right.setAllColumnsShowFocus(False)
        self.tree_widget_right.setStyleSheet("""
            QTreeWidget::item:selected {
                background-color: lightblue;
                color: black; 
            }
        """)

        self.tree_widget_right.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree_widget_right.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree_widget_right.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.tree_widget_right.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        ridght_scroll_bar = self.tree_widget_right.horizontalScrollBar()
        ridght_scroll_bar.setSingleStep(20)
        selection_model = self.tree_widget_right.selectionModel()
        selection_model.selectionChanged.connect(self.on_item_selected_right)

        #self.tree_widget_left.expandAll()

        
        self.tree_widget_right.setColumnWidth(0, 200)
        for column in range(1, self.file_model.columnCount(file_model_root_index)):
            self.tree_widget_right.setColumnWidth(column, 75)


        # Заполняем деревья данными из списка полных путей
        # for item in self.item_list:
        #     self.add_file_to_tree(self.tree_widget_left, item)
        #     self.add_file_to_tree(self.tree_widget_right, item)

        

        # Строка пути
        self.main_font = QFont('Times New Roman', 14)
        self.setStyleSheet("QLabel { background-color: lightgrey }")        # Все label имеют свето-серый цвет
        self.address_label_left = QLabel("Путь")                            ## TODO: настроить шрифт
        self.address_label_left.setFont(self.main_font)
        self.address_label_right = QLabel("Путь")
        self.address_label_right.setFont(self.main_font)

        

        # Кнопки со стрелками
        arrow_left_button = QToolButton()
        arrow_left_button.setIcon(QIcon('data/icons/left_arrow.png'))
        arrow_left_button.setToolTip("Загрузить")
        arrow_left_button.clicked.connect(self.upload_to_cloud)

        arrow_right_button = QToolButton()
        arrow_right_button.setIcon(QIcon('data/icons/right_arrow.png'))
        arrow_right_button.setToolTip("Скачать")
        arrow_right_button.clicked.connect(self.download_from_cloud)

        # Кнопка обновления
        reload_view_button = QToolButton()
        reload_view_button.setIcon(QIcon('data/icons/reload_button.png'))
        reload_view_button.setToolTip("Обновить    | F5")
        reload_view_button.clicked.connect(self.reload_tree)
        reload_view_button.setShortcut("F5")

        # Кнопка новой папки
        new_dir_button = QToolButton()
        new_dir_button.setIcon(QIcon('data/icons/add_folder.png'))
        new_dir_button.setToolTip("Создать папку    | Ctrl+N")
        new_dir_button.clicked.connect(self.add_folder)
        new_dir_button.setShortcut("Ctrl+N")

        # Кнопка удаления папки
        remove_dir_button = QToolButton()
        remove_dir_button.setToolTip("Удалить    | Ctrl+D")
        remove_dir_button.setIcon(QIcon("data/icons/delete_icon.png"))
        remove_dir_button.clicked.connect(self.remove_file_or_folder)
        remove_dir_button.setShortcut("Ctrl+D")

        # Кнопка создания бэкапа
        make_backup_button = QToolButton()
        make_backup_button.setToolTip("Создать резервную копию    | Ctrl+P")
        make_backup_button.setIcon(QIcon("data/icons/create_backup.png"))
        make_backup_button.setText('Создать копию')
        make_backup_button.clicked.connect(self.create_incremental_backup)
        make_backup_button.setShortcut("Ctrl+P")

        # Кнопка восстановления бэкапа
        restore_backup_button = QToolButton()
        restore_backup_button.setToolTip("Восстановить резервную копию    | Ctrl+R")
        restore_backup_button.setIcon(QIcon("data/icons/restore_backup.png"))
        restore_backup_button.setText('Восстановить копию')
        restore_backup_button.clicked.connect(self.restore_backup)
        restore_backup_button.setShortcut("Ctrl+R")

        # Кнопка настройки рабочей папки
        configure_workfolder_button = QToolButton()
        configure_workfolder_button.setToolTip("Настройка рабочей папки")
        configure_workfolder_button.setIcon(QIcon("data/icons/configure_folder.png"))
        configure_workfolder_button.setText('Настройка рабочей папки')
        configure_workfolder_button.clicked.connect(self.configure_workfolder)


        # Выпадающий список рабочих папок
        self.workFolderBox = QComboBox()
        self.workFolderBox.setObjectName("workFolderBox")
        self.workFolderBox.setFixedSize(250, 20)
        self.workFolderBox.setToolTip("Список рабочих папок")

        self.workFolderBox.addItem(self.root_work_folder_tree.get_name())
        self.initial_load_work_folders()
        self.workFolderBox.setCurrentIndex(0)
        self.workFolderBox.currentIndexChanged.connect(self.handle_work_folder_box_selection)


        # Меню бар
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Файл")
        self.exit_action = file_menu.addAction("Выход")
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        self.reload_action = file_menu.addAction("Обновить")
        #self.reload_action.setShortcut("F5")
        self.reload_action.triggered.connect(self.reload_tree)

        self.save_folder_action = file_menu.addAction("Сохранить")
        self.save_folder_action.setShortcut("Ctrl+S")
        self.save_folder_action.triggered.connect(self.saveFolders)

        self.folder_setting_action = file_menu.addAction("Создание и удаление рабочих папок")
        self.folder_setting_action.triggered.connect(self.init_workfolder_UI)

        # Настройка выкладки
        verticalMainLayout = QVBoxLayout()

        hLayout1 = QHBoxLayout()
        hLayout1.addWidget(reload_view_button)
        hLayout1.addWidget(new_dir_button)
        hLayout1.addWidget(remove_dir_button)
        hLayout1.addWidget(make_backup_button)
        hLayout1.addWidget(restore_backup_button)
        hLayout1.addWidget(self.workFolderBox)
        hLayout1.addWidget(configure_workfolder_button)
        hLayout1.setAlignment(Qt.AlignLeft)

        leftLayot = QVBoxLayout()
        #leftLayot.addWidget(reload_view_button)
        leftLayot.addWidget(self.address_label_left)
        leftLayot.addWidget(self.tree_widget_left)
        

        buttonLayout = QVBoxLayout()
        buttonLayout.addSpacing(400)
        buttonLayout.addWidget(arrow_left_button)
        buttonLayout.addWidget(arrow_right_button)
        buttonLayout.addSpacing(400)

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.address_label_right)
        rightLayout.addWidget(self.tree_widget_right)
        
        hLayout2 = QHBoxLayout()
        hLayout2.addLayout(leftLayot)
        hLayout2.addLayout(buttonLayout)
        hLayout2.addLayout(rightLayout)

        verticalMainLayout.addLayout(hLayout1)
        verticalMainLayout.addLayout(hLayout2)
        

        central_widget = QWidget()
        central_widget.setLayout(verticalMainLayout)
        self.setCentralWidget(central_widget)


# ================ BACKUP BLOCK ===============================================

    @pyqtSlot()
    def create_incremental_backup(self, dialog_call = False):
        if self.current_selected_work_folder_tree == self.root_work_folder_tree:
            self.errorHandler.handle('Error making backup: workfolder must be selected.')
            return
        
        if dialog_call:
            # TODO: сделать вызов с кнопки с вызовом диалога на ввод имени бэкапа.
            new_name = 'Получаем имя из диалога'
        else:
            new_name = datetime.__format__(datetime.now(), "%d-%m-%Y")

        workFolder = self.current_selected_work_folder_tree.get_work_folder()
        workFolderFiles = workFolder.get_files().copy()

        files_to_add = []   # пути файлов, которые нужно добавить
        deleted_files = []  # пути удаленных файлов
        last_number = 0
        for backup in workFolder.get_sorted_backups_list():
            if backup.get_number() > last_number: last_number = backup.get_number()

            backup_files = backup.get_files()
            backup_deleted_files = backup.get_deleted_files()

            files_to_remove = []
            for file in workFolderFiles:
                local_path = file.get_local_path()
                cloud_path = f'{workFolder.get_backups_path()}/{backup.get_number()}/{os.path.basename(local_path)}'
                if not os.path.exists(local_path):
                    if local_path in backup_deleted_files:
                        files_to_remove.append(file)
                        if local_path in deleted_files:
                            deleted_files.remove(local_path)
                        #deleted_files.append(local_path)           # TODO: Неправильно работает с удаленными файлами.
                        continue
                    else:
                        if not local_path in deleted_files:
                            deleted_files.append(local_path)
                        continue
                
                if local_path not in backup_files:
                    continue

                cloud_hash = self.y.get_meta(cloud_path)['sha256']
                local_hash = calculate_sha256(local_path)

                if not local_hash == cloud_hash:
                    files_to_add.append(local_path)
                files_to_remove.append(file)

            for file in files_to_remove:
                workFolderFiles.remove(file)

        # Сверка оставшихся файлов с полным бэкапом.
        if not len(workFolderFiles) == 0:
            for file in workFolderFiles:
                local_path = file.get_local_path()
                cloud_path = file.get_cloud_path()

                cloud_hash = self.y.get_meta(cloud_path)['sha256']
                local_hash = calculate_sha256(local_path)
                if not local_hash == cloud_hash:
                    files_to_add.append(local_path)


        if len(files_to_add) == 0:
            self.errorHandler.handle('New backup is not needed.')
            return
        
        last_number += 1
        new_backup = Backup(name=new_name + ' ' + str(last_number), path=f'{workFolder.get_backups_path()}/{last_number}', number=last_number, creation=datetime.now())
        # Получаем список файлов, которые нужно добавить в новый бэкап и список файлов, которые были удалены.
        for file in files_to_add:
            new_backup.add_file(file)
        for file in deleted_files:
            new_backup.add_deleted_file(file)
        
        self._upload_backup(new_backup)


    def _upload_backup(self, backup: Backup):
        try:
            self.y.mkdir(backup.get_path())
        except Exception as e:
            self.errorHandler.handle(f'Error making backup dir: {e}')
            return
        
        self.current_selected_work_folder_tree.add_backup(backup)
        for file in backup.get_files():
            name = os.path.basename(file)
            try:
                self.y.upload(file, backup.get_path() + f'/{name}')
            except Exception as e:
                self.errorHandler.handle(f'Error uploading file to backup: {e}')
    

    def _restore_files(self, files):
        for file in files:
            local_path, cloud_path = file
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception as e:
                    self.errorHandler.handle(f'Error removing file: {e}')

            try:
                self.y.download(cloud_path, local_path)
            except Exception as e:
                self.errorHandler.handle(f'Error downloading file: {e}')
        self.errorHandler.handle('Backup restoring complete.')
        

    @pyqtSlot()
    def restore_backup(self):
        '(Восстановление туда же, откуда сохранялось и восстановление в определенную папку)'
        '(Функция получения списка удаленных файлов до нужной даты)(Функция удаления файла и скачивания)'

        '1) Берем бэкап, который нужно восстановить.'
        '2) Восстанавливаем из него файлы. Записываем восстановленные файлы в список. Записываем список удаленных файлов.'
        '3) Проверяем файлы из следующего бэкапа. Если они не были уже восстановлены и их нет в списке удаленных, то восстанавливаем. Добавляем к списку восстановленных. Добавляем список удаленных'
        '4) Дошли до полной копии. Восстанавливаем только те, которые не были восстановлены или удалены.'

        workFolder = self.current_selected_work_folder_tree.get_work_folder()
        workFolderFiles = workFolder.get_files().copy()

        dialog = BackupResotoreUI(self.current_selected_work_folder_tree.get_work_folder().get_sorted_backups_list(), self)
        result = dialog.exec_()

        if result == QDialog.Rejected:
            return
        
        selected_backup = dialog.get_input_value()
        #print(f'SELECTED BACKUP: {selected_backup.get_name()} | {selected_backup.get_path()}')
        files_to_restore = []       # хранит пары (локальный путь, облачный путь)
        deleted_files = []
        tmp_filepath_list = []
        if not selected_backup.get_name() == 'Full backup':
            for backup in workFolder.get_sorted_backups_list(until_date=datetime.strptime(selected_backup.get_creation_time(), Backup.datetime_format)):
                deleted_files += backup.get_deleted_files()
                for file in backup.get_files():
                    local_path = file
                    filename = os.path.basename(local_path)
                    cloud_path = f'{workFolder.get_backups_path()}/{backup.get_number()}/{filename}'

                    if not local_path in tmp_filepath_list and not local_path in deleted_files:
                        tmp_filepath_list.append(local_path)
                        files_to_restore.append((local_path, cloud_path))
        
        # Просмотрели все бэкапы. Имеем список файлов для восстановления
        # Смотрим оставшийся полный бэкап
        for file in workFolderFiles:
            local_path = file.get_local_path()
            cloud_path = file.get_cloud_path()

            if not local_path in tmp_filepath_list and not local_path in deleted_files:
                tmp_filepath_list.append(local_path)
                cloud_hash = self.y.get_meta(cloud_path)['sha256']
                local_hash = calculate_sha256(local_path)
                if not local_hash == cloud_hash:
                    files_to_restore.append((local_path, cloud_path))


        #print(f'Restoring backup. Files to restore: {files_to_restore}')
        self._restore_files(files_to_restore)



# ================ MISC BLOCK ===============================================      
    def closeEvent(self, event = QCloseEvent()):
        self.saveFolders()
        ErrorHandler.handle("===================== Session end ===============================================")
        # Вызов метода closeEvent базового класса
        super().closeEvent(event)


# ================ SELECTION AND SIGNAL HANDLING BLOCK ===============================================
    def handle_work_folder_box_selection(self):
        workFolderTree = self.work_folder_tree_map.get(self.workFolderBox.currentText())
        workFolder = workFolderTree.get_work_folder()
        workFolderRoot = workFolderTree.get_root()
        self.current_selected_work_folder_tree = workFolderTree

        self.tree_widget_left.clear()
        self.build_tree(self.tree_widget_left, workFolderRoot)

        self.current_selected_treeWidget: QTreeWidgetItem = self.tree_widget_left.topLevelItem(0)
        self.current_selected_cloud_item: TreeItem = self.item_map.get(id(self.current_selected_treeWidget))
        self.address_label_left.setText(self.current_selected_cloud_item.get_path())

    @pyqtSlot()
    def handle_item_selection_left(self):
        selected_items = self.tree_widget_left.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            item_id = id(selected_item)

            # Используем идентификатор для получения объекта TreeItem из словаря
            tree_item = self.item_map.get(item_id)
            self.current_selected_treeWidget: QTreeWidgetItem = selected_item
            self.tmp_selected_treeWidget: QTreeWidgetItem = selected_item
            self.current_selected_cloud_item: TreeItem = tree_item
            self.tmp_selected_cloud_item: TreeItem = tree_item

            #print("Selected left: " + tree_item.get_path())
            if tree_item:
                self.item_selected_signal.emit()

    def handle_item_selected_signal(self):                                              ## Signal handler
        #self.current_selected_treeWidget.takeChildren()
        self.address_label_left.setText(self.current_selected_cloud_item.get_path())

    @pyqtSlot()
    def on_item_selected_right(self):
        index = self.tree_widget_right.currentIndex()
        self.current_selected_local_item: QModelIndex = index
        self.tmp_selected_local_item: QModelIndex = index
        full_path = self.file_model.filePath(index)
        self.address_label_right.setText(full_path)
        #print("Выбран элемент:", full_path)


# ================ VIEW BLOCK ===============================================
    @pyqtSlot()
    def reload_tree(self):
        self.tree_widget_left.clear()
        self.item_map = {}

        root = TreeItem(self.y.get_meta(self.cloud_path_root, limit=0))
        if not self.current_selected_work_folder_tree == self.root_work_folder_tree:
            build_hierarchy(root, self.app_folder, self.current_selected_work_folder_tree.get_backups_path())
        else:
            build_hierarchy(root, self.app_folder)
        #root.set_parent(self.app_folder_root)
        self.root = root

        self.build_tree(self.tree_widget_left, self.root)
        self.tree_widget_left.expandItem(self.tree_widget_left.itemFromIndex(self.tree_widget_left.rootIndex()))

    def build_tree(self, tree_widget, tree_item: TreeItem):
        datetime_format = "%d-%m-%Y %H:%M"
        if tree_item.get_type() == 'file':
            item = QTreeWidgetItem(tree_widget, [tree_item.get_name(), tree_item.get_mime_type(), 
                                                 tree_item.get_size(), tree_item.get_created().strftime(datetime_format), tree_item.get_modified().strftime(datetime_format)])
        else:
            item = QTreeWidgetItem(tree_widget, [tree_item.get_name(), 'Папка', 
                                                 tree_item.get_size(), tree_item.get_created().strftime(datetime_format), tree_item.get_modified().strftime(datetime_format)])
        # TODO: Разные ли id у предметов из разных рабочих папок?
        self.item_map[id(item)] = tree_item
        # Рекурсивно добавляем дочерние элементы
        for child_item in tree_item.child_items:
            self.build_tree(item, child_item)

    def update_on_file_upload(self, cloud_path):
        new_item = TreeItem(self.y.get_meta(cloud_path, limit=0))
        new_tree_widget = QTreeWidgetItem(None, [new_item.get_name(), new_item.get_mime_type()])

        parent_item = self.current_selected_cloud_item
        tree_widget = self.current_selected_treeWidget
        
        if parent_item.is_file():
            parent_item = parent_item.get_parent()
            tree_widget = tree_widget.parent()

        parent_item.add_child(new_item)
        tree_widget.addChild(new_tree_widget)

        self.item_map[id(new_tree_widget)] = new_item

        #if new_item.is_dir():
            #self.tmp_selected_cloud_item = new_item
            #self.tmp_selected_treeWidget = new_tree_widget

        
        #print('updated: ' + cloud_path)

    def update_on_folder_upload(self, cloud_path):
        parent_item = self.current_selected_cloud_item
        tree_widget = self.current_selected_treeWidget
        if parent_item.is_file():
            parent_item = parent_item.get_parent()
            tree_widget = tree_widget.parent()

        new_folder_item = TreeItem(self.y.get_meta(cloud_path, limit=0))

        build_hierarchy(new_folder_item)
        self.build_tree(tree_widget, new_folder_item)
        parent_item.add_child(new_folder_item)
        #print("Updated")

    # Connected to update_on_upload_signal. Emitted in def upload_to_cloud
    def handle_update_on_upload_signal(self, cloud_path):
        if self.y.is_dir(cloud_path):
            self.update_on_folder_upload(cloud_path)
        else:
            self.update_on_file_upload(cloud_path)

    def handle_update_on_delete_signal(self):
        print('deleted')

# ================ CLOUD BLOCK ===============================================
    def _get_folder_children(self, path):
        dir_model = QDir()
        dir_model.cd(path)
        children_list = [child for child in dir_model.entryInfoList() if child.absolutePath() == dir_model.path()]
        return children_list
    

    def _construct_paths(self):
        #local_path = self.address_label_right.text()
        #cloud_path = self.address_label_left.text()
        local_path = self.file_model.filePath(self.current_selected_local_item)
        file_name = self.file_model.fileName(self.current_selected_local_item)
        cloud_path = self.current_selected_cloud_item.get_path()

        if self.current_selected_cloud_item.is_file():
            parent_item = self.current_selected_cloud_item.get_parent()
            cloud_path = parent_item.get_path() + f'/{file_name}'
        else:
            cloud_path += f'/{file_name}'
        return local_path, cloud_path
    
    def _upload_file_to_cloud(self, local_path, cloud_path):
        try:
            self.y.upload(local_path, cloud_path)
            if not self.current_selected_work_folder_tree == self.root_work_folder_tree:
                self.current_selected_work_folder_tree.add_file(WorkFolderFile(local_path, os.path.basename(local_path), cloud_path))
        except Exception as e:
            self.errorHandler.handle(f"Error uploading file: {e}")
            #print(f"Error uploading file: {e}")

    def _upload_folder_to_cloud(self, local_path, cloud_path):
        try:
            self.y.mkdir(cloud_path)
        except Exception as e:
            self.errorHandler.handle(f"Error mkdir: {e}")
            #print(f"Error mkdir: {e}")
        local_children = self._get_folder_children(local_path)#(self.file_model.filePath(self.current_selected_local_item))
        for child in local_children:
            new_cloud_path = cloud_path + f'/{child.fileName()}'
            if self.file_model.isDir(self.file_model.index(child.absoluteFilePath())):
                self._upload_folder_to_cloud(child.absoluteFilePath(), new_cloud_path)
            else:
                self._upload_file_to_cloud(child.absoluteFilePath(), new_cloud_path)
        
    @pyqtSlot()
    def upload_to_cloud(self):
        local_path, cloud_path = self._construct_paths()
        print(f'Uploading {local_path} to {cloud_path}.')
        if self.file_model.isDir(self.current_selected_local_item):
            if  not self.current_selected_work_folder_tree == self.root_work_folder_tree:
                self.current_selected_work_folder_tree.add_folder(local_path)
            self._upload_folder_to_cloud(local_path, cloud_path)
        else:
            self._upload_file_to_cloud(local_path, cloud_path)
        print("Upload complete.")
        self.update_on_upload_signal.emit(cloud_path)
        

    @pyqtSlot()
    def download_from_cloud(self):
        local_path = self.address_label_right.text()
        cloud_path = self.address_label_left.text()
        
        if self.current_selected_cloud_item.is_file():
            if self.file_model.isDir(self.current_selected_local_item):
                local_path += f'/{self.current_selected_cloud_item.get_name()}'
            else:
                local_path = self.file_model.filePath(self.current_selected_local_item.parent()) + f'/{self.current_selected_cloud_item.get_name()}'
        else:
            if self.file_model.isDir(self.current_selected_local_item):
                local_path = self.file_model.filePath(self.current_selected_local_item)
            else:
                local_path = self.file_model.filePath(self.current_selected_local_item.parent())


        temp_folder = tempfile.mkdtemp()

        # Скачиваем файл
        download_path = os.path.join(temp_folder, 'downloaded_file.zip')
        print(download_path)

        cloud_path = _cloud_path_fixer(cloud_path)

        try:
            self.y.download(cloud_path, download_path)
        except Exception as e:
            self.errorHandler.handle(f"Error downloading file: {e}")
            #print(f"Error downloading file: {e}")

        # TODO: Нельзя работать со скачанной директорией пока не закроется программа.
        with ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(local_path)

        os.remove(download_path)
        os.rmdir(temp_folder)

    @pyqtSlot()
    def add_folder(self):
        new_folder_name = ''
        cloud_path = ''

        dialog = CustomDialog(self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            new_folder_name = dialog.get_input_value()

        if new_folder_name == '':
            return
        if self.current_selected_cloud_item.is_dir():
            cloud_path = self.current_selected_cloud_item.get_path() + f'/{new_folder_name}'
        else:
            cloud_path = self.current_selected_cloud_item.get_parent().get_path() + f'/{new_folder_name}'
        
        cloud_path = _cloud_path_fixer(cloud_path)

        try:
            self.y.mkdir(cloud_path)
            self.update_on_upload_signal.emit(cloud_path)
        except Exception as e:
            self.errorHandler.handle(f'Failed mkdir: {e}. {cloud_path}')
            #print(f'Failed mkdir: {e}')

    # TODO: ПЕРЕДЕЛАТЬ!!! 
    # При удалении папки должна удаляться папка и все ее дети.
    # При удалении из рабочей папки файлы также должны пропадать из списка файлов рабочей папки.
    @pyqtSlot()
    def remove_file_or_folder(self):
        cloud_path = self.current_selected_cloud_item.get_path()
        treeItem = self.current_selected_treeWidget

        if self.current_selected_work_folder_tree == self.root_work_folder_tree:
            try:
                self.y.remove(cloud_path)
                treeItem.parent().removeChild(treeItem)
            except Exception as e:
                self.errorHandler.handle(f'Error removing dir: {e}')

# ================ WORKFOLDER BLOCK ===============================================
    def initial_load_work_folders(self):
        if not os.path.exists(self.work_folder_list_file):
            print(f"File {self.work_folder_list_file} doesn't exist")
            return False

        if os.path.getsize(self.work_folder_list_file) == 0:
            print(f"File {self.work_folder_list_file} is empty")
            return False
        
        work_folder_list = load_workfolders_from_xml(self.work_folder_list_file)
        name_list = []
        for workFolder in work_folder_list:
            workFolder = WorkFolder(work_folder=workFolder)
            
            workFolderRoot = TreeItem(self.y.get_meta(workFolder.get_path(), limit=0))
            build_hierarchy(workFolderRoot)
            workFolderTree = WorkFolderTree(workFolder, workFolderRoot)

            name_list.append(workFolder.get_name())
            self.work_folder_tree_map[workFolder.get_name()] = workFolderTree
            self.work_folder_tree_list.append(workFolderTree)

        self.workFolderBox.addItems(name_list)
        #print(name_list)
        return True
    
    def saveFolders(self):
        folder_list = []
        for treeFolder in self.work_folder_tree_list:
            folder_list.append(treeFolder.get_work_folder())
        
        try:
            save_workfolders_to_xml(folder_list, self.work_folder_list_file)
        except Exception as e:
            print(f'Error saving workfolders: {e}')
        #save_workfolders_to_xml(folder_list, 'tmpXML.xml')
        

    def init_workfolder_UI(self):
        #def _getFolderNameList(self):

        workFolderList = list(self.work_folder_tree_map.keys())
        workFolderUI = WorkFolderUI(workFolderList=workFolderList, parent=self)
        workFolderUI.sendDataSignal.connect(self._recieveData)
        workFolderUI.show()

    def _recieveData(self, status: int, changeList: ChangeList):     # ()
        if status == 0:
            return
        
        toCreateList = changeList.return_data().get('Create')
        toDeleteList = changeList.return_data().get('Delete')
        
        for item in toCreateList:
            path = f'{self.app_folder}/{item}'
            try:
                self.y.mkdir(path)
                self.workFolderBox.addItem(item)
                folderTree = WorkFolderTree(WorkFolder(path, item), TreeItem(self.y.get_meta(path, limit=0)))
                self.y.mkdir(folderTree.get_backups_path())
                self.work_folder_tree_list.append(folderTree)
                self.work_folder_tree_map[item] = folderTree

            except Exception as e:
                self.errorHandler.handle(f'Error making directory: {e}')

        for item in toDeleteList:
            #self.remove_work_folder(folder_path = self.work_folder_tree_map.get(item).get_path())
            self.remove_work_folder(item)


    # Удаление всех упоминаний папки из списков, в которых она хранится
    def _delete_work_folder(self, work_folder: WorkFolderTree):
        try:
            self.work_folder_tree_map.pop(work_folder.get_name())
            self.work_folder_tree_list.pop(self.work_folder_tree_list.index(work_folder))
            self.workFolderBox.removeItem(self.workFolderBox.findText(work_folder.get_name()))
            self.tree_widget_left.clear()
            self.workFolderBox.setCurrentIndex(0)

            self.build_tree(self.tree_widget_left, self.root_work_folder_tree.get_root())

            self.current_selected_treeWidget: QTreeWidgetItem = self.tree_widget_left.topLevelItem(0)
            self.current_selected_cloud_item: TreeItem = self.item_map.get(id(self.current_selected_treeWidget))
        except Exception as e:
            self.errorHandler.handle(f'Error removing workfolder: {e}')
        

    # Исползуется при обработке изменений в списке рабочих папок
    def remove_work_folder(self, folder_name):
        folder = self.work_folder_tree_map.get(folder_name)

        try:
            self.y.remove(folder.get_path())
            self._delete_work_folder(folder)
            #self.reload_tree_partial(cloud_path=self.app_folder, get_parent=False)

        except Exception as e:
            self.errorHandler.handle(f'Error removing workfolder: {e}')

    
    def configure_workfolder(self):
        if self.current_selected_work_folder_tree == self.root_work_folder_tree:
            self.errorHandler.handle('Only workfolder configurable.')
            return
        ext_list = []
        for folder in self.current_selected_work_folder_tree.get_folders():
            extensions = get_file_formats(folder)
            ext_list = list(set(ext_list + extensions))

        #for folder in self.current_selected_work_folder_tree.get_folders():
        #    print(folder)
        #for ext in ext_list:
        #   print(ext)

        dialog = ConfigureWorkfolderUI(self.current_selected_work_folder_tree.get_config(), ext_list, self)
        result = dialog.exec_()

        if result == QDialog.Rejected:
            return
        
        new_config = dialog.get_data()
        self.current_selected_work_folder_tree.set_config(new_config)
    
    @classmethod
    def get_token(self, y: yadisk.YaDisk):
        self.y = y

def get_file_formats(folder_path):
    formats = []
    for _, _, files in os.walk(folder_path):
        for file in files:
            _, file_extension = os.path.splitext(file)
            file_extension = file_extension.lstrip('.').rstrip()
            if str(file_extension) == '' or str(file_extension) == ' ':
                continue
            formats.append(file_extension)
    return formats
        
        
def build_hierarchy(root:TreeItem, appFolder = '', backups_folder = ''):
    x = y.listdir(root.get_path())
    for item in list(x):
        #treeItem = TreeItem([item['path'], item['name'], item['type'], item['mime_type']], parent=root)
        if (not appFolder == '' and item['path'] == appFolder) or (not backups_folder == '' and item['path'] == backups_folder):
            continue
        treeItem = TreeItem(item, parent=root)
        root.add_child(treeItem)
        if treeItem.get_type() == 'dir':
            build_hierarchy(treeItem)


def calculate_sha256(file_path):
    sha256_hash = sha256()

    with open(file_path, "rb") as file:
        # Считываем блоки данных и обновляем хэш-сумму
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)

    # Получаем окончательное значение хэш-суммы
    return sha256_hash.hexdigest()

def _cloud_path_fixer(cloud_path: str):
    return cloud_path.replace('//', '/')


# ================ AUTOBACKUP BLOCK ===============================================
def get_files_with_exact_formats(workfolder: WorkFolder) -> list:
    file_list = [file.get_local_path() for file in  workfolder.get_files()]
    folders = workfolder.get_folders()
    ext_list = workfolder.get_config().get_formats()
    
    result_files = []
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            for file in files:
                local_path = os.path.join(root, file).replace('\\', '/')
                cloud_path = workfolder.get_path() + '/' + file
                _, file_ext = os.path.splitext(file)
                if file_ext.lstrip('.').rstrip() in ext_list and not local_path in file_list:
                    result_files.append(WorkFolderFile(local_path, file, cloud_path))

    return result_files

def create_incremental_backups_by_command(workfolder_list):
    
    new_name = datetime.__format__(datetime.now(), "%d-%m-%Y")
    for workFolder in workfolder_list:
        config = workFolder.get_config()
        if not config.get_autobackup():
            continue
        #workFolder = self.current_selected_work_folder_tree.get_work_folder()
        workFolderFiles = workFolder.get_files().copy()

        files_to_add = []   # пути файлов, которые нужно добавить
        deleted_files = []  # пути удаленных файлов
        last_number = 0
        for backup in workFolder.get_sorted_backups_list():
            if backup.get_number() > last_number: last_number = backup.get_number()

            backup_files = backup.get_files()
            backup_deleted_files = backup.get_deleted_files()

            files_to_remove = []
            for file in workFolderFiles:
                local_path = file.get_local_path()
                cloud_path = f'{workFolder.get_backups_path()}/{backup.get_number()}/{os.path.basename(local_path)}'
                if not os.path.exists(local_path):
                    if local_path in backup_deleted_files:
                        files_to_remove.append(file)
                        if local_path in deleted_files:
                            deleted_files.remove(local_path)
                        #deleted_files.append(local_path)           # TODO: Неправильно работает с удаленными файлами.
                        continue
                    else:
                        if not local_path in deleted_files:
                            deleted_files.append(local_path)
                        continue
                
                if local_path not in backup_files:
                    continue

                cloud_hash = y.get_meta(cloud_path)['sha256']
                local_hash = calculate_sha256(local_path)

                if not local_hash == cloud_hash:
                    files_to_add.append(local_path)
                files_to_remove.append(file)

            for file in files_to_remove:
                workFolderFiles.remove(file)

        # Сверка оставшихся файлов с полным бэкапом.
        if not len(workFolderFiles) == 0:
            for file in workFolderFiles:
                local_path = file.get_local_path()
                cloud_path = file.get_cloud_path()

                cloud_hash = y.get_meta(cloud_path)['sha256']
                local_hash = calculate_sha256(local_path)
                if not local_hash == cloud_hash:
                    files_to_add.append(local_path)


        if len(files_to_add) == 0:
            ErrorHandler.handle(f'New backup for {workFolder.get_name()} is not needed.')
            continue
        
        last_number += 1
        new_backup = Backup(name=new_name + ' ' + str(last_number), path=f'{workFolder.get_backups_path()}/{last_number}', number=last_number, creation=datetime.now())
        # Получаем список файлов, которые нужно добавить в новый бэкап и список файлов, которые были удалены.
        for file in files_to_add:
            new_backup.add_file(file)
        for file in deleted_files:
            new_backup.add_deleted_file(file)
        
        _upload_backup_by_command(new_backup, workFolder)

def _upload_backup_by_command(backup: Backup, workFolder: WorkFolder):
    try:
        y.mkdir(backup.get_path())
    except Exception as e:
        ErrorHandler.handle(f'Error making backup directory: {e}')
        return
    
    workFolder.add_backup(backup)
    for file in backup.get_files():
        name = os.path.basename(file)
        try:
            y.upload(file, backup.get_path() + f'/{name}')
        except Exception as e:
            ErrorHandler.handle(f'Error uploading file to backup: {e}')

def _upload_file_to_cloud(local_path, cloud_path):
    try:
        y.upload(local_path, cloud_path)
        return True
    except Exception as e:
        ErrorHandler.handle(f"Error uploading file: {e}")
        return False

def initial_load_work_folders_by_command() -> (bool, list):
    if not os.path.exists(FileTreeViewer.work_folder_list_file):
        return (False, [])

    if os.path.getsize(FileTreeViewer.work_folder_list_file) == 0:
        return (False, [])
    
    work_folder_list = load_workfolders_from_xml(FileTreeViewer.work_folder_list_file)
    res = []
    for workFolder in work_folder_list:
        res.append(WorkFolder(work_folder=workFolder))

    return (True, res)

def saveFolders_by_command(workfolder_list: list):
    try:
        save_workfolders_to_xml(workfolder_list, FileTreeViewer.work_folder_list_file)
    except Exception as e:
        ErrorHandler.handle(f'Error saving workfolders: {e}')
    #save_workfolders_to_xml(folder_list, 'tmpXML.xml')
        
def make_auto_backup():
    ErrorHandler.handle('Autobackup start')
    status, workfolder_list = initial_load_work_folders_by_command()
    if not status: 
        ErrorHandler.handle('No workfolders that need backup.')
        return False
    for workFolder in workfolder_list:
        new_files_list = get_files_with_exact_formats(workFolder)
        for file in new_files_list:
            if _upload_file_to_cloud(file.get_local_path(), file.get_cloud_path()):
                workFolder.add_file(file)
                with open('log.txt', 'a') as f:
                    ErrorHandler.handle(f'File {file.get_local_path()} added.')
    
    create_incremental_backups_by_command(workfolder_list)
    saveFolders_by_command(workfolder_list)

@pyqtSlot()
def get_token(y: yadisk.YaDisk):
    return y

if __name__ == '__main__':
    token = "y0_AgAAAABFAbmLAArAjwAAAADwrN9yWawqWRH8Sp2wcpW6h6sv_4QzKhs"
    #y = yadisk.YaDisk(token=token)
    ErrorHandler.handle("===================== Session start =============================================")
    y = Authenticate.authenticate()

    #root = TreeItem(y.get_meta('/Folder', limit=0))
    #build_hierarchy(root)

    #make_auto_backup()
    #sys.exit()

    if len(sys.argv) > 1 and sys.argv[1] == "/auto_backup":
        make_auto_backup()
        ErrorHandler.handle("===================== Session end ===============================================")
        sys.exit()
    else:
        # Запустить основное приложение
        app = QApplication(sys.argv)
        window = FileTreeViewer(y)
        #window.show()
        sys.exit(app.exec_())
    
