import threading
import time
from typing import *

def unique_caller(func):
    called = [False]
    lock = threading.Lock()

    def f(*args, **kwargs):
        if not called[0]:
            called[0] = True
            print('called')
            try:
                with lock:
                    func()
            finally:
                called[0] = False
        else:
            print('pass')
            with lock:
                pass

    return f

@unique_caller
def f():
    time.sleep(10)


threds = []
for i in range(10):
    t = threading.Thread(target=f)
    t.start()
    threds.append(t)

for t in threds:
    t.join()