'use client';

/**
 * Debug Wizard Component
 *
 * Memory-Enhanced Debugging Wizard with:
 * - Error input and file upload
 * - Historical pattern correlation
 * - Fix recommendations
 * - Resolution recording
 */

import { useState } from 'react';
import type {
  AnalysisInput,
  AnalysisResult,
  AnalysisResponse,
  ErrorType,
  HistoricalMatch,
  Prediction,
  FileInput,
} from '@/lib/debug-wizard/types';
import {
  AccessTier,
  getTierLimits,
  getTierDisplay,
  validateFilesForTier,
  getUpgradePath,
} from '@/lib/debug-wizard/tiers';

// ============================================================================
// Types
// ============================================================================

interface WizardState {
  step: 'input' | 'analyzing' | 'results';
  error_message: string;
  file_path: string;
  stack_trace: string;
  line_number: string;
  code_snippet: string;
  correlate_with_history: boolean;
  files: FileInput[];
  inputMode: 'files' | 'folder' | 'paste';
}

// Files/folders to exclude from uploads
const EXCLUDED_PATTERNS = [
  'node_modules',
  '.git',
  '.next',
  '__pycache__',
  '.pytest_cache',
  'dist',
  'build',
  '.venv',
  'venv',
  '.env',
  '.DS_Store',
  'package-lock.json',
  'yarn.lock',
  'pnpm-lock.yaml',
  '.ico',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.svg',
  '.woff',
  '.woff2',
  '.ttf',
  '.eot',
];

// Check if a file path should be excluded
function shouldExcludeFile(path: string): boolean {
  const normalizedPath = path.toLowerCase();
  return EXCLUDED_PATTERNS.some(pattern =>
    normalizedPath.includes(pattern.toLowerCase())
  );
}

// Group files by directory for tree view
function groupFilesByDirectory(files: FileInput[]): Map<string, FileInput[]> {
  const groups = new Map<string, FileInput[]>();

  for (const file of files) {
    const parts = file.path.split('/');
    const dir = parts.length > 1 ? parts.slice(0, -1).join('/') : '(root)';

    if (!groups.has(dir)) {
      groups.set(dir, []);
    }
    groups.get(dir)!.push(file);
  }

  return groups;
}

// ============================================================================
// Helper Components
// ============================================================================

