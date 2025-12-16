# Product Hunt Launch Assets - Actionable Specifications

**Purpose:** Detailed specifications for creating Product Hunt launch assets
**Status:** Ready for execution
**Target Launch:** Week 3 (Dec 29 - Jan 4)

---

## 1. Thumbnail Requirements (1270x760px)

### Design Concept: "Memory Changes Everything"

**Visual Theme:**
A split-screen design showing the transformation from "stateless" to "memory-enabled" AI.

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Left Side (40%)              Right Side (60%)              │
│  ┌─────────────────┐         ┌─────────────────────────┐   │
│  │                 │         │                         │   │
│  │   Brain icon    │   →     │   Brain + Database      │   │
│  │   with "?"      │         │   connected nodes       │   │
│  │   (faded/gray)  │         │   (glowing cyan/blue)   │   │
│  │                 │         │                         │   │
│  └─────────────────┘         └─────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           EMPATHY FRAMEWORK                          │   │
│  │   "AI that remembers, predicts, and learns"         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Text/Tagline

**Primary Text (large, centered at bottom):**
```
EMPATHY FRAMEWORK
```

**Tagline (smaller, below logo):**
```
AI that remembers, predicts, and learns
```

**Alternative taglines (if space allows a secondary callout):**
- "10 lines of code to persistent memory"
- "Your AI finally remembers"

### Color Scheme (Brand Colors)

| Element | Color | Hex |
|---------|-------|-----|
| Background | Dark Blue | #1a1a2e |
| Primary Accent | Bright Cyan | #00d4ff |
| Secondary Accent | Electric Blue | #4361ee |
| Success/Positive | Green | #10b981 |
| Text (primary) | White | #ffffff |
| Text (secondary) | Light Gray | #f3f4f6 |
| Faded/Before state | Medium Gray | #6b7280 |

### Design Elements

1. **Left side (before):** Faded brain icon with question mark, gray tones
2. **Right side (after):** Glowing brain connected to database nodes, cyan/blue glow effects
3. **Arrow transition:** Subtle gradient arrow from gray to cyan
4. **Connection lines:** Thin, glowing cyan lines between nodes
5. **Background:** Gradient from #1a1a2e (left) to slightly lighter (right)

### Tool Recommendations

**Primary (Full Design Control):**
- **Figma** - Best for team collaboration and precision
  - Use "Thumbnail" frame at 1270x760px
  - Export as PNG at 2x for retina

**Quick Alternative:**
- **Canva Pro** - Good templates, faster execution
  - Search "Tech product thumbnail" or "SaaS thumbnail"
  - Customize with brand colors

**Icon Resources:**
- Heroicons (brain, database, nodes): https://heroicons.com
- Iconify: https://iconify.design
- Custom: Use AI image generation for brain+database hybrid

### File Specifications

- **Filename:** `empathy-thumbnail-producthunt-1270x760.png`
- **Format:** PNG (no transparency)
- **Dimensions:** Exactly 1270x760px
- **File size:** Under 2MB
- **Color space:** sRGB

---

## 2. Gallery Screenshots (5 Images)

All screenshots should be 1200x800px or 16:9 aspect ratio, with consistent styling.

### Screenshot 1: Hero/Overview

**Purpose:** First impression - show what the framework does

**Content to Capture:**
```
┌─────────────────────────────────────────────────────────────────┐
│  EMPATHY FRAMEWORK                                              │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Your AI finally remembers.                                     │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Persistent │  │ Anticipatory│  │  Multi-     │             │
│  │  Memory     │  │ Intelligence│  │  Agent      │             │
│  │             │  │             │  │             │             │
│  │  Git-based  │  │ 30-90 day   │  │ Human↔AI   │             │
│  │  patterns + │  │ predictions │  │ AI↔AI      │             │
│  │  Redis      │  │             │  │ coordination│             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  $ pip install empathy-framework                                │
│  $ empathy-memory serve                                         │
│  ✓ Memory system ready                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Annotation:**
- Highlight the 3-pillar value props with icons
- Show the 2-command installation

**Caption:** "Persistent AI memory in 2 commands. Git-based patterns, anticipatory predictions, multi-agent coordination."

---

### Screenshot 2: Code Example (10-Line Memory Integration)

**Purpose:** Show how simple it is to add persistent memory

**Terminal/Code to Capture:**
```python
# 10 Lines to Persistent Memory

