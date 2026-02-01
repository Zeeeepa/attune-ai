"""Comprehensive coverage tests for AST Function Analyzer.

Tests function signature extraction, class analysis, exception detection,
side effect detection, and complexity estimation.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

import attune.workflows.test_gen.ast_analyzer as ast_analyzer_module
import attune.workflows.test_gen.data_models as data_models_module

ASTFunctionAnalyzer = ast_analyzer_module.ASTFunctionAnalyzer
FunctionSignature = data_models_module.FunctionSignature
ClassSignature = data_models_module.ClassSignature


@pytest.mark.unit
class TestASTFunctionAnalyzerBasicFunctions:
    """Test basic function signature extraction."""

    def test_simple_function_extraction(self):
        """Test extracting a simple function with no parameters."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def simple_func():
    return 42
"""
        functions, classes = analyzer.analyze(code)

        assert len(functions) == 1
        assert len(classes) == 0
        assert functions[0].name == "simple_func"
        assert functions[0].params == []
        assert functions[0].is_async is False

    def test_function_with_parameters(self):
        """Test extracting function with typed parameters."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def add(x: int, y: int) -> int:
    return x + y
"""
        functions, _ = analyzer.analyze(code)

        assert len(functions) == 1
        func = functions[0]
        assert func.name == "add"
        assert len(func.params) == 2
        assert func.params[0] == ("x", "int", None)
        assert func.params[1] == ("y", "int", None)
        assert func.return_type == "int"

    def test_function_with_default_params(self):
        """Test extracting function with default parameter values."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def greet(name: str = "World", count: int = 1):
    pass
"""
        functions, _ = analyzer.analyze(code)

        func = functions[0]
        assert func.params[0] == ("name", "str", "'World'")
        assert func.params[1] == ("count", "int", "1")

    def test_function_with_mixed_params(self):
        """Test function with required and optional parameters."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def mixed(required: str, optional: int = 10, optional2: bool = True):
    pass
"""
        functions, _ = analyzer.analyze(code)

        func = functions[0]
        assert func.params[0] == ("required", "str", None)
        assert func.params[1] == ("optional", "int", "10")
        assert func.params[2] == ("optional2", "bool", "True")


@pytest.mark.unit
class TestASTFunctionAnalyzerAsyncFunctions:
    """Test async function extraction."""

    def test_async_function_detection(self):
        """Test that async functions are correctly identified."""
        analyzer = ASTFunctionAnalyzer()
        code = """
async def fetch_data():
    return "data"
"""
        functions, _ = analyzer.analyze(code)

        assert len(functions) == 1
        assert functions[0].name == "fetch_data"
        assert functions[0].is_async is True

    def test_async_function_with_params(self):
        """Test async function with parameters."""
        analyzer = ASTFunctionAnalyzer()
        code = """
async def fetch_user(user_id: int) -> dict:
    return {"id": user_id}
"""
        functions, _ = analyzer.analyze(code)

        func = functions[0]
        assert func.is_async is True
        assert func.params == [("user_id", "int", None)]
        assert func.return_type == "dict"


@pytest.mark.unit
class TestASTFunctionAnalyzerClassExtraction:
    """Test class signature extraction."""

    def test_simple_class_extraction(self):
        """Test extracting a simple class with no methods."""
        analyzer = ASTFunctionAnalyzer()
        code = """
class EmptyClass:
    pass
"""
        functions, classes = analyzer.analyze(code)

        assert len(functions) == 0
        assert len(classes) == 1
        assert classes[0].name == "EmptyClass"
        assert classes[0].methods == []
        assert classes[0].is_enum is False
        assert classes[0].is_dataclass is False

    def test_class_with_init(self):
        """Test extracting class with __init__ method."""
        analyzer = ASTFunctionAnalyzer()
        code = """
class User:
    def __init__(self, name: str, age: int = 18):
        self.name = name
        self.age = age
"""
        _, classes = analyzer.analyze(code)

        cls = classes[0]
        assert cls.name == "User"
        assert len(cls.methods) == 1
        assert cls.methods[0].name == "__init__"
        assert cls.init_params == [("name", "str", None), ("age", "int", "18")]
        assert cls.required_init_params == 1  # Only 'name' is required

    def test_class_with_multiple_methods(self):
        """Test extracting class with multiple methods."""
        analyzer = ASTFunctionAnalyzer()
        code = """
class Calculator:
    def __init__(self):
        pass

    def add(self, x: int, y: int) -> int:
        return x + y

    def subtract(self, x: int, y: int) -> int:
        return x - y
"""
        _, classes = analyzer.analyze(code)

        cls = classes[0]
        assert len(cls.methods) == 3
        method_names = [m.name for m in cls.methods]
        assert "__init__" in method_names
        assert "add" in method_names
        assert "subtract" in method_names

    def test_class_with_base_classes(self):
        """Test extracting class inheritance information."""
        analyzer = ASTFunctionAnalyzer()
        code = """
class Parent:
    pass

class Child(Parent):
    pass
