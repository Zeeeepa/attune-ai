"""Unit tests for test_templates module.

Tests template generation for functions and classes.
"""

import pytest

from empathy_os.workflows.test_gen.test_templates import (
    generate_test_cases_for_params,
    generate_test_for_class,
    generate_test_for_function,
    get_param_test_values,
    get_type_assertion,
)


class TestGenerateTestCasesForParams:
    """Tests for generate_test_cases_for_params function."""

    def test_string_params(self):
        """Test generation with string parameters."""
        params = [("name", "str", None)]
        result = generate_test_cases_for_params(params)

        assert "valid_args" in result
        assert '"test_value"' in result["valid_args"]
        assert "parametrize_cases" in result
        assert len(result["parametrize_cases"]) <= 5
        assert "edge_cases" in result

    def test_int_params(self):
        """Test generation with int parameters."""
        params = [("count", "int", None)]
        result = generate_test_cases_for_params(params)

        assert "42" in result["valid_args"]
        assert "0" in result["parametrize_cases"]
        assert "edge_cases" in result

    def test_float_params(self):
        """Test generation with float parameters."""
        params = [("value", "float", None)]
        result = generate_test_cases_for_params(params)

        assert "3.14" in result["valid_args"]
        assert "0.0" in result["parametrize_cases"]

    def test_bool_params(self):
        """Test generation with bool parameters."""
        params = [("flag", "bool", None)]
        result = generate_test_cases_for_params(params)

        assert "True" in result["valid_args"]
        assert "True" in result["parametrize_cases"]
        assert "False" in result["parametrize_cases"]

    def test_list_params(self):
        """Test generation with list parameters."""
        params = [("items", "list", None)]
        result = generate_test_cases_for_params(params)

        assert "[1, 2, 3]" in result["valid_args"]
        assert "[]" in result["parametrize_cases"]

    def test_dict_params(self):
        """Test generation with dict parameters."""
        params = [("config", "dict", None)]
        result = generate_test_cases_for_params(params)

        assert '{"key": "value"}' in result["valid_args"]
        assert "{}" in result["parametrize_cases"]

    def test_param_with_default(self):
        """Test generation with default value."""
        params = [("timeout", "int", 30)]
        result = generate_test_cases_for_params(params)

        # When type is int, uses standard int value, not default
        assert "42" in result["valid_args"]

    def test_non_tuple_param(self):
        """Test generation with non-tuple parameter."""
        params = ["simple_param"]
        result = generate_test_cases_for_params(params)

        assert "None" in result["valid_args"]

    def test_multiple_params(self):
        """Test generation with multiple parameters."""
        params = [
            ("name", "str", None),
            ("count", "int", 0),
            ("enabled", "bool", True),
        ]
        result = generate_test_cases_for_params(params)

        assert len(result["valid_args"]) == 3
        assert '"test_value"' in result["valid_args"]
        # Uses standard int value (42) not default (0)
        assert "42" in result["valid_args"]
        assert "True" in result["valid_args"]

    def test_limits_parametrize_cases(self):
        """Test that parametrize cases are limited to 5."""
        params = [("value", "int", None)]
        result = generate_test_cases_for_params(params)

        assert len(result["parametrize_cases"]) <= 5

    def test_deduplicates_edge_cases(self):
        """Test that edge cases are deduplicated."""
        params = [("a", "str", None), ("b", "str", None)]
        result = generate_test_cases_for_params(params)

        # Edge cases should be unique
        assert len(result["edge_cases"]) == len(set(result["edge_cases"]))


