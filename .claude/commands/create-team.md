# Create Custom Agent Team - Socratic Guide

You are helping the user create a custom AI agent team for their project using the Empathy Framework. Use the AskUserQuestion tool to gather requirements through a guided conversation.

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

## Step 5: Cost Preference

Use AskUserQuestion with:
- Question: "What's your cost preference for this team?"
- Header: "Cost"
- Options:
  - "Minimize cost (Recommended)" - Use cheap tier where possible ($0.03-0.10 per run)
  - "Balance cost/quality" - Mix of cheap and capable ($0.10-0.30 per run)
  - "Maximize quality" - Use capable/premium tiers ($0.30-0.60 per run)

## Step 6: Generate the Team Template

After gathering all answers, generate the team specification:

```json
{
  "id": "[goal-based-id]",
  "name": "[Descriptive Team Name]",
  "description": "[Based on goal]",
  "collaboration_pattern": "[Selected pattern]",
  "agents": [
    {
      "role": "[Role 1]",
      "purpose": "[What this agent does]",
      "tier": "[Based on cost preference]",
      "base_template": "generic"
    }
  ],
  "estimated_cost_range": {
    "min": 0.03,
    "max": 0.30
  }
}
```

Then tell the user:
1. Show the generated template in a code block
2. Save it to `.empathy/meta_workflows/templates/[id].json`
3. Explain how to run it: `empathy meta-workflow run [id]`

## Important

- Use AskUserQuestion for EACH step - don't ask multiple questions at once
- Wait for user response before proceeding to next step
- For role selection, use multiSelect: true
- Generate meaningful agent names and purposes based on the goal
