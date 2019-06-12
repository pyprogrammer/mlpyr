import ast
import types
import inspect

from mlpyr.transformers.tag import Tag
from mlpyr.transformers.GraphExtractor import GraphExtractor


class Tracker:
    extracted_name = "_mlpyr_compiled"

    @staticmethod
    def tag(func):
        setattr(func, Tracker.extracted_name, True)
        return func

    @staticmethod
    def is_tagged(func):
        return hasattr(func, Tracker.extracted_name)


def _extract_class(cls: type):
    pass


def _extract_function(func: types.FunctionType, modified_globals, modified_locals):
    if Tracker.is_tagged(func):
        return func


    code = inspect.getsource(func)
    filename = inspect.getsourcefile(func)
    parsed = ast.parse(code, inspect.getsourcefile(func))

    visitors = [
        Tag(),
    ]

    for visitor in visitors:
        if isinstance(visitor, ast.NodeVisitor):
            visitor.visit(parsed)
        else:
            parsed = visitor.visit(parsed)
    pre_decorated = ast.fix_missing_locations(parsed)

    exec(compile(pre_decorated, filename, "exec"), modified_globals, modified_locals)
    compiled = modified_locals[func.__name__]
    Tracker.tag(compiled)
    print(GraphExtractor(modified_globals, modified_locals).extract_function(pre_decorated.body[0]))
    return compiled


def extract(obj):
    current_frameinfo = inspect.currentframe()
    decorated_frame = inspect.getouterframes(current_frameinfo)[1].frame

    modified_globals = {"Tracker": Tracker}
    modified_globals.update(decorated_frame.f_globals)

    modified_locals = {}
    modified_locals.update(decorated_frame.f_locals)

    if isinstance(obj, type):
        return _extract_class(obj)
    else:
        return _extract_function(obj, modified_globals, modified_locals)