class TestGetTypeAssertion:
    """Tests for get_type_assertion function."""

    def test_string_assertion(self):
        """Test assertion for string type."""
        result = get_type_assertion("str")
        assert result == "assert isinstance(result, str)"

    def test_int_assertion(self):
        """Test assertion for int type."""
        result = get_type_assertion("int")
        assert result == "assert isinstance(result, int)"

    def test_float_assertion(self):
        """Test assertion for float type."""
        result = get_type_assertion("float")
        assert result == "assert isinstance(result, (int, float))"

    def test_bool_assertion(self):
        """Test assertion for bool type."""
        result = get_type_assertion("bool")
        assert result == "assert isinstance(result, bool)"

    def test_list_assertion(self):
        """Test assertion for list type."""
        result = get_type_assertion("list")
        assert result == "assert isinstance(result, list)"

    def test_dict_assertion(self):
        """Test assertion for dict type."""
        result = get_type_assertion("dict")
        assert result == "assert isinstance(result, dict)"

    def test_tuple_assertion(self):
        """Test assertion for tuple type."""
        result = get_type_assertion("tuple")
        assert result == "assert isinstance(result, tuple)"

    def test_unknown_type(self):
        """Test assertion for unknown type returns None."""
        result = get_type_assertion("CustomClass")
        assert result is None

    def test_case_insensitive(self):
        """Test that type matching is case insensitive."""
        result = get_type_assertion("STR")
        assert result == "assert isinstance(result, str)"


class TestGetParamTestValues:
    """Tests for get_param_test_values function."""

    def test_string_values(self):
        """Test values for string type."""
        result = get_param_test_values("str")
        assert '"hello"' in result
        assert '"world"' in result
        assert '"test_string"' in result

    def test_int_values(self):
        """Test values for int type."""
        result = get_param_test_values("int")
        assert "0" in result
        assert "1" in result
        assert "42" in result
        assert "-1" in result

    def test_float_values(self):
        """Test values for float type."""
        result = get_param_test_values("float")
        assert "0.0" in result
        assert "1.0" in result
        assert "3.14" in result

    def test_bool_values(self):
        """Test values for bool type."""
        result = get_param_test_values("bool")
        assert "True" in result
        assert "False" in result

    def test_list_values(self):
        """Test values for list type."""
        result = get_param_test_values("list")
        assert "[]" in result
        assert "[1, 2, 3]" in result

    def test_dict_values(self):
        """Test values for dict type."""
        result = get_param_test_values("dict")
        assert "{}" in result
        assert '{"key": "value"}' in result

    def test_unknown_type_defaults(self):
        """Test default values for unknown type."""
        result = get_param_test_values("CustomType")
        assert result == ['"test_value"']


