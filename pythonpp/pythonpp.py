import functools
import inspect
import sys
import types


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

__customConstructor = __empty
__publicScope = None
__privateScope = None
__bottomLevel = None
__namespacing = None
__isStaticContainer = __empty
__BLACKLIST = {"constructor", "namespace", "method", "static"}

# @__parametrized
# No parameterization when using one parameter
def constructor(func):
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
    global __customConstructor
    __customConstructor = func


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
    global __BLACKLIST

    # Adding stuff to the current scope to speed up lookup times
    globs = globals

    class Container:
        pass

    class Scope:
        def __init__(self, instance, static):
            object.__setattr__(self, "instance", instance)
            object.__setattr__(self, "static", static)

        def __getattribute__(self, name):
            if name == "static":
                return object.__getattribute__(self, "static")
            return object.__getattribute__(
                object.__getattribute__(self, "instance"), name
            )

        def __setattr__(self, name, value):
            if name in globs()["__BLACKLIST"]:
                raise AttributeError('Methods and variables cannot be named "{name}".'.format(name=name))
            object.__setattr__(object.__getattribute__(self, "instance"), name, value)

    class ContainerWrapper:
        def __init__(self, container):
            object.__setattr__(self, "container", container)

        def __getattribute__(self, name):
            return getattr(object.__getattribute__(self, "container"), name)

        def __setattr__(self, name, value):
            return setattr(object.__getattribute__(self, "container"), name, value)

    def blockStatic(name):
        permitted = name.startswith("__") and name.endswith("__")
        if (not permitted) and hasattr(cls, name):
            raise AttributeError(
                'Access to static variable or method "{name}" from an instance is not permitted.'.format(name=name)
            )

    class StaticContainerWrapper(ContainerWrapper):
        pass

    staticPrivateScope = StaticContainerWrapper(Container())
    staticPublicScope = StaticContainerWrapper(cls)

    def recursivelyInitNamespace(public, private):
        global __namespacing
        for base in cls.__bases__:
            if hasattr(base, "namespace"):
                __namespacing = base
                base.namespace(public, private)
                __namespacing = None
        __namespacing = cls
        cls.namespace(public, private)
        __namespacing = None

    def isStaticContainer(scope):
        return isinstance(scope, StaticContainerWrapper)

    def __init__(firstArg, *args, **kwargs):
        # firstArg is self if bottom level is not set
        # firstArg may not be self otherwise
        global __customConstructor, __publicScope, __privateScope, __bottomLevel, __namespacing, __isStaticContainer
        nonlocal staticPublicScope, staticPrivateScope, isStaticContainer
        if __bottomLevel is None:
            __publicScope = Scope(firstArg, staticPublicScope)
            __privateScope = Scope(ContainerWrapper(Container()), staticPrivateScope)
            __bottomLevel = cls
            __isStaticContainer = isStaticContainer
        recursivelyInitNamespace(__publicScope, __privateScope)

        copiedGetAttribute = __copyMethod(cls.__getattribute__)
        copiedSetAttribute = __copyMethod(cls.__setattr__)

        def __getattribute__(self, name):
            nonlocal copiedGetAttribute
            blockStatic(name)
            copiedGetAttribute(self, name)
            return object.__getattribute__(self, name)

        def __setattr__(self, name, value):
            nonlocal copiedSetAttribute
            blockStatic(name)
            copiedSetAttribute(self, name, value)
            return object.__setattr__(self, name, value)

        cls.__getattribute__ = __getattribute__
        cls.__setattr__ = __setattr__
        """
        argLength = len(inspect.signature(__customConstructor).parameters)
        requiredArgs = len(args)
        if argLength == requiredArgs + 1:
            if isinstance(firstArg, cls):
                warnings.warn(
                    f"The first argument specified, {firstArg}, is an instance of {cls}. "
                    + "Check your constructor's arguments to make sure you are passing "
                    + "the correct number of arguments.",
                    RuntimeWarning,
                )
            __customConstructor(firstArg, *args, **kwargs)
        elif argLength == requiredArgs:
        else:
            raise TypeError("Your constructor arguments did not match.")
        """
        if __customConstructor.__name__ == cls.__name__:
            __customConstructor(*args, **kwargs)
        else:
            raise AttributeError(
                'The constructor for "{clsname}" must match the class name.'.format(clsname=cls.__name__)
            )

        if cls == __bottomLevel:
            __publicScope = None
            __privateScope = None
            __bottomLevel = None
            __customConstructor = __empty
            __isStaticContainer = __empty

    cls.__init__ = __init__

    def staticConstructor(*args, **kwargs):
        nonlocal staticPublicScope
        cls.__init__(staticPublicScope, *args, **kwargs)

    cls.constructor = staticConstructor

    recursivelyInitNamespace(
        Scope(Container(), staticPublicScope), Scope(Container(), staticPrivateScope),
    )

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
    global __namespacing, __BLACKLIST
    if func.__name__ in __BLACKLIST:
        raise AttributeError('Methods cannot be named "{funcname}".'.format(funcname=func.__name__))
    elif func.__name__ == __namespacing.__qualname__:
        raise AttributeError(
            'The method name "{funcname}" is reserved for the constructor.'.format(funcname=func.__name__)
        )
    if not __isStaticContainer(cls):
        setattr(cls, func.__name__, func)

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
