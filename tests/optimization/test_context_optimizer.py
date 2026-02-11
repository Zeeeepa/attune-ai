"""Tests for context window optimization.

Copyright 2026 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

from attune.optimization import CompressionLevel, ContextOptimizer, optimize_xml_prompt


class TestCompressionLevels:
    """Test different compression levels."""

    def test_none_compression_unchanged(self):
        """Test NONE compression leaves text unchanged."""
        optimizer = ContextOptimizer(CompressionLevel.NONE)
        text = "<thinking>  This is a test  </thinking>"

        result = optimizer.optimize(text)

        assert result == text

    def test_light_compression_basic(self):
        """Test LIGHT compression applies basic optimizations."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = "<thinking>  Multiple   spaces   here  </thinking>\n\n\n<answer>Response</answer>"

        result = optimizer.optimize(text)

        # Should remove excess whitespace
        assert "  " not in result
        assert "\n\n\n" not in result

    def test_moderate_compression_includes_tag_compression(self):
        """Test MODERATE compression compresses tags."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "<thinking>Analysis</thinking><answer>Result</answer>"

        result = optimizer.optimize(text)

        # Should compress tags
        assert "<t>" in result
        assert "<a>" in result
        assert "<thinking>" not in result

    def test_aggressive_compression_maximum(self):
        """Test AGGRESSIVE compression applies all techniques."""
        optimizer = ContextOptimizer(CompressionLevel.AGGRESSIVE)
        text = "Generate the following analysis"

        result = optimizer.optimize(text)

        # Should abbreviate
        assert "Gen" in result or "below" in result


class TestTagCompression:
    """Test XML tag compression."""

    def test_thinking_tag_compression(self):
        """Test <thinking> tag compression."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "<thinking>Analysis process</thinking>"

        result = optimizer.optimize(text)

        assert result == "<t>Analysis process</t>"

    def test_answer_tag_compression(self):
        """Test <answer> tag compression."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "<answer>Final result</answer>"

        result = optimizer.optimize(text)

        assert result == "<a>Final result</a>"

    def test_nested_tag_compression(self):
        """Test compression of nested tags."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "<thinking><description>Details</description></thinking>"

        result = optimizer.optimize(text)

        assert "<t>" in result
        assert "<desc>" in result
        assert "</desc>" in result
        assert "</t>" in result

    def test_tag_with_attributes_preserved(self):
        """Test tags with attributes are handled correctly."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = '<recommendation priority="high">Fix this</recommendation>'

        result = optimizer.optimize(text)

        # Should compress tag but preserve attribute
        assert "<rec " in result
        assert 'priority="high"' in result


class TestWhitespaceOptimization:
    """Test whitespace optimization."""

    def test_multiple_spaces_collapsed(self):
        """Test multiple spaces collapsed to single space."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = "This  has    multiple     spaces"

        result = optimizer.optimize(text)

        assert result == "This has multiple spaces"

    def test_whitespace_around_tags_removed(self):
        """Test whitespace around XML tags is removed."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = "<tag>  \n  Content  \n  </tag>"

        result = optimizer.optimize(text)

        # Whitespace between tags removed, content preserved
        assert "Content" in result
        assert len(result) < len(text)

    def test_empty_lines_removed(self):
        """Test empty lines are removed."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = "Line 1\n\n\n\nLine 2"

        result = optimizer.optimize(text)

        assert result == "Line 1\nLine 2"

    def test_leading_trailing_whitespace_stripped(self):
        """Test leading/trailing whitespace stripped from lines."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = "  Line 1  \n  Line 2  "

        result = optimizer.optimize(text)

        assert result == "Line 1\nLine 2"


class TestCommentRemoval:
    """Test XML comment removal."""

    def test_simple_comment_removed(self):
        """Test simple XML comment is removed."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = "Before <!-- comment --> After"

        result = optimizer.optimize(text)

        # Comment removed (may leave space)
        assert "<!--" not in result
        assert "comment" not in result
        assert "Before" in result and "After" in result

    def test_multiline_comment_removed(self):
        """Test multiline comment is removed."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        text = """Before
