import datetime

from tqdm import tqdm


class TqdmPlus(tqdm):

    def __str__(self):
        return f"Progress: {self.progress:3.2f}% [{self.current+1}/{self.items}]"

    def format_time(self, seconds):
        seconds = int(seconds)
        return str(datetime.timedelta(seconds=seconds))

    @property
    def rate(self):
        return self.format_dict["rate"]

    @property
    def elapsed(self):
        return self.format_dict["elapsed"]

    @property
    def items(self):
        return self.format_dict["total"]

    @property
    def current(self):
        return self.format_dict["n"]

    @property
    def progress_norm(self):
        return float(self.current+1)/float(self.items)

    @property
    def progress(self):
        return self.progress_norm * 100

    @property
    def progress_str(self):
        return str(self)

    @property
    def eta_seconds(self):
        if self.rate is None:
            return 999
        remaining_items = self.items - self.current
        return int(remaining_items/self.rate)

    @property
    def rate_str(self):
        if self.rate is None:
            return "[???]"
        rate = self.rate
        if self.rate < 1:
            postfix = "s/it"
            rate = 1/self.rate
        else:
            postfix = "it/s"
        return f"{rate:.2f}{postfix}"

    @property
    def time_rate_str(self):
        return f"[Elapsed: {self.format_time(self.elapsed)}, ETA: {self.format_time(self.eta_seconds)}, {self.rate_str}]"
