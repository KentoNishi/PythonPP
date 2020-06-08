import types
import functools


def __copyMethod(f):
    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


class __PrivateScope:
    def __init__(self, values=dict()):
        for name, value in values.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


def PythonPP(cls):
    copiedInit = __copyMethod(cls.__init__)

    def newInit(self):
        copiedInit(self)
        self.instance(__PrivateScope())

    cls.__init__ = newInit
    cls.static(cls, __PrivateScope())
    return cls


def __parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@__parametrized
def method(func, cls):
    setattr(cls, func.__name__, func)

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
