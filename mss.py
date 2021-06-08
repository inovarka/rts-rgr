import random
import numpy
from queue import Queue, PriorityQueue

N = 6
m = 6

class Process:
    def __init__(self, pid=None, t_prev=0, priorities=(1, N), lamb=1, Td=(1 / m) * 20):

        self.pid = pid
        self.priority = random.randint(*priorities)
        self.Td = Td

        self.T_execution = 1 / m
        self.T_end = None
        self.wait = 0  
        self.T_in_system = self.T_execution
        self.lamb = lamb
        self.approach = -1/self.lamb * numpy.log(random.random())
        self.T_approach = t_prev + self.approach

        self.T_cur_exec = 0

    def in_sys_count(self):
        return self.T_in_system + self.wait

    def __str__(self):
        return "Process " + str(self.pid)

    def __lt__(self, other):
        return self.priority < other.priority


class MSS:
    def __init__(self, lamb):
        self.requests = 2000
        self.lamb = lamb
        self.queue = Queue()
        self.handled = []
        self.garbage = []
        self.counter = 1

        """ Initial state """
        self.first_e = Process(pid=0, lamb=self.lamb)
        self.first_e.T_approach = 0

        self.event_next = None
        self.event_current = None
        self.saved_next = None
        self.in_proc = self.first_e
        self.processor = 0  

        self.T_appr = 0  
        self.T_end = self.first_e.T_execution  
        self.downtime = 0  
        self.Td = (1 / m) * 20
        self.tau = (1 / m) / 2

        self.downtime_all = 0


    def generate(self, eid):
        """ Generating Task """
        return Process(pid=eid, lamb=self.lamb, t_prev=self.T_appr)

    def generate_req(self, rid):
        """ Generating Request """
        return [Process(
                        pid=int(str(rid) + str(i)), 
                        lamb=self.lamb, 
                        t_prev=self.T_appr
                        ) for i in range(random.randint(1, 5))]

    def save_event_current(self, eve):
        self.event_current = eve

    def save_event_next(self, eve):
        self.event_next = eve


def main():
    r1 = Process(0, lamb=5)
    # r1.show_processes()

if __name__ == '__main__':
    main()
