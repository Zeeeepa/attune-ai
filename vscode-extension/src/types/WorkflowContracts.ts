/**
 * Data contracts for workflow inputs and outputs
 *
 * These interfaces define the shape of data exchanged between:
 * - VSCode extension and Python workflows
 * - Webview panels and extension host
 *
 * Copyright 2025 Smart AI Memory, LLC
 * Licensed under Fair Source 0.9
 */

/**
 * Standard finding structure for all workflows
 */
export interface WorkflowFinding {
    /** Unique identifier for this finding */
    id: string;

    /** File path (workspace-relative) */
    file: string;

    /** Line number (1-indexed) */
    line: number;

    /** Column number (1-indexed, optional) */
    column?: number;

    /** Severity level */
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';

    /** Category of finding */
    category: 'security' | 'performance' | 'maintainability' | 'style' | 'correctness';

    /** Brief message (1 line) */
    message: string;

    /** Extended details (optional) */
    details?: string;

    /** Recommended fix (optional) */
    recommendation?: string;

    /** Code snippet context (optional) */
    snippet?: {
        before: string;
        after: string;
    };
}

/**
 * Code review workflow output
 */
export interface CodeReviewResult {
    /** List of findings */
    findings: WorkflowFinding[];

    /** Summary statistics */
    summary: {
        total_findings: number;
        by_severity: Record<string, number>;
        by_category: Record<string, number>;
        files_affected: string[];
    };

    /** Overall verdict */
    verdict: 'approve' | 'approve_with_suggestions' | 'request_changes' | 'reject';

    /** Security score (0-100) */
    security_score: number;

    /** Formatted report (for terminal display) */
    formatted_report: string;

    /** Model tier used */
    model_tier_used: string;

    /** Costs */
    costs?: {
        input_tokens: number;
        output_tokens: number;
        total_cost_usd: number;
    };
}

/**
 * Refactor plan workflow output
 */
export interface RefactorPlanResult {
    /** Technical debt items */
    debt_items: Array<{
        file: string;
        line?: number;
        severity: 'critical' | 'high' | 'medium' | 'low';
        category: string;
        description: string;
        estimated_effort: string;
    }>;

    /** Analysis summary */
    analysis: {
        trajectory: 'improving' | 'stable' | 'degrading';
        hotspots: string[];
        priority_areas: string[];
    };

    /** Grouped by file */
    by_file: Record<string, any[]>;
}

/**
 * Test generation workflow output
 */
export interface TestGenResult {
    /** Files analyzed */
    files_analyzed: string[];

    /** Coverage metrics */
    coverage: {
        total_lines: number;
        covered_lines: number;
        coverage_percent: number;
        by_file: Record<string, number>;
    };

    /** Suggested tests */
    suggested_tests: Array<{
        file: string;
        test_type: 'unit' | 'integration' | 'edge_case';
        priority: 'high' | 'medium' | 'low';
        description: string;
    }>;
}

/**
 * Generic workflow result wrapper
 */
export interface WorkflowResult<T = any> {
    /** Workflow name */
    workflow: string;

    /** Success status */
    success: boolean;

    /** Error message (if failed) */
    error?: string;

    /** Workflow-specific result data */
    result: T;

    /** Execution metadata */
    metadata: {
        duration_seconds: number;
        timestamp: string;
        input_params: Record<string, any>;
    };
}
