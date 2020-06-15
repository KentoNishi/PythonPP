import functools
import inspect
import sys
import types

__empty = lambda *args, **kwargs: None
__customConstructor = __empty
__customStaticinit = __empty
__publicScope = None
__privateScope = None
__bottomLevel = None
__namespacing = None
__isStaticContainer = __empty
__staticNamespacing = False
__BLACKLIST = {
    "constructor",
    "method",
    "method",
    "namespace",
    "private",
    "public",
    "special",
    "static",
    "staticinit",
}


def __parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


def __is_special(name):
    return name.startswith("__") and name.endswith("__")


def __copy_method(f):
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


def constructor(func):
    """
    The constructor decorator for Python++ classes.
    ### Example
    ```
    @PythonPP
    class MyClass:
        def namespace(public, private):
            @constructor
            def MyConstructor(parameter):
                private.variable = parameter
    ```
    """
    global __customConstructor
    __customConstructor = func


def staticinit(func):
    """
    The static initializer decorator for Python++ classes.
    ### Example
    ```
    @PythonPP
    class MyClass:
        def namespace(public, private):
            @staticinit
            def MyStaticInit(parameter):
                private.static.variable = parameter
    ```
    """
    global __namespacing, __staticNamespacing

    if __staticNamespacing:
        __namespacing.staticinit = func


def special(func):
    """
    The special method decorator for Python++ classes.
    ### Example
    ```
    @PythonPP
    class MyClass:
        def namespace(public, private):
            @special
            def __str__():
                return f"MyClass instance where private.variable = {private.variable}"
    ```
    """

    global __namespacing

    if not __is_special(func.__name__):
        raise AttributeError(
            (
                'The function "{methodName}" is not a built in function. '
                + 'Use "__" before and after the method name to declare it as a special method.'
            ).format(methodName=func.__name__)
        )

    def getReplacement(theMethod):
        def replacementInternal(self, *args, **kwargs):
            return theMethod(*args, **kwargs)

        return replacementInternal

    setattr(
        __namespacing, func.__name__, getReplacement(func),
    )


@__parametrized
def method(func, scope):
    """
    The method decorator for Python++ classes.

    ### Example
    ```
    @PythonPP
    class MyClass:
        def namespace(public, private):
            @method(public)
            def publicMethod():
                pass # public instance method here
            @method(private)
            def privateMethod():
                pass # private instance method here
            @method(public.static)
            def publicStaticMethod():
                pass # public static method here
            @method(private.static)
            def privateStaticMethod():
                pass # private static method here
    ```
    
    ### Parameters
    `scope`: The method scope.
    Either `public`, `private`, `public.static`, or `private.static`.
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
    elif __is_special(func.__name__):
        raise AttributeError(
            (
                'The method name "{funcname}" starts and ends with "__". '
                + "Such method names are reserved for special methods created with @special."
            ).format(funcname=func.__name__)
        )
    if not __isStaticContainer(scope):
        try:
            setattr(scope, func.__name__, func)
        except AttributeError:
            pass

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner


def PythonPP(cls):
    """
    The class decorator for Python++ classes.

    ### Example
    ```
    @PythonPP
    class MyClass:
        def namespace(public, private):
            pass # Methods and variables here
    ```
    """
    global __BLACKLIST, __staticNamespacing

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
            if object.__getattribute__(self, "instance") is None:
                raise AttributeError(
                    "The variable or method cannot be retrieved because the instance scope is empty."
                )
            return object.__getattribute__(
                object.__getattribute__(self, "instance"), name
            )

        def __setattr__(self, name, value):
            if name in globs()["__BLACKLIST"]:
                raise AttributeError(
                    'Methods and variables cannot be named "{name}".'.format(name=name)
                )
            if object.__getattribute__(self, "instance") is None:
                raise AttributeError(
                    "The variable or method cannot be created because the instance scope is empty."
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
        permitted = __is_special(name)
        if (not permitted) and hasattr(cls, name):
            raise AttributeError(
                'Access to static variable or method "{name}" from an instance is not permitted.'.format(
                    name=name
                )
            )

    class StaticContainerWrapper(ContainerWrapper):
        def __getattribute__(self, name):
            if (globs()["__bottomLevel"] is not None) and not globs()[
                "__staticNamespacing"
            ]:
                return
            return super().__getattribute__(name)

        def __setattr__(self, name, value):
            if (globs()["__bottomLevel"] is not None) and not globs()[
                "__staticNamespacing"
            ]:
                return
            return super().__setattr__(name, value)

    static_private_scope = StaticContainerWrapper(Container())
    static_public_scope = StaticContainerWrapper(cls)

    def getStaticConstructor(theClass):
        def static_constructor(*args, **kwargs):
            nonlocal static_public_scope
            theClass.__init__(static_public_scope, *args, **kwargs)

        return static_constructor

    def recursivelyInitNamespace(public, private):
        global __namespacing, __customConstructor
        for base in cls.__bases__:
            if hasattr(base, "namespace"):
                __namespacing = base
                base.constructor = getStaticConstructor(base)
                base.namespace(public, private)
                __namespacing = None
                __customConstructor = __empty
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
            __customConstructor = __empty
        recursivelyInitNamespace(__publicScope, __privateScope)

        def __getattribute__(self, name):
            blockStatic(name)
            # copied_get_attribute(self, name)
            return object.__getattribute__(self, name)

        def __setattr__(self, name, value):
            blockStatic(name)
            return object.__setattr__(self, name, value)

        if __customConstructor is __empty:
            pass
        else:
            __customConstructor(*args, **kwargs)

        if cls == __bottomLevel:
            __publicScope = None
            __privateScope = None
            __bottomLevel = None
            __isStaticContainer = __empty

        cls.__getattribute__ = __getattribute__
        cls.__setattr__ = __setattr__

        for base in cls.__bases__:
            if hasattr(base, "constructor"):
                del base.constructor

    cls.__init__ = __init__
    cls.staticinit = __empty

    __staticNamespacing = True
    for base in cls.__bases__:
        if hasattr(base, "namespace"):
            base.staticinit = __empty
    recursivelyInitNamespace(
        Scope(None, static_public_scope), Scope(None, static_private_scope),
    )
    cls.staticinit()
    __staticNamespacing = False

    def recursivelyClearStaticinits(theClass):
        if hasattr(theClass, "staticinit"):
            del theClass.staticinit
        for base in theClass.__bases__:
            recursivelyClearStaticinits(base)

    recursivelyClearStaticinits(cls)

    return cls
