import ast


class Tag(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef):
        node = self.generic_visit(node)
        # Last element of the decorator list corresponds to the first one to be applied.
        node.decorator_list.append(
            ast.Attribute(value=ast.Name(id='Tracker', ctx=ast.Load()), attr='tag', ctx=ast.Load()))
        return node



