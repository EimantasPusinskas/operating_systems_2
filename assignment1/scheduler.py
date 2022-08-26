# Name: Eimantas Pusinskas
# Student ID: 120312336

from queues import QueueV0
from process import Process
import time

class scheduler(object):

    def __init__(self):

        # creates 8 queues and adds them to a list to create a matrix of queues 
        # which will represent the multilevel feedback queues
        self._queues = []
        for i in range(8):
            q = QueueV0()
            self._queues.append(q)

        # captures the total time elapsed since the schduler has started running/
        # the total CPU time every process has had
        self._time = 0
        self._blocked = []
        self._load = "high"
        self._voltage = "high"
        self._capacity = "high"
        self._upcoming_io = []

    def __str__(self):
        queueStr = ""
        queueStr += f"Time Elapsed: {self._time}\nBlocked Queue: {[self._blocked[i].pid for i in range(len(self._blocked))]}\n"
        for queue in self._queues:
            queueStr += f"{self._queues.index(queue)} : {queue}"
            if self._queues[-1] != queue:
                queueStr += "\n"
        return queueStr
    

    """
        adds a process to a queue depending on its priority
    """
    def add_process(self, process):
        self._queues[process.priority].enqueue(process)

        # if a process has any IO operations scheduled it is also added to an upcoming_io list which will 
        # help in the execute() function to see if there is any upcoming IO for any process
        # my reasoning for using this list is to increase efficiency by not having to search through every queue
        # to find a process with upcoming IO and instead having it all in one list
        if process.io != None:
            self._upcoming_io.append(process)
            self._upcoming_io.sort(key = lambda x:x._io_time_left)

    """
        process is donwgraded in priority
    """
    def downgrade_process_priority(self, queue_num):
        proc = self._queues[queue_num].dequeue()
        if proc.priority < 7:
            proc.priority += 1
            self._queues[proc.priority].enqueue(proc)


    def terminate_process(self, queue_num):
        self._queues[queue_num].dequeue()

    
    """
        this function determines the time slice for a process and simulates giving a process CPU control for that time
        the time slice is determined by three factors;
        1. if there are any upcoming IO operations meant to be starting.
            It uses the upcoming_io list to look this up. Since the list is ordered by the IO time each process is starting
            from lowest to highest, it gets the first process in the list if the list is not empty and sets the time left till 
            IO starts as the second time slice. Suppose there are 4 time units till the next IO operation starts, then time slice A = 4
        2. if there are any IO operations finishing
            it uses the blocked list to look up when the next IO operation finishes and sets the time slice as the time left till this IO finishes
            suppose time slice B = 6
        3. if the process will finish its execution in less than the time it will be given CPU control. e.g. process priority = 3, and so its time slice 
            will be 2**3 = 8 time units, but it only need 2 time units and so only 6 will be given. Thus time slice C = 6
        initially all 3 time slices will have the same time slice that is determined by a processes priority. e.g process priority = 3, all time slices [A-C] = 2**3 = 8
        but if any of the three conditions above are satisfied then that will be its new time slice
        And so we have three different potential time slices in my example above (time slice A = 4, time slice B = 6, time slice C = 6)
        the final time slice that is used is the minimum of these three different time slices and so the time slice = 4
    """
    def execute(self, queue_num):
        # time slice for a queue depending on its priority
        time_slice = 2 ** queue_num

        # process that will be given CPU control
        proc = self._queues[queue_num].first()

        # check every incoming io operation, if the time slice will collide with the
        # expected io, it adjusts time slice accordingly
        time_sliceA = time_slice
        for io_upcoming in self._upcoming_io:
            if self._time + time_slice >= io_upcoming.io:
                time_sliceA = io_upcoming.io - self._time
                break

        # checks when every io finishes, adjusts time slice accordingly
        time_sliceB = time_slice
        for blocked in self._blocked:
            if time_slice >= blocked._io_time_left:
                time_sliceB = blocked._io_time_left
                break

                
        # if the time slice allocated is larger than the 
        # time required for full execution of the process then
        # only the required amount of time is allocated for execution
        time_sliceC = time_slice
        if time_slice >= proc.time:
            time_sliceC = proc.time
        
        # the minimum time of all three slices is used as the final time slice 
        time_slice = min(time_sliceA, time_sliceB, time_sliceC)

        # updates io time left for any process in the blocked queue
        for blocked in self._blocked:
            blocked._io_time_left -= time_slice

        # updates total time passed since the very start
        self._time += time_slice
   
        # updates a processes time required left for execution
        proc.time -= time_slice
    
        # mimicks the waiting process of a process by
        # having control of the CPU for the time slice
        if time_slice != 0:
            time.sleep(time_slice/1000)

        # if a process doesn't finish execution within its time slice, it's priority is downgraded if possible
        # if it has the lowest priority possible, it is dequeued and enqueued at the same queue to maintain the round-robin policy for that queue
        # otherwise a process has finished and it is terminated
        if proc.time > 0 and proc.priority != 7:
            self.downgrade_process_priority(queue_num)
        elif proc.time > 0 and proc.priority == 7:
            self._queues[7].dequeue()
            self.add_process(proc)
        else:
            self.terminate_process(queue_num)

        # prints queues for testing
        print(sch)
        print("-------------")

    """
        this function gets the next ready process
        the next ready process in my implementation will always be at the front of the queue
        therefore only the queue number is returned from the function
        if a process at the front of a queue is ready to start IO, it is blocked, dequeued, and enqueue at the blocked list
        this ensures that a process at the front of a queue is always ready for execution

    """
    def get_next_process(self):
        i = 0 
        found = False
        queue = None
        while (found == False) and (i < 8):
            # checks that the queue i is not empty
            if (self._queues[i].length() != 0) and (self._queues[i].first().state == "ready"):
                proc = self._queues[i].first()
                # blocks process if it is time for it to execute io operation
                if proc.io != None and self._time >= proc.io:
                    proc.state = "blocked"
                    self._blocked.append(proc)
                    self._queues[i].dequeue()

                    print(f"PID:{proc.pid} Expected block time {proc.io}. Actual time blocked {self._time}. ")
                    print("-------------")
                    
                    # once a process is bloked and added to the blocked list, it is removed from the upcoming IO list,
                    #  since its has IO is no longer upcoming and instead is about to start
                    for io_proc in self._upcoming_io:
                        if io_proc.pid == proc.pid:
                            del self._upcoming_io[self._upcoming_io.index(io_proc)]
                            break
                else:
                    queue = i
                    found = True
            else:
                i += 1
        return queue
   

    """
        this function iterates over every process in the blocked list, 
        checks if its IO has finished and if true, removes process from blocked list, 
        increases its priority by 1 and enqueues it back in the multilevel feedback queue

    """
    def unblock(self):
        for proc in self._blocked:
            if proc.io_time_left <= 0:
                print(f"PID:{proc.pid} Expected unblock time {proc._io + proc._io_time_required}. Actual unblock time {self._time}")
                print("------------")

                proc.state = "ready"
                proc.io = None
                proc.io_time_left = 0
                if proc.priority != 0:
                    proc.priority -= 1

                self._queues[proc.priority].enqueue(proc)
                del self._blocked[self._blocked.index(proc)]
                
    """
        checks if the system load is low
        the load is considered low if the only processes are in the idle queue 
        and there are less than two processes
    """
    def if_load_low(self):
        low = True
        for i in range(6):
            if self._queues[i].length() != 0:
                low = False
        
        if low == True and self._queues[7].length() < 2:
            return True
        else:
            return False

    
    def decrease_power(self):
        self._load = "low"
        self._capacity = "low"
        self._voltage = "low"
    
    def increase_power(self):
        self._load = "high"
        self._capacity = "high"
        self._voltage = "high"     


    """
        this simulates the scheduler sleeping
        the sleep function is used to prevent from exceeding maximum recursion
    """
    def sleep(self):
        print("zzz")
        time.sleep(60) 
 

    """
        this simulates the CPU running with an infinite loop
    """
    def run(self):
        while True:
            if self.get_next_process() != None or len(self._blocked) != 0:

                if len(self._blocked) != 0:
                    self.unblock()

                next_proc = self.get_next_process()
                self.execute(next_proc)

                if self.if_load_low() == True:
                    self.decrease_power()
                else:
                    self.increase_power()

            else:
                self.sleep()
         

if __name__ == "__main__":
    sch = scheduler()
    proc1 = Process(1, 100, 1, "ready", 20, 10)
    proc2 = Process(2, 200, 2, "ready", None, None)
    proc3 = Process(3, 100, 5, "ready", None, None)
    proc4 = Process(4, 150, 3, "ready", 200, 50)
    proc5 = Process(5, 400, 7, "ready", None, None)
    proc6 = Process(6, 130, 2, "ready", None, None)
    sch.add_process(proc1)
    sch.add_process(proc2)
    sch.add_process(proc3)
    sch.add_process(proc4)
    sch.add_process(proc5)
    sch.add_process(proc6)

    print(sch)
    print("-------------")

    sch.run()

    
  
   

  