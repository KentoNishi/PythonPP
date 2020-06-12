import time

from pythonpp import PythonPP, method, constructor, special

@PythonPP
class NewTest:
    def namespace(public, private):

        public.static.pubstat = 420
        private.static.privstat = 19

        @constructor
        def NewTest(name, level):
            public.publicvar = 1
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

        @method(public.static)
        def get_private_static_variable():
            return private.static.privstat

        @method(public.static)
        def get_max_level():
            assert "public" in dir()
            assert "private" in dir()
            assert not hasattr(private, "name"), (
                "You should not be able to access "
                "instance variables from static scope"
            )
            assert not hasattr(public, "publicvar")
            return 12

        @method(private.static)
        def get_secret_key():
            assert "public" in dir()
            assert "private" in dir()
            return 420

        @special
        def __call__():
            return private.top_secret()

        @special
        def __str__():
            return "{name} is at level {level}".format(
                name=private.name,
                level=private.level
            )

obj = None

def test_creation():
    global obj
    obj = NewTest("steven", 10)
    assert type(obj) is NewTest

def test_public_get():
    assert obj.get_name() == "steven"
    assert obj.get_level() == 10

def test_public_set():
    obj.set_name("Steven")
    obj.set_level(11)
    assert obj.get_name() == "Steven"
    assert obj.get_level() == 11

def test_special_func():
    assert obj() == "Steven"*22
    assert str(obj) == "Steven is at level 11"

def test_private_encapsulation():
    assert not hasattr(obj, "private")
    assert not hasattr(obj, "name")

def test_public_access():
    assert obj.publicvar == 1

def test_public_static_method():
    assert NewTest.get_max_level() == 12

def test_private_static_encapsulation():
    assert not hasattr(NewTest, "get_secret_key")

def test_private_static_getter():
    assert NewTest.get_private_static_variable() == 19

def benchmark():
    obj = NewTest("steven", 10)
    assert obj.get_name() == "steven"
    assert obj.get_level() == 10
    obj.set_name("Steven")
    obj.set_level(11)
    assert obj.get_name() == "Steven"
    assert obj.get_level() == 11
    assert obj() == "Steven"*22
    assert str(obj) == "Steven is at level 11"

# obj = NewTest("steven", 10)
# def benchmark_no_assert(v):
#     obj.get_name()
#     obj.get_level()
#     obj.set_name("Steven")
#     obj.set_level(11)
#     obj.get_name()
#     obj.get_level()
#     obj()
#     str(obj)

if __name__ == "__main__":
    NUM_ITERATIONS = 100000
    beg = time.time()
    for _ in range(NUM_ITERATIONS):
        benchmark()
    print(time.time() - beg, "seconds")
