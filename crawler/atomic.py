import threading

class AtomicCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self._count
    
    def decrement(self):
        with self._lock:
            self._count -= 1

    def increment(self):
        with self._lock:
            self._count += 1