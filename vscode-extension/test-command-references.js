"use strict";
/**
 * Command Reference Validation Test
 *
 * WHY THIS WASN'T CAUGHT:
 * - No automated test for command references
 * - VSCode commands are registered at runtime
 * - TypeScript doesn't validate string command names
 * - Manual testing didn't trigger this UI path
 *
 * This test validates that all executeCommand() calls reference registered commands.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * Find all executeCommand calls in the codebase
 */
function findCommandReferences(dir) {
    const references = [];
    const files = findTypeScriptFiles(dir);
    for (const file of files) {
        const content = fs.readFileSync(file, 'utf-8');
        const lines = content.split('\n');
        lines.forEach((line, index) => {
            // Skip commented lines
            const trimmed = line.trim();
            if (trimmed.startsWith('//') || trimmed.startsWith('*') || trimmed.startsWith('/*')) {
                return;
            }
            // Match: executeCommand('command-name') or executeCommand("command-name")
            const match = line.match(/executeCommand\s*\(\s*['"]([^'"]+)['"]/);
            if (match) {
                references.push({
                    file: path.relative(dir, file),
                    line: index + 1,
                    command: match[1],
                });
            }
        });
    }
    return references;
}
/**
 * Find all command registrations in the codebase
 */
function findCommandRegistrations(dir) {
    const registrations = [];
    const files = findTypeScriptFiles(dir);
    for (const file of files) {
        const content = fs.readFileSync(file, 'utf-8');
        const lines = content.split('\n');
        lines.forEach((line, index) => {
            // Match: registerCommand('command-name' or name: 'command-name'
            const registerMatch = line.match(/registerCommand\s*\(\s*['"]([^'"]+)['"]/);
            const nameMatch = line.match(/name:\s*['"]([^'"]+)['"]/);
            if (registerMatch) {
                registrations.push({
                    file: path.relative(dir, file),
                    line: index + 1,
                    command: registerMatch[1],
                });
            }
            else if (nameMatch && !line.includes('//')) {
                registrations.push({
                    file: path.relative(dir, file),
                    line: index + 1,
                    command: nameMatch[1],
                });
            }
        });
    }
    return registrations;
}
/**
 * Find all TypeScript files in directory
 */
function findTypeScriptFiles(dir) {
    const files = [];
    function scan(currentDir) {
        const entries = fs.readdirSync(currentDir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(currentDir, entry.name);
            if (entry.isDirectory() && entry.name !== 'node_modules' && entry.name !== 'out') {
                scan(fullPath);
            }
            else if (entry.isFile() && entry.name.endsWith('.ts')) {
                files.push(fullPath);
            }
        }
    }
    scan(dir);
    return files;
}
/**
 * Check if a command is a built-in VSCode command or auto-registered
 */
function isBuiltInCommand(command) {
    // Common VSCode built-in commands
    const builtIns = [
        'vscode.open',
        'vscode.openWith',
        'workbench.action.',
        'workbench.view.',
        'editor.action.',
        'setContext',
        'markdown.showPreview',
    ];
    // VSCode auto-registers .focus commands for webview panels
    if (command.endsWith('.focus')) {
        return true;
    }
    return builtIns.some(prefix => command.startsWith(prefix));
}
/**
 * Main validation
 */
function validateCommandReferences() {
    const srcDir = path.join(__dirname, 'src');
    console.log('🔍 Scanning for command references...\n');
    const references = findCommandReferences(srcDir);
    const registrations = findCommandRegistrations(srcDir);
    const registeredCommands = new Set(registrations.map(r => r.command));
    console.log(`Found ${references.length} command references`);
    console.log(`Found ${registrations.length} command registrations\n`);
    // Find broken references
    const broken = [];
    for (const ref of references) {
        if (!registeredCommands.has(ref.command) && !isBuiltInCommand(ref.command)) {
            broken.push(ref);
        }
    }
    // Report results
    if (broken.length === 0) {
        console.log('✅ All command references are valid!\n');
        return 0;
    }
    else {
        console.log(`❌ Found ${broken.length} broken command reference(s):\n`);
        for (const ref of broken) {
            console.log(`  ${ref.file}:${ref.line}`);
            console.log(`    Command: "${ref.command}"`);
            console.log(`    Status: NOT REGISTERED\n`);
        }
        console.log('💡 Fix these by either:');
        console.log('  1. Registering the command in extension.ts');
        console.log('  2. Removing the executeCommand() call');
        console.log('  3. Commenting out if feature is disabled\n');
        return 1;
    }
}
// Run validation
const exitCode = validateCommandReferences();
process.exit(exitCode);
//# sourceMappingURL=test-command-references.js.map