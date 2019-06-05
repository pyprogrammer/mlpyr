import ast
import types
import inspect

from mlpyr.transformers.predecorate import PreDecorator


class Tracker:
    extracted_name = "_mlpyr_compiled"

    @staticmethod
    def tag(func):
        setattr(func, Tracker.extracted_name, True)
        return func

    @staticmethod
    def is_tagged(func):
        return hasattr(func, Tracker.extracted_name)


def extract(func: types.FunctionType):
    if Tracker.is_tagged(func):
        return func

    current_frameinfo = inspect.currentframe()
    decorated_frame = inspect.getouterframes(current_frameinfo)[1].frame

    code = inspect.getsource(func)
    filename = inspect.getsourcefile(func)
    parsed = ast.parse(code, inspect.getsourcefile(func))
    pre_decorated = ast.fix_missing_locations(PreDecorator().visit(parsed))

    modified_globals = {"Tracker": Tracker}
    modified_globals.update(decorated_frame.f_globals)

    modified_locals = {}
    modified_locals.update(decorated_frame.f_locals)

    exec(compile(pre_decorated, filename, "exec"), modified_globals, modified_locals)
    compiled = modified_locals[func.__name__]
    Tracker.tag(compiled)
    return compiled
