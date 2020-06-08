# PythonPP
Python 3, but with proper encapsulation.

[View on PyPI](https://pypi.org/project/pythonpp/)

PythonPP stands for ***Python** **P**lus **P**lus*.

## Contributors

[Ronak Badhe](https://github.com/r2dev2bb8)
/
[Kento Nishi](https://github.com/KentoNishi)

## Installation
The package is available on PyPI.
You can install the package with the following command:
```shell
pip install pythonpp
```

## Usage
A detailed example of a class utilizing PythonPP is available in
[this Jupyter notebook](https://github.com/r2dev2bb8/PythonPP/blob/master/examples/example.ipynb).

**A PythonPP object must extend PythonPP's `objpp` class.**
**The constructor must also call the `__init__` method of the parent `objpp` class.**
When no ``__init`` method is defined, `super().__init__()` will be executed automatically.


Example:
```python
from pythonpp import *

# Class extends pythonpp's objpp class.
class Test(objpp):
    # Class constructor
    def __init__(self):
        # Call objpp's constructor.
        super().__init__()
    def namespace(public, private):
        # public: the public scope.
        # private: the private scope.
        pass
```

Alternatively, you can create your class without using a wildcard import.

```python
import pythonpp as ppp

class Test(ppp.objpp):
    def __init__(self):
        super().__init__()
    def namespace(public, private):
        pass
```

**All variable and method declarations must be done in the `namespace` method.**

 The namespace method has two parameters.

| Parameter | Value |
|:----------|:------|
| `public`  | The public scope. All variables in this scope can be accessed externally.
| `private` | The private scope. All variables in this scope can only be accessed internally. |

You can define public and private variables using these scopes.

**All variables and methods are declared private by default.**

Example:
```python
# public variable
public.hello = "hello"

# private variable
private.world = "world"
```

You can also use the public and private scopes to declare methods.

Example:
```python
# public method
@method(public)
def publicMethod():
    print("Called publicMethod")

# private method
@method(private)
def privateMethod():
    print("Called privateMethod")
```

Public variables and methods can be accessed as usual.

Example:
```python
test = Test()
# works as normal
print(test.hello)
# also works as normal
test.publicMethod()
```

However, private variables and methods **cannot be accessed** externally.

Example:
```python
test = Test()
# results in an error
print(test.world)
# also results in an error
test.privateMethod()
```

## Example Class
View the full Jupyter notebook [here](https://github.com/r2dev2bb8/PythonPP/blob/master/examples/example.ipynb).

```python
from pythonpp import *

class Test(objpp):
    # Class constructor
    def __init__(self):
        # Call objpp's constructor.
        super().__init__()

    # Place all methods and field declerations here.
    def namespace(public, private):
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
```