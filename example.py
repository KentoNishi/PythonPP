from pythonpp import *

class test(objpp):
    def __init__(self, toyeet):
        self.toyeet = toyeet
        super().__init__()

    def namespace(public, private):
        private.h1 = "hello"

        @privatemethod(private)
        def privateAlgo(ipt):
            return ipt.capitalize()

        @publicmethod(public)
        def get1(key):
            if key == "yee":
                return private.privateAlgo(private.h1)
            return "screw you"

        @publicmethod(public)
        def get2():
            return ["hidden_2"]

        @publicmethod(public)
        def set1(new1):
            private.h1 = new1


if __name__ == "__main__":
    obj = test(toyeet=True)
    print(obj.get1("yee"))
    obj.set1("ho")
    print(obj.get1("yee"))
