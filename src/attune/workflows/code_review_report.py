"""Code Review Report Formatting.

Human-readable report formatter for code review results.
Extracted from code_review.py for maintainability.

Contains:
- format_code_review_report: Formats code review output as a readable report

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

from __future__ import annotations


def format_code_review_report(result: dict, input_data: dict) -> str:
    """Format code review output as a human-readable report.

    Args:
        result: The architect_review stage result
        input_data: Input data from previous stages

    Returns:
        Formatted report string

    """
    lines = []

    # Check for input validation error
    if input_data.get("error"):
        lines.append("=" * 60)
        lines.append("CODE REVIEW - INPUT ERROR")
        lines.append("=" * 60)
        lines.append("")
        lines.append(input_data.get("error_message", "No code provided for review."))
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    # Header
    verdict = result.get("verdict", "unknown").upper().replace("_", " ")
    verdict_icon = {
        "APPROVE": "✅",
        "APPROVE WITH SUGGESTIONS": "🔶",
        "REQUEST CHANGES": "⚠️",
        "REJECT": "❌",
    }.get(verdict, "❓")

    lines.append("=" * 60)
    lines.append("CODE REVIEW REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Verdict: {verdict_icon} {verdict}")
    lines.append("")

    # Classification summary
    classification = input_data.get("classification", "")
    if classification:
        lines.append("-" * 60)
        lines.append("CLASSIFICATION")
        lines.append("-" * 60)
        lines.append(classification[:500])
        lines.append("")

    # Security scan results
    has_critical = input_data.get("has_critical_issues", False)
    security_score = input_data.get("security_score", 100)
    security_icon = "🔴" if has_critical else ("🟡" if security_score < 90 else "🟢")

    lines.append("-" * 60)
    lines.append("SECURITY ANALYSIS")
    lines.append("-" * 60)
    lines.append(f"Security Score: {security_icon} {security_score}/100")
    lines.append(f"Critical Issues: {'Yes' if has_critical else 'No'}")
    lines.append("")

    # Security findings
    security_findings = input_data.get("security_findings", [])
    if security_findings:
        lines.append("Security Findings:")
        for finding in security_findings[:10]:
            severity = finding.get("severity", "unknown").upper()
            title = finding.get("title", "N/A")
            sev_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                severity,
                "⚪",
            )
            lines.append(f"  {sev_icon} [{severity}] {title}")
        lines.append("")

    # Scan results summary
    scan_results = input_data.get("scan_results", "")
    if scan_results:
        lines.append("Scan Summary:")
        # Truncate scan results for readability
        summary = scan_results[:800]
        if len(scan_results) > 800:
            summary += "..."
        lines.append(summary)
        lines.append("")

    # Architectural review
    arch_review = result.get("architectural_review", "")
    if arch_review:
        lines.append("-" * 60)
        lines.append("ARCHITECTURAL REVIEW")
        lines.append("-" * 60)
        lines.append(arch_review)
        lines.append("")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        lines.append("-" * 60)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 60)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    # Crew review results (if available)
    crew_review = input_data.get("crew_review", {})
    if crew_review and crew_review.get("available") and not crew_review.get("fallback"):
        lines.append("-" * 60)
        lines.append("CREW REVIEW ANALYSIS")
        lines.append("-" * 60)
        lines.append(f"Quality Score: {crew_review.get('quality_score', 'N/A')}/100")
        lines.append(f"Finding Count: {crew_review.get('finding_count', 0)}")
        agents = crew_review.get("agents_used", [])
        if agents:
            lines.append(f"Agents Used: {', '.join(agents)}")
        summary = crew_review.get("summary", "")
        if summary:
            lines.append(f"Summary: {summary[:300]}")
        lines.append("")

    # Check if we have any meaningful content to show
    content_sections = [
        input_data.get("classification"),
        input_data.get("security_findings"),
        input_data.get("scan_results"),
        result.get("architectural_review"),
        result.get("recommendations"),
    ]
    has_content = any(content_sections)

    # If no content was generated, add a helpful message
    if not has_content and len(lines) < 15:  # Just header/footer, no real content
        lines.append("-" * 60)
        lines.append("NO ISSUES FOUND")
        lines.append("-" * 60)
        lines.append("")
        lines.append("The code review workflow completed but found no issues to report.")
        lines.append("This could mean:")
        lines.append("  • No code was provided for review (check input parameters)")
        lines.append("  • The code is clean and follows best practices")
        lines.append("  • The workflow needs configuration (check .attune/workflows.yaml)")
        lines.append("")
        lines.append("Tip: Try running with a specific file or diff:")
        lines.append('  empathy workflow run code-review --input \'{"target": "path/to/file.py"}\'')
        lines.append("")

    # Footer
    lines.append("=" * 60)
    model_tier = result.get("model_tier_used", "unknown")
    lines.append(f"Review completed using {model_tier} tier model")
    lines.append("=" * 60)

    return "\n".join(lines)
