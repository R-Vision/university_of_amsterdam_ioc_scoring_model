import os
from timeit import default_timer as timer
from typing import Dict

is_enabled = os.environ.get("HOWLONG_ENABLE", "false").lower()
is_enabled = is_enabled == "true" or is_enabled == "1"

howlong_time_dict: Dict[str, int] = dict()
howlong_call_count_dict: Dict[str, int] = dict()

if is_enabled:

    class HowLong:
        def __init__(self, name):
            self.start = None
            self.name = name

        def __enter__(self):
            self.start = timer()

        def __exit__(self, type, value, traceback):
            delta = timer() - self.start
            howlong_time_dict[self.name] = howlong_time_dict.get(self.name, 0) + delta
            howlong_call_count_dict[self.name] = (
                howlong_call_count_dict.get(self.name, 0) + 1
            )


else:

    class HowLong:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            pass

        def __exit__(self, type, value, traceback):
            pass


def howlong_flush_stat():
    print("[HOWLONG] Flushing stat...")

    for name in howlong_time_dict.keys():
        time = howlong_time_dict[name]
        call_count = howlong_call_count_dict[name]

        print(f"{name}: {call_count}; {round(time, 2)} sec.")

    print("[HOWLONG] Done")