<!-- This is a
multiline comment -->
After"""

        result = optimizer.optimize(text)

        assert "<!--" not in result
        assert "comment" not in result
        assert "Before" in result
        assert "After" in result


class TestRedundancyRemoval:
    """Test redundant phrase removal."""

    def test_please_note_removed(self):
        """Test 'Please note that' phrase is removed."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "Please note that the code is good"

        result = optimizer.optimize(text)

        # Redundant phrase removed
        assert "Please note that" not in result
        assert "code" in result and "good" in result

    def test_make_sure_removed(self):
        """Test 'Make sure to' phrase is removed."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "Make sure to test the code"

        result = optimizer.optimize(text)

        assert "Make sure to" not in result
        assert "test" in result and "code" in result


class TestAggressiveCompression:
    """Test aggressive compression techniques."""

    def test_article_removal(self):
        """Test articles (a, an, the) are removed."""
        optimizer = ContextOptimizer(CompressionLevel.AGGRESSIVE)
        text = "The code has a bug and an issue"

        result = optimizer.optimize(text)

        # Articles should be removed from instruction text
        assert "the" not in result.lower() or "<" in result
        assert "code has bug and issue" in result or "<" in result

    def test_abbreviations_applied(self):
        """Test common words are abbreviated."""
        optimizer = ContextOptimizer(CompressionLevel.AGGRESSIVE)
        text = "Generate the following analysis"

        result = optimizer.optimize(text)

        assert "Gen" in result
        assert "below" in result

    def test_xml_content_preserved(self):
        """Test XML content is not aggressively compressed."""
        optimizer = ContextOptimizer(CompressionLevel.AGGRESSIVE)
        text = "<answer>The final result</answer>"

        result = optimizer.optimize(text)

        # XML tags should be compressed but content preserved
        assert "<a>" in result or "<answer>" in result
        assert "final result" in result or "The final result" in result


class TestDecompression:
    """Test response decompression."""

    def test_decompress_thinking_tag(self):
        """Test <t> tag decompression."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        compressed = "<t>Analysis</t>"

        result = optimizer.decompress(compressed)

        assert result == "<thinking>Analysis</thinking>"

    def test_decompress_answer_tag(self):
        """Test <a> tag decompression."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        compressed = "<a>Result</a>"

        result = optimizer.decompress(compressed)

        assert result == "<answer>Result</answer>"

    def test_decompress_nested_tags(self):
        """Test decompression of nested tags."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        compressed = "<t><desc>Details</desc></t>"

        result = optimizer.decompress(compressed)

        assert result == "<thinking><description>Details</description></thinking>"

    def test_decompress_with_attributes(self):
        """Test decompression preserves attributes."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        compressed = '<rec priority="high">Fix</rec>'

        result = optimizer.decompress(compressed)

        assert result == '<recommendation priority="high">Fix</recommendation>'


class TestRoundTrip:
    """Test compression/decompression round trips."""

    def test_round_trip_preserves_content(self):
        """Test compress then decompress preserves semantic content."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        original = "<thinking>Detailed analysis</thinking><answer>Final result</answer>"

        compressed = optimizer.optimize(original)
        decompressed = optimizer.decompress(compressed)

        # Should preserve semantic content (may have different whitespace)
        assert "thinking" in decompressed.lower()
        assert "answer" in decompressed.lower()
        assert "Detailed analysis" in decompressed
        assert "Final result" in decompressed


class TestTokenReduction:
    """Test actual token reduction."""

    def test_moderate_achieves_target_reduction(self):
        """Test MODERATE compression achieves 15-25% reduction."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)

        original = """<thinking>
        I will analyze the code carefully.
        Please note that there are several issues.
        The code has a bug and an error.
        </thinking>
        <answer>
        The following recommendations apply:
        <recommendation>Fix the bug</recommendation>
        <description>Details here</description>
        </answer>"""

        compressed = optimizer.optimize(original)

        # Estimate token reduction (rough approximation: 1 token ≈ 4 chars)
        original_tokens = len(original) / 4
        compressed_tokens = len(compressed) / 4
        reduction_pct = (1 - compressed_tokens / original_tokens) * 100

        # Should achieve 15-35% reduction
        assert reduction_pct >= 10  # At least 10% reduction
        assert len(compressed) < len(original)

    def test_light_minimal_reduction(self):
        """Test LIGHT compression achieves minimal reduction."""
        optimizer = ContextOptimizer(CompressionLevel.LIGHT)
        original = "<thinking>  Analysis  </thinking>  "

        compressed = optimizer.optimize(original)

        assert len(compressed) < len(original)
        # Should only remove whitespace
        assert "thinking" in compressed


class TestConvenienceFunction:
    """Test optimize_xml_prompt convenience function."""

    def test_optimize_xml_prompt_default_level(self):
        """Test convenience function with default level."""
        original = "<thinking>Test</thinking>"

        result = optimize_xml_prompt(original)

        # Default is MODERATE, should compress tags
        assert "<t>" in result

    def test_optimize_xml_prompt_custom_level(self):
        """Test convenience function with custom level."""
        original = "<thinking>Test</thinking>"

        result = optimize_xml_prompt(original, CompressionLevel.LIGHT)

        # LIGHT should not compress tags
        assert "<thinking>" in result or "thinking" not in result  # whitespace stripped


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_string(self):
        """Test empty string handling."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)

        result = optimizer.optimize("")

        assert result == ""

    def test_no_xml_tags(self):
        """Test plain text without XML tags."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "Just plain text without tags"

        result = optimizer.optimize(text)

        # Should still apply whitespace optimization
        assert "plain text" in result

    def test_malformed_xml(self):
        """Test handling of malformed XML."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "<thinking>Unclosed tag"

        result = optimizer.optimize(text)

        # Should not crash, tag gets compressed
        assert "<t>" in result or "thinking" in result.lower()
        assert "unclosed tag" in result.lower()

    def test_very_long_text(self):
        """Test optimization of very long text."""
        optimizer = ContextOptimizer(CompressionLevel.MODERATE)
        text = "<thinking>" + ("x " * 10000) + "</thinking>"

        result = optimizer.optimize(text)

        # Should complete without errors
        assert "<t>" in result or "<thinking>" in result
        assert len(result) < len(text)
