import types
import functools
import sys
import traceback


def __parametrized(dec):
    """
    Allows existence of function wrappers with arguments which can have functions with arguments.
    """

    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


__empty = lambda *args, **kwargs: None
__callback = __empty

__customConstructor = __empty
__publicScope = None
__privateScope = None
__bottomLevel = None


@__parametrized
def constructor(func, public, private):
    """
    Constructor Wrapper for Python++ classes
    The decorator does not take any arguments.
    The scope is assumed to be a public instance method.

    Example:
    
    @constructor
    def __init__(variable1, variable2):
        private.variable1 = variable1
        private.static.variable2 = variable2
    """
    __callback(func, public, private)


def __copyMethod(f):
    """
    Creates a clone of a given method.
    """
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
        return __empty
    return g


def PythonPP(cls):
    """
    The class wrapper to create Python++ objects.
    Use this decorator on a class to declare it as a Python++ class.

    Example:

    @PythonPP
    class Test:
        def namespace(public, private):
            public.static.testVariable = "Hello World!"
    """

    class Container:
        pass

    class Scope:
        def __init__(self, instance, static):
            object.__setattr__(self, "instance", instance)
            object.__setattr__(self, "static", static)

        def __getattribute__(self, name):
            if name == "static":
                return self.static
            return object.__getattribute__(self, "instance").__getattribute__(name)

        def __setattr__(self, name, value):
            object.__setattr__(object.__getattribute__(self, "instance"), name, value)

    staticPrivateScope = Container()

    def callback(func, public, private):
        global __customConstructor, __publicScope, __privateScope
        __customConstructor = func
        __publicScope = public
        __privateScope = private

    global __callback
    __callback = callback

    def __init__(self, *args, **kwargs):
        global __customConstructor, __publicScope, __privateScope, __bottomLevel
        if __bottomLevel == None:
            __publicScope = Scope(self, self.__class__)
            __privateScope = Scope(Container(), staticPrivateScope)
            __bottomLevel = cls
        __customConstructor = __empty
        for base in cls.__bases__:
            if(hasattr(base, "namespace")):
                base.namespace(__publicScope, __privateScope)
        cls.namespace(__publicScope, __privateScope)
        __customConstructor(*args, **kwargs)
        if(cls == __bottomLevel):
            __publicScope = None
            __privateScope = None
            __bottomLevel = None

    cls.__init__ = __init__
    return cls


@__parametrized
def method(func, cls):
    """
    Used to expose methods to a particular scope

    Example use case:
    @method(public)
    def publicmethod(*args, **kwargs):
        for arg in args:
            print(arg)

    :param cls - the scope which the method is exposed to
    """
    object.__setattr__(cls, func.__name__, func)

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
