# Name: Eimantas Pusinskas
# Student ID: 120312336

class Process(object):

    def __init__(self, PID, memory):
        self._PID = PID
        self._memory = memory

    def getPID(self):
        return self._PID

    def getMemory(self):
        return self._memory

    pid = property(getPID)
    memory = property(getMemory)
    
    def __str__(self):
        return f"PID: {self.pid} | Memory Required: {self.memory} MB"