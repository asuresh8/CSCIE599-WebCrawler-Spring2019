"""atomic.py

This module contains a few atomic data structures that are used by the crawler manager
"""
import threading
import heapq

class AtomicQueue:
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
    
    def add(self, elem):
        with self._lock:
            self._queue.append(elem)
    
    def contains(self, elem):
        with self._lock:
            return elem in self._queue

    def poll(self):
        with self._lock:
            if len(self._queue) == 0:
                return None
            else:
                return self._queue.pop(0)

    def size(self):
        with self._lock:
            return len(self._queue)


class AtomicPriorityQueue:

    def __init__(self):
        self.heap = []
        self._lock = threading.Lock()

    def add(self, item, priority):
        with self._lock:
            pair = (priority,item)
            heapq.heappush(self.heap,pair)

    def contains(self, item):
        with self._lock:
            return item in (x[1] for x in self.heap)

    def poll(self):
        with self._lock:
            if len(self.heap) == 0:
                return None
            else:
                return heapq.heappop(self.heap)

    def size(self):
        with self._lock:
            return len(self.heap)
    

class AtomicSet:
    def __init__(self):
        self._set = set()
        self._lock = threading.Lock()
    
    def add(self, elem):
        with self._lock:
            self._set.add(elem)

    def contains(self, elem):
        with self._lock:
            return elem in self._set

    def get(self):
        with self._lock:
            return self._set.copy()

    def remove(self, elem):
        with self._lock:
            if elem in self._set:
                self._set.remove(elem)
    
    def size(self):
        with self._lock:
            return len(self._set)

class AtomicCounter:
    def __init__(self):
        self._count = 0
        self._lock = threading.Lock()

    def get(self):
        with self._lock:
            return self._count
    
    def increment(self):
        with self._lock:
            self._count += 1