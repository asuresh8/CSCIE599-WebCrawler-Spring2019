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

    def reset(self):
        with self._lock:
            self._queue.clear()


class AtomicPriorityCountQueue(dict):
    """Dictionary that can be used as a priority queue.
        Keys are urls and priority is based on the number of occurences
        of a specific url in the domain that is being crawled.
        Based upon: https://gist.github.com/matteodellamico/4451520
    """
    
    def __init__(self, *args, **kwargs):
        super(AtomicPriorityCountQueue, self).__init__(*args, **kwargs)
        self._rebuild_heap()
        self._lock = threading.Lock()

    def _rebuild_heap(self):
        self._heap = [(c, u) for u, c in self.items()]
        heapq._heapify_max(self._heap)

    def __setitem__(self, url, count):
        super(AtomicPriorityCountQueue, self).__setitem__(url, count)
        
        if len(self._heap) < 2 * len(self):
            heapq.heappush(self._heap, (count, url))
        
        self._rebuild_heap()

    def poll(self):
        """Return the url with the highest number of
           local occurences.
        """
        with self._lock:
            if len(self._heap) == 0:
                return (None, None)
            else:
                heap = self._heap
                c, u = heapq._heappop_max(heap)

                while u not in self or self[u] != c:
                    c, u = heapq._heappop_max(heap)
                del self[u]
                return (c, u)

    
    def add(self, url, count=None):
        with self._lock:
            if url not in self and count is None:
                self[url] = 1
                self._rebuild_heap()
            elif url not in self:
                self[url] = count
                self._rebuild_heap()
            else:
                count = self[url]
                count += 1
                self.__setitem__(url, count)
    
    def contains(self, url):
        with self._lock:
            return url in self
    
    def size(self):
        with self._lock:
            return len(self._heap)

    def update(self, *args, **kwargs):
        # Just rebuild the heap from scratch after passing to super.
        super(AtomicPriorityCountQueue, self).update(*args, **kwargs)
        self._rebuild_heap()

    def reset(self):
        with self._lock:
            if self._heap is not None:
                self._heap.clear()
            self.clear()


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

    def reset(self):
        with self._lock:
            self._set.clear()

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

    def reset(self):
        with self._lock:
            self._count = 0
