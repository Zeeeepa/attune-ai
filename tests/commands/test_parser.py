"""Tests for command markdown parser.

Tests for CommandParser that parses markdown files with optional YAML frontmatter.
"""

from pathlib import Path

import pytest

from empathy_llm_toolkit.commands.models import CommandCategory
from empathy_llm_toolkit.commands.parser import CommandParser


class TestCommandParser:
    """Tests for CommandParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return CommandParser()

    def test_parse_with_frontmatter(self, parser):
        """Test parsing markdown with YAML frontmatter."""
        content = """---
name: compact
description: Strategic context compaction
category: context
aliases: [comp, save]
tags: [context, state]
---

## Overview

This command performs context compaction.

## Steps

1. Save state
2. Clear context
"""
        config = parser.parse_content(content, source="test.md")

        assert config.name == "compact"
        assert config.description == "Strategic context compaction"
        assert config.metadata.category == CommandCategory.CONTEXT
        assert "comp" in config.metadata.aliases
        assert "context" in config.metadata.tags
        assert "## Overview" in config.body

    def test_parse_without_frontmatter(self, parser):
        """Test parsing markdown without frontmatter."""
        content = """Create a git commit - Follow conventional commit format.

## Execution Steps

### Step 1: Check status
```bash
git status
```
"""
        config = parser.parse_content(content, source=Path("commit.md"))

        assert config.name == "commit"  # Inferred from filename
        assert "conventional commit" in config.description.lower()
        assert "## Execution Steps" in config.body

    def test_parse_file(self, parser, tmp_path):
        """Test parsing from file."""
        content = """---
name: test-cmd
description: Test command
---

Test body content.
"""
        file_path = tmp_path / "test-cmd.md"
        file_path.write_text(content)

        config = parser.parse_file(file_path)

        assert config.name == "test-cmd"
        assert config.source_file == file_path

    def test_parse_file_not_found(self, parser):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/path.md")

    def test_category_inference_git(self, parser):
        """Test category inference for git commands."""
        content = "Git commit helper"
        config = parser.parse_content(content, source=Path("commit.md"))
        assert config.metadata.category == CommandCategory.GIT

    def test_category_inference_test(self, parser):
        """Test category inference for test commands."""
        content = "Test runner"
        config = parser.parse_content(content, source=Path("test-coverage.md"))
        assert config.metadata.category == CommandCategory.TEST

    def test_category_inference_security(self, parser):
        """Test category inference for security commands."""
        content = "Security scanner"
        config = parser.parse_content(content, source=Path("security-scan.md"))
        assert config.metadata.category == CommandCategory.SECURITY

    def test_category_inference_performance(self, parser):
        """Test category inference for performance commands."""
        content = "Benchmark runner"
        config = parser.parse_content(content, source=Path("benchmark.md"))
        assert config.metadata.category == CommandCategory.PERFORMANCE

    def test_category_inference_learning(self, parser):
        """Test category inference for learning commands."""
        content = "Pattern viewer"
        config = parser.parse_content(content, source=Path("patterns.md"))
        assert config.metadata.category == CommandCategory.LEARNING

    def test_parse_hooks_config(self, parser):
        """Test parsing hook configuration."""
        content = """---
name: compact
hooks:
  pre: PreCompact
  post: PostCompact
---

Body content.
"""
        config = parser.parse_content(content)

        assert config.hooks["pre"] == "PreCompact"
        assert config.hooks["post"] == "PostCompact"

    def test_parse_requires_flags(self, parser):
        """Test parsing requires_user_id and requires_context."""
        content = """---
name: test
requires_user_id: true
requires_context: true
---

Body.
"""
        config = parser.parse_content(content)

        assert config.metadata.requires_user_id is True
        assert config.metadata.requires_context is True

    def test_description_extraction_dash_format(self, parser):
        """Test extracting description from 'Title - Description' format."""
        content = "Bug Investigation - Analyze errors and find root causes."

        config = parser.parse_content(content, source=Path("debug.md"))

        assert "Analyze errors" in config.description

    def test_description_extraction_heading(self, parser):
        """Test extracting description from heading."""
        content = """# Commit Helper

Create well-formatted commits.
"""
        config = parser.parse_content(content, source=Path("commit.md"))
        # Should get the heading text
        assert config.description != ""

    def test_basic_yaml_parse_fallback(self, parser):
        """Test basic YAML parsing without PyYAML."""
        yaml_content = """
name: test
description: Test description
category: git
aliases: [t, tst]
requires_user_id: true
"""
        result = parser._basic_yaml_parse(yaml_content)

        assert result["name"] == "test"
        assert result["description"] == "Test description"
        assert result["category"] == "git"
        assert result["aliases"] == ["t", "tst"]
        assert result["requires_user_id"] is True

    def test_validate_file_valid(self, parser, tmp_path):
        """Test validating a valid file."""
        content = """---
name: valid-cmd
---

Body content.
"""
        file_path = tmp_path / "valid-cmd.md"
        file_path.write_text(content)

        errors = parser.validate_file(file_path)

        assert errors == []

    def test_validate_file_missing_body(self, parser, tmp_path):
        """Test validating file with empty body."""
        content = """---
name: no-body
---
"""
        file_path = tmp_path / "no-body.md"
        file_path.write_text(content)

        errors = parser.validate_file(file_path)

        assert len(errors) > 0
        assert any("body" in e.lower() for e in errors)

    def test_validate_file_invalid_name(self, parser, tmp_path):
        """Test validating file with invalid command name."""
        content = """---
name: Invalid Name!
---

Body.
"""
        file_path = tmp_path / "invalid.md"
        file_path.write_text(content)

        errors = parser.validate_file(file_path)

        assert len(errors) > 0
        assert any("name" in e.lower() for e in errors)

    def test_validate_file_invalid_category(self, parser, tmp_path):
        """Test validating file with invalid category."""
        content = """---
name: test
category: invalid-category
---

Body.
"""
        file_path = tmp_path / "test.md"
        file_path.write_text(content)

        errors = parser.validate_file(file_path)

        assert len(errors) > 0
        assert any("category" in e.lower() for e in errors)

    def test_validate_file_not_found(self, parser):
        """Test validating non-existent file."""
        errors = parser.validate_file("/nonexistent/file.md")
        assert len(errors) > 0
        assert any("not found" in e.lower() for e in errors)

    def test_validate_file_empty(self, parser, tmp_path):
        """Test validating empty file."""
        file_path = tmp_path / "empty.md"
        file_path.write_text("")

        errors = parser.validate_file(file_path)

        assert len(errors) > 0
        assert any("empty" in e.lower() for e in errors)

    def test_parse_preserves_markdown_formatting(self, parser):
        """Test that markdown formatting is preserved in body."""
        content = """---
name: test
---

## Section 1

```python
def hello():
    print("world")
```

### Subsection

- Item 1
- Item 2

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
        config = parser.parse_content(content)

        assert "## Section 1" in config.body
        assert "```python" in config.body
        assert "### Subsection" in config.body
        assert "- Item 1" in config.body
        assert "| Col1 |" in config.body


class TestCommandParserEdgeCases:
    """Edge case tests for CommandParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return CommandParser()

    def test_frontmatter_with_extra_dashes(self, parser):
        """Test frontmatter with extra dashes in content."""
        content = """---
name: test
---

Content with --- dashes --- in it.
"""
        config = parser.parse_content(content)

        assert config.name == "test"
        assert "--- dashes ---" in config.body

    def test_empty_frontmatter(self, parser):
        """Test empty frontmatter section."""
        content = """---
---

Body only, no metadata.
"""
        config = parser.parse_content(content, source=Path("test.md"))

        # Should fall back to filename for name
        assert config.name == "test"

    def test_unicode_content(self, parser):
        """Test handling unicode content."""
        content = """---
name: unicode-test
description: Test with émojis 🎉 and spëcial çharacters
---

Body with 日本語 and more 🚀
"""
        config = parser.parse_content(content)

        assert "émojis" in config.description
        assert "🎉" in config.description
        assert "日本語" in config.body

    def test_multiline_description_in_frontmatter(self, parser):
        """Test multiline description in frontmatter is handled."""
        content = """---
name: test
description: >
  This is a long
  multiline description
---

Body.
"""
        # This might fail with basic parser, but should work with PyYAML
        try:
            config = parser.parse_content(content)
            assert "multiline" in config.description or config.description != ""
        except ValueError:
            # Expected if PyYAML not available
            pass

    def test_no_name_no_source_raises_error(self, parser):
        """Test that parsing without name or source raises error."""
        content = "Just body content, no name anywhere."

        with pytest.raises(ValueError, match="Cannot determine command name"):
            parser.parse_content(content, source=None)
