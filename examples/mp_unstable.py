from pythonpp import *
from multiprocessing import Process, freeze_support

# Class extends pythonpp's ClsPP class.
@PythonPP
class Test:
    # Place all methods and field declarations here.
    def namespace(public, private):
        public.static.staticVar = "Static Variable"
        @constructor
        def __init__(key):
            private.key = key
        # public variable
        public.hello = "hello"
        # private variable
        private.world = "world"

        # public method
        @method(public)
        def publicMethod():
            print("Called publicMethod")
        
        # private method
        @method(private)
        def privateMethod():
            print("Called privateMethod")

        # public method to call the private method.
        @method(public)
        def callPrivateMethod():
            print("Calling privateMethod()")
            # Call the private method
            private.privateMethod()

        @method(public.static)
        def getKey_Fail():
            return private.key

        @method(public)
        def getKey():
            return private.key


@PythonPP
class Test1:
    def namespace(public, private):
        @constructor
        def __init__(key):
            private.key = key
            
        @method(public)
        def revealArgs():
            print(private.key)

@PythonPP
class Test2:
    def namespace(public, private):
        @constructor
        def __init__(key):
            private.key = key
            
        @method(public)
        def revealArgs():
            print(private.key)

def test1stuff():
    for i in range(10):
        a = Test("ssh")
        # print(a.getKey())

def test2stuff():
    for i in range(10):
        a = Test2("hello", "world")
        a.revealArgs()

if __name__ == "__main__":
    freeze_support()
    t1 = Process(target=test1stuff)
    t2 = Process(target=test2stuff)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

