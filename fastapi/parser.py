# parser.py

import ast

class ASTParser:
    def __init__(self):
        self.parsers = {
            "python": self.parse_python
        }

    def parse(self, code: str, language: str):
        if language not in self.parsers:
            raise ValueError(f"Unsupported language: {language}")
        return self.parsers[language](code)

    def parse_python(self, code: str):
        try:
            tree = ast.parse(code)
            return self._walk(tree)
        except SyntaxError as e:
            raise ValueError("Parsing failed") from e

    def _walk(self, node):
        if not isinstance(node, ast.AST):
            return str(node)
        result = {
            "type": type(node).__name__,
            "fields": {},
            "children": []
        }
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                result["fields"][field] = [self._walk(item) for item in value if isinstance(item, ast.AST)]
            elif isinstance(value, ast.AST):
                result["fields"][field] = self._walk(value)
            else:
                result["fields"][field] = str(value)
        return result