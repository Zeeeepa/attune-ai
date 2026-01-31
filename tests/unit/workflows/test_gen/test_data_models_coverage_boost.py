"""Comprehensive tests for test generation data models.

Tests for FunctionSignature and ClassSignature dataclasses.

Module: workflows/test_gen/data_models.py (38 lines)
"""

import pytest

from empathy_os.workflows.test_gen.data_models import ClassSignature, FunctionSignature

# ============================================================================
# FunctionSignature Dataclass Tests
# ============================================================================


@pytest.mark.unit
class TestFunctionSignature:
    """Test suite for FunctionSignature dataclass."""

    def test_create_function_signature_with_all_fields(self):
        """Test creating FunctionSignature with all fields."""
        signature = FunctionSignature(
            name="calculate_total",
            params=[("amount", "float", None), ("tax_rate", "float", "0.1")],
            return_type="float",
            is_async=False,
            raises={"ValueError", "TypeError"},
            has_side_effects=False,
            docstring="Calculate total with tax.",
            complexity=2,
            decorators=["@staticmethod"],
        )

        assert signature.name == "calculate_total"
        assert len(signature.params) == 2
        assert signature.params[0] == ("amount", "float", None)
        assert signature.params[1] == ("tax_rate", "float", "0.1")
        assert signature.return_type == "float"
        assert signature.is_async is False
        assert "ValueError" in signature.raises
        assert "TypeError" in signature.raises
        assert signature.has_side_effects is False
        assert signature.docstring == "Calculate total with tax."
        assert signature.complexity == 2
        assert "@staticmethod" in signature.decorators

    def test_create_function_signature_with_defaults(self):
        """Test creating FunctionSignature with default values."""
        signature = FunctionSignature(
            name="simple_func",
            params=[],
            return_type=None,
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring=None,
        )

        assert signature.name == "simple_func"
        assert signature.params == []
        assert signature.return_type is None
        assert signature.is_async is False
        assert signature.raises == set()
        assert signature.has_side_effects is False
        assert signature.docstring is None
        assert signature.complexity == 1  # Default
        assert signature.decorators == []  # Default

    def test_function_signature_for_async_function(self):
        """Test FunctionSignature for async function."""
        signature = FunctionSignature(
            name="fetch_data",
            params=[("url", "str", None)],
            return_type="dict",
            is_async=True,
            raises={"HTTPError"},
            has_side_effects=True,
            docstring="Fetch data from URL.",
        )

        assert signature.is_async is True
        assert signature.has_side_effects is True

    def test_function_signature_with_complex_params(self):
        """Test FunctionSignature with complex parameter types."""
        signature = FunctionSignature(
            name="process_items",
            params=[
                ("items", "list[dict[str, Any]]", None),
                ("validate", "bool", "True"),
                ("callback", "Callable[[dict], bool] | None", "None"),
            ],
            return_type="list[dict]",
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring=None,
        )

        assert len(signature.params) == 3
        assert signature.params[0][1] == "list[dict[str, Any]]"
        assert signature.params[1][2] == "True"  # Default value
        assert signature.params[2][2] == "None"  # Default value

    def test_function_signature_with_decorators(self):
        """Test FunctionSignature with multiple decorators."""
        signature = FunctionSignature(
            name="decorated_func",
            params=[],
            return_type=None,
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring=None,
            decorators=["@staticmethod", "@deprecated", "@lru_cache(maxsize=128)"],
        )

        assert len(signature.decorators) == 3
        assert "@staticmethod" in signature.decorators
        assert "@deprecated" in signature.decorators
        assert "@lru_cache(maxsize=128)" in signature.decorators

    def test_function_signature_raises_multiple_exceptions(self):
        """Test FunctionSignature with multiple exception types."""
        signature = FunctionSignature(
            name="risky_operation",
            params=[],
            return_type=None,
            is_async=False,
            raises={"IOError", "PermissionError", "TimeoutError"},
            has_side_effects=True,
            docstring=None,
        )

        assert len(signature.raises) == 3
        assert "IOError" in signature.raises
        assert "PermissionError" in signature.raises
        assert "TimeoutError" in signature.raises

    def test_function_signature_complexity_levels(self):
        """Test FunctionSignature with different complexity levels."""
        simple = FunctionSignature(
            name="simple",
            params=[],
            return_type=None,
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring=None,
            complexity=1,
        )

        complex_func = FunctionSignature(
            name="complex",
            params=[],
            return_type=None,
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring=None,
            complexity=10,
        )

        assert simple.complexity == 1
        assert complex_func.complexity == 10


