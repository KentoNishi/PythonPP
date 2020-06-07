class privateScope:
    def __init__(self, values=dict()):
        for name, value in values.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
    
class objpp:
    def __init__(self):
        self.namespace(privateScope())

    def namespace(public, private):
        pass


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


@parametrized
def publicmethod(func, cls):
    setattr(cls, func.__name__, func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner

privatemethod = publicmethod
