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
    class Wrapper:
        pass

    class Scope(Wrapper):
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
                super().__getattribute__("static").__setattr__(name, value)
            except AttributeError:
                super().__getattribute__("instance").__setattr__(name, value)

    copiedGetAttr = None
    copiedInit = __copyMethod(cls.__init__)

    def newGetAttr(self, name):
        print(name)
        try:
            return object.__getattribute__(
                object.__getattribute__(self, "__class__"), name
            )
        except AttributeError:
            return copiedGetAttr(self, name)

    def newSetAttr(self, name, value):
        try:
            object.__getattribute__(object.__getattribute__(self, "__class__"), name)
            object.__getattribute__(self, "__class__").__setattr__(name, value)
        except AttributeError:
            object.__setattr__(self, name, value)

    def newInit(self):
        nonlocal copiedInit, copiedGetAttr
        copiedInit(self)
        staticPublicScope = self.__class__
        staticPrivateScope = __PrivateScope()
        publicScope = Scope(self, self.__class__)
        privateScope = Scope(__PrivateScope(), staticPrivateScope)
        self.__class__.namespace(publicScope, privateScope)
        copiedGetAttr = __copyMethod(self.__getattribute__)
        self.__getattribute__ = newGetAttr
        self.__setattr__ = newSetAttr

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
