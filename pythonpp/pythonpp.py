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


def __parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@__parametrized
def constructor(func, cls):
    cls.user_constructor = func
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner


def PythonPP(cls):
    class Wrapper:
        pass

    initDone = False

    class Scope(Wrapper):
        def __init__(self, instance, static):
            super().__setattr__("instance", instance)
            super().__setattr__("static", static)

        def __getattribute__(self, name):
            if name == "static":
                return super().__getattribute__("static")
            return super().__getattribute__("instance").__getattribute__(name)

        def __setattr__(self, name, value):
            object.__setattr__(super().__getattribute__("instance"), name, value)

    class PublicStaticWrapper(Wrapper):
        def __init__(self, static):
            super().__setattr__("static", static)

        def __getattribute__(self, name):
            return object.__getattribute__(super().__getattribute__("static"), name)

        def __setattr__(self, name, value):
            if initDone or not hasattr(super().__getattribute__("static"), name):
                setattr(
                    super().__getattribute__("static"), name, value,
                )

    class PrivateStaticWrapper(Wrapper):
        def __init__(self, static):
            super().__setattr__("static", static)

        def __getattribute__(self, name):
            return object.__getattribute__(super().__getattribute__("static"), name)

        def __setattr__(self, name, value):
            if initDone or not hasattr(super().__getattribute__("static"), name):
                object.__setattr__(super().__getattribute__("static"), name, value)

    copiedInit = __copyMethod(cls.__init__)

    def setAttr(self, name, value):
        object.__setattr__(self, name, value)

    def getAttr(self, name):
        if hasattr(cls, name):
            raise AttributeError("You cannot access static variables from an instance.")
        return object.__getattribute__(self, name)

    def newInit(self, *args, **kwargs):
        nonlocal copiedInit
        copiedInit(self)

        staticPublicScope = PublicStaticWrapper(cls)
        staticPrivateScope = PrivateStaticWrapper(__PrivateScope())
        publicScope = Scope(self, staticPublicScope)
        privateScope = Scope(__PrivateScope(), staticPrivateScope)

        cls.namespace(publicScope, privateScope)
        self.user_constructor(*args, **kwargs)

        initDone = True
        cls.__getattribute__ = getAttr
        cls.__setattr__ = setAttr

    cls.__init__ = newInit
    return cls


@__parametrized
def method(func, cls):
    setattr(cls, func.__name__, func)

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
