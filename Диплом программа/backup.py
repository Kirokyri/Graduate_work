from datetime import datetime


class Backup():                     # Папка бэкапа
    datetime_format = "%d-%m-%Y %H:%M:%S"
    def __init__(self, name: str, path: str, number: int,  creation: datetime):
        self.name = name                        # Название бэкапа (дается пользователем)
        self.path = path                        # Путь к папке бэкапа на облаке
        self.number = number                    # Номер бэкапа для этой рабочей папки
        self.creation_datetime = creation       # Дата создания бэкапа
        self.deleted_files = []                 # Список файлов, удаленных с момента прошлого бэкапа. Содержит локальные пути
        self.files = []                         # Список файлов, которые содержатся в данном бэкапе. Содержит локальные пути

    
    def get_name(self):
        return self.name
    def set_name(self, name: str):
        self.name = name
    
    def get_path(self):
        return self.path
    def set_path(self, path: str):
        self.path = path

    def get_number(self):
        return self.number
    def set_number(self, number: int):
        self.number = number
    
    def get_creation_time(self) -> str:
        return datetime.strftime(self.creation_datetime, self.datetime_format)
    def set_creation_time(self, creation: datetime):
        self.creation_datetime = creation

    def get_deleted_files(self) -> list:
        return self.deleted_files
    def add_deleted_file(self, file: str):
        self.deleted_files.append(file)
    def remove_deleted_file(self, file: str):
        self.deleted_files.remove(file)

    def get_files(self) -> list:
        return self.files
    def add_file(self, file: str):
        self.files.append(file)
    def add_files(self, files: list):
        for file in files:
            self.add_file(file)
    def remove_file(self, file: str):
        self.files.remove(file)
    

