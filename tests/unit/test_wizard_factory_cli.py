"""Tests for empathy_os.wizard_factory_cli"""
from argparse import ArgumentParser
from unittest.mock import Mock, patch

from empathy_os.wizard_factory_cli import (
    add_wizard_factory_commands,
    cmd_wizard_factory_analyze,
    cmd_wizard_factory_create,
    cmd_wizard_factory_generate_tests,
    cmd_wizard_factory_list_patterns,
)


def test_cmd_wizard_factory_create_basic():
    """Test cmd_wizard_factory_create with basic inputs."""
    # Create mock args
    args = Mock()
    args.name = "test_wizard"
    args.domain = "software"
    args.type = "domain"
    args.methodology = "pattern"
    args.patterns = "linear_flow"
    args.interactive = False

    # Mock subprocess.run and sys.exit
    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)

        # Call function
        cmd_wizard_factory_create(args)

        # Verify subprocess was called with correct command
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "python" in call_args
        assert "-m" in call_args
        assert "scaffolding" in call_args
        assert "create" in call_args
        assert "test_wizard" in call_args

        # Verify exit was called with return code
        mock_exit.assert_called_once_with(0)


def test_cmd_wizard_factory_create_with_interactive():
    """Test cmd_wizard_factory_create with interactive flag."""
    args = Mock()
    args.name = "test_wizard"
    args.domain = None
    args.type = "domain"
    args.methodology = "pattern"
    args.patterns = None
    args.interactive = True

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)
        cmd_wizard_factory_create(args)

        call_args = mock_run.call_args[0][0]
        assert "--interactive" in call_args


def test_cmd_wizard_factory_list_patterns_basic():
    """Test cmd_wizard_factory_list_patterns with basic inputs."""
    args = Mock()

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)
        cmd_wizard_factory_list_patterns(args)

        # Verify correct command
        call_args = mock_run.call_args[0][0]
        assert "python" in call_args
        assert "scaffolding" in call_args
        assert "list-patterns" in call_args

        mock_exit.assert_called_once_with(0)


def test_cmd_wizard_factory_list_patterns_nonzero_exit():
    """Test cmd_wizard_factory_list_patterns with non-zero exit code."""
    args = Mock()

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=1)
        cmd_wizard_factory_list_patterns(args)

        mock_exit.assert_called_once_with(1)


def test_cmd_wizard_factory_generate_tests_basic():
    """Test cmd_wizard_factory_generate_tests with basic inputs."""
    args = Mock()
    args.wizard_id = "test_wizard_001"
    args.patterns = "linear_flow,approval"
    args.output = "/tmp/tests"

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)
        cmd_wizard_factory_generate_tests(args)

        call_args = mock_run.call_args[0][0]
        assert "test_generator" in call_args
        assert "generate" in call_args
        assert "test_wizard_001" in call_args
        assert "--patterns" in call_args
        assert "linear_flow,approval" in call_args
        assert "--output" in call_args
        assert "/tmp/tests" in call_args


def test_cmd_wizard_factory_generate_tests_without_output():
    """Test cmd_wizard_factory_generate_tests without output directory."""
    args = Mock()
    args.wizard_id = "test_wizard"
    args.patterns = "linear_flow"
    args.output = None

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)
        cmd_wizard_factory_generate_tests(args)

        call_args = mock_run.call_args[0][0]
        assert "--output" not in call_args


def test_cmd_wizard_factory_analyze_basic():
    """Test cmd_wizard_factory_analyze with basic inputs."""
    args = Mock()
    args.wizard_id = "test_wizard"
    args.patterns = "linear_flow"
    args.json = False

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)
        cmd_wizard_factory_analyze(args)

        call_args = mock_run.call_args[0][0]
        assert "test_generator" in call_args
        assert "analyze" in call_args
        assert "test_wizard" in call_args


def test_cmd_wizard_factory_analyze_with_json():
    """Test cmd_wizard_factory_analyze with JSON output."""
    args = Mock()
    args.wizard_id = "test_wizard"
    args.patterns = "linear_flow"
    args.json = True

    with patch('empathy_os.wizard_factory_cli.subprocess.run') as mock_run, \
         patch('empathy_os.wizard_factory_cli.sys.exit') as mock_exit:

        mock_run.return_value = Mock(returncode=0)
        cmd_wizard_factory_analyze(args)

        call_args = mock_run.call_args[0][0]
        assert "--json" in call_args


def test_add_wizard_factory_commands_basic():
    """Test add_wizard_factory_commands with basic inputs."""
    # Create a mock ArgumentParser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # Call function
    add_wizard_factory_commands(subparsers)

    # Verify wizard-factory command was added
    # Parse to check it works
    args = parser.parse_args(["wizard-factory", "create", "test_wizard"])
    assert args.wizard_factory_command == "create"


def test_add_wizard_factory_commands_creates_subcommands():
    """Test add_wizard_factory_commands creates all subcommands."""
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    add_wizard_factory_commands(subparsers)

    # Test each subcommand can be parsed
    # create subcommand
    args1 = parser.parse_args(["wizard-factory", "create", "test_wizard"])
    assert hasattr(args1, 'name')
    assert args1.name == "test_wizard"

    # list-patterns subcommand
    args2 = parser.parse_args(["wizard-factory", "list-patterns"])
    assert args2.wizard_factory_command == "list-patterns"

    # generate-tests subcommand
    args3 = parser.parse_args(["wizard-factory", "generate-tests", "wiz_id", "--patterns", "p1"])
    assert args3.wizard_id == "wiz_id"
    assert args3.patterns == "p1"

    # analyze subcommand
    args4 = parser.parse_args(["wizard-factory", "analyze", "wiz_id", "--patterns", "p1"])
    assert args4.wizard_id == "wiz_id"

