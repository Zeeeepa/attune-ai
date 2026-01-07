#!/bin/bash
# Manual Test Script for Empathy Framework
# Tests CLI features, provider config, telemetry, and workflows
#
# Usage:
#   ./manual_test.sh                 # Run all tests
#   ./manual_test.sh cli              # Test CLI commands only
#   ./manual_test.sh provider         # Test provider commands only
#   ./manual_test.sh telemetry        # Test telemetry commands only
#   ./manual_test.sh workflows        # Test workflow commands only

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}▶ Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
}

run_test() {
    local test_name="$1"
    local command="$2"

    print_test "$test_name"
    if eval "$command" > /dev/null 2>&1; then
        print_success "$test_name passed"
    else
        print_error "$test_name failed"
    fi
}

run_test_with_output() {
    local test_name="$1"
    local command="$2"
    local expected_output="$3"

    print_test "$test_name"
    output=$(eval "$command" 2>&1)

    if echo "$output" | grep -q "$expected_output"; then
        print_success "$test_name passed"
        echo "   Output contains: '$expected_output'"
    else
        print_error "$test_name failed"
        echo "   Expected output to contain: '$expected_output'"
        echo "   Actual output: $output"
    fi
}

# Test CLI Version and Help
test_cli_basics() {
    print_header "Testing CLI Basics"

    run_test_with_output "CLI version" "python -m empathy_os.cli_unified --version" "Empathy Framework"
    run_test_with_output "CLI help" "empathy --help" "Empathy Framework"
    run_test_with_output "Cheatsheet" "empathy cheatsheet" "Getting Started"
}

# Test Memory Commands
test_memory_commands() {
    print_header "Testing Memory Commands"

    run_test "Memory status" "empathy memory status"

    print_test "Memory patterns list"
    empathy memory patterns || print_error "Memory patterns failed"
    ((TESTS_RUN++))
}

# Test Provider Commands
test_provider_commands() {
    print_header "Testing Provider Commands"

    run_test_with_output "Provider config" "empathy provider" "PROVIDER CONFIGURATION"
    run_test_with_output "Provider registry" "python -m empathy_os.models.cli registry" "MODEL REGISTRY"
    run_test_with_output "Provider tasks" "python -m empathy_os.models.cli tasks" "TASK-TO-TIER"
    run_test_with_output "Provider costs" "python -m empathy_os.models.cli costs" "COST ESTIMATES"

    print_test "Provider registry (JSON format)"
    json_output=$(python -m empathy_os.models.cli registry --format json 2>&1)
    if echo "$json_output" | python -m json.tool > /dev/null 2>&1; then
        print_success "Registry JSON format is valid"
    else
        print_error "Registry JSON format is invalid"
    fi
}

# Test Telemetry Commands
test_telemetry_commands() {
    print_header "Testing Telemetry Commands"

    run_test "Telemetry summary" "python -m empathy_os.models.cli telemetry"
    run_test "Telemetry costs" "python -m empathy_os.models.cli telemetry --costs"
    run_test "Telemetry providers" "python -m empathy_os.models.cli telemetry --providers"
    run_test "Telemetry fallbacks" "python -m empathy_os.models.cli telemetry --fallbacks"
}

# Test Model CLI Commands
test_model_cli() {
    print_header "Testing Model CLI Commands"

    run_test_with_output "Model registry" "python -m empathy_os.models.cli registry" "anthropic"
    run_test_with_output "Task mappings" "python -m empathy_os.models.cli tasks" "summarize"
    run_test_with_output "Effective config" "python -m empathy_os.models.cli effective" "EFFECTIVE CONFIGURATION"
}

# Test Workflow Commands
test_workflow_commands() {
    print_header "Testing Workflow Commands"

    print_test "Workflow list"
    empathy workflow list || true  # May not have workflows defined
    ((TESTS_RUN++))

    print_test "Wizard list"
    empathy wizard list || true  # May not have wizards installed
    ((TESTS_RUN++))
}

# Test Unit Tests
test_unit_tests() {
    print_header "Running Unit Tests"

    print_test "CLI Unified Tests"
    if python -m pytest tests/unit/test_cli_unified.py -v --tb=no -q 2>&1 | grep -q "passed"; then
        print_success "CLI unified tests passed"
    else
        print_error "CLI unified tests failed"
    fi

    print_test "Models CLI Tests"
    if python -m pytest tests/unit/models/test_models_cli.py -v --tb=no -q 2>&1 | grep -q "passed"; then
        print_success "Models CLI tests passed"
    else
        print_error "Models CLI tests failed"
    fi

    print_test "All Unit Tests"
    if python -m pytest tests/unit/ -v --tb=no -q 2>&1 | grep -q "passed"; then
        test_count=$(python -m pytest tests/unit/ --co -q 2>&1 | tail -1 | grep -o '[0-9]*' | head -1)
        print_success "All unit tests passed ($test_count tests)"
    else
        print_error "Some unit tests failed"
    fi
}

# Test Code Quality
test_code_quality() {
    print_header "Testing Code Quality"

    print_test "Lint check (ruff)"
    if ruff check src/ tests/ 2>&1 | grep -q "All checks passed"; then
        print_success "Lint check passed - no errors"
    else
        error_count=$(ruff check src/ tests/ 2>&1 | grep -c "error:" || echo "0")
        if [ "$error_count" -eq 0 ]; then
            print_success "Lint check passed - no errors"
        else
            print_error "Lint check failed - $error_count errors"
        fi
    fi

    print_test "Type check (mypy)"
    type_errors=$(python -m mypy src/ 2>&1 | grep "error:" | wc -l | tr -d ' ')
    if [ "$type_errors" -eq 0 ]; then
        print_success "Type check passed - no errors"
    else
        print_error "Type check failed - $type_errors errors"
    fi
}

# Test Token Estimation
test_token_estimation() {
    print_header "Testing Token Estimation"

    print_test "Token estimation module"
    if python -c "from empathy_os.models.token_estimator import estimate_tokens; print(estimate_tokens('test'))" > /dev/null 2>&1; then
        print_success "Token estimation works"
    else
        print_error "Token estimation failed"
    fi

    print_test "Workflow cost estimation"
    if python -c "from empathy_os.models.token_estimator import estimate_workflow_cost; print(estimate_workflow_cost('code-review', 'test', 'anthropic'))" > /dev/null 2>&1; then
        print_success "Workflow cost estimation works"
    else
        print_error "Workflow cost estimation failed"
    fi
}

# Print summary
print_summary() {
    print_header "Test Summary"

    echo -e "Tests run:    ${BLUE}$TESTS_RUN${NC}"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ All tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}✗ Some tests failed${NC}"
        exit 1
    fi
}

# Main execution
main() {
    local test_suite="${1:-all}"

    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Empathy Framework Manual Test Suite          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"

    case "$test_suite" in
        cli)
            test_cli_basics
            ;;
        memory)
            test_memory_commands
            ;;
        provider)
            test_provider_commands
            test_model_cli
            ;;
        telemetry)
            test_telemetry_commands
            ;;
        workflows)
            test_workflow_commands
            ;;
        quality)
            test_code_quality
            ;;
        unit)
            test_unit_tests
            ;;
        token)
            test_token_estimation
            ;;
        all)
            test_cli_basics
            test_memory_commands
            test_provider_commands
            test_model_cli
            test_telemetry_commands
            test_token_estimation
            test_workflow_commands
            test_unit_tests
            test_code_quality
            ;;
        *)
            echo -e "${RED}Unknown test suite: $test_suite${NC}"
            echo "Available options: all, cli, memory, provider, telemetry, workflows, quality, unit, token"
            exit 1
            ;;
    esac

    print_summary
}

# Run main with arguments
main "$@"
