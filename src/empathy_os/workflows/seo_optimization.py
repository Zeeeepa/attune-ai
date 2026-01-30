"""SEO Optimization Workflow

Cost-optimized multi-tier workflow for SEO auditing and optimization.

Tier usage:
- CHEAP (Haiku): File scanning, link validation
- CAPABLE (Sonnet): Content analysis, suggestion generation
- PREMIUM (Opus): Strategic recommendations, user-facing reports
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from empathy_os.workflows.base import BaseWorkflow, WorkflowResult, WorkflowStage


@dataclass
class SEOOptimizationConfig:
    """Configuration for SEO optimization workflow."""

    docs_path: Path
    site_url: str
    target_keywords: list[str]
    mode: str = "audit"  # audit, suggest, fix
    interactive: bool = True


class SEOOptimizationWorkflow(BaseWorkflow):
    """Multi-tier workflow for SEO optimization.

    This workflow demonstrates:
    1. Cost-optimized tier routing (CHEAP → CAPABLE → PREMIUM)
    2. Interactive approval workflow
    3. Multi-agent coordination
    4. Structured reporting

    Usage:
        workflow = SEOOptimizationWorkflow()
        result = await workflow.execute(
            docs_path=Path("docs"),
            site_url="https://example.com",
            mode="fix"
        )
    """

    def __init__(self):
        """Initialize SEO optimization workflow."""
        super().__init__(
            name="seo-optimization",
            description="Audit and optimize SEO for documentation sites",
        )

    async def execute(
        self,
        docs_path: Path | str = Path("docs"),
        site_url: str = "https://smartaimemory.com",
        target_keywords: list[str] | None = None,
        mode: str = "audit",
        interactive: bool = True,
        user_goal: str | None = None,
        **kwargs: Any,
    ) -> WorkflowResult:
        """Execute SEO optimization workflow with Socratic questioning.

        Args:
            docs_path: Path to documentation directory
            site_url: Base URL of the site
            target_keywords: List of target keywords for SEO
            mode: Operation mode (audit, suggest, fix)
            interactive: Enable interactive approval for fixes
            user_goal: User's primary goal (launch, visibility, health, specific)
            **kwargs: Additional workflow parameters

        Returns:
            WorkflowResult with findings, suggestions, and cost breakdown
        """
        # Convert to Path if string
        docs_path = Path(docs_path) if isinstance(docs_path, str) else docs_path

        # Default keywords if not provided
        if target_keywords is None:
            target_keywords = ["AI framework", "anticipatory AI", "multi-agent systems"]

        # Initial Discovery Questions (Socratic approach)
        if interactive and user_goal is None:
            user_goal = await self._ask_initial_discovery()

        # Create config with user context
        config = SEOOptimizationConfig(
            docs_path=docs_path,
            site_url=site_url,
            target_keywords=target_keywords,
            mode=mode,
            interactive=interactive,
        )

        # Store user goal in workflow metadata for context-aware recommendations
        self._user_goal = user_goal

        # Stage 1: Scan files (CHEAP - Haiku)
        # Fast file scanning and basic validation
        scan_stage = WorkflowStage(
            name="scan",
            tier="cheap",
            description="Scanning markdown files and extracting metadata",
        )
        scan_result = await self._run_stage(
            stage=scan_stage,
            task=self._scan_files,
            config=config,
        )

        # Stage 2: Analyze content (CAPABLE - Sonnet)
        # Detailed SEO analysis and issue detection
        analyze_stage = WorkflowStage(
            name="analyze",
            tier="capable",
            description="Analyzing SEO issues and generating suggestions",
        )
        analyze_result = await self._run_stage(
            stage=analyze_stage,
            task=self._analyze_seo,
            config=config,
            scan_data=scan_result,
        )

        # If mode is just audit, skip the premium tier
        if mode == "audit":
            return WorkflowResult(
                success=True,
                data={
                    "scan": scan_result,
                    "analysis": analyze_result,
                    "mode": "audit",
                },
                metadata={
                    "files_scanned": scan_result.get("file_count", 0),
                    "issues_found": analyze_result.get("total_issues", 0),
                },
            )

        # Stage 3: Generate recommendations (PREMIUM - Opus)
        # High-quality strategic recommendations and user-facing reports
        recommend_stage = WorkflowStage(
            name="recommend",
            tier="premium",
            description="Generating strategic recommendations and implementation plan",
        )
        recommend_result = await self._run_stage(
            stage=recommend_stage,
            task=self._generate_recommendations,
            config=config,
            analysis=analyze_result,
        )

        # Stage 4: Implement fixes (CAPABLE - Sonnet)
        # Apply approved fixes (only if mode=fix)
        implementation_result = None
        if mode == "fix":
            implement_stage = WorkflowStage(
                name="implement",
                tier="capable",
                description="Implementing approved SEO fixes",
            )
            implementation_result = await self._run_stage(
                stage=implement_stage,
                task=self._implement_fixes,
                config=config,
                recommendations=recommend_result,
            )

        return WorkflowResult(
            success=True,
            data={
                "scan": scan_result,
                "analysis": analyze_result,
                "recommendations": recommend_result,
                "implementation": implementation_result,
                "mode": mode,
            },
            metadata={
                "files_scanned": scan_result.get("file_count", 0),
                "issues_found": analyze_result.get("total_issues", 0),
                "fixes_applied": (
                    implementation_result.get("applied", 0)
                    if implementation_result
                    else 0
                ),
            },
        )

    async def _scan_files(self, config: SEOOptimizationConfig) -> dict[str, Any]:
        """Scan files for SEO data (CHEAP tier - fast scanning).

        This is a lightweight operation perfect for Haiku:
        - File enumeration
        - Basic metadata extraction
        - Link validation
        """
        from examples.seo_optimization.utils import SEOAuditor

        auditor = SEOAuditor(config)

        # Quick file scan
        markdown_files = list(config.docs_path.rglob("*.md"))

        return {
            "file_count": len(markdown_files),
            "files": [str(f) for f in markdown_files],
            "docs_path": str(config.docs_path),
            "site_url": config.site_url,
        }

    async def _analyze_seo(
        self, config: SEOOptimizationConfig, scan_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze SEO issues (CAPABLE tier - detailed analysis).

        This requires Sonnet's reasoning capabilities:
        - Pattern detection
        - Content quality analysis
        - Issue categorization
        """
        from examples.seo_optimization.utils import (
            SEOAuditor,
            ContentOptimizer,
            TechnicalSEOSpecialist,
            LinkAnalyzer,
            SEOReporter,
        )

        # Initialize analyzers
        auditor = SEOAuditor(config)
        content_optimizer = ContentOptimizer(config)
        technical_specialist = TechnicalSEOSpecialist(config)
        link_analyzer = LinkAnalyzer(config)
        reporter = SEOReporter()

        # Run analysis
        audit_results = {
            "meta_tags": auditor.check_meta_tags(),
            "content": content_optimizer.analyze_content(),
            "technical": technical_specialist.check_technical_elements(),
            "links": link_analyzer.analyze_links(),
        }

        # Generate report
        report = reporter.generate_report(audit_results)

        return report

    async def _generate_recommendations(
        self, config: SEOOptimizationConfig, analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate strategic recommendations with Socratic questioning (PREMIUM tier).

        This requires Opus's synthesis capabilities:
        - Prioritizing fixes by impact
        - Calculating confidence scores
        - Generating educational explanations
        - Identifying when to ask questions
        """
        recommendations = []
        needs_clarification = []

        # Process all issues with confidence scoring
        for issue in analysis.get("issues", []):
            confidence = self._calculate_confidence(issue)
            explanation = self._format_educational_explanation(issue, confidence)

            recommendation = {
                "priority": "high" if issue["severity"] == "critical" else "medium",
                "title": f"Fix {issue['element']} in {Path(issue['file']).name}",
                "file": issue["file"],
                "issue": issue,
                "confidence": confidence,
                "explanation": explanation,
            }

            # Confidence threshold: 0.8 (80%)
            if confidence >= 0.8:
                # High confidence - proceed with recommendation
                recommendations.append(recommendation)
            else:
                # Low confidence - flag for user clarification
                recommendation["question"] = self._generate_clarifying_question(
                    issue, confidence
                )
                needs_clarification.append(recommendation)

        # Sort recommendations by priority and confidence
        recommendations.sort(
            key=lambda r: (r["priority"] == "high", r["confidence"]), reverse=True
        )

        return {
            "total_recommendations": len(recommendations),
            "high_priority": len([r for r in recommendations if r["priority"] == "high"]),
            "needs_clarification": len(needs_clarification),
            "recommendations": recommendations,
            "clarification_needed": needs_clarification,
        }

    def _generate_clarifying_question(
        self, issue: dict[str, Any], confidence: float
    ) -> str:
        """Generate clarifying question for low-confidence issues.

        Args:
            issue: SEO issue dictionary
            confidence: Confidence score

        Returns:
            Question to ask the user
        """
        element = issue.get("element")
        file_name = Path(issue["file"]).name

        # Question templates based on issue type
        question_templates = {
            "keyword_density": (
                f"The keyword density in {file_name} is low. "
                f"Should I suggest adding target keywords to headings, "
                f"or is the current wording intentional for your brand voice?"
            ),
            "meta_description": (
                f"I can generate a meta description for {file_name}. "
                f"What's most important to emphasize: technical details, "
                f"benefits, or use cases?"
            ),
            "content_length": (
                f"{file_name} is only 150 words. "
                f"Should I suggest expanding it, or is brevity intentional?"
            ),
            "heading_structure": (
                f"The heading structure in {file_name} could be improved. "
                f"Should I prioritize SEO optimization or preserve your "
                f"current content organization?"
            ),
        }

        return question_templates.get(
            element,
            f"I'm {confidence * 100:.0f}% confident about fixing {element} in {file_name}. "
            f"Would you like me to suggest a fix, or would you prefer to review it first?",
        )

    async def _implement_fixes(
        self, config: SEOOptimizationConfig, recommendations: dict[str, Any]
    ) -> dict[str, Any]:
        """Implement approved fixes (CAPABLE tier - execution).

        This is straightforward implementation work for Sonnet:
        - File modifications
        - Validation
        - Reporting
        """
        from examples.seo_optimization.utils import SEOFixer

        fixer = SEOFixer(config)
        applied = []
        skipped = []

        for rec in recommendations.get("recommendations", []):
            if config.interactive:
                # In interactive mode, would show approval prompt
                # For now, we'll skip implementation
                skipped.append(rec)
            else:
                # Auto-apply
                success = fixer.apply_fix(rec)
                if success:
                    applied.append(rec)
                else:
                    skipped.append(rec)

        return {
            "applied": len(applied),
            "skipped": len(skipped),
            "total": len(recommendations.get("recommendations", [])),
            "applied_fixes": applied,
            "skipped_fixes": skipped,
        }

    async def _ask_initial_discovery(self) -> str:
        """Ask initial discovery questions using AskUserQuestion (Socratic approach).

        Returns:
            User's primary goal (launch, visibility, health, specific)
        """
        # Note: This method would use the AskUserQuestion tool when called from Claude Code
        # The actual implementation is handled by the Claude Code agent invoking this workflow

        # Discovery question structure for agent to use
        discovery_question = {
            "question": "What's most important to you right now with your documentation SEO?",
            "header": "Goal",
            "multiSelect": False,
            "options": [
                {
                    "label": "Launch preparation",
                    "description": "Getting the site ready for public release - need comprehensive coverage",
                },
                {
                    "label": "Search visibility",
                    "description": "Improving rankings for specific keywords - focus on high-impact changes",
                },
                {
                    "label": "Health check",
                    "description": "Regular maintenance and catching issues - balanced approach",
                },
                {
                    "label": "Specific issue",
                    "description": "You've noticed something that needs fixing - targeted investigation",
                },
            ],
        }

        # When running in Claude Code, this question structure would be passed to AskUserQuestion
        # For standalone execution, default to health check
        return "health"

    def _calculate_confidence(self, issue: dict[str, Any]) -> float:
        """Calculate confidence score for a recommendation.

        Confidence factors:
        - Standard best practice (+0.3)
        - Matches config patterns (+0.2)
        - Previous similar approvals (+0.2)
        - Low risk/reversible (+0.1)
        - Clear data supporting (+0.2)

        Args:
            issue: SEO issue dictionary

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0

        # Standard best practices (high confidence)
        best_practices = ["meta_description", "page_title", "h1_count", "sitemap"]
        if issue.get("element") in best_practices:
            confidence += 0.3

        # Critical severity = clear fix (high confidence)
        if issue.get("severity") == "critical":
            confidence += 0.3

        # Technical fixes are straightforward (medium confidence)
        technical_fixes = ["sitemap", "robots_txt", "canonical"]
        if issue.get("element") in technical_fixes:
            confidence += 0.2

        # Content fixes require more context (lower confidence)
        content_fixes = ["keyword_density", "heading_structure", "content_length"]
        if issue.get("element") in content_fixes:
            confidence -= 0.1

        return min(1.0, max(0.0, confidence))

    def _format_educational_explanation(
        self, issue: dict[str, Any], confidence: float
    ) -> dict[str, str]:
        """Format educational explanation for an issue.

        Args:
            issue: SEO issue dictionary
            confidence: Confidence score

        Returns:
            Dictionary with impact, time, and reasoning
        """
        # Map severity to impact
        impact_map = {
            "critical": "High - directly affects search rankings",
            "warning": "Medium - affects user experience and rankings",
            "info": "Low - minor improvement opportunity",
        }

        # Estimate time based on issue type
        time_estimates = {
            "meta_description": "2-3 minutes",
            "page_title": "1-2 minutes",
            "h1_count": "1 minute",
            "sitemap": "5 minutes (one-time setup)",
            "robots_txt": "3 minutes",
            "broken_link": "5-10 minutes (per link)",
        }

        element = issue.get("element", "unknown")
        severity = issue.get("severity", "info")

        explanation = {
            "impact": impact_map.get(severity, "Variable impact"),
            "time": time_estimates.get(element, "5-15 minutes"),
            "why": self._get_reasoning(issue),
            "confidence": f"{confidence * 100:.0f}% confident",
        }

        return explanation

    def _get_reasoning(self, issue: dict[str, Any]) -> str:
        """Get educational reasoning for why an issue matters.

        Args:
            issue: SEO issue dictionary

        Returns:
            Explanation of why the issue matters
        """
        reasoning_map = {
            "meta_description": (
                "Search engines display this in results. "
                "A compelling description improves click-through rate by 20-30%."
            ),
            "page_title": (
                "The most important on-page SEO element. "
                "Appears in browser tabs, search results, and social shares."
            ),
            "h1_count": (
                "Pages should have exactly one H1 tag. "
                "Multiple H1s confuse search engines about page hierarchy."
            ),
            "sitemap": (
                "Helps search engines discover and index all your pages. "
                "Critical for sites with complex navigation."
            ),
            "robots_txt": (
                "Controls which pages search engines can crawl. "
                "Prevents indexing of admin pages, duplicates, etc."
            ),
            "broken_link": (
                "Broken links hurt user experience and SEO. "
                "Search engines penalize sites with many broken links."
            ),
        }

        element = issue.get("element", "unknown")
        return reasoning_map.get(
            element,
            "This affects how search engines understand and rank your content.",
        )

    def _create_clarification_question(
        self, recommendations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create AskUserQuestion structure for low-confidence recommendations.

        This demonstrates how the workflow would use AskUserQuestion tool when
        running in Claude Code for Socratic interaction.

        Args:
            recommendations: List of recommendations needing clarification

        Returns:
            Question structure for AskUserQuestion tool
        """
        if not recommendations:
            return None

        # Example: Asking about prioritization when multiple issues exist
        if len(recommendations) > 5:
            return {
                "question": f"I found {len(recommendations)} SEO issues. If you could only fix ONE thing before launch, what matters most?",
                "header": "Priority",
                "multiSelect": False,
                "options": [
                    {
                        "label": "Missing meta descriptions (Recommended)",
                        "description": "High impact - directly affects search result click-through rates",
                    },
                    {
                        "label": "Page titles optimization",
                        "description": "Medium impact - improves relevance and rankings",
                    },
                    {
                        "label": "Content structure",
                        "description": "Medium impact - better keyword placement and readability",
                    },
                    {
                        "label": "Show me details first",
                        "description": "I want to review all issues before deciding",
                    },
                ],
            }

        # Example: Asking about batch operations
        return {
            "question": f"You have {len(recommendations)} pages without descriptions. Should I:",
            "header": "Approach",
            "multiSelect": False,
            "options": [
                {
                    "label": "Continue asking for each one",
                    "description": "Ensures accuracy - I'll show you each one",
                },
                {
                    "label": "Auto-generate all of them (Recommended)",
                    "description": "Faster - I'll use the same approach, you review after",
                },
                {
                    "label": "Batch approve",
                    "description": "Show me 5 at once, approve/reject in bulk",
                },
            ],
        }


# Register workflow
WORKFLOW_CLASS = SEOOptimizationWorkflow
