import atomic

class Context:
    def __init__(self, logger):
        self.logger = logger
        self.active_thread_count = atomic.AtomicCounter()