from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.memory import MemoryConfig

# Configure memory
memory = MemoryConfig(
    short_term="redis://localhost:6379",
    long_term="./patterns/",           # Git-based
    auto_persist=True
)

# Initialize with memory
llm = EmpathyLLM(provider="anthropic", memory=memory)

# Use - memory automatically persists across sessions
response = await llm.interact("Debug this error: TypeError...")
# Next session: AI remembers previous debugging context!
```

**Visual Style:**
- Dark theme terminal (VS Code or iTerm2)
- Syntax highlighting enabled
- Font: JetBrains Mono or Fira Code, 16pt
- Add subtle comment highlighting

**Annotations to Add:**
- Arrow pointing to line 6-8: "Git-based = zero infrastructure"
- Arrow pointing to last comment: "Memory persists across sessions"

**Caption:** "10 lines of code to AI that remembers. Git-based pattern storage requires zero infrastructure."

---

### Screenshot 3: Memory-Enhanced Debugging Wizard in Action

**Purpose:** Show the debugging wizard with historical pattern matching

**Terminal Output to Capture:**
```
$ python examples/debugging_demo.py

╔══════════════════════════════════════════════════════════════════╗
║     MEMORY-ENHANCED DEBUGGING WIZARD                             ║
╚══════════════════════════════════════════════════════════════════╝

Analyzing error: TypeError: Cannot read property 'items' of undefined

🧠 CHECKING HISTORICAL PATTERNS...

📚 HISTORICAL MATCH FOUND (Similarity: 87%)

  Date: 2025-09-15 (3 months ago)
  File: src/components/ProductList.tsx
  Root Cause: API returned null instead of empty array
  Fix Applied: Added default empty array fallback
  Resolution Time: 15 minutes

💡 RECOMMENDED FIX:
  Based on historical pattern, try: data?.items ?? []
  Expected resolution time: ~12 minutes

🔮 ANTICIPATORY INSIGHT:
  Pattern suggests 3 similar locations may have same vulnerability.
  Consider running: empathy scan --pattern null_reference
```

**Annotations to Add:**
- Highlight "HISTORICAL MATCH FOUND" banner with green box
- Circle the "87%" similarity score
- Box around "Resolution Time: 15 minutes" with note: "Team knowledge compounds"

**Caption:** "Debugging wizard finds similar bugs from 3 months ago. Team knowledge compounds across sessions."

---

### Screenshot 4: Historical Bug Pattern Matching

**Purpose:** Deep dive into the pattern storage and matching capability

**Content to Capture:**
```
$ empathy patterns list --type bug

📊 BUG PATTERN LIBRARY (19 patterns stored)
═══════════════════════════════════════════

Pattern Type       | Count | Last Match    | Avg Resolution
───────────────────┼───────┼───────────────┼───────────────
async_timing       │   3   │ 2 days ago    │ 10 min
import_error       │   3   │ 5 days ago    │ 3 min
null_reference     │  10   │ today         │ 15 min
type_mismatch      │   2   │ 1 week ago    │ 12 min

Top Pattern: null_reference (10 occurrences)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Most Recent: bug_20251212_3c5b9951 (resolved)
  Root Cause: API returns undefined instead of empty array
  Fix Applied: Added optional chaining and default array fallback
  Resolution Time: 15 min

Pattern Evolution:
  Sep 2025: 3 bugs  →  Oct 2025: 4 bugs  →  Nov 2025: 2 bugs  →  Dec 2025: 1 bug
  ✓ Trend: DECREASING (team is learning!)