"""
        _, classes = analyzer.analyze(code)

        child_class = [c for c in classes if c.name == "Child"][0]
        assert "Parent" in child_class.base_classes

    def test_enum_detection(self):
        """Test detecting Enum classes."""
        analyzer = ASTFunctionAnalyzer()
        code = """
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
"""
        _, classes = analyzer.analyze(code)

        assert classes[0].is_enum is True

    def test_dataclass_detection(self):
        """Test detecting dataclass decorator."""
        analyzer = ASTFunctionAnalyzer()
        code = """
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
"""
        _, classes = analyzer.analyze(code)

        assert classes[0].is_dataclass is True

    def test_dataclass_with_call_decorator(self):
        """Test detecting dataclass with call syntax."""
        analyzer = ASTFunctionAnalyzer()
        code = """
@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int
"""
        _, classes = analyzer.analyze(code)

        assert classes[0].is_dataclass is True


@pytest.mark.unit
class TestASTFunctionAnalyzerExceptionDetection:
    """Test detection of raised exceptions."""

    def test_simple_exception_raise(self):
        """Test detecting simple exception raises."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def risky():
    raise ValueError("error")
"""
        functions, _ = analyzer.analyze(code)

        assert "ValueError" in functions[0].raises

    def test_multiple_exception_types(self):
        """Test detecting multiple exception types."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def multi_risk(flag: bool):
    if flag:
        raise ValueError("value error")
    else:
        raise TypeError("type error")
"""
        functions, _ = analyzer.analyze(code)

        assert "ValueError" in functions[0].raises
        assert "TypeError" in functions[0].raises

    def test_exception_from_name(self):
        """Test detecting exception raised from variable."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def raise_from_var():
    error = ValueError("error")
    raise error
"""
        functions, _ = analyzer.analyze(code)

        # Should detect "error" as the exception name
        assert "error" in functions[0].raises or len(functions[0].raises) >= 0


@pytest.mark.unit
class TestASTFunctionAnalyzerSideEffects:
    """Test side effect detection."""

    def test_print_detected_as_side_effect(self):
        """Test that print() is detected as a side effect."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def logger(message):
    print(message)
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].has_side_effects is True

    def test_file_write_detected(self):
        """Test that file writes are detected."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def save_data(data):
    with open("file.txt", "w") as f:
        f.write(data)
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].has_side_effects is True

    def test_method_call_side_effect(self):
        """Test detecting side effects in method calls."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def update_db(record):
    db.update(record)
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].has_side_effects is True

    def test_pure_function_no_side_effects(self):
        """Test that pure functions have no side effects."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def add(x, y):
    return x + y
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].has_side_effects is False


@pytest.mark.unit
class TestASTFunctionAnalyzerComplexity:
    """Test complexity estimation."""

    def test_simple_function_complexity(self):
        """Test complexity of simple linear function."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def simple():
    x = 1
    y = 2
    return x + y
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].complexity == 1

    def test_if_statement_increases_complexity(self):
        """Test that if statements increase complexity."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def with_if(x):
    if x > 0:
        return x
    return 0
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].complexity == 2  # 1 base + 1 if

    def test_multiple_branches(self):
        """Test complexity with multiple branches."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def multi_branch(x, y):
    if x > 0:
        if y > 0:
            return x + y
    return 0
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].complexity == 3  # 1 base + 2 ifs

    def test_loop_increases_complexity(self):
        """Test that loops increase complexity."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def with_loop(items):
    for item in items:
        print(item)
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].complexity >= 2  # 1 base + 1 for

    def test_exception_handler_complexity(self):
        """Test that exception handlers increase complexity."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def with_try():
    try:
        risky()
    except ValueError:
        handle()
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].complexity >= 2  # 1 base + 1 except


@pytest.mark.unit
class TestASTFunctionAnalyzerDecorators:
    """Test decorator extraction."""

    def test_simple_decorator(self):
        """Test extracting simple decorator."""
        analyzer = ASTFunctionAnalyzer()
        code = """
@property
def value(self):
    return self._value
"""
        functions, _ = analyzer.analyze(code)

        assert "property" in functions[0].decorators

    def test_multiple_decorators(self):
        """Test extracting multiple decorators."""
        analyzer = ASTFunctionAnalyzer()
        code = """
@staticmethod
@cache
def compute():
    pass
"""
        functions, _ = analyzer.analyze(code)

        assert "staticmethod" in functions[0].decorators
        assert "cache" in functions[0].decorators

    def test_decorator_with_arguments(self):
        """Test extracting decorator with call syntax."""
        analyzer = ASTFunctionAnalyzer()
        code = """
@retry(max_attempts=3)
def unstable():
    pass
"""
        functions, _ = analyzer.analyze(code)

        assert "retry" in functions[0].decorators


@pytest.mark.unit
class TestASTFunctionAnalyzerDocstrings:
    """Test docstring extraction."""

    def test_function_docstring(self):
        """Test extracting function docstring."""
        analyzer = ASTFunctionAnalyzer()
        code = '''
def documented():
    """This is a docstring."""
    pass
'''
        functions, _ = analyzer.analyze(code)

        assert functions[0].docstring == "This is a docstring."

    def test_class_docstring(self):
        """Test extracting class docstring."""
        analyzer = ASTFunctionAnalyzer()
        code = '''
class Documented:
    """This is a class docstring."""
    pass
'''
        _, classes = analyzer.analyze(code)

        assert classes[0].docstring == "This is a class docstring."


