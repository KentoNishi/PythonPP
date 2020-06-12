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

        @method(public)
        def call():
            return private.top_secret()

        @method(public)
        def str():
            return "{name} is at level {level}".format(
                name=private.name, level=private.level
            )

        @method(public)
        def repr():
            return public.str()


if __name__ == "__main__":
    obj = NewTest("steven", 10)
    print(obj)
    print(obj())
