from workFolder import WorkFolder, WorkFolderFile
from myTreeItem import TreeItem
from backup import Backup
from config import Config


class WorkFolderTree():
    def __init__(self, workFolder: WorkFolder, rootTreeItem: TreeItem):
        self.workFolder = workFolder
        self.root = rootTreeItem

    def get_work_folder(self):
        return self.workFolder
    def set_work_folder(self, workFolder: WorkFolder):
        self.workFolder = workFolder

    def get_root(self):
        return self.root
    def set_root(self, root:TreeItem):
        self.root = root

    def get_path(self):
        return self.workFolder.get_path()
    def set_path(self, path):
        self.workFolder.set_path(path)

    def get_name(self):
        return self.workFolder.get_name()
    def set_name(self, name):
        self.workFolder.set_name(name)

    def get_files(self) -> list:
        return self.workFolder.get_files()
    def add_file(self, file: 'WorkFolderFile'):
        self.workFolder.add_file(file)
    def del_file(self, file: 'WorkFolderFile'):
        self.workFolder.del_file(file)

    def get_backups(self) -> list:
        return self.workFolder.get_backups()
    def add_backup(self, backup: Backup):
        self.workFolder.add_backup(backup)
    def del_backup(self, backup: Backup):
        self.workFolder.del_backup(backup)

    def get_config(self) -> Config:
        return self.workFolder.get_config()
    def set_config(self, config: Config):
        self.workFolder.set_config(config)
    def add_format(self, format: str):
        self.workFolder.add_format(format)
    def remove_format(self, format: str):
        self.workFolder.remove_format(format)

    def get_folders(self) -> list:
        return self.workFolder.get_folders()
    def add_folder(self, folder_path: str):
        self.workFolder.add_folder(folder_path)
    def remove_folder(self, folder_path: str):
        self.workFolder.remove_folder(folder_path)



    def get_backup(self, backupNumber: int) -> Backup:
        #return next((backup for backup in self.workFolder.get_backups() if backup.get_number() == backupNumber), None)
        return self.workFolder.get_backup(backupNumber)
    
    def get_backup_name_list(self) -> list:
        return self.workFolder.get_backup_name_list()
    
    def get_last_backup(self) -> Backup:
        return self.workFolder.get_last_backup()
    
    def get_backups_path(self):
        return self.workFolder.get_backups_path()
    def set_backups_path(self, path: str):
        self.workFolder.set_backups_path(path)