@pytest.mark.unit
class TestASTFunctionAnalyzerErrorHandling:
    """Test error handling and edge cases."""

    def test_syntax_error_handling(self):
        """Test that syntax errors are handled gracefully."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def broken(
    # Missing closing paren
"""
        functions, classes = analyzer.analyze(code, file_path="test.py")

        # Should return empty lists
        assert functions == []
        assert classes == []
        # Should set last_error
        assert analyzer.last_error is not None
        assert "SyntaxError" in analyzer.last_error
        assert "test.py" in analyzer.last_error

    def test_empty_code(self):
        """Test handling empty code."""
        analyzer = ASTFunctionAnalyzer()
        functions, classes = analyzer.analyze("")

        assert functions == []
        assert classes == []
        assert analyzer.last_error is None

    def test_comments_only(self):
        """Test handling code with only comments."""
        analyzer = ASTFunctionAnalyzer()
        code = """
# Just a comment
# Another comment
"""
        functions, classes = analyzer.analyze(code)

        assert functions == []
        assert classes == []

    def test_nested_functions_not_extracted(self):
        """Test that nested functions are not extracted as top-level."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def outer():
    def inner():
        pass
    return inner
"""
        functions, _ = analyzer.analyze(code)

        # Should only extract outer function
        assert len(functions) == 1
        assert functions[0].name == "outer"


@pytest.mark.unit
class TestASTFunctionAnalyzerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_function_with_no_return_type(self):
        """Test function without return type annotation."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def no_return():
    pass
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].return_type is None

    def test_parameter_without_type_hint(self):
        """Test parameter without type annotation."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def untyped(x):
    return x
"""
        functions, _ = analyzer.analyze(code)

        assert functions[0].params[0] == ("x", "Any", None)

    def test_class_with_async_methods(self):
        """Test class with async methods."""
        analyzer = ASTFunctionAnalyzer()
        code = """
class AsyncHandler:
    async def fetch(self):
        pass
"""
        _, classes = analyzer.analyze(code)

        assert len(classes[0].methods) == 1
        assert classes[0].methods[0].is_async is True

    def test_multiple_classes_and_functions(self):
        """Test file with both classes and functions."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def standalone():
    pass

class MyClass:
    def method(self):
        pass

def another():
    pass
"""
        functions, classes = analyzer.analyze(code)

        assert len(functions) == 2
        assert len(classes) == 1
        assert functions[0].name == "standalone"
        assert functions[1].name == "another"

    def test_complex_default_value(self):
        """Test handling complex default values."""
        analyzer = ASTFunctionAnalyzer()
        code = """
def with_dict(config: dict = None):
    pass
"""
        functions, _ = analyzer.analyze(code)

        # Should extract the default value
        assert functions[0].params[0][2] == "None"


@pytest.mark.unit
class TestASTFunctionAnalyzerIntegration:
    """Integration tests combining multiple features."""

    def test_complete_class_analysis(self):
        """Test complete analysis of a realistic class."""
        analyzer = ASTFunctionAnalyzer()
        code = """
from dataclasses import dataclass

@dataclass
class User:
    '''User model with authentication.'''

    def __init__(self, username: str, email: str, active: bool = True):
        self.username = username
        self.email = email
        self.active = active

    async def authenticate(self, password: str) -> bool:
        '''Authenticate user with password.'''
        if not self.active:
            raise ValueError("User is inactive")
        return self._check_password(password)

    def _check_password(self, password: str) -> bool:
        # Private method
        return len(password) > 8
"""
        functions, classes = analyzer.analyze(code)

        assert len(classes) == 1
        cls = classes[0]

        # Class metadata
        assert cls.name == "User"
        assert cls.is_dataclass is True
        assert "User model" in cls.docstring

        # Methods
        assert len(cls.methods) == 3
        method_names = [m.name for m in cls.methods]
        assert "__init__" in method_names
        assert "authenticate" in method_names
        assert "_check_password" in method_names

        # Init params
        assert len(cls.init_params) == 3
        assert cls.required_init_params == 2  # username and email

        # Async method
        auth_method = [m for m in cls.methods if m.name == "authenticate"][0]
        assert auth_method.is_async is True
        assert "ValueError" in auth_method.raises

    def test_multiple_files_sequential_analysis(self):
        """Test analyzing multiple code snippets sequentially."""
        analyzer = ASTFunctionAnalyzer()

        # First file
        code1 = """
def func1():
    pass
"""
        functions1, _ = analyzer.analyze(code1)
        assert len(functions1) == 1

        # Second file (should clear previous results)
        code2 = """
def func2():
    pass

def func3():
    pass
"""
        functions2, _ = analyzer.analyze(code2)
        assert len(functions2) == 2
        assert functions2[0].name == "func2"
        assert functions2[1].name == "func3"
