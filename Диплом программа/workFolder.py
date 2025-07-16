import xml.etree.ElementTree as ET
from backup import Backup
from datetime import datetime
from config import Config

class WorkFolder():
    def __init__(self, cloud_path: str = None, name: str = None, work_folder: 'WorkFolder' = None):
        if work_folder:
            self.cloud_path = work_folder.get_path()
            self.name = work_folder.get_name()
            self.files = work_folder.get_files()
            self.backups = work_folder.get_backups()
            self.folders = work_folder.get_folders()
            self.config = work_folder.get_config()
        else:
            self.cloud_path = cloud_path
            self.name = name
            self.files = []
            self.backups = []
            self.folders = []
            self.config = Config()

        self.backups_path = f'{self.cloud_path}/Backups'

    def get_path(self):
        return self.cloud_path
    def set_path(self, path):
        self.cloud_path = path

    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name

    def get_files(self) -> list:
        return self.files
    def add_file(self, file: 'WorkFolderFile'):
        self.files.append(file)
    def del_file(self, file: 'WorkFolderFile'):
        self.files.remove(file)

    def get_config(self) -> Config:
        return self.config
    def set_config(self, config: Config):
        self.config = config
    def add_format(self, format: str):
        self.config.add_format(format)
    def remove_format(self, format: str):
        self.config.remove_format(format)

    def get_backups(self) -> list:
        return self.backups
    def add_backup(self, backup: Backup):
        self.backups.append(backup)
    def del_backup(self, backup: Backup):
        self.backups.remove(backup)

    def get_folders(self) -> list:
        return self.folders
    def add_folder(self, folder_path: str):
        self.folders.append(folder_path)
    def remove_folder(self, folder_path: str):
        self.folders.remove(folder_path)

    def get_backups_path(self):
        return self.backups_path
    def set_backups_path(self, path: str):
        self.backups_path = path

    def get_backup(self, backupNumber: int) -> Backup:
        return next((backup for backup in self.backups if backup.get_number() == backupNumber), None)
    
    def get_backup_name_list(self) -> list:
        res = []
        res = [backup.get_name() for backup in self.backups]
        #for backup in self.backups:
        #    res.append(backup.get_name())
        return res
    
    # Отсортированный список бэкапов. Самые новые в начале
    def get_sorted_backups_list(self, until_date = None) -> list:
        mylist = self.backups.copy()
        if until_date is not None:
            mylist = filter(lambda x: x.creation_datetime <= until_date, mylist)
        return sorted(mylist, key=lambda x: x.creation_datetime, reverse=True)

    def get_last_backup(self) -> Backup:
        #return max(self.backups, key=lambda x: x.number, default=None)
        return max(self.backups, key=lambda x: x.creation_datetime, default=None)
    

    def to_xml(self):
        folder_element = ET.Element('WorkFolder')
        
        cloud_path_element = ET.SubElement(folder_element, 'CloudPath')
        cloud_path_element.text = self.cloud_path

        name_element = ET.SubElement(folder_element, 'Name')
        name_element.text = self.name

        files_element = ET.SubElement(folder_element, 'Files')
        for file in self.files:
            file_element = ET.SubElement(files_element, 'File')

            local_path_element = ET.SubElement(file_element, 'LocalPath')
            local_path_element.text = file.local_path

            file_name_element = ET.SubElement(file_element, 'FileName')
            file_name_element.text = file.name

            cloud_path_element = ET.SubElement(file_element, 'CloudPath')
            cloud_path_element.text = file.cloud_path

        backups_element = ET.SubElement(folder_element, 'Backups')
        for backup in self.backups:
            backup_element = ET.SubElement(backups_element, 'Backup')

            name_element = ET.SubElement(backup_element, 'Name')
            name_element.text = backup.name

            path_element = ET.SubElement(backup_element, 'Path')
            path_element.text = backup.path

            number_element = ET.SubElement(backup_element, 'Number')
            number_element.text = str(backup.number)

            creation_element = ET.SubElement(backup_element, 'Creation')
            creation_element.text = backup.creation_datetime.strftime(Backup.datetime_format)
            
            deleted_files_element = ET.SubElement(backup_element, 'DeletedFiles')
            for file in backup.deleted_files:
                deleted_file_element = ET.SubElement(deleted_files_element, 'DeletedFile')
                deleted_file_element.text = file

            backup_files_element = ET.SubElement(backup_element, 'BackupFiles')
            for file in backup.files:
                backup_file_element = ET.SubElement(backup_files_element, 'BackupFile')
                backup_file_element.text = file

        folders_element = ET.SubElement(folder_element, 'Folders')
        for folder in self.folders:
            _folder_element = ET.SubElement(folders_element, 'Folder')
            _folder_element.text = folder
        
        config_element = ET.SubElement(folder_element, 'Config')
        for ext in self.config.get_formats():
            ext_element = ET.SubElement(config_element, 'Extension')
            ext_element.text = ext
        auto_backup_element = ET.SubElement(config_element, 'Auto_backup')
        auto_backup_element.text = str(self.config.get_autobackup())

        return folder_element

    @classmethod
    def from_xml(cls, xml_element):
        cloud_path = xml_element.find('CloudPath').text
        name = xml_element.find('Name').text

        work_folder = cls(cloud_path, name)

        files_element = xml_element.find('Files')
        for file_element in files_element.findall('File'):
            local_path = file_element.find('LocalPath').text
            file_name = file_element.find('FileName').text
            cloud_path = file_element.find('CloudPath').text

            work_folder.add_file(WorkFolderFile(local_path, file_name, cloud_path))

        backups_element = xml_element.find('Backups')
        for backup_element in backups_element.findall('Backup'):
            backup_name = backup_element.find('Name').text
            path = backup_element.find('Path').text
            number = backup_element.find('Number').text
            creation = backup_element.find('Creation').text
 
            backup = Backup(backup_name, path, int(number), datetime.strptime(creation, Backup.datetime_format))
            deleted_files_element = backup_element.find('DeletedFiles')
            for file in deleted_files_element.findall('DeletedFile'):
                backup.add_deleted_file(file.text)
            backup_files_element = backup_element.find('BackupFiles')
            for file in backup_files_element.findall('BackupFile'):
                backup.add_file(file.text)

            work_folder.add_backup(backup)

        folders_element = xml_element.find('Folders')
        for folder in folders_element.findall('Folder'):
            folder_path = folder.text
            work_folder.add_folder(folder_path)

        config = Config()
        config_element = xml_element.find('Config')
        for ext in config_element.findall('Extension'):
            config.add_format(ext.text)
        auto_backup_element = config_element.find('Auto_backup')
        config.set_autobackup(bool(auto_backup_element.text))

        work_folder.set_config(config)
        return work_folder


