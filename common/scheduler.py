import sched
from threading import Thread
import time

s = sched.scheduler(time.time, time.sleep)

def schedule_event(func: callable, delay: int, priority: int):
    s.enter(delay, priority, func)

def run_scheduler():
    t = Thread(target=s.run)
    t.start()