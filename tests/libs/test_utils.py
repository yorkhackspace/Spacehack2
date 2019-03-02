from threading import Event, Thread
import time
import sys

class TimeoutTest:
    def __init__(self, timeout=30.0):
        self.complete = Event()
        self.success = Event()
        self.timeout = timeout

    def passed(self):
        self.success.set()
        self.complete.set()
        # This won't exit if it's in a thread
        sys.exit(0)

    def await_completion(self):
        self.complete.wait()

    def run(self, uut_func, test_func):
        def timeout():
            self.complete.wait(self.timeout)
            self.complete.set()
        uut = Thread(target=uut_func)
        act = Thread(target=test_func)
        timer = Thread(target=timeout)

        uut.start()
        act.start()
        timer.start()

        self.await_completion()

        uut.join()
        act.join()
        timer.join()

        if not self.success.isSet():
            sys.exit(1)
        sys.exit(0)