class WorkFolderFile():
    def __init__(self, local_path: str, name: str, cloud_path: str = None):
        self.local_path = local_path
        self.name = name
        if cloud_path:
            self.cloud_path = cloud_path
        else:
            self.cloud_path = ''

    def get_local_path(self):
        return self.local_path
    def set_local_path(self, path):
        self.local_path = path

    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name

    def get_cloud_path(self):
        return self.cloud_path
    def set_cloud_path(self, path):
        self.cloud_path = path


def save_workfolders_to_xml(workfolders, filename):
    root = ET.Element('Root')

    for folder in workfolders:
        folder_element = folder.to_xml()
        root.append(folder_element)

    tree = ET.ElementTree(root)
    tree.write(filename)

def load_workfolders_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    workfolders = []
    for folder_element in root.findall('WorkFolder'):
        workfolders.append(WorkFolder.from_xml(folder_element))

    return workfolders


""" if __name__ == "__main__":
    # Пример использования записи и считывания нескольких объектов WorkFolder в один файл XML
    folder1 = WorkFolder("/Folder/Folder1", "Folder1")
    file1 = WorkFolderFile("path/to/file1", "File2.docx", "/Folder/Folder1/File2.docx")
    folder1.add_file(file1)

    folder2 = WorkFolder("/Folder/Folder2", "Folder2")
    file2 = WorkFolderFile("path/to/file2", "File21.docx", "/Folder/Folder2/File21.docx")
    folder2.add_file(file2)

    # Запись в XML
    save_workfolders_to_xml([folder1, folder2], "WorkFolders.xml")

    # Считывание из XML
    restored_workfolders = load_workfolders_from_xml("WorkFolders.xml")

    for restored_folder in restored_workfolders:
        print(restored_folder.get_path())
        print(restored_folder.get_name())
        for file in restored_folder.get_files():
            print(file.get_local_path())
            print(file.get_name())
            print(file.get_cloud_path()) """