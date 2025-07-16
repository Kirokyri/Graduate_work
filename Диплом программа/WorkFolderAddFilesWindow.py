import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QFileDialog, QWidget
from PyQt5.QtCore import pyqtSignal
from workFolder import WorkFolderFile


class AddFilesDialog(QMainWindow):
    send_data_signal = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.selected_files = []

    def init_ui(self):
        self.setWindowTitle("Выбор файлов и папок")

        btn_select_files = QPushButton("Выбрать файлы", self)
        btn_select_files.clicked.connect(self.open_file_dialog)

        btn_select_folders = QPushButton("Выбрать папки", self)
        btn_select_folders.clicked.connect(self.open_folder_dialog)

        layout = QVBoxLayout()
        layout.addWidget(btn_select_files)
        layout.addWidget(btn_select_folders)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Использовать стандартный файловый диалог
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы", "", "All Files (*);;Text Files (*.txt)", options=options)
        if files:
            for file in files:
                #self.selected_files.append({'path':file, 'name':get_full_file_name(file)})
                self.selected_files.append(WorkFolderFile(file, get_full_file_name(file)))


    def open_folder_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Использовать стандартный файловый диалог
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку", options=options)
        if folder:
            print("Выбранная папка:", folder)

def get_full_file_name(file_path):
    file_name, file_extension = os.path.splitext(os.path.basename(file_path))
    return f"{file_name}{file_extension}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AddFilesDialog()
    main_window.show()
    sys.exit(app.exec_())