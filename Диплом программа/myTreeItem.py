from yadisk.objects.resources import ResourceObject

class TreeItem:
    def __init__(self, data : ResourceObject, parent: 'TreeItem' = None, compressed:bool = False):
        self.data = data
        self.compressed = compressed
        self.parent_item = parent
        self.child_items = []
        self.column_cnt = 2 # file, type
        self.columns_to_show = []       # TODO: Добавить сюда нужные имена колонок и при создании QTreeWidget разыменовывать массив 

    def get_path(self):
        return self.data['path']
    def set_path(self, path):
        self.data['path'] = path

    def get_name(self):
        return self.data['name']
    def set_name(self, name):
        self.data['name'] = name
    
    def get_type(self):
        return self.data['type']
    def set_type(self, type):
        self.data['type'] = type

    def get_mime_type(self):
        return self.data['mime_type']
    def set_mime_type(self, mime):
        self.data['mime_type'] = mime

    def get_modified(self):
        return self.data['modified']
    def get_created(self):
        return self.data['created']
    def get_size(self):
        size = str(self.data['size'])
        if size == 'None':
            size = ' '
        return size

    def is_dir(self):
        if self.get_type() == 'dir':
            return True
        return False
        
    def is_file(self):
        if not self.is_dir():
            return True
        return False
    
    def add_child(self, child: 'TreeItem'):
        self.child_items.append(child)

    def set_parent(self, parent: 'TreeItem'):
        self.parent_item = parent

    def delete_children(self):
        self.child_items.clear()

    def child(self, number: int) -> 'TreeItem':
        if number < 0 or number >= len(self.child_items):
            return None
        return self.child_items[number]

    def last_child(self):
        return self.child_items[-1] if self.child_items else None

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        #return len(self.item_data)
        return self.column_cnt
    
    # def data(self, column: int):
    #     if column < 0 or column >= len(self.item_data):
    #         return None
    #     return self.item_data[column]
    
    def insert_children(self, position: int, count: int, columns: int) -> bool:
        if position < 0 or position > len(self.child_items):
            return False

        for row in range(count):
            data = [None] * columns
            item = TreeItem(data.copy(), self)
            self.child_items.insert(position, item)

        return True
    
    def get_parent(self):
        return self.parent_item
    
    def set_data(self, column: int, value):
        if column < 0 or column >= len(self.item_data):
            return False

        self.item_data[column] = value
        return True

    def __repr__(self) -> str:
       return(self.child_items)