# ============================================================================
# ClassSignature Dataclass Tests
# ============================================================================


@pytest.mark.unit
class TestClassSignature:
    """Test suite for ClassSignature dataclass."""

    def test_create_class_signature_with_all_fields(self):
        """Test creating ClassSignature with all fields."""
        method1 = FunctionSignature(
            name="get_total",
            params=[("self", "Self", None)],
            return_type="float",
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring="Get total.",
        )

        method2 = FunctionSignature(
            name="set_value",
            params=[("self", "Self", None), ("value", "float", None)],
            return_type="None",
            is_async=False,
            raises=set(),
            has_side_effects=True,
            docstring="Set value.",
        )

        signature = ClassSignature(
            name="Calculator",
            methods=[method1, method2],
            init_params=[("initial_value", "float", "0.0")],
            base_classes=["BaseCalculator"],
            docstring="Calculator class.",
            is_enum=False,
            is_dataclass=False,
            required_init_params=0,
        )

        assert signature.name == "Calculator"
        assert len(signature.methods) == 2
        assert signature.methods[0].name == "get_total"
        assert signature.methods[1].name == "set_value"
        assert len(signature.init_params) == 1
        assert signature.init_params[0] == ("initial_value", "float", "0.0")
        assert signature.base_classes == ["BaseCalculator"]
        assert signature.docstring == "Calculator class."
        assert signature.is_enum is False
        assert signature.is_dataclass is False
        assert signature.required_init_params == 0

    def test_create_class_signature_with_defaults(self):
        """Test creating ClassSignature with default values."""
        signature = ClassSignature(
            name="SimpleClass",
            methods=[],
            init_params=[],
            base_classes=[],
            docstring=None,
        )

        assert signature.name == "SimpleClass"
        assert signature.methods == []
        assert signature.init_params == []
        assert signature.base_classes == []
        assert signature.docstring is None
        assert signature.is_enum is False  # Default
        assert signature.is_dataclass is False  # Default
        assert signature.required_init_params == 0  # Default

    def test_class_signature_for_enum(self):
        """Test ClassSignature for Enum class."""
        signature = ClassSignature(
            name="Color",
            methods=[],
            init_params=[],
            base_classes=["Enum"],
            docstring="Color enum.",
            is_enum=True,
        )

        assert signature.is_enum is True
        assert "Enum" in signature.base_classes

    def test_class_signature_for_dataclass(self):
        """Test ClassSignature for dataclass."""
        signature = ClassSignature(
            name="Person",
            methods=[],
            init_params=[("name", "str", None), ("age", "int", None)],
            base_classes=[],
            docstring="Person dataclass.",
            is_dataclass=True,
            required_init_params=2,
        )

        assert signature.is_dataclass is True
        assert signature.required_init_params == 2
        assert len(signature.init_params) == 2

    def test_class_signature_with_multiple_base_classes(self):
        """Test ClassSignature with multiple base classes."""
        signature = ClassSignature(
            name="MultipleInheritance",
            methods=[],
            init_params=[],
            base_classes=["Base1", "Base2", "Mixin"],
            docstring=None,
        )

        assert len(signature.base_classes) == 3
        assert "Base1" in signature.base_classes
        assert "Base2" in signature.base_classes
        assert "Mixin" in signature.base_classes

    def test_class_signature_with_many_methods(self):
        """Test ClassSignature with multiple methods."""
        methods = [
            FunctionSignature(
                name=f"method_{i}",
                params=[("self", "Self", None)],
                return_type=None,
                is_async=False,
                raises=set(),
                has_side_effects=False,
                docstring=None,
            )
            for i in range(5)
        ]

        signature = ClassSignature(
            name="ComplexClass",
            methods=methods,
            init_params=[],
            base_classes=[],
            docstring=None,
        )

        assert len(signature.methods) == 5
        for i, method in enumerate(signature.methods):
            assert method.name == f"method_{i}"

    def test_class_signature_with_complex_init_params(self):
        """Test ClassSignature with complex init parameters."""
        signature = ClassSignature(
            name="ComplexInit",
            methods=[],
            init_params=[
                ("required_param", "str", None),
                ("optional_param", "int", "10"),
                ("config", "dict[str, Any]", "{}"),
            ],
            base_classes=[],
            docstring=None,
            required_init_params=1,
        )

        assert len(signature.init_params) == 3
        assert signature.init_params[0][2] is None  # No default
        assert signature.init_params[1][2] == "10"  # Has default
        assert signature.init_params[2][2] == "{}"  # Has default
        assert signature.required_init_params == 1


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.unit
class TestIntegration:
    """Integration tests for data models working together."""

    def test_class_signature_contains_function_signatures(self):
        """Test that ClassSignature properly contains FunctionSignature objects."""
        method = FunctionSignature(
            name="process",
            params=[("self", "Self", None), ("data", "str", None)],
            return_type="bool",
            is_async=False,
            raises={"ValueError"},
            has_side_effects=False,
            docstring="Process data.",
        )

        class_sig = ClassSignature(
            name="Processor",
            methods=[method],
            init_params=[],
            base_classes=[],
            docstring=None,
        )

        # Verify method is accessible and correct
        assert len(class_sig.methods) == 1
        assert class_sig.methods[0].name == "process"
        assert class_sig.methods[0].return_type == "bool"
        assert "ValueError" in class_sig.methods[0].raises

    def test_function_signature_params_structure(self):
        """Test that FunctionSignature params follow correct structure."""
        signature = FunctionSignature(
            name="example",
            params=[
                ("arg1", "str", None),  # Required param
                ("arg2", "int", "5"),  # Optional param with default
            ],
            return_type=None,
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring=None,
        )

        # Each param is a tuple: (name, type_hint, default)
        for param in signature.params:
            assert isinstance(param, tuple)
            assert len(param) == 3
            assert isinstance(param[0], str)  # name
            assert isinstance(param[1], str)  # type_hint
            # param[2] can be str or None (default)

    def test_comprehensive_class_signature(self):
        """Test comprehensive ClassSignature with all features."""
        init_method = FunctionSignature(
            name="__init__",
            params=[("self", "Self", None), ("name", "str", None)],
            return_type="None",
            is_async=False,
            raises=set(),
            has_side_effects=True,
            docstring="Initialize.",
        )

        getter = FunctionSignature(
            name="get_name",
            params=[("self", "Self", None)],
            return_type="str",
            is_async=False,
            raises=set(),
            has_side_effects=False,
            docstring="Get name.",
        )

        signature = ClassSignature(
            name="NamedEntity",
            methods=[init_method, getter],
            init_params=[("name", "str", None)],
            base_classes=["BaseEntity"],
            docstring="Named entity class.",
            is_enum=False,
            is_dataclass=False,
            required_init_params=1,
        )

        # Verify comprehensive signature
        assert signature.name == "NamedEntity"
        assert len(signature.methods) == 2
        assert signature.methods[0].name == "__init__"
        assert signature.methods[1].name == "get_name"
        assert signature.required_init_params == 1
        assert "BaseEntity" in signature.base_classes
