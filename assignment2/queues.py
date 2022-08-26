# Name: Eimantas Pusinskas
# Student ID: 120312336

class QueueV0:
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

    def enqueue(self, item):
        self.body.append(item)

    def dequeue(self):
        return self.body.pop(0)

    def length(self):
        return len(self.body)

    def first(self):
        return self.body[0]


