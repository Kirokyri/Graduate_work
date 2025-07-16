class Config():
    def __init__(self) -> None:
        self.chosen_formats = []
        self.auto_backup = False

    def get_formats(self) -> list:
        return self.chosen_formats
    def get_autobackup(self) -> bool:
        return self.auto_backup
    
    def add_format(self, format: str):
        if not format in self.chosen_formats:
            self.chosen_formats.append(format)
    def remove_format(self, format: str):
        if format in self.chosen_formats:
            self.chosen_formats.remove(format)

    def set_autobackup(self, flag: bool):
        self.auto_backup = flag

    