function ErrorTypeIcon({ type }: { type: ErrorType }) {
  const icons: Record<ErrorType, string> = {
    null_reference: '0',
    type_mismatch: 'T',
    async_timing: 'A',
    import_error: 'I',
    api_error: 'N',
    unknown: '?',
  };
  const colors: Record<ErrorType, string> = {
    null_reference: 'bg-red-500',
    type_mismatch: 'bg-orange-500',
    async_timing: 'bg-purple-500',
    import_error: 'bg-yellow-500',
    api_error: 'bg-blue-500',
    unknown: 'bg-gray-500',
  };
  return (
    <span
      className={`inline-flex items-center justify-center w-6 h-6 rounded text-white text-xs font-bold ${colors[type]}`}
      title={type.replace('_', ' ')}
    >
      {icons[type]}
    </span>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    info: 'bg-blue-100 text-blue-800',
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[severity] || colors.info}`}>
      {severity}
    </span>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const percent = Math.round(value * 100);
  const color =
    percent >= 80 ? 'bg-green-500' : percent >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${percent}%` }} />
      </div>
      <span className="text-sm text-gray-600">{percent}%</span>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export default function DebugWizard() {
  const [tier] = useState<AccessTier>(AccessTier.FREE);
  const [state, setState] = useState<WizardState>({
    step: 'input',
    error_message: '',
    file_path: '',
    stack_trace: '',
    line_number: '',
    code_snippet: '',
    correlate_with_history: true,
    files: [],
    inputMode: 'files',
  });
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [collapsedDirs, setCollapsedDirs] = useState<Set<string>>(new Set());
  const [uploadStats, setUploadStats] = useState<{ total: number; excluded: number } | null>(null);

  const limits = getTierLimits(tier);
  const tierDisplay = getTierDisplay(tier);
  const upgradeTier = getUpgradePath(tier);

  // ============================================================================
  // Handlers
  // ============================================================================

  const handleInputChange = (field: keyof WizardState, value: string | boolean) => {
    setState((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = async (files: File[], preservePaths = false) => {
    const maxFiles = limits.maxFiles ?? 100;
    const maxSizeMB = limits.maxFileSizeMB ?? 1;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;

    const newFiles: FileInput[] = [];
    let excludedCount = 0;

    for (const file of files) {
      // Get the file path - use webkitRelativePath for folder uploads, otherwise just the name
      const filePath = preservePaths && file.webkitRelativePath
        ? file.webkitRelativePath
        : file.name;

      // Skip excluded files/folders
      if (shouldExcludeFile(filePath)) {
        excludedCount++;
        continue;
      }

      // Check file size
      if (file.size > maxSizeBytes) {
        // Skip silently for folder uploads, show error for single files
        if (!preservePaths) {
          setError(`File "${file.name}" exceeds the ${maxSizeMB}MB limit.`);
        }
        excludedCount++;
        continue;
      }

      // Skip empty files
      if (file.size === 0) {
        excludedCount++;
        continue;
      }

      // Read file content
      try {
        const content = await file.text();
        newFiles.push({
          path: filePath,
          content: content,
          size_bytes: file.size,
        });
      } catch (err) {
        console.error('Error reading file:', err);
        excludedCount++;
      }
    }

    // Check file count limit after filtering
    const totalFiles = state.files.length + newFiles.length;
    if (totalFiles > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed. You have ${state.files.length} and tried to add ${newFiles.length} (after filtering).`);
      return;
    }

    if (newFiles.length > 0) {
      setState((prev) => ({
        ...prev,
        files: [...prev.files, ...newFiles],
        // Auto-fill file path from first file if not set
        file_path: prev.file_path || newFiles[0].path,
      }));
      setError(null);
      setUploadStats({ total: files.length, excluded: excludedCount });
    } else if (files.length > 0) {
      setError('No valid files found after filtering. All files were excluded or too large.');
    }
  };

  const toggleDirCollapse = (dir: string) => {
    setCollapsedDirs(prev => {
      const next = new Set(prev);
      if (next.has(dir)) {
        next.delete(dir);
      } else {
        next.add(dir);
      }
      return next;
    });
  };

  const removeFile = (index: number) => {
    setState((prev) => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index),
    }));
  };

  const handleAnalyze = async () => {
    setError(null);

    // Validate input
    if (!state.error_message.trim()) {
      setError('Please enter an error message to analyze');
      return;
    }

    // Validate files if any
    if (state.files.length > 0) {
      const validation = validateFilesForTier(tier, state.files);
      if (!validation.valid) {
        setError(validation.errors.join('; '));
        return;
      }
    }

    setState((prev) => ({ ...prev, step: 'analyzing' }));

    try {
      const input: AnalysisInput = {
        error_message: state.error_message,
        file_path: state.file_path || 'unknown',
        stack_trace: state.stack_trace || undefined,
        line_number: state.line_number ? parseInt(state.line_number, 10) : undefined,
        code_snippet: state.code_snippet || undefined,
        correlate_with_history: state.correlate_with_history,
        file_contents: state.files.length > 0 ? state.files : undefined,
      };

      const response = await fetch('/api/debug-wizard/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });

      const data: AnalysisResponse = await response.json();

      if (!data.success || !data.data) {
        throw new Error(data.error || 'Analysis failed');
      }

      setResult(data.data);
      setState((prev) => ({ ...prev, step: 'results' }));
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setState((prev) => ({ ...prev, step: 'input' }));
    }
  };

  const handleReset = () => {
    setState({
      step: 'input',
      error_message: '',
      file_path: '',
      stack_trace: '',
      line_number: '',
      code_snippet: '',
      correlate_with_history: true,
      files: [],
      inputMode: 'files',
    });
    setResult(null);
    setError(null);
    setCollapsedDirs(new Set());
    setUploadStats(null);
  };

  const handleCopyFix = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Demo fill handlers
  const fillNullRefDemo = () => {
    setState((prev) => ({
      ...prev,
      error_message: "TypeError: Cannot read property 'map' of undefined",
      file_path: 'src/components/UserList.tsx',
      stack_trace: `TypeError: Cannot read property 'map' of undefined
    at UserList (src/components/UserList.tsx:15:23)
    at renderWithHooks (node_modules/react-dom/cjs/react-dom.development.js:14985:18)`,
      line_number: '15',
      code_snippet: `const users = data.users;
return users.map(user => <UserCard key={user.id} user={user} />);`,
    }));
  };

  const fillAsyncDemo = () => {
    setState((prev) => ({
      ...prev,
      error_message: 'UnhandledPromiseRejection: Promise rejected before await',
      file_path: 'src/api/fetchData.ts',
      stack_trace: `UnhandledPromiseRejection: Promise rejected
    at fetchUserData (src/api/fetchData.ts:23:5)`,
      line_number: '23',
      code_snippet: `async function fetchUserData() {
  const result = fetchData(); // Missing await!
  return result.data;
}`,
    }));
  };

  const fillImportDemo = () => {
    setState((prev) => ({
      ...prev,
      error_message: "ModuleNotFoundError: No module named 'structlog'",
      file_path: 'src/utils/logger.py',
      stack_trace: `ModuleNotFoundError: No module named 'structlog'
  File "src/utils/logger.py", line 1, in <module>
    import structlog`,
      line_number: '1',
      code_snippet: `import structlog

logger = structlog.get_logger()`,
    }));
  };

  // ============================================================================
  // Render: Input Step
  // ============================================================================

  if (state.step === 'input') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 rounded-t-lg">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">D</span>
              <div>
                <h2 className="text-2xl font-bold">Memory-Enhanced Debugging Wizard</h2>
                <p className="text-purple-200 text-sm">
                  AI that remembers past bugs and their fixes
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 mt-3">
              <span className="px-2 py-1 bg-purple-500 rounded text-xs">
                {tierDisplay.name}
              </span>
              <span className="text-purple-200 text-xs">
                {limits.maxFiles === null ? 'Unlimited files' : `Up to ${limits.maxFiles} files`}
              </span>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="m-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Input Form */}
          <div className="p-6 space-y-6">
            {/* Error Message */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Error Message <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={3}
                value={state.error_message}
                onChange={(e) => handleInputChange('error_message', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                placeholder="Paste your error message here..."
              />
            </div>

            {/* File Upload Section */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Code (optional)
                <span className="text-gray-500 font-normal ml-2">
                  Max {limits.maxFiles === null ? 'unlimited' : limits.maxFiles} file{limits.maxFiles !== 1 ? 's' : ''}, {limits.maxFileSizeMB ? `${limits.maxFileSizeMB}MB each` : 'no size limit'}
                </span>
              </label>

              {/* Input Mode Tabs */}
              <div className="flex border-b border-gray-200 mb-4">
                <button
                  type="button"
                  onClick={() => setState(prev => ({ ...prev, inputMode: 'files' }))}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    state.inputMode === 'files'
                      ? 'border-purple-600 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  📄 Individual Files
                </button>
                <button
                  type="button"
                  onClick={() => setState(prev => ({ ...prev, inputMode: 'folder' }))}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    state.inputMode === 'folder'
                      ? 'border-purple-600 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  📁 Select Folder
                </button>
                <button
                  type="button"
                  onClick={() => setState(prev => ({ ...prev, inputMode: 'paste' }))}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    state.inputMode === 'paste'
                      ? 'border-purple-600 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  📋 Paste Code
                </button>
              </div>

              {/* Files Mode */}
              {state.inputMode === 'files' && (
                <div
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                    state.files.length > 0 ? 'border-purple-400 bg-purple-50' : 'border-gray-300 hover:border-purple-400'
                  }`}
                  onDragOver={(e) => {
                    e.preventDefault();
                    e.currentTarget.classList.add('border-purple-500', 'bg-purple-50');
                  }}
                  onDragLeave={(e) => {
                    e.currentTarget.classList.remove('border-purple-500', 'bg-purple-50');
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    e.currentTarget.classList.remove('border-purple-500', 'bg-purple-50');
                    const droppedFiles = Array.from(e.dataTransfer.files);
                    handleFileUpload(droppedFiles, false);
                  }}
                >
                  {state.files.length === 0 ? (
                    <>
                      <div className="text-4xl mb-2">📄</div>
                      <p className="text-gray-600 mb-2">Drag & drop source files here</p>
                      <p className="text-sm text-gray-500 mb-3">or</p>
                      <label className="px-4 py-2 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700 inline-block">
                        Browse Files
                        <input
                          type="file"
                          multiple
                          accept=".ts,.tsx,.js,.jsx,.py,.java,.go,.rs,.rb,.php,.c,.cpp,.h,.hpp,.cs,.swift,.kt,.scala,.vue,.svelte,.json,.yaml,.yml,.md,.txt"
                          className="hidden"
                          onChange={(e) => {
                            if (e.target.files) {
                              handleFileUpload(Array.from(e.target.files), false);
                            }
                          }}
                        />
                      </label>
                      <p className="text-xs text-gray-400 mt-3">
                        Supports: .ts, .tsx, .js, .jsx, .py, .java, .go, .rs, .rb, .php, .c, .cpp, .cs, .swift, .kt, .scala, .vue, .svelte
                      </p>
                    </>
                  ) : null}
                </div>
              )}

              {/* Folder Mode */}
              {state.inputMode === 'folder' && state.files.length === 0 && (
                <div className="border-2 border-dashed rounded-lg p-6 text-center border-gray-300 hover:border-purple-400 transition-colors">
                  <div className="text-4xl mb-2">📁</div>
                  <p className="text-gray-600 mb-2">Select an entire folder to analyze</p>
                  <p className="text-sm text-gray-500 mb-3">
                    Automatically excludes: node_modules, .git, build, dist, images
                  </p>
                  <label className="px-4 py-2 bg-purple-600 text-white rounded-lg cursor-pointer hover:bg-purple-700 inline-block">
                    Select Folder
                    <input
                      type="file"
                      // @ts-expect-error webkitdirectory is non-standard but widely supported
                      webkitdirectory=""
                      directory=""
                      multiple
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files) {
                          handleFileUpload(Array.from(e.target.files), true);
                        }
                      }}
                    />
                  </label>
                  <p className="text-xs text-gray-400 mt-3">
                    Works in Chrome, Edge, and Safari. Firefox users: use individual files.
                  </p>
                </div>
              )}

              {/* Paste Mode */}
              {state.inputMode === 'paste' && state.files.length === 0 && (
                <div className="space-y-3">
                  <textarea
                    rows={8}
                    value={state.code_snippet}
                    onChange={(e) => handleInputChange('code_snippet', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono text-sm"
                    placeholder="Paste your code here..."
                  />
                  <p className="text-xs text-gray-500">
                    Tip: Include the file path in the &quot;File Path&quot; field below for better analysis.
                  </p>
                </div>
              )}

              {/* Selected Files Display - Tree View */}
              {state.files.length > 0 && (
                <div className="border-2 border-purple-400 bg-purple-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <span className="font-medium text-purple-700">
                        {state.files.length} file{state.files.length !== 1 ? 's' : ''} selected
                      </span>
                      {uploadStats && uploadStats.excluded > 0 && (
                        <span className="text-sm text-gray-500 ml-2">
                          ({uploadStats.excluded} excluded)
                        </span>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setState(prev => ({ ...prev, files: [] }));
                        setUploadStats(null);
                        setCollapsedDirs(new Set());
                      }}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Clear all
                    </button>
                  </div>

                  {/* Tree View */}
                  <div className="space-y-1 max-h-60 overflow-y-auto bg-white rounded border border-purple-200 p-2">
                    {Array.from(groupFilesByDirectory(state.files)).map(([dir, dirFiles]) => (
                      <div key={dir}>
                        {/* Directory Header */}
                        <button
                          type="button"
                          onClick={() => toggleDirCollapse(dir)}
                          className="flex items-center gap-2 w-full text-left py-1 px-2 hover:bg-gray-100 rounded text-sm"
                        >
                          <span className="text-gray-400">
                            {collapsedDirs.has(dir) ? '▶' : '▼'}
                          </span>
                          <span className="text-yellow-600">📁</span>
                          <span className="font-medium text-gray-700">{dir}</span>
                          <span className="text-xs text-gray-400">({dirFiles.length})</span>
                        </button>

                        {/* Files in Directory */}
                        {!collapsedDirs.has(dir) && (
                          <div className="ml-6 space-y-0.5">
                            {dirFiles.map((file) => {
                              const fileName = file.path.split('/').pop() || file.path;
                              const fileIndex = state.files.findIndex(f => f.path === file.path);
                              return (
                                <div
                                  key={file.path}
                                  className="flex items-center justify-between py-1 px-2 hover:bg-gray-50 rounded group"
                                >
                                  <div className="flex items-center gap-2 min-w-0">
                                    <span className="text-blue-500">📄</span>
                                    <span className="text-sm font-mono truncate">{fileName}</span>
                                    <span className="text-xs text-gray-400">
                                      ({Math.round(file.content.length / 1024 * 10) / 10}KB)
                                    </span>
                                  </div>
                                  <button
                                    type="button"
                                    onClick={() => removeFile(fileIndex)}
                                    className="text-red-500 hover:text-red-700 opacity-0 group-hover:opacity-100 transition-opacity"
                                  >
                                    ✕
                                  </button>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Add More Files */}
                  <div className="mt-3 flex gap-3">
                    <label className="text-sm text-purple-600 hover:text-purple-800 cursor-pointer">
                      + Add files
                      <input
                        type="file"
                        multiple
                        accept=".ts,.tsx,.js,.jsx,.py,.java,.go,.rs,.rb,.php,.c,.cpp,.h,.hpp,.cs,.swift,.kt,.scala,.vue,.svelte,.json,.yaml,.yml,.md,.txt"
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files) {
                            handleFileUpload(Array.from(e.target.files), false);
                          }
                        }}
                      />
                    </label>
                    <label className="text-sm text-purple-600 hover:text-purple-800 cursor-pointer">
                      + Add folder
                      <input
                        type="file"
                        // @ts-expect-error webkitdirectory is non-standard but widely supported
                        webkitdirectory=""
                        directory=""
                        multiple
                        className="hidden"
                        onChange={(e) => {
                          if (e.target.files) {
                            handleFileUpload(Array.from(e.target.files), true);
                          }
                        }}
                      />
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* File Path and Line Number (manual entry fallback) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  File Path
                  <span className="text-gray-500 font-normal ml-2">(or enter manually if not uploading)</span>
                </label>
                <input
                  type="text"
                  value={state.file_path}
                  onChange={(e) => handleInputChange('file_path', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="src/components/MyComponent.tsx"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Line Number</label>
                <input
                  type="text"
                  value={state.line_number}
                  onChange={(e) => handleInputChange('line_number', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="42"
                />
              </div>
            </div>

            {/* Stack Trace */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stack Trace (optional)
              </label>
              <textarea
                rows={4}
                value={state.stack_trace}
                onChange={(e) => handleInputChange('stack_trace', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono text-sm"
                placeholder="Paste full stack trace..."
              />
            </div>

            {/* Code Snippet */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code Snippet (optional)
              </label>
              <textarea
                rows={4}
                value={state.code_snippet}
                onChange={(e) => handleInputChange('code_snippet', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 font-mono text-sm"
                placeholder="Paste relevant code..."
              />
            </div>

            {/* Options */}
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={state.correlate_with_history}
                  onChange={(e) => handleInputChange('correlate_with_history', e.target.checked)}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <span className="text-sm text-gray-700">Search historical bug patterns</span>
              </label>
            </div>

            {/* Quick Fill Demos */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm font-medium text-gray-700 mb-3">Try a demo:</p>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={fillNullRefDemo}
                  className="px-3 py-1.5 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
                >
                  Null Reference
                </button>
                <button
                  type="button"
                  onClick={fillAsyncDemo}
                  className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded text-sm hover:bg-purple-200"
                >
                  Async/Await
                </button>
                <button
                  type="button"
                  onClick={fillImportDemo}
                  className="px-3 py-1.5 bg-yellow-100 text-yellow-700 rounded text-sm hover:bg-yellow-200"
                >
                  Import Error
                </button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="border-t border-gray-200 p-6 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {limits.dailyRequestLimit !== null && (
                <span>
                  Daily limit: {limits.dailyRequestLimit} analyses
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!state.error_message.trim()}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Analyze Bug
            </button>
          </div>
        </div>

        {/* Upgrade CTA */}
        {limits.showUpgradeCTA && upgradeTier && (
          <div className="mt-6 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-purple-900">
                  Want more power?
                </h4>
                <p className="text-sm text-purple-700">
                  Upgrade to {getTierDisplay(upgradeTier).name} for expanded limits and features.
                </p>
              </div>
              <a
                href={getTierDisplay(upgradeTier).ctaLink}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
              >
                {getTierDisplay(upgradeTier).ctaText}
              </a>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ============================================================================
  // Render: Analyzing Step
  // ============================================================================

  if (state.step === 'analyzing') {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg p-12 text-center">
          <div className="animate-spin w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full mx-auto mb-6" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Analyzing your bug...</h3>
          <p className="text-gray-600">Searching historical patterns and generating recommendations</p>
        </div>
      </div>
    );
  }

  // ============================================================================
  // Render: Results Step
  // ============================================================================

  if (state.step === 'results' && result) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white border-2 border-gray-200 rounded-lg shadow-lg">
          <div className="bg-gradient-to-r from-green-600 to-teal-600 text-white p-6 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-3xl">V</span>
                <div>
                  <h2 className="text-2xl font-bold">Analysis Complete</h2>
                  <p className="text-green-200 text-sm">
                    Found {result.matches_found} historical pattern
                    {result.matches_found !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm"
              >
                New Analysis
              </button>
            </div>
          </div>

          {/* Error Classification */}
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ErrorTypeIcon type={result.error_classification.error_type} />
              Error Classification
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Error Type</p>
                <p className="font-medium capitalize">
                  {result.error_classification.error_type.replace('_', ' ')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">File</p>
                <p className="font-medium font-mono text-sm">
                  {result.error_classification.file_path}
                  {result.error_classification.line_number &&
                    `:${result.error_classification.line_number}`}
                </p>
              </div>
            </div>

            {/* Likely Causes */}
            <div className="mt-4">
              <p className="text-sm text-gray-500 mb-2">Likely Causes</p>
              <div className="space-y-2">
                {result.error_classification.likely_causes.map((cause, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 bg-gray-50 p-3 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-sm">{cause.cause}</p>
                      <p className="text-sm text-gray-600">{cause.check}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-gray-500">
                        {Math.round(cause.likelihood * 100)}% likely
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Fix */}
          {result.recommended_fix && (
            <div className="p-6 border-b border-gray-200 bg-purple-50">
              <h3 className="text-lg font-semibold text-purple-900 mb-4">
                Recommended Fix (from Historical Match)
              </h3>
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-medium text-purple-900">
                      {result.recommended_fix.original_fix}
                    </p>
                    <p className="text-sm text-gray-500">
                      Based on: {result.recommended_fix.based_on}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">Expected time</p>
                    <p className="font-medium">{result.recommended_fix.expected_resolution_time}</p>
                  </div>
                </div>

                {result.recommended_fix.fix_code && (
                  <div className="mt-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium text-gray-700">Example Fix Code:</p>
                      <button
                        type="button"
                        onClick={() => handleCopyFix(result.recommended_fix!.fix_code!)}
                        className="text-sm text-purple-600 hover:text-purple-800"
                      >
                        {copied ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <pre className="bg-gray-900 text-green-400 p-3 rounded text-sm overflow-x-auto">
                      {result.recommended_fix.fix_code}
                    </pre>
                  </div>
                )}

                {result.recommended_fix.adaptation_notes.length > 0 && (
                  <div className="mt-3 bg-yellow-50 border border-yellow-200 rounded p-3">
                    <p className="text-sm font-medium text-yellow-800 mb-1">Adaptation Notes:</p>
                    <ul className="text-sm text-yellow-700 space-y-1">
                      {result.recommended_fix.adaptation_notes.map((note, idx) => (
                        <li key={idx}>- {note}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="mt-3">
                  <p className="text-sm text-gray-500 mb-1">Confidence</p>
                  <ConfidenceBar value={result.recommended_fix.confidence} />
                </div>
              </div>
            </div>
          )}

          {/* Historical Matches */}
          {result.historical_matches.length > 0 && (
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Historical Matches ({result.historical_matches.length})
              </h3>
              <div className="space-y-3">
                {result.historical_matches.map((match: HistoricalMatch, idx: number) => (
                  <div
                    key={idx}
                    className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <ErrorTypeIcon type={match.error_type} />
                        <span className="font-medium">{match.file}</span>
                      </div>
                      <span className="text-sm text-gray-500">{match.date}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Root cause:</strong> {match.root_cause}
                    </p>
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Fix:</strong> {match.fix_applied}
                    </p>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-500">
                        Resolved in {match.resolution_time_minutes} min
                      </span>
                      <span className="text-purple-600">
                        {Math.round(match.similarity_score * 100)}% match
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {match.matching_factors.map((factor, fidx) => (
                        <span
                          key={fidx}
                          className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs"
                        >
                          {factor}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Predictions */}
          {result.predictions.length > 0 && (
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Predictions & Insights
              </h3>
              <div className="space-y-3">
                {result.predictions.map((prediction: Prediction, idx: number) => (
                  <div
                    key={idx}
                    className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <SeverityBadge severity={prediction.severity} />
                      <span className="font-medium capitalize">
                        {prediction.type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{prediction.description}</p>
                    {prediction.prevention_steps.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-gray-500 mb-1">Prevention steps:</p>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {prediction.prevention_steps.map((step, sidx) => (
                            <li key={sidx} className="flex items-start gap-2">
                              <span className="text-green-500">-</span>
                              {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
            <ul className="space-y-2">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-3 text-gray-700">
                  <span className="text-purple-500 mt-0.5">-</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>

          {/* Memory Benefit */}
          <div className="p-6 bg-gradient-to-r from-purple-50 to-indigo-50">
            <h3 className="text-lg font-semibold text-purple-900 mb-3">
              Memory Benefit
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <p className="text-2xl font-bold text-purple-600">
                  {result.memory_benefit.matches_found}
                </p>
                <p className="text-sm text-gray-600">Patterns Found</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-200">
                <p className="text-2xl font-bold text-green-600">
                  {result.memory_benefit.time_saved_estimate}
                </p>
                <p className="text-sm text-gray-600">Time Saved</p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-purple-200 md:col-span-1">
                <p className="text-sm text-gray-700">{result.memory_benefit.value_statement}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="button"
            onClick={handleReset}
            className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
          >
            Analyze Another Bug
          </button>
          {limits.resolutionRecordingEnabled && result.bug_id && (
            <button
              type="button"
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
              onClick={() => {
                // TODO: Implement resolution recording modal
                alert(
                  `Resolution recording for bug ${result.bug_id} coming soon!\n\nAfter you fix this bug, you can record the resolution to help future debugging.`
                );
              }}
            >
              Record Resolution
            </button>
          )}
        </div>
      </div>
    );
  }

  return null;
}