class TestGenerateTestForFunction:
    """Tests for generate_test_for_function."""

    def test_simple_function(self):
        """Test generation for simple synchronous function."""
        func = {
            "name": "add_numbers",
            "params": [("a", "int", None), ("b", "int", None)],
            "param_names": ["a", "b"],
            "is_async": False,
            "return_type": "int",
            "raises": [],
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        assert "import pytest" in result
        assert "from mymodule import add_numbers" in result
        # With int params, generates parametrize test
        assert "@pytest.mark.parametrize" in result
        assert "test_add_numbers_with_various_inputs" in result
        assert "test_add_numbers_returns_correct_type" in result
        assert "assert isinstance(result, int)" in result

    def test_async_function(self):
        """Test generation for async function."""
        func = {
            "name": "fetch_data",
            "params": [("url", "str", None)],
            "param_names": ["url"],
            "is_async": True,
            "return_type": "dict",
            "raises": [],
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        assert "@pytest.mark.asyncio" in result
        # With str params, generates parametrize test
        assert "async def test_fetch_data_with_various_inputs" in result
        assert "await fetch_data" in result

    def test_function_with_exceptions(self):
        """Test generation for function that raises exceptions."""
        func = {
            "name": "validate",
            "params": [("data", "dict", None)],
            "param_names": ["data"],
            "is_async": False,
            "return_type": "bool",
            "raises": ["ValueError", "TypeError"],
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        assert "def test_validate_raises_valueerror():" in result
        assert "def test_validate_raises_typeerror():" in result
        assert "with pytest.raises(ValueError):" in result
        assert "with pytest.raises(TypeError):" in result

    def test_function_with_parametrize(self):
        """Test generation with parametrized tests."""
        func = {
            "name": "process",
            "params": [("value", "str", None)],
            "param_names": ["value"],
            "is_async": False,
            "return_type": "str",
            "raises": [],
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        # Should include parametrized test
        assert "@pytest.mark.parametrize" in result or "def test_process" in result

    def test_function_with_none_params(self):
        """Test handling of None params."""
        func = {
            "name": "no_params",
            "params": None,
            "param_names": None,
            "is_async": False,
            "return_type": "None",
            "raises": None,
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        assert "import pytest" in result
        assert "from mymodule import no_params" in result

    def test_function_with_side_effects(self):
        """Test that functions with side effects skip type assertions."""
        func = {
            "name": "save_file",
            "params": [("path", "str", None)],
            "param_names": ["path"],
            "is_async": False,
            "return_type": "bool",
            "raises": [],
            "has_side_effects": True,
        }
        result = generate_test_for_function("mymodule", func)

        # Should not include type assertion for side-effect functions
        assert "test_save_file" in result
        assert "test_save_file_returns_correct_type" not in result

    def test_async_function_with_exceptions(self):
        """Test async function with exception handling."""
        func = {
            "name": "async_validate",
            "params": [("data", "dict", None)],
            "param_names": ["data"],
            "is_async": True,
            "return_type": "bool",
            "raises": ["ValueError"],
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        assert "@pytest.mark.asyncio" in result
        assert "async def test_async_validate_raises_valueerror():" in result
        assert "await async_validate(None)" in result

    def test_function_with_edge_cases(self):
        """Test generation includes edge case tests."""
        func = {
            "name": "process_numbers",
            "params": [("nums", "list", None)],
            "param_names": ["nums"],
            "is_async": False,
            "return_type": "list",
            "raises": [],
            "has_side_effects": False,
        }
        result = generate_test_for_function("mymodule", func)

        # Should include edge case tests
        assert "test_process_numbers" in result


class TestGenerateTestForClass:
    """Tests for generate_test_for_class."""

    def test_simple_class(self):
        """Test generation for simple class."""
        cls = {
            "name": "Calculator",
            "init_params": [("initial_value", "int", 0)],
            "methods": [
                {"name": "add", "params": [("self",), ("value", "int", None)], "is_async": False, "raises": []},
                {"name": "subtract", "params": [("self",), ("value", "int", None)], "is_async": False, "raises": []},
            ],
            "required_init_params": 0,
            "docstring": "A simple calculator.",
        }
        result = generate_test_for_class("mymodule", cls)

        assert "import pytest" in result
        assert "from mymodule import Calculator" in result
        assert "@pytest.fixture" in result
        assert "def calculator_instance():" in result
        assert "class TestCalculator:" in result
        assert "def test_initialization(self):" in result

    def test_class_with_required_params(self):
        """Test class with required initialization parameters."""
        cls = {
            "name": "Database",
            "init_params": [("connection", "str", None), ("timeout", "int", 30)],
            "methods": [
                {"name": "connect", "params": [("self",)], "is_async": False, "raises": []},
                {"name": "disconnect", "params": [("self",)], "is_async": False, "raises": []},
            ],
            "required_init_params": 2,
            "docstring": "Database connection.",
        }
        result = generate_test_for_class("mymodule", cls)

        assert "Database(" in result
        # Should have arguments for both required params
        assert result.count(",") >= 1

    def test_class_pads_required_params(self):
        """Test that class generation pads missing required params."""
        cls = {
            "name": "Service",
            "init_params": [],
            "methods": [],
            "required_init_params": 2,
            "docstring": "A service.",
        }
        result = generate_test_for_class("mymodule", cls)

        # Should pad with test values
        assert '"test_value"' in result

    def test_class_fixture_naming(self):
        """Test that fixture uses lowercase class name."""
        cls = {
            "name": "MyClassName",
            "init_params": [],
            "methods": [],
            "required_init_params": 0,
        }
        result = generate_test_for_class("mymodule", cls)

        assert "def myclassname_instance():" in result
