import time

from pythonpp import *

@PythonPP
class NewTest:
    def namespace(public, private):

        public.publicvar = 1

        @constructor
        def NewTest(name, level):
            private.name = name
            private.level = level

        @method(public)
        def get_name():
            return private.name

        @method(public)
        def get_level():
            return private.level

        @method(public)
        def set_name(new_name):
            assert type(new_name) is str
            private.name = new_name

        @method(public)
        def set_level(new_level):
            assert type(new_level) is int
            private.level = new_level
            
        @method(private)
        def top_secret():
            return private.name * private.level * 2

        @builtin
        def call():
            return private.top_secret()

        @builtin
        def str():
            return "{name} is at level {level}".format(
                name=private.name,
                level=private.level
            )

# def benchmark():
#     obj = NewTest("steven", 10)
#     assert obj.get_name() == "steven"
#     assert obj.get_level() == 10
#     obj.set_name("Steven")
#     obj.set_level(11)
#     assert obj.get_name() == "Steven"
#     assert obj.get_level() == 11
#     assert obj() == "Steven"*22
#     assert str(obj) == "Steven is at level 11"

obj = NewTest("steven", 10)
def benchmark_no_assert(v):
    obj.get_name()
    obj.get_level()
    obj.set_name("Steven")
    obj.set_level(11)
    obj.get_name()
    obj.get_level()
    obj()
    str(obj)

if __name__ == "__main__":
    NUM_ITERATIONS = 100000
    beg = time.time()
    for _ in range(NUM_ITERATIONS):
        benchmark_no_assert("re")
    print(time.time() - beg, "seconds")
