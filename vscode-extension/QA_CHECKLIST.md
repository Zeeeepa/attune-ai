# Empathy Framework v1.4.0 - QA Checklist

## Pre-Testing Setup
```bash
cd vscode-extension
npm run compile
# Press F5 in VSCode to launch Extension Development Host
```

---

## 1. Socratic Refinement Flow (Core Feature)

### 1.1 Capable Tier Triggers
- [ ] Run `test-gen` workflow (Cmd+Shift+E W → Test Generation)
  - Expected: QuickPick appears asking "What type of tests?"
  - [ ] Select an option, verify second question appears
  - [ ] Complete flow, verify workflow runs with refined input

- [ ] Run `security-audit` workflow
  - Expected: QuickPick asks about depth
  - [ ] Verify workflow executes after answering

### 1.2 Premium Tier Triggers
- [ ] Run `code-review` workflow
  - Expected: QuickPick asks "What should I focus on?" then "How thorough?"
  - [ ] Verify both questions appear sequentially

### 1.3 Cheap Tier Skips Refinement
- [ ] Run `morning` workflow (Cmd+Shift+E M)
  - Expected: Runs immediately, NO questions
- [ ] Run `ship` workflow (Cmd+Shift+E S)
  - Expected: Runs immediately, NO questions

### 1.4 Context Menu Skip
- [ ] Right-click a file → Run code-review
  - Expected: Should skip refinement (explicit file target)
  - Verify setting: `empathy.socraticRefinement.skipForContextMenu`

---

## 2. Pattern Learning

### 2.1 Pattern Save
- [ ] Run `test-gen` on a file, answer questions
- [ ] Run `test-gen` on SAME file again
  - Expected: "Previous Settings Found" QuickPick appears
  - Options: "Use Previous Settings", "Choose New Settings", "Cancel"

### 2.2 Pattern Recall
- [ ] Select "Use Previous Settings"
  - Expected: Workflow runs with saved answers, no questions

### 2.3 New Settings Override
- [ ] Select "Choose New Settings"
  - Expected: Question flow starts fresh

---

## 3. Agent Workflow Designer

### 3.1 Keyboard Shortcut
- [ ] Press Cmd+Shift+E Q
  - Expected: Agent Designer input box opens
  - Title shows "Agent Workflow Designer (1/12)"

### 3.2 Conversation Flow
- [ ] Type a goal like "I want to analyze security vulnerabilities"
  - Expected: Response appears in Output channel
  - [ ] Continue conversation, verify multi-turn works

### 3.3 Result Handling
- [ ] When YAML output appears, verify QuickPick offers:
  - "Copy to Clipboard"
  - "Open in New File"
  - "Done"

---

## 4. Guided Panel

### 4.1 Research Synthesis Button
- [ ] Open Guided Panel (search "Empathy Guide" in command palette)
- [ ] Click "Research" button (magnifying glass icon)
  - Expected: Research Synthesis workflow launches

### 4.2 Other Action Buttons
- [ ] Click "Morning" → runs morning workflow
- [ ] Click "Ship Check" → runs ship workflow
- [ ] Click "Workflows" → opens workflow picker

---

## 5. Settings Verification

### 5.1 Refinement Toggle
- [ ] Set `empathy.socraticRefinement.enabled: false`
- [ ] Run `test-gen` workflow
  - Expected: NO questions, runs immediately
- [ ] Reset to `true`

### 5.2 Beta Features Gate
- [ ] Verify `empathy.showBetaFeatures: false` (default)
- [ ] Memory Panel should NOT appear in sidebar
- [ ] Set to `true`, reload → Memory Panel appears

---

## 6. Edge Cases

### 6.1 No API Key
- [ ] Remove ANTHROPIC_API_KEY from environment
- [ ] Run Agent Designer
  - Expected: Fallback responses work (no crash)

### 6.2 Cancel Mid-Flow
- [ ] Start refinement questions, press Escape
  - Expected: Workflow cancelled gracefully, no error

### 6.3 Empty Workspace
- [ ] Open VSCode with no folder
- [ ] Run a workflow
  - Expected: Graceful handling (may show "no context" message)

---

## 7. Regression Checks

- [ ] Dashboard loads without errors
- [ ] Health tab shows metrics
- [ ] Workflow history appears in Dashboard
- [ ] Keyboard shortcuts all work:
  - Cmd+Shift+E M (morning)
  - Cmd+Shift+E S (ship)
  - Cmd+Shift+E F (fix-all)
  - Cmd+Shift+E W (workflows)
  - Cmd+Shift+E D (dashboard)
  - Cmd+Shift+E Q (agent designer)
  - Cmd+Shift+E T (tests)
  - Cmd+Shift+E C (costs)

---

## Sign-Off

| Area | Tested | Pass/Fail | Notes |
|------|--------|-----------|-------|
| Socratic Refinement | | | |
| Pattern Learning | | | |
| Agent Designer | | | |
| Guided Panel | | | |
| Settings | | | |
| Edge Cases | | | |
| Regression | | | |

**Tester:** _______________
**Date:** _______________
**Version:** 1.4.0
