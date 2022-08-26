# Name: Eimantas Pusinskas
# Student ID: 120312336

class Block(object):

    def __init__ (self, size):
        self._size = size
        self._allocated = False
        self._process = None
        self._pages = []
        self._accessed = 0

    def get_size(self):
        return self._size

    def set_size(self, size):
        self._size = size

    def get_pages(self):
        return self._pages
    
    def add_page(self, page):
        self._pages.append(page)

    def get_process(self):
        return self._process
    
    def set_process(self, process):
        self._process = process

    size = property(get_size, set_size)
    process = property(get_process, set_process)

