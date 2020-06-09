import types
import functools
import sys
import traceback


def __constructorCallback(func):
    """
    Called by the constructor.
    Dynamically replaced by PythonPP.
    """
    pass


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
    __constructorCallback(func)


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
        return lambda *args, **kwargs: None
    return g


def __parametrized(dec):
    """
    Allows existence of function wrappers with arguments which can have functions with arguments.
    """

    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


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

    class __PrivateScope:
        """
        A private scope type.
        This is just an object but it can set attributes with dot notation.
        """

        def __init__(self, values=dict()):
            for name, value in values.items():
                setattr(self, name, value)

        def __setattr__(self, name, value):
            object.__setattr__(self, name, value)

    class Wrapper:
        """
        An empty wrapper for scopes and data carrier classes.
        """

        pass

    initDone = False
    # signals if the constructor of the class finished executing.

    class Scope(Wrapper):
        """
        A Scope type which defaults attributes to instance.
        
        eg. If one gets an attribute, it will return instance.attribute
        """

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

    userConstructor = lambda *args, **kwargs: None

    def newConstructorCallback(func):
        """
        The replacement constructor decorator that takes the place of
        __constructorCallback. userConstructor is set to the function passed
        to the @constructor decorator.
        """
        nonlocal userConstructor
        userConstructor = func

        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        return inner

    copiedInit = __copyMethod(cls.__init__)

    def setAttr(self, name, value):
        object.__setattr__(self, name, value)

    builtinAttr = False

    def getAttr(self, name):
        """
        A get attribute function which doesn't allow access to static variables from instance methods.
        """
        nonlocal builtinAttr
        if name.startswith("__") and name.endswith("__"):
            builtinAttr = True
        if (not builtinAttr) and hasattr(cls, name):
            raise AttributeError("You cannot access static variables from an instance.")
        result = object.__getattribute__(self, name)
        builtinAttr = False
        return result

    def newInit(self, *args, **kwargs):
        """
        The replacement __init__ function for the user's class.
        Executes the original constructor, call
        """
        nonlocal copiedInit, userConstructor, newConstructorCallback, initDone
        global __constructorCallback

        __constructorCallback = newConstructorCallback

        copiedInit(self)

        staticPublicScope = PublicStaticWrapper(cls)
        staticPrivateScope = PrivateStaticWrapper(__PrivateScope())
        publicScope = Scope(self, staticPublicScope)
        privateScope = Scope(__PrivateScope(), staticPrivateScope)

        cls.namespace(publicScope, privateScope)
        userConstructor(*args, **kwargs)

        initDone = True
        cls.__getattribute__ = getAttr
        cls.__setattr__ = setAttr

    cls.__init__ = newInit

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
    setattr(cls, func.__name__, func)

    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner
