# Create Custom Agent - Socratic Guide

You are helping the user create a custom AI agent for the Empathy Framework. Use the AskUserQuestion tool to gather requirements through a guided conversation.

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
  - "Cheap (Recommended)" - Fast & low-cost ($0.001-0.01), good for simple analysis
  - "Capable" - Balanced ($0.01-0.05), good for most development tasks
  - "Premium" - Highest quality ($0.05-0.20), for complex reasoning

## Step 4: Define Success Criteria

Use AskUserQuestion with:
- Question: "How will you measure success?"
- Header: "Success"
- Options:
  - "Issues found & reported" - Agent finds and documents problems
  - "Content generated" - Agent produces requested output
  - "Validation passed" - Agent confirms quality/correctness
  - "Recommendations provided" - Agent suggests improvements

## Step 5: Generate the Agent Spec

After gathering all answers, generate the agent specification:

```json
{
  "name": "[Generated from purpose + focus]",
  "role": "[Description based on answers]",
  "tier": "[Selected tier]",
  "base_template": "generic",
  "success_criteria": "[Selected criteria]",
  "tools": []
}
```

Then tell the user:
1. Show the generated spec in a code block
2. Offer to save it: `empathy meta-workflow create-agent -q --name "X" --role "Y" --tier "Z" -o agent-spec.json`
3. Explain how to use it in a team: `empathy meta-workflow create-team`

## Important

- Use AskUserQuestion for EACH step - don't ask multiple questions at once
- Wait for user response before proceeding to next step
- Keep the conversation focused and efficient
- Generate a descriptive agent name based on their choices
