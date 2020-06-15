# Python++
A robust Java-style OOP system for Python, with support for statics, encapsulation, and inheritance.

[View on PyPI](https://pypi.org/project/pythonpp/)

PythonPP stands for ***Python** **P**lus **P**lus*.

Python++ allows Python programmers to use object oriented programming principles in Python.


## Installation
The package is available on PyPI.
You can install the package with the following command:
```shell
pip install pythonpp
```

## Usage

### Class Declaration
Declare Python++ classes with the `@PythonPP` decorator.

```python
@PythonPP
class MyClass:
    pass # class code here
``` 

### Namespace and Scopes
Declare variables and methods for Python++ classes within `namespace(public, private)`.

```python
@PythonPP
class MyClass:
    def namespace(public, private):
        pass # methods and variables here
```

### Static Initializers
Declare static initializers for Python++ classes using the `@staticinit` decorator.
Static initializers do not have access to instance variables and methods.
Static initializers cannot have input parameters.

```python
@PythonPP
class MyClass:
    def namespace(public, private):
        @staticinit
        def StaticInit():
            public.static.publicStaticVar = "Static variable (public)"
            private.static.privateStaticVar = "Static variable (private)"
```

Alternatively, static variables can be declared in the bare `namespace` **if the variable assignments are constant**. Using bare static variable declarations are **not recommended**.


### Constructors
Constructors can be declared using the `@constructor` decorator. Constructors can have input parameters.

```python
@PythonPP
class MyClass:
    def namespace(public, private):
        @constructor
        def Constructor(someValue):
            public.publicInstanceVar = "Instance variable (public)"
            public.userDefinedValue = someValue
```

### Method Declarations
Methods are declared using the `@method(scope)` decorator with the `public` and `private` scopes in `namespace`.

```python
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

### Special Methods
Declare special built-in methods using the `@special` decorator.
```python
@PythonPP
class MyClass:
    def namespace(public, private):
        @special
        def __str__():
            return "Some string value"
```

### Inheritance
Classes can extend other classes using standard Python class inheritance.
```python
@PythonPP
class ParentClass:
    def namespace(public, private):
        @staticinit
        def StaticInit():
            public.static.staticVar = "Static variable"

        @constructor
        def Constructor(param):
            print("Parent constructor")
            public.param = param

@PythonPP
class ChildClass(ParentClass): # ChildClass extends ParentClass
    def namespace(public, private):
        @staticinit
        def StaticInit():
            ParentClass.staticinit() # Call parent static initializer
            public.static.staticVar2 = "Static variable 2"

        @constructor
        def Constructor(param):
            # Call parent constructor
            ParentClass.constructor(param)
```

## Full Example
You can view the full Jupyter notebook [here](https://github.com/r2dev2bb8/PythonPP/blob/master/examples/example.ipynb).

## Contributors

[Kento Nishi](https://github.com/KentoNishi)
/
[Ronak Badhe](https://github.com/r2dev2bb8)
