# Name: Eimantas Pusinskas
# Student ID: 120312336

class Process(object):
    def __init__(self, pid, time, priority, state, io, io_time):
        self._pid = pid
        self._time = time
        self._priority = priority
        self._state = state
        self._io = io
        self._io_time_left = io_time
        self._io_time_required = io_time

    def get_time(self):
        return self._time

    def set_time(self, time):
        self._time = time

    def get_priority(self):
        return self._priority

    def set_priority(self, priority):
        self._priority = priority

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    def get_pid(self):
        return self._pid

    def get_io(self):
        return self._io
    
    def set_io(self, io):
        self._io = io

    def get_io_time_left(self):
        return self._io_time_left

    def set_io_time_left(self, io_time):
        self._io_time_left = io_time

    time = property(get_time, set_time)
    priority = property(get_priority, set_priority)
    state = property(get_state, set_state)
    pid = property(get_pid)
    io = property(get_io, set_io)
    io_time_left = property(get_io_time_left, set_io_time_left)

    def __str__(self):
        return f"[PID:{self._pid}-TIME:{self._time}-{self._state}]"

    