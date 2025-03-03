import time


class RateCounter:

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.count = 0

    def start(self):
        self.start_time = time.perf_counter()
        return self

    def increment(self):
        self.count += 1

    def elapsed(self):
        return time.perf_counter() - self.start_time

    def rate(self):
        return self.count/self.elapsed()

    def print_elapsed(self):
        print(f"Elapsed Time: {self.elapsed()}")
