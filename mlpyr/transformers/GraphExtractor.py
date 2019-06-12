import ast
import typing
import itertools

from ..internal import graph


class GraphExtractor:
    # Map of variable names to their symbols.
    sym_db: typing.Dict[str, graph.Sym]

    def __init__(self, globals_, locals_):
        self.value_ids = itertools.count()
        self.sym_db = {}
        self.globals = globals_
        self.locals = locals_

    def get_new_id(self):
        return f"%v{next(self.value_ids)}"

    def extract_args(self, arguments: ast.arguments):
        args = []
        for arg in arguments.args:
            arg_name = arg.arg
            arg_type = arg.annotation
            if arg_type is None:
                raise ValueError("Arguments must have annotations.")
            args.append(graph.Sym(arg_name, self.eval(arg_type)))
        return args

    def eval(self, node):
        if isinstance(node, ast.Expression):
            return eval(compile(node, filename="<string>", mode="eval"), self.globals, self.locals)
        return self.eval(ast.Expression(node))

    def extract_function(self, node: ast.FunctionDef):
        entry = graph.BlockLabel("main")
        func_args = self.extract_args(node.args)
        for arg in func_args:
            self.sym_db[arg.name] = arg

        if node.returns is None:
            raise ValueError("Functions must have return annotations")

        ret_type = self.eval(node.returns)

        func = graph.Function(name=node.name, entry=entry, blocks=[], args=func_args, ret_type=ret_type)
        entry_block = graph.Block(entry, body=[], inputs=func_args, terminator=graph.Ret(None))
        func.blocks.append(entry_block)

        scope = [entry_block]

        for child in node.body:
            if isinstance(child, (ast.If, ast.For, ast.While)):
                # These are control flow nodes
                pass

            elif isinstance(child, ast.Return):
                sym, history = self.extract_compute(child.value)
                scope[-1].body.extend(history)
                scope[-1].terminator = graph.Ret(sym)

            elif isinstance(child, ast.Assign):
                # Since python has simultaneous transfer semantics (i.e. a, b = b, a), we need to use temporaries.
                # For now, only handle direct assignments.
                eval_child = self.extract_compute(child.value)
                temporary = graph.Sym(self.get_new_id(), None)
                temp_copy = graph.Assign(temporary, eval_child[0])
                scope[-1].body.extend(eval_child[1] + [temp_copy])

                for target in child.targets:
                    if not isinstance(target, ast.Name):
                        raise NotImplementedError("Can only assign to variables right now")
                    new_sym = graph.Sym(target.id, None)
                    self.sym_db[target.id] = new_sym
                    scope[-1].body.append(graph.Assign(new_sym, temporary))

            elif isinstance(child, ast.AnnAssign):
                pass

            elif isinstance(child, ast.AugAssign):
                pass

            elif isinstance(child, ast.Expr):
                # possibly nested computations, but can never create a new block.
                scope[-1].body.extend(self.extract_compute(child.value)[1])
        return func

    def extract_compute(self, node) -> typing.Tuple[graph.Sym, typing.List]:
        if isinstance(node, ast.BinOp):
            left, lops = self.extract_compute(node.left)
            right, rops = self.extract_compute(node.right)
            retval = graph.Sym(self.get_new_id(), type(None))
            return retval, lops + rops + [graph.Assign(retval, graph.Op(node.op.__class__.__name__, [left, right]))]

        if isinstance(node, ast.Name):
            return self.sym_db.get(node.id, graph.Sym(node.id, None)), []

        if isinstance(node, ast.Num):
            sym = graph.Sym(self.get_new_id(), type(node.n))
            return sym, [graph.Assign(sym, graph.Constant(node.n))]

        if isinstance(node, ast.Call):
            sym, history = self.extract_compute(node.func)
            args, arg_histories = zip(*[self.extract_compute(arg) for arg in node.args])
            result = graph.Sym(self.get_new_id(), type(None))
            return result, history + sum(arg_histories, []) + [graph.Assign(result, graph.CallIndirect(sym, args))]

        raise NotImplementedError("Not implemented")
