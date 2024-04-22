from functools import partial
import time

def memoize(max_age=0):
    """
    Cache the return value of a method for up to `max_age` seconds. If `max_age` is 0 (default), cache indefinitely.
    """
    class Memoizer(object):
        """
        Modified from https://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods/
        """
        def __init__(self, func):
            self.func = func
        def __get__(self, obj, objtype=None):
            if obj is None:
                return self.func
            return partial(self, obj)
        def __call__(self, *args, **kw):
            obj = args[0]
            try:
                cache = obj.__cache
            except AttributeError:
                cache = obj.__cache = {}
            
            key = (self.func, args[1:], frozenset(kw.items()))
            
            if key not in cache or (max_age != 0 and time.time() - cache[key][0] > max_age):
                cache[key] = (time.time(), self.func(*args, **kw))
            
            return cache[key][1]

    return Memoizer