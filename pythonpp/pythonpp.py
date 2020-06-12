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

    ### Example:
    
    ```python
    @constructor
    def __init__(variable1, variable2):
        private.variable1 = variable1
        private.static.variable2 = variable2
    ```
    """
    global __customConstructor
    __customConstructor = func


# No parameterization when using one parameter
# __add__ has two, self and other
# ah crap
# we have to add *arg and **kwarg then
# already have
# nvm im dumb i think this'll work
def builtin(func):
    assert func.__name__.startswith("__") and func.__name__.endswith(
        "__"
    ), "The method specified must be a builtin method."

    global __namespacing

    def getReplacement(theMethod):
        def replacementInternal(self, *args, **kwargs):
            return theMethod(*args, **kwargs)

        return replacementInternal

    setattr(
        __namespacing, func.__name__, getReplacement(func),
    )

    # is this is? or do we need parametrize
    # cause __add__ is __add__(self, other)
    # right we might need to do that
    # but wait
    # No parameterization when using one parameter
    # for @constructor


def __copy_method(f):
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

    ### Example:

    ```python
    @PythonPP
    class Test:
        def namespace(public, private):
            public.static.testVariable = "Hello World!"
    ```
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
                raise AttributeError(
                    'Methods and variables cannot be named "{name}".'.format(name=name)
                )
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
                'Access to static variable or method "{name}" from an instance is not permitted.'.format(
                    name=name
                )
            )

    class StaticContainerWrapper(ContainerWrapper):
        pass

    static_private_scope = StaticContainerWrapper(Container())
    static_public_scope = StaticContainerWrapper(cls)

    def getStaticConstructor(theClass):
        def static_constructor(*args, **kwargs):
            nonlocal static_public_scope
            theClass.__init__(static_public_scope, *args, **kwargs)

        return static_constructor

    def recursivelyInitNamespace(public, private):
        global __namespacing
        for base in cls.__bases__:
            if hasattr(base, "namespace"):
                __namespacing = base
                base.constructor = getStaticConstructor(base)
                base.namespace(public, private)
                __namespacing = None
        __namespacing = cls
        cls.namespace(public, private)
        __namespacing = None

    def isStaticContainer(scope):
        return isinstance(scope, StaticContainerWrapper)

    def __init__(self, *args, **kwargs):
        global __customConstructor, __publicScope, __privateScope, __bottomLevel, __namespacing, __isStaticContainer
        nonlocal static_public_scope, static_private_scope, isStaticContainer

        if __bottomLevel is None:
            __publicScope = Scope(self, static_public_scope)
            __privateScope = Scope(ContainerWrapper(Container()), static_private_scope)
            __bottomLevel = cls
            __isStaticContainer = isStaticContainer
        recursivelyInitNamespace(__publicScope, __privateScope)

        def __getattribute__(self, name):
            blockStatic(name)
            # copied_get_attribute(self, name)
            return object.__getattribute__(self, name)

        def __setattr__(self, name, value):
            blockStatic(name)
            # copied_set_attribute(self, name, value)
            print("Setting attribute", name)
            if name == "__str__":
                print("IT'S SETTING __STR__!")
            return object.__setattr__(self, name, value)

        if __customConstructor.__name__ == cls.__name__:
            __customConstructor(*args, **kwargs)
        else:
            raise AttributeError(
                'The constructor for "{clsname}" must match the class name.'.format(
                    clsname=cls.__name__
                )
            )
        if hasattr(cls, "constructor"):
            del cls.constructor

        if cls == __bottomLevel:
            __publicScope = None
            __privateScope = None
            __bottomLevel = None
            __customConstructor = __empty
            __isStaticContainer = __empty

        cls.__getattribute__ = __getattribute__
        cls.__setattr__ = __setattr__

    cls.__init__ = __init__

    recursivelyInitNamespace(
        Scope(Container(), static_public_scope),
        Scope(Container(), static_private_scope),
    )

    return cls


@__parametrized
def method(func, cls):
    """
    Used to expose methods to a particular scope

    ### Example use case:

    ```python
    @method(public)
    def publicmethod(*args, **kwargs):
        for arg in args:
            print(arg)
    ```

    :``param cls`` - the scope which the method is exposed to
    """
    global __namespacing, __BLACKLIST
    if func.__name__ in __BLACKLIST:
        raise AttributeError(
            'Methods cannot be named "{funcname}".'.format(funcname=func.__name__)
        )
    elif func.__name__ == __namespacing.__qualname__:
        raise AttributeError(
            'The method name "{funcname}" is reserved for the constructor.'.format(
                funcname=func.__name__
            )
        )

    if not __isStaticContainer(cls):
        setattr(cls, func.__name__, func)

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
