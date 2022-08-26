# Name: Eimantas Pusinskas
# Student ID: 120312336

from queues import *
from process import *
from block import *
from random import randint

class BuddySystemBST(object):
    	
    class node(object):
        def __init__ (self, size):
            self._block = Block(size)
            self._parent = None
            self._leftchild = None
            self._rightchild = None

        def __str__ (self):
            return f"{self._block.size} KB"

        def get_block(self):
            return self._block

        def set_block(self, block):
            self._block = block
    
        block = property(get_block, set_block)


    def __init__(self, size):
        self._root = self.node(size)
        self._block_nodes = self._root
        
    def get_root(self):
        return self._root         

    # checks if a node is a leaf node
    def is_leaf(self, node):
        if node._leftchild == None and node._rightchild == None:
            return True
        else:
            return False

    # returns a list of all leaf nodes in the tree
    def get_leaf_nodes(self):
        root = self.get_root()
        blocks = []
        blocks = self._get_leaf_nodes(root, blocks)
        return blocks
        
    def _get_leaf_nodes(self, node, blocks):
        if self.is_leaf(node):
            blocks.append(node)
        else:
            if node._leftchild != None:
                self._get_leaf_nodes(node._leftchild, blocks)

            if node._rightchild != None:
                self._get_leaf_nodes(node._rightchild, blocks)
        return blocks 

    # splits a node by instantiating to node objects and setting them
    # as the original nodes children
    def split_node(self, node):
        parent_block_size = node.block.size

        left_child = self.node(parent_block_size//2)
        right_child = self.node(parent_block_size//2)

        node._leftchild = left_child
        node._rightchild = right_child

        left_child._parent = node
        right_child._parent = node

        return node

    def print_leaf_nodes(self):
        nodes = self.get_leaf_nodes()
        output = "< "
        for node in nodes:
            output += f"({node}:"
            if node.block._allocated == True:
                output += "1) "
            else:
                output += "0) "
        output += ">"
        print(output)

    # returns a list of every node in the tree
    def get_all_nodes(self):
        nodes = []
        root = self.get_root()
        nodes = self._get_all_nodes(root, nodes)
        return nodes

    def _get_all_nodes(self, node, nodes):
        nodes.append(node)

        if node._leftchild != None:
            self._get_all_nodes(node._leftchild, nodes)

        if node._rightchild != None:
            self._get_all_nodes(node._rightchild, nodes)
        return nodes

    def print_all_nodes(self):
        nodes = self.get_all_nodes()
        output = ""
        for node in nodes:
            output += f"({node.block.size}, "
            if node.block._allocated == True:
                output += "1) "
            else:
                output += "0) "
        print(output)

    # removes two children nodes of a parent node
    def merge_children_nodes(self, node):
        node._leftchild.block = None
        node._leftchild._parent = None
        node._leftchild = None

        node._rightchild.block = None
        node._rightchild._parent = None
        node._rightchild = None

    # sets a node to being deallocated. in other words the node is now free for memory allocation
    def deallocate_node(self, node):
        node.block._allocated = False
        node.block._process = None  
        node.block._accessed = 0
                
            

class memory(object):

    def __init__(self):
        # in KB, 1 = 1KB, 1024 = 1024KB = 1MB
        self._user_space_mem_size = 4096
        self._page_size = 4
        self._allocation_queue = QueueV0()  #this is the queue where processes in need of memory allocation are enqueue
        self._buddy_tree = BuddySystemBST(self._user_space_mem_size)
        self._bitmap = {0:0}
        self._replacement_queue = QueueV0() # this is the queue used for the second chance algorithm

    def request_memory_allocation(self, process):
        self._allocation_queue.enqueue(process)

    # processes requesting memory are dequeued on a FIFO basis and allocated memory
    def allocate_memory(self):
        if self._allocation_queue.length() != 0:
            proc = self._allocation_queue.dequeue()
            node_found = self._allocate_memory(proc)
            self._replacement_queue.enqueue(node_found)
            print(f"process {proc.pid}: requested {proc.memory}KB - allocated {node_found.block.size}KB")
            return node_found

    def _allocate_memory(self, proc):
        if self.is_memory_full():
            self.replace()

        # the amount of memory that the process is requesting
        mem_required = proc.memory
    
        if mem_required < self._page_size:
            mem_required = self._page_size
        
        # the memory requested by the process is rounded to the nearest power of 2
        mem_required -= 1
        k = 1  
        while k < mem_required:
            k *= 2
        target_size = k

        # finds a free block that suits the process and allocates the block to that process
        block_nodes = self._buddy_tree.get_leaf_nodes()
        found = False
        node_found = None
        for node in block_nodes:
            if node.block.size == target_size and node.block._allocated == False:
                found = True
                node.block.process = proc
                node.block._allocated = True
                node.block._accessed = 0
                self.update_bitmap()
                node_found = node
                break
        
        if found == False:
            # finds if any free blocks can be split recursively to be allocated to the process
            block_node_to_split = None
            max_free_node_size = 0
            for node in block_nodes:
                if node.block.size > max_free_node_size and node.block._allocated == False and node.block.size >= target_size:
                    max_free_node_size = node.block.size
                    block_node_to_split = node
                    break
            
            # if a node suitable for a split is found, it is split until its size matches the target_size 
            # and then allocates the left-most split leaf node to the process requesting memory
            # otherwise blocks are deallocated recursively unitl the process requesting memory 
            # can have memory allocated to it 
            if block_node_to_split != None:
                free_block_node = self.split_until_allocated(target_size, block_node_to_split)
                free_block_node.block.process = proc
                free_block_node.block._allocated = True
                free_block_node.block._accessed = 0
                self.update_bitmap()
                node_found = free_block_node
            else:
                self.replace()
                node_found = self._allocate_memory(proc)

        return node_found

    # split tree nodes recursively until the leaf nodes of that subtree
    # match the target size
    def split_until_allocated(self, target_size, block_node_to_split):
        free_block_node = None
        parent_node = self._buddy_tree.split_node(block_node_to_split)
        if parent_node._leftchild.block.size == target_size:
            free_block_node = parent_node._leftchild
        else:
            free_block_node = self.split_until_allocated(target_size, parent_node._leftchild)
        return free_block_node

    # does a simple check to see if the memory is completely full
    def is_memory_full(self):
        full = True
        for block in self._bitmap:
            if self._bitmap[block] == 0:
                full = False
                break
        return full

    # deallocated blocks from memory using the second chance algorithm
    def replace(self):
        if self._replacement_queue.length() != 0:
            node = self._replacement_queue.dequeue()     
            if node.block._accessed == 1:
                node.block._accessed = 0
                self._replacement_queue.enqueue(node)
                print(f"process {node.block.process.pid} has been given a second chance")
            else:
                print(f"process {node.block.process.pid} has been deallocated")
                self.remove_block(node)
           
            self.update_bitmap()
         
    def update_bitmap(self):
        block_nodes = self._buddy_tree.get_leaf_nodes()
        self._bitmap = {}
        for node in block_nodes:
            if node.block._allocated == True:
                self._bitmap[block_nodes.index(node)] = 1
            else:
                self._bitmap[block_nodes.index(node)] = 0
        return self._bitmap

    # merges a block and its buddy if both are not allocated
    # othewise the block is simply deallocated and the tree stays as it is
    def remove_block(self, node):
        if self._buddy_tree.is_leaf(node) == True:
            if self._buddy_tree.is_leaf(node._parent._rightchild) == True and node._parent._rightchild.block._allocated == False:
                node._parent.block._allocated = False
                self._buddy_tree.merge_children_nodes(node._parent) 
            else:
                self._buddy_tree.deallocate_node(node)
            self.update_bitmap()

    def calculate_fragmentation(self):
        nodes = self._buddy_tree.get_leaf_nodes()
        internal_memory_consumed = 0
        external_memory_consumed = 0
        for node in nodes:
            if node.block.process != None:
                internal_memory_consumed += node.block.process.memory
                external_memory_consumed += node.block.size

        # fragmentation result is the percentage of unused memory
        internal_fragmentation = ((external_memory_consumed - internal_memory_consumed) / external_memory_consumed ) * 100
        external_fragmentation = ((self._user_space_mem_size - external_memory_consumed) / self._user_space_mem_size) * 100
        print(f"-----------------\nFragmentation: \nInternal: {internal_fragmentation}% \nExternal: {external_fragmentation }%\n-----------------")

    


if __name__ == "__main__":
    def basic_test():
        mem = memory()
        proc1 = Process(1, 50)
        mem.request_memory_allocation(proc1)
        proc1_node = mem.allocate_memory()

        proc2 = Process(2, 254)
        mem.request_memory_allocation(proc2)
        mem.allocate_memory()

        proc4 = Process(4, 120)
        mem.request_memory_allocation(proc4)
        mem.allocate_memory()
        
        proc5 = Process(5, 1000)
        mem.request_memory_allocation(proc5)
        mem.allocate_memory()

        proc6 = Process(6, 500)
        mem.request_memory_allocation(proc6)
        mem.allocate_memory()

        proc7 = Process(7, 2010)
        mem.request_memory_allocation(proc7)
        mem.allocate_memory()


        print(mem._bitmap)
        mem._buddy_tree.print_leaf_nodes()

        print("----------------------")

        #mem.remove_block(proc1_node)
        #print(mem._bitmap)
        #mem._buddy_tree.print_leaf_nodes()

        proc8 = Process(8, 60)
        mem.request_memory_allocation(proc8)
        mem.allocate_memory()
        mem._buddy_tree.print_leaf_nodes()
        mem.calculate_fragmentation()

        
        proc9 = Process(9, 100)
        mem.request_memory_allocation(proc9)
        mem.allocate_memory()
        mem._buddy_tree.print_leaf_nodes()

        proc10 = Process(10, 1500)
        mem.request_memory_allocation(proc10)
        mem.allocate_memory()
        mem._buddy_tree.print_leaf_nodes()

        #proc11 = Process(11, 1)
        #mem.request_memory_allocation(proc11)
        #mem.allocate_memory()
        #mem._buddy_tree.print_leaf_nodes()

        mem.calculate_fragmentation()

    def random_test():
        mem = memory()
         
        for i in range(250):
            proc = Process(i, randint(mem._page_size, 32))
            mem.request_memory_allocation(proc)
            node = mem.allocate_memory()

            node.block._accessed = randint(0,1)

        mem.calculate_fragmentation()
        mem._buddy_tree.print_leaf_nodes()
        

    #basic_test()
    random_test()