import ast

class CallAnnotator(ast.NodeTransformer):
    def visit_Call(self, call: ast.Call):
        pass
