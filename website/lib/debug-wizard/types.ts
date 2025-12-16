/**
 * Debug Wizard Type Definitions
 * TypeScript mirror of the Python Memory-Enhanced Debugging Wizard
 *
 * These types define the data structures for the debugging wizard,
 * enabling type-safe communication between frontend and API.
 */

// ============================================================================
// Error Classification Types
// ============================================================================

/**
 * Known error type categories the wizard can classify
 */
export type ErrorType =
  | 'null_reference'
  | 'type_mismatch'
  | 'async_timing'
  | 'import_error'
  | 'api_error'
  | 'unknown';

/**
 * Bug resolution status
 */
export type BugStatus = 'investigating' | 'resolved' | 'wont_fix' | 'duplicate';

/**
 * Severity levels for predictions and issues
 */
export type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';

// ============================================================================
// Bug Resolution & History Types
// ============================================================================

/**
 * A historical bug resolution pattern
 * Mirrors Python BugResolution dataclass
 */
export interface BugResolution {
  bug_id: string;
  date: string;
  file_path: string;
  error_type: ErrorType;
  error_message: string;
  root_cause: string;
  fix_applied: string;
  fix_code: string | null;
  resolution_time_minutes: number;
  resolved_by: string;
  confidence: number;
  status: BugStatus;
}

/**
 * A match from historical bug patterns
 * Mirrors Python HistoricalMatch dataclass
 */
export interface HistoricalMatch {
  date: string;
  file: string;
  error_type: ErrorType;
  root_cause: string;
  fix_applied: string;
  fix_code: string | null;
  resolution_time_minutes: number;
  similarity_score: number;
  matching_factors: string[];
}

// ============================================================================
// Analysis Input/Output Types
// ============================================================================

/**
 * Input context for bug analysis
 */
export interface AnalysisInput {
  /** The error message to analyze */
  error_message: string;
  /** File path where error occurred */
  file_path: string;
  /** Optional stack trace */
  stack_trace?: string;
  /** Optional line number */
  line_number?: number;
  /** Optional code snippet around the error */
  code_snippet?: string;
  /** Enable historical pattern matching */
  correlate_with_history?: boolean;
  /** Optional file contents for context */
  file_contents?: FileInput[];
}

/**
 * File input for multi-file analysis
 */
export interface FileInput {
  path: string;
  content: string;
  size_bytes: number;
}

/**
 * Likely cause identified by the wizard
 */
export interface LikelyCause {
  cause: string;
  check: string;
  likelihood: number;
}

/**
 * Current error classification result
 */
export interface ErrorClassification {
  error_type: ErrorType;
  error_message: string;
  file_path: string;
  line_number: number | null;
  file_type: string;
  likely_causes: LikelyCause[];
}

/**
 * Recommended fix based on historical match
 */
export interface RecommendedFix {
  based_on: string;
  original_fix: string;
  fix_code: string | null;
  expected_resolution_time: string;
  confidence: number;
  adaptation_notes: string[];
}

/**
 * Level 4 prediction
 */
export interface Prediction {
  type: string;
  severity: Severity;
  description: string;
  prevention_steps: string[];
}

/**
 * Memory benefit calculation result
 */
export interface MemoryBenefit {
  matches_found: number;
  time_saved_estimate: string;
  value_statement: string;
  historical_insight: string | null;
}

/**
 * Complete analysis result from the wizard
 */
export interface AnalysisResult {
  /** Classification of the current error */
  error_classification: ErrorClassification;
  /** Similar bugs from history */
  historical_matches: HistoricalMatch[];
  /** Whether historical correlation was enabled */
  historical_correlation_enabled: boolean;
  /** Number of historical matches found */
  matches_found: number;
  /** AI-recommended fix based on history */
  recommended_fix: RecommendedFix | null;
  /** Level 4 predictions */
  predictions: Prediction[];
  /** Actionable recommendations */
  recommendations: string[];
  /** Overall confidence in the analysis */
  confidence: number;
  /** Quantified benefit of persistent memory */
  memory_benefit: MemoryBenefit;
  /** Bug ID for tracking resolution */
  bug_id?: string;
}

// ============================================================================
// Resolution Recording Types
// ============================================================================

/**
 * Input for recording a bug resolution
 */
export interface ResolutionInput {
  bug_id: string;
  root_cause: string;
  fix_applied: string;
  fix_code?: string;
  resolution_time_minutes: number;
  resolved_by?: string;
}

/**
 * Result of recording a resolution
 */
export interface ResolutionResult {
  success: boolean;
  bug_id: string;
  message: string;
}

// ============================================================================
// Validation Types
// ============================================================================

/**
 * File validation result
 */
export interface FileValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  config: {
    deployment_mode: 'web' | 'local';
    max_files: number | null;
    max_file_size_mb: number | null;
    folder_upload_enabled: boolean;
  };
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Standard API response wrapper
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  tier?: string;
  usage?: {
    requests_used: number;
    requests_limit: number;
    storage_used_mb: number;
    storage_limit_mb: number;
  };
}

/**
 * Analysis API response
 */
export type AnalysisResponse = ApiResponse<AnalysisResult>;

/**
 * Resolution recording API response
 */
export type ResolutionResponse = ApiResponse<ResolutionResult>;

/**
 * Validation API response
 */
export type ValidationResponse = ApiResponse<FileValidationResult>;
