import random
import numpy
from typing import List
from queue import Empty, PriorityQueue
from mss import Process, MSS, m


class EDFProcess(Process):
    def __lt__(self, other):
        return self.Td - self.wait < self.Td - other.wait


class System(MSS):
    def __init__(self, lamb):
        super().__init__(lamb)
        self.handled.append(self.in_proc)
        self.queue = PriorityQueue()

        self.moments = []
        self.thrown = []

    def handling(self):

        while self.counter < self.requests:

            if self.processor:
                self.unpack_req(self.saved_next)
                self.in_proc = self.queue.get_nowait()
                in_proc_tsys = self.in_proc.in_sys_count()

                if in_proc_tsys >= self.Td:
                    self.processor = 0
                    self.T_end += in_proc_tsys - self.Td + self.downtime
                    self.garbage.append(self.in_proc)

                    self.counter += 1
                    self.saved_next = None
                    continue

                self.processor = 0
                self.T_end += self.in_proc.T_execution + self.downtime
                self.handled.append(self.in_proc)

                self.counter += 1
                self.saved_next = None
                continue

            if not self.saved_next:

                e = self.generate_req(self.counter)

                self.save_event_next(eve=e)
                self.T_appr = self.event_next[0].T_approach

                if (self.T_appr - self.T_end) > 0 and self.queue.empty():
                    self.downtime = self.T_appr - self.T_end

                else:
                    self.downtime = 0

                self.downtime_all += self.downtime

            else:
                self.T_appr = self.event_next[0].T_approach

                if (self.T_appr - self.T_end) > 0 and self.queue.empty():
                    self.downtime = self.T_appr - self.T_end

                else:
                    self.downtime = 0

                self.downtime_all += self.downtime

            A = self.T_appr < self.T_end
            B = self.T_appr > self.T_end

            if A:
                for i in self.event_next:
                    i.wait += self.T_end - self.T_appr
                self.unpack_req(self.event_next)
                self.saved_next = None

                self.counter += 1
                continue

            if B:
                self.saved_next = self.event_next

                if self.queue.empty():
                    self.processor = 1
                else:
                    eve = self.queue.get_nowait()

                    try:
                        while eve.wait > self.Td:
                            self.garbage.append(eve)
                            eve = self.queue.get_nowait()

                        while (eve.T_in_system + eve.wait) > self.Td:
                            self.garbage.append(eve)
                            self.T_end += (eve.T_in_system +
                                           eve.wait) - self.Td
                            eve = self.queue.get_nowait()
                    except Empty:
                        self.processor = 1
                        continue

                    self.moments.append(self.T_end)
                    self.thrown.append(len(self.garbage))

                    self.in_proc = eve
                    self.T_end += self.in_proc.T_execution
                    self.handled.append(self.in_proc)
                    for i in self.queue.queue:
                        i.wait += self.in_proc.T_execution

        return {
            "queue": self.queue,
            "handled": self.handled,
            'garbage': self.garbage,
        }

    def unpack_req(self, request: List[EDFProcess]):
        for i in request:
            self.queue.put_nowait(i)

    def generate_req(self, rid):

        return [EDFProcess(
            pid=int(str(rid) + str(i)),
            lamb=self.lamb,
            t_prev=self.T_appr
        ) for i in range(random.randint(1, 5))]


if __name__ == "__main__":
    from pprint import pprint
    from bokeh.models.widgets import Panel, Tabs
    from bokeh.io import output_file, show
    from bokeh.plotting import figure
    from collections import Counter

    intensities = numpy.linspace(0.1, 6, 60)
    attempts = [System(i) for i in intensities]
    results = [s.handling()['handled'] for s in attempts]
    waitings = []
    downtime_part = []
    processor_working = []

    att_count = len(attempts)

    for s in range(att_count):
        waitings.append(sum([i.wait for i in results[s]]) / len(results[s]))
        processor_working.append(
            sum([i.T_in_system+i.wait for i in results[s]]))

    for i in range(att_count):
        downtime_part.append(
            (attempts[i].downtime_all / (attempts[i].downtime_all + processor_working[i]))*100)

    waiting_times_rounded = [[round(j.wait, 1) for j in i] for i in results]
    req_from_wt = [Counter(i) for i in waiting_times_rounded]

    output_file("EDF.html")
    tabs = []

    p1 = figure(plot_width=900, plot_height=500,
                x_axis_label='??????????????????????????', y_axis_label='?????? ????????????????????')
    p1.line(intensities, waitings, line_width=3, color="#494dff")
    tabs.append(Panel(child=p1, title="????????????????????/??????????????????????????"))

    p2 = figure(plot_width=900, plot_height=500,
                x_axis_label='??????????????????????????', y_axis_label='???????????????? ??????????????')
    p2.line(intensities, downtime_part, line_width=3, color="#494dff")
    tabs.append(Panel(child=p2, title="??????????????/??????????????????????????"))

    tabs = Tabs(tabs=tabs)

    show(tabs)
