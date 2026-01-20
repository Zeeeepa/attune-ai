# Create Custom Agent Team - Socratic Guide

You are helping the user create a custom AI agent team for their project using the Empathy Framework. Use the AskUserQuestion tool to gather requirements through a guided conversation.

**Cost: $0** - Teams run within Claude Code using your Max subscription.

## Step 1: Understand the Team's Mission

Use AskUserQuestion with:

- Question: "What is the team's overall goal?"
- Header: "Team Goal"
- Options:
  - "Code quality pipeline" - Review, test, and improve code quality
  - "Release preparation" - Prepare code for production deployment
  - "Documentation sync" - Keep docs aligned with code
  - "Security audit" - Comprehensive security analysis

## Step 2: Determine Team Size

Use AskUserQuestion with:

- Question: "How many agents should be on this team?"
- Header: "Team Size"
- Options:
  - "2 agents (Recommended)" - Simple workflow: analyze then act
  - "3 agents" - Standard: analyze, execute, validate
  - "4 agents" - Comprehensive: analyze, execute, validate, report
  - "5 agents" - Full pipeline with multiple specialists

## Step 3: Define Collaboration Pattern

Use AskUserQuestion with:

- Question: "How should agents work together?"
- Header: "Collaboration"
- Options:
  - "Sequential (Recommended)" - Each agent waits for the previous one
  - "Parallel then merge" - Run analysis in parallel, then synthesize
  - "Pipeline" - Output of each feeds into the next

## Step 4: Select Agent Roles

Based on team size and goal, present role options. For a 3-agent team:

Use AskUserQuestion with multiSelect: true:

- Question: "Which roles should your team have? (Select 3)"
- Header: "Roles"
- Options:
  - "Analyst" - Examines code/docs and identifies issues
  - "Generator" - Creates content (tests, docs, fixes)
  - "Reviewer" - Checks quality and correctness
  - "Validator" - Verifies results meet criteria

## Step 5: Model Selection

Use AskUserQuestion with:

- Question: "What model quality do you need?"
- Header: "Models"
- Options:
  - "Haiku (Recommended)" - Fast & efficient for most agents
  - "Mix (Haiku + Sonnet)" - Haiku for analysis, Sonnet for complex tasks
  - "Sonnet only" - Higher quality for all agents
  - "Opus for critical" - Use Opus for the most important agent

## Step 6: Memory Enhancement (Optional)

Use AskUserQuestion with:

- Question: "Should this team use project memory?"
- Header: "Memory"
- Options:
  - "No memory (Recommended)" - Stateless execution, simplest setup
  - "Short-term only" - Share context between agents in same session
  - "Long-term learning" - Persist patterns across sessions for improvement
  - "Full memory" - Both short-term context and long-term learning

If user selects memory options, the generated skill will include:

**Short-term memory features:**
- Agents can read context from previous agent results
- Session-scoped data sharing via `/memory` command
- Useful for multi-step workflows where later agents need earlier findings

**Long-term memory features:**
- Store successful patterns: "This security fix resolved X issue"
- Learn from execution history: "Last 5 runs found issues in Y module"
- Recall relevant patterns: "Similar issues were found before in Z"

## Step 7: Generate the Team as Claude Code Skill

After gathering all answers, generate a Claude Code skill file:

Create file at `.claude/commands/[team-name].md`:

```markdown
# [Team Name]

[Description based on team goal]

## What This Does

Runs [N] specialized agents in [pattern] order:

- **[Role 1]** - [Purpose]
- **[Role 2]** - [Purpose]
- **[Role N]** - [Purpose]

## Usage

/[team-name]

## Instructions for Claude

When the user invokes /[team-name], execute these steps using the Task tool.
This runs entirely within Claude Code using the user's Max subscription ($0 cost).

### Step 1: [Role 1]

Use the Task tool with subagent_type="Explore"[, model="haiku"]:

[Prompt for agent 1 based on role and goal]

### Step 2: [Role 2]

Use the Task tool with subagent_type="Explore"[, model="sonnet"]:

[Prompt for agent 2 based on role and goal]

### Step N: Synthesize Results

Combine outputs from all agents into a final report:

## Report Format

[Structured output format based on team goal]

## Cost

**$0** - Runs entirely within Claude Code using your Max subscription.

## Memory Integration (if enabled)

[Include this section only if user selected memory options]

### Short-term Context (if selected)

Each agent step should pass its key findings to the next:

```
### Step N Results Summary
- Key finding 1: [extracted from output]
- Key finding 2: [extracted from output]

This context is available to Step N+1.
```

### Long-term Learning (if selected)

After successful completion, store learned patterns:

```
Use the Bash tool to store this pattern:
empathy memory store --type "workflow_success" --content "[summary of what worked]"
```

Before execution, recall relevant patterns:

```
Use the Bash tool to check for relevant history:
empathy memory search "[team goal keywords]"
```

## Alternative: API Mode

To use API-based execution instead:

empathy meta-workflow run [team-id] --real --use-defaults
```

Then tell the user:

1. Show the generated skill file content
2. Save it to `.claude/commands/[team-name].md`
3. Explain how to run it: `/[team-name]`
4. Note: Also saved as template for API mode (optional)

## Important

- Use AskUserQuestion for EACH step - don't ask multiple questions at once
- Wait for user response before proceeding to next step
- For role selection, use multiSelect: true
- Generate meaningful agent names and purposes based on the goal
- Always create a .claude/commands/ skill file for $0 execution
- Sequential pattern: Run Task tools one at a time
- Parallel pattern: Run multiple Task tools in parallel, then synthesize
