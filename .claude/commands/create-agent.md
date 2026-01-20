# Create Custom Agent - Socratic Guide

You are helping the user create a custom AI agent for the Empathy Framework. Use the AskUserQuestion tool to gather requirements through a guided conversation.

**Cost: $0** - Agents run within Claude Code using your Max subscription.

## Step 1: Understand the Purpose

First, ask the user what they want their agent to do:

Use AskUserQuestion with:

- Question: "What should this agent do?"
- Header: "Purpose"
- Options:
  - "Analyze code" - Review and analyze source code for issues or patterns
  - "Generate content" - Create tests, documentation, or other content
  - "Review & validate" - Check work for quality, security, or correctness
  - "Transform data" - Convert, migrate, or restructure code/data

## Step 2: Determine Specialization

Based on their answer, ask about specific focus:

Use AskUserQuestion with:

- Question: "What specific area should this agent focus on?"
- Header: "Focus Area"
- Options vary by purpose (e.g., for "Analyze code"):
  - "Security vulnerabilities"
  - "Performance issues"
  - "Code quality & style"
  - "Architecture & design"

## Step 3: Select Model Tier

Use AskUserQuestion with:

- Question: "What quality/cost balance do you need?"
- Header: "Model Tier"
- Options:
  - "Haiku (Recommended)" - Fast & efficient, good for simple analysis
  - "Sonnet" - Balanced, good for most development tasks
  - "Opus" - Highest quality, for complex reasoning

## Step 4: Define Success Criteria

Use AskUserQuestion with:

- Question: "How will you measure success?"
- Header: "Success"
- Options:
  - "Issues found & reported" - Agent finds and documents problems
  - "Content generated" - Agent produces requested output
  - "Validation passed" - Agent confirms quality/correctness
  - "Recommendations provided" - Agent suggests improvements

## Step 5: Memory Enhancement (Optional)

Use AskUserQuestion with:

- Question: "Should this agent use project memory?"
- Header: "Memory"
- Options:
  - "No memory (Recommended)" - Stateless execution, simplest setup
  - "Short-term context" - Remember findings within current session
  - "Long-term learning" - Learn patterns across sessions for improvement

If user selects memory options, the generated skill will include:

**Short-term memory features:**

- Agent can reference earlier findings in the same session
- Useful for iterative analysis (analyze → fix → verify cycle)

**Long-term memory features:**

- Store successful patterns: "This fix resolved X type of issue"
- Recall relevant history: "Similar issues found before in Y module"
- Track metrics over time: "Coverage improved from X% to Y%"

## Step 6: Generate the Agent as Claude Code Skill

After gathering all answers, generate a Claude Code skill file:

Create file at `.claude/commands/[agent-name].md`:

```markdown
# [Agent Name]

[Description based on user's purpose and focus]

## Instructions for Claude

When the user invokes /[agent-name], use the Task tool with subagent_type="Explore":

Prompt:
You are a [role] analyzing this codebase.

[Instructions based on purpose]:
- For "Analyze code": Examine src/ for [focus area] issues
- For "Generate content": Create [content type] for the codebase
- For "Review & validate": Check code for [focus area] compliance
- For "Transform data": Convert/migrate code as specified

Success Criteria:
- [Selected criteria from Step 4]

Output a structured report with findings and recommendations.

## Model Recommendation

Use model="[selected tier]" in the Task tool for this agent.

## Cost

**$0** - Runs within Claude Code using your Max subscription.
```

Then tell the user:

1. Show the generated skill file content
2. Save it to `.claude/commands/[agent-name].md`
3. Explain how to run it: `/[agent-name]`
4. Explain how to use it in a team: `/create-team`

## Important

- Use AskUserQuestion for EACH step - don't ask multiple questions at once
- Wait for user response before proceeding to next step
- Keep the conversation focused and efficient
- Generate a descriptive agent name based on their choices
- Always create a .claude/commands/ skill file for $0 execution
