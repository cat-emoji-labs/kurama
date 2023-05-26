import ast

OPENAI_MODEL = "gpt-3.5-turbo"

DEFAULT_AST_ALLOWED_TYPES = (
    ast.Module,
    ast.Expr,
    ast.Dict,
    ast.Str,
    ast.Attribute,
    ast.Num,
    ast.Name,
    ast.Load,
    ast.Tuple,
    ast.List,
    ast.UnaryOp,  # for descending/ascending in a pipeline
    ast.USub,  # for descending/ascending in a pipeline
)
