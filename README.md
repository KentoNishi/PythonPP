# Python++
Python 3, but with proper encapsulation.

[View on PyPI](https://pypi.org/project/pythonpp/)

PythonPP stands for ***Python** **P**lus **P**lus*.

Python++ allows Python programmers to use object oriented programming principles in Python.
Similar to Java, variables and methods can be **encapsulated**, or made **private**. 

Encapsulation is useful when storing sensitive persistent data within instances of objects.
For example, a programmer may want to hold a user's password in a variable - however,
in vanilla Python, the password variable can be manipulated by any external code in possession of the object instance. 
Python++ prevents such behavior by introducing private variables and methods to Python.

## Installation
The package is available on PyPI.
You can install the package with the following command:
```shell
pip install --upgrade --no-cache-dir pythonpp
```

## Usage

### Importing the Library

**A Python++ class must extend `pythonpp`'s `ClsPP` class.**
**The constructor must also call the `__init__` method of the parent `ClsPP` class.**

When no ``__init__`` method is defined, `super().__init__()` will be executed automatically.


Example:
```python
from pythonpp import *

# Class extends pythonpp's ClsPP class.
class Test(ClsPP):
    # Class constructor
    def __init__(self):
        # Call ClsPP's constructor.
        super().__init__()
    
    def namespace(public, private):
        # public: the public scope.
        # private: the private scope.
        pass
```

Alternatively, you can create your class without using a wildcard import.

```python
import pythonpp as ppp

class Test(ppp.ClsPP):
    def __init__(self):
        super().__init__()
        
    def namespace(public, private):
        pass
```

### Scopes and `namespace`

**All variable and method declarations must be done in the `namespace` method.**

 The namespace method has two parameters.

| Parameter | Value |
|:----------|:------|
| `public`  | The public scope. All variables in this scope can be accessed externally.
| `private` | The private scope. All variables in this scope can only be accessed internally. |

You can define public and private variables using these scopes.

**All variables and methods are declared private by default when the scope is not specified.**
**When you create a variable or method, it is highly recommended that you declare it private unless <u>absolutely necessary</u>.**

Example:
```python
class Test(ClsPP):
    def __init__(self):
        super().__init__()

    def namespace(public, private):
        # public variable
        public.hello = "hello"

        # private variable
        private.world = "world"
```

You can declare public and private methods using the `@method(scope)` decorator.

Example:
```python
class Test(ClsPP):
    def __init__(self):
        super().__init__()

    def namespace(public, private):
        # public method
        @method(public)
        def publicMethod():
            print("Called publicMethod")

        # private method
        @method(private)
        def privateMethod():
            print("Called privateMethod")
```

### External Access

Public variables and methods can be accessed the same way as in vanilla Python. However, private variables and methods **cannot be accessed** externally.

Example:
```python
from pythonpp import *

class Test(ClsPP):
    # Class constructor
    def __init__(self):
        # Call ClsPP's constructor.
        super().__init__()

    # Place all methods and field declarations here.
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
```python
test = Test()

# works as normal
print(test.hello)

# also works as normal
test.publicMethod()

# results in an error
print(test.world)

# also results in an error
test.privateMethod()
```

### Inheritance

All Python++ classes must extend the `ClsPP` class. You can also create Python++ classes that extend other classes using multiple inheritance.

For Python++ to work properly, you must call `ClsPP`'s constructor at some point in the `__init__` method.

Example:
```python
# parent class
class Parent():
    # Parent constructor
    def __init__(self):
        print("Parent constructor")

# child class
class Child(ClsPP, Parent):
    # child constructor
    def __init__(self):
        print("Child constructor")
        super(ClsPP, self).__init__()
        super(Parent, self).__init__()

    def namespace(public, private):
        pass
```

Alternatively, you can call the superclass constructors like so:

```python
# child class
class Child(ClsPP, Parent):
    # child constructor
    def __init__(self):
        # Same as super(ClsPP, self).__init__()
        ClsPP.__init__(self)
        # Same as super(Parent, self).__init__()
        Parent.__init__(self)

    def namespace(public, private):
        pass
```

## Full Example
You can view the full Jupyter notebook [here](https://github.com/r2dev2bb8/PythonPP/blob/master/examples/example.ipynb).

## Contributors

[Ronak Badhe](https://github.com/r2dev2bb8)
/
[Kento Nishi](https://github.com/KentoNishi)