💾 Storage: ./patterns/debugging/ (git-tracked, version-controlled)
```

**Annotations to Add:**
- Highlight "Trend: DECREASING (team is learning!)" with green box
- Arrow pointing to storage line: "Zero infrastructure - just git"

**Caption:** "Bug patterns stored and tracked over time. Watch trends improve as team knowledge compounds."

---

### Screenshot 5: Before/After Comparison

**Purpose:** Visual comparison showing the transformation

**Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    BEFORE vs AFTER                               │
├────────────────────────────┬────────────────────────────────────┤
│                            │                                    │
│  WITHOUT MEMORY            │  WITH EMPATHY FRAMEWORK            │
│  ─────────────────         │  ───────────────────────           │
│                            │                                    │
│  ❌ Start from zero        │  ✅ "Similar bug fixed 3mo ago"   │
│     every session          │                                    │
│                            │                                    │
│  ❌ Re-explain context     │  ✅ Already knows your codebase   │
│     every time             │                                    │
│                            │                                    │
│  ❌ Same alerts            │  ✅ Learns team decisions          │
│     every scan             │                                    │
│                            │                                    │
│  ❌ React to problems      │  ✅ Predict 30-90 days ahead      │
│                            │                                    │
│  ❌ Knowledge lost         │  ✅ Team knowledge compounds      │
│     when devs leave        │                                    │
│                            │                                    │
├────────────────────────────┴────────────────────────────────────┤
│                                                                 │
│  pip install empathy-framework && empathy-memory serve          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Visual Style:**
- Left side: Red/gray tones (X marks)
- Right side: Green/cyan tones (checkmarks)
- Clear visual separation
- Installation command at bottom

**Caption:** "Memory changes everything. Stop re-teaching your AI, start building on what you learned."

---

### Screenshot Styling Guide (All 5)

**Terminal Settings:**
- Theme: One Dark or Dracula
- Font: JetBrains Mono, 16pt
- Size: 100x30 characters minimum
- Prompt: Simple `$ ` prefix

**Annotation Style:**
- Highlight color: #00d4ff (cyan) or #10b981 (green)
- Border radius: 8px
- Arrow style: Thick, curved
- Text callouts: White text on dark background

**File Naming:**
```
empathy-gallery-01-hero-1200x800.png
empathy-gallery-02-code-1200x800.png
empathy-gallery-03-debugging-1200x800.png
empathy-gallery-04-patterns-1200x800.png
empathy-gallery-05-comparison-1200x800.png
```

---

## 3. First Comment Template (Maker's Comment)

**Title:** Hey Product Hunt! Here's why I built this.

**Comment:**

```
I've been building AI tools for years. The biggest frustration? Every session starts from zero.

Your AI doesn't remember the architecture decisions from yesterday. It doesn't know your team's coding patterns. It can't coordinate with other agents. It just waits for problems instead of predicting them.

So I built the Empathy Framework to fix that.

**The 5 problems we solve:**

1. **Stateless** → Dual-layer memory (git patterns + optional Redis)
2. **Cloud-dependent** → Local-first. Nothing leaves your infrastructure
3. **Isolated** → Multi-agent orchestration (Human↔AI, AI↔AI)
4. **Reactive** → Anticipatory intelligence predicts 30-90 days ahead
5. **Expensive** → Persistent memory = no more re-teaching context

**Try it now (2 commands):**

```bash
pip install empathy-framework
empathy-memory serve
```

**What's included:**
- Memory-enhanced debugging wizard (finds similar bugs from months ago)
- 30+ production wizards (security, performance, testing, docs)
- Code health assistant with auto-fix
- Fair Source licensed: Free for teams ≤5

**I'd love your feedback on:**
1. What memory features would help your team most?
2. How should this integrate with your workflow?
3. What wizards should we build next?

