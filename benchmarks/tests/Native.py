import time


class NativeTest:
    def __init__(self, name, level):
        self.publicvar = 1
        self.__name = name
        self.__level = level

    def get_name(self):
        return self.__name

    def get_level(self):
        return self.__level

    def set_name(self, new_name):
        assert type(new_name) is str
        self.__name = new_name

    def set_level(self, new_level):
        assert type(new_level) is int
        self.__level = new_level

    def __top_secret(self):
        return self.__name * self.__level * 2

    def __call__(self):
        return self.__top_secret()

    def __str__(self):
        return "{name} is at level {level}".format(name=self.__name, level=self.__level)


def benchmark():
    obj = NativeTest("steven", 10)
    assert obj.get_name() == "steven"
    assert obj.get_level() == 10
    obj.set_name("Steven")
    obj.set_level(11)
    assert obj.get_name() == "Steven"
    assert obj.get_level() == 11
    assert obj() == "Steven" * 22
    assert str(obj) == "Steven is at level 11"

# obj = NativeTest("steven", 10)
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
