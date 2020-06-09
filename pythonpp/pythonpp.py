import types
import functools


def __copyMethod(f):
    try:
        g = types.FunctionType(
            f.__code__,
            f.__globals__,
            name=f.__name__,
            argdefs=f.__defaults__,
            closure=f.__closure__,
        )
        g = functools.update_wrapper(g, f)
        g.__kwdefaults__ = f.__kwdefaults__
    except AttributeError:
        return lambda *args, **kwargs: None
    return g


class __PrivateScope:
    def __init__(self, values=dict()):
        for name, value in values.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


def PythonPP(cls):
    copiedInit = __copyMethod(cls.__init__)
    staticPrivateScope = __PrivateScope()

    class ScopeWrapper:
        pass

    class Scope(ScopeWrapper):
        def __init__(self, instance, static):
            super().__setattr__("instance", instance)
            super().__setattr__("static", static)

        def __getattribute__(self, name):
            try:
                if name == "static":
                    return super().__getattribute__("static")
                return super().__getattribute__("instance").__getattribute__(name)
            except AttributeError:
                return super().__getattribute__("static").__getattribute__(name)

        def __setattr__(self, name, value):
            try:
                object.__getattribute__(super().__getattribute__("static"), name)
                raise Exception(f'A static variable named "{name}" already exists.')
            except AttributeError:
                super().__getattribute__("instance").__setattr__(name, value)

    def newInit(self):
        copiedInit(self)
        publicScope = Scope(self, self.__class__)
        privateScope = Scope(__PrivateScope(), staticPrivateScope)
        self.__class__.namespace(publicScope, privateScope)

    cls.__init__ = newInit
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