Happy to answer any questions!
```

---

## 4. Tagline Options (Max 60 Characters)

| # | Tagline | Chars | Focus |
|---|---------|-------|-------|
| 1 | **AI that remembers, predicts, and learns across sessions** | 56 | Complete value prop |
| 2 | **Persistent memory for AI tools. Your AI finally remembers.** | 59 | Memory focus |
| 3 | **10 lines of code to AI that never forgets** | 44 | Simplicity |
| 4 | **AI memory that compounds team knowledge over time** | 50 | Team value |
| 5 | **Stop re-teaching your AI. Start building on what you learned.** | 60 | Pain point |

**Recommended:** Option 1 or Option 5

Option 1 covers all three pillars (memory, prediction, learning) while Option 5 directly addresses the pain point.

---

## 5. Short Description (Max 260 Characters)

**Option A (256 chars):**
```
AI tools forget everything between sessions. Empathy Framework fixes that with persistent memory (git-based patterns + Redis), anticipatory intelligence (30-90 day predictions), and multi-agent coordination. 2 commands to AI that finally remembers.
```

**Option B (258 chars):**
```
Your AI starts from zero every session. Empathy adds persistent memory that compounds team knowledge, predicts problems 30-90 days ahead, and coordinates multiple agents. Git-based patterns require zero infrastructure. Fair Source: free for small teams.
```

**Option C (Focused - 245 chars):**
```
Persistent AI memory in 10 lines of code. Debug a bug once, your AI remembers it forever. Predict tech debt trends. Learn security decisions. Git-based pattern storage requires zero infrastructure. Works with Claude, GPT-4, Ollama. Free for teams ≤5.
```

**Recommended:** Option A (covers all value props concisely)

---

## 6. Asset Creation Checklist

### Pre-Production
- [ ] Set up Figma/Canva workspace with brand colors
- [ ] Download icon assets (Heroicons, custom brain+database)
- [ ] Configure terminal for screenshots (theme, font, size)
- [ ] Run demos to capture live output

### Thumbnail
- [ ] Create 1270x760 design
- [ ] Add logo and tagline
- [ ] Export PNG at full resolution
- [ ] Test display at small sizes (thumbnail preview)

### Gallery Screenshots
- [ ] Screenshot 1: Hero/Overview (create or composite)
- [ ] Screenshot 2: Code example (capture from editor)
- [ ] Screenshot 3: Debugging wizard output (run demo, capture)
- [ ] Screenshot 4: Pattern library view (run command, capture)
- [ ] Screenshot 5: Before/After comparison (design)
- [ ] Add annotations to each screenshot
- [ ] Optimize file sizes (<500KB each)

### Copy
- [ ] Finalize tagline selection
- [ ] Finalize description selection
- [ ] Review first comment for character limits
- [ ] Prepare response templates for common questions

### Quality Check
- [ ] All images display correctly on dark/light backgrounds
- [ ] Text is readable at small sizes
- [ ] Brand colors are consistent
- [ ] Links in copy are correct
- [ ] No PII or sensitive data in screenshots

---

## 7. Timeline

| Day | Task | Owner |
|-----|------|-------|
| D-7 | Thumbnail design complete | Design |
| D-5 | All 5 gallery screenshots captured | Marketing |
| D-4 | Annotations added, files optimized | Design |
| D-3 | Copy finalized and reviewed | Marketing |
| D-2 | All assets uploaded to Product Hunt draft | Marketing |
| D-1 | Final review, test all links | All |
| D-0 | Launch! Post first comment immediately | Founder |

---

## 8. Additional Resources

**Existing Marketing Content:**
- `/docs/marketing/PRODUCT_HUNT.md` - Full launch details
- `/docs/marketing/VISUAL_ASSET_SPECS.md` - Brand guidelines
- `/docs/marketing/SCREENSHOT_GUIDE.md` - Screenshot best practices
- `/docs/marketing/THREE_THINGS_NOT_POSSIBLE_BEFORE.md` - Key value props

**Demo Commands for Screenshots:**
```bash
# Debugging demo output
python examples/debugging_demo.py

# Pattern library view
empathy patterns list --type bug

# Health check
empathy health --deep
```

**Asset Storage:**
All final assets should be saved to:
```
docs/marketing/assets/
├── product-hunt/
│   ├── empathy-thumbnail-producthunt-1270x760.png
│   ├── empathy-gallery-01-hero-1200x800.png
│   ├── empathy-gallery-02-code-1200x800.png
│   ├── empathy-gallery-03-debugging-1200x800.png
│   ├── empathy-gallery-04-patterns-1200x800.png
│   └── empathy-gallery-05-comparison-1200x800.png
└── originals/
    └── [pre-annotation versions]
```

---

**Document Version:** 1.0
**Last Updated:** December 16, 2025
**Author:** Marketing Team
