# Name: Eimantas Pusinskas
# Student ID: 120312336

# this code for the class QueueV0 has been taken from the module Data Structures & Algorithms I
# I do not take any credit for writing this code 
# all credit goes to Ken Brown and the UCC Department of Computer Science 

import time
import sys

class QueueV0:
    """ A queue using a python list, with the head at the front.

    """
    def __init__(self):
        self.body = []
        
    def __str__(self):
        if len(self.body) == 0:
            return '<--<'
        stringlist = ['<']
        for item in self.body:
            stringlist.append('-' + str(item))
        stringlist.append('-<')
        return ''.join(stringlist)
        # output = '<-'
        # i = 0
        # for item in self.body:
        #     output = output + str(item) + '-'
        # output = output +'<'
        # return output

    def summary(self):
        """ Return a string summary of the queue. """
        return ('length:' + str(len(self.body)))
    
    def get_size(self):
        """ Return the internal size of the queue. """
        return sys.getsizeof(self.body)

    def enqueue(self, item):
        """ Add an item to the queue.

        Args:
            item - (any type) to be added to the queue.
        """
        self.body.append(item)

    def dequeue(self):
        """ Return (and remove) the item in the queue for longest. """
        return self.body.pop(0)

    def length(self):
        """ Return the number of items in the queue. """
        return len(self.body)

    def first(self):
        """ Return the first item in the queue. """
        return self.body[0]



