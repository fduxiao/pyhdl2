"""
Events
"""


class BaseEvent:
    """base class"""
    def trigger(self):
        """an event can be triggerred"""

    def __call__(self):
        self.trigger()


class Event(BaseEvent):
    """An Event based on a list of other events"""

    def __init__(self, *args: callable):
        self.events = list(args)

    def append(self, event: callable):
        """append another event"""
        self.events.append(event)

    def add(self, func: callable):
        """add a callable and return it"""
        self.events.append(func)
        return func

    def trigger(self):
        for event in self.events:
            event()


class Logger(list):
    """
    A logger with time.
    """
    time = 0

    def reset(self):
        """reset the logger"""

        super().clear()
        self.time = 0

    def raw_log(self, *args):
        """log some raw information"""
        self.append((self.time, *args))

    def log(self, *func: callable) -> BaseEvent:
        """log callables"""
        def event():
            self.append((self.time, *map(lambda f: f(), func)))
        return Event(event)

    def auto_inc(self):
        """the event used with simulator"""
        while True:
            yield
            self.time += 1
