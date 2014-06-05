import functools

class memoize:
  def __init__(self, function):
    self.function = function
    self.memoized = {}

  def __call__(self, *args):
    try:
        return self.memoized[args]
    except KeyError:
        self.memoized[args] = self.function(*args)
        return self.memoized[args]


def immutable(method):
    @functools.wraps(method)
    def wrapped_method(self, *vargs, **kwargs):
        obj = self.clone()
        method(obj, *vargs, **kwargs)
        return obj

    return wrapped_method


def noop(value):
    return value


def soak(*vargs, **kwargs):
    pass