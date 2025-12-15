# Launch Prep Research

**Created:** December 15, 2025 (Day 2)
**Purpose:** Research to support Week 1-2 launch activities

---

## Redis DevRel Contacts

Found via LinkedIn and Redis blog research.

### Primary Targets (DevRel Team)

| Name | Role | LinkedIn | Notes |
|------|------|----------|-------|
| **Ricardo Ferreira** | Lead Developer Advocate | [linkedin.com/in/riferrei](https://linkedin.com/in/riferrei) | Leads DevRel team, highly technical |
| **Raphael De Lio** | Developer Advocate | Search on LinkedIn | 1 year at Redis (as of Nov 2025), writes Medium content |
| **Guy Royse** | Senior Developer Advocate | Search on LinkedIn | Does live coding, AI/Vector Search focus |

### Engagement Strategy

1. **Follow them on Twitter/LinkedIn first**
2. **Engage with their content** (meaningful comments, not spam)
3. **Share our Redis blog and tag them** (after blog is published)
4. **DM after establishing presence** (Week 2-3)

### Redis Programs

- **Redis Insiders Program** - Community advocates program
  - URL: https://redis.io/blog/redis-insiders-program/
  - Could apply after establishing relationship

- **Redis Partners** - Technology partnership
  - URL: https://redis.com/partners/
  - Apply Week 2 (see REDIS_PARTNERSHIP_PLAN.md)

---

## Competitive Landscape

Understanding the competition helps us position and respond to questions.

### Direct Competitors (AI Memory/Agent Frameworks)

| Framework | Focus | Our Differentiator |
|-----------|-------|-------------------|
| **CrewAI** | Role-based multi-agent | We add persistent memory + predictions |
| **Langroid** | Lightweight agents | We're also lightweight BUT with long-term memory |
| **AutoGen** | Microsoft's agent framework | We're local-first, not cloud-dependent |
| **LangChain** | LLM orchestration | We're simpler, memory-focused vs their "bloated" reputation |
| **Pieces** | Developer context/memory | They're IDE-focused; we're framework/API |

### Common Criticisms of AI Frameworks (to address)

From Reddit research:
1. **"Bloated/complex documentation"** - Our response: Simple 2-command start
2. **"Just use vanilla Python"** - Our response: You can! We're a thin layer
3. **"AI tools slow me down"** - Our response: Memory eliminates re-explanation overhead
4. **"Trust issues with AI code"** - Our response: Pattern-based review catches historical bugs

### Key Stats to Reference

- DORA 2024: "Delivery stability decreases 7.2% with AI adoption" (we address this with memory)
- Stack Overflow 2024: "AI usage up to 76%, but trust stuck at 43%" (we build trust via patterns)
- CodeRide: "65% of developers struggle with context loss" (our core problem statement)

---

## Reddit Engagement Targets

### Subreddits to Monitor

| Subreddit | Subscribers | Strategy |
|-----------|-------------|----------|
| r/programming | 6M+ | Technical posts, Show HN style |
| r/Python | 1.3M+ | Framework comparisons, how-to |
| r/MachineLearning | 3M+ | Architecture discussions |
| r/LocalLLaMA | 500K+ | Local-first angle |
| r/redis | 30K+ | Redis blog cross-post |
| r/devops | 300K+ | Enterprise/infrastructure angle |

### Thread Topics to Find & Engage

Search for recent threads about:
1. "AI coding assistant memory" / "context window"
2. "LLM agent frameworks comparison"
3. "Multi-agent AI" / "agent orchestration"
4. "AI tools for developers 2025"
5. "Redis use cases" / "Redis AI"

### Engagement Rules

1. **Be helpful first** - Answer questions, don't pitch
2. **Reference Empathy only when relevant** - "We solved this with X approach"
3. **Share code/examples** - Technical communities love specifics
4. **Don't self-promote in first comment** - Build credibility first
5. **Link to blog/docs, not repo** - Adds value, not just promotion

---

## Expanded Response Templates

### General Questions

**Q: What makes this different from [CrewAI/LangChain/AutoGen]?**
```
Those are great frameworks for orchestration, but they're stateless—every session starts fresh. Empathy adds:

1. Persistent memory (git-based patterns that survive across sessions)
2. Anticipatory intelligence (30-90 day predictions based on pattern analysis)
3. Pattern-based code review (catches bugs before they happen based on team history)

Think of it as: [Framework X] + long-term memory + predictions.

You can actually use Empathy alongside LangChain/CrewAI—we're the memory layer.
```

**Q: Why would I use this instead of just using GPT/Claude directly?**
```
Direct LLM usage works great for one-off tasks. But for ongoing development:

- GPT/Claude forget everything between sessions (you re-explain context daily)
- They can't coordinate (multiple agents working together)
- They're reactive (wait for problems vs preventing them)

Empathy sits on top of any LLM (including GPT/Claude) and adds:
- Memory that persists across sessions
- Multi-agent coordination
- Pattern-based predictions

Two commands: `pip install empathy-framework && empathy-memory serve`
```

**Q: Is this just another LangChain wrapper?**
```
No, we don't use LangChain at all. Empathy is built from scratch with a different philosophy:

- LangChain: Tool orchestration, complex abstractions
- Empathy: Memory + coordination + predictions, minimal abstractions

We're ~3K lines of core code vs LangChain's 100K+. You can read the whole codebase in an afternoon.

That said, you CAN use Empathy with LangChain if you want—we're the memory layer that any framework can use.
```

### Technical Questions

**Q: How does the memory actually work?**
```
Dual-layer architecture:

Layer 1: Git-based patterns (long-term)
- Bug patterns, security decisions, team learnings
- Stored in your repo as JSON files
- Version-controlled, survives forever
- Zero infrastructure needed

Layer 2: Redis (real-time, optional)
- Session context, agent coordination
- Sub-millisecond queries
- Auto-expires, no cleanup needed

Individual devs use just Layer 1 (git). Teams add Layer 2 (Redis) for coordination.
```

**Q: What's the performance overhead?**
```
Redis operations: <1ms
- Session read: 0.3ms
- Agent coordination: 0.4ms
- Pub/sub: 0.1ms

LLM calls: 100-2000ms

Memory adds <1% overhead. The LLM call dominates.
```

**Q: Does this work offline?**
```
Yes! The git-based pattern layer works completely offline.

Redis layer requires network (for multi-agent coordination), but gracefully degrades—if Redis is unavailable, you get local-only mode.

Students can use the full memory system with just git, no servers needed.
```

### Skepticism Responses

**Q: Another AI framework? Why should I care?**
```
Fair question. Here's what's actually different:

Most frameworks focus on *how* to call LLMs. We focus on *what* they remember.

The result:
- 78.7% reduction in security scan noise (patterns learn your decisions)
- Pattern-based review catches bugs before commit (based on your team's history)
- No more "let me re-explain our architecture" every morning

Two commands to try: `pip install empathy-framework && empathy health`

If it's not useful in 5 minutes, it's not for you.
```

**Q: "Anticipatory intelligence" sounds like marketing BS**
```
Fair point—let me be specific.

It's pattern analysis, not magic:
1. We track tech debt over time (not just "you have 50 TODOs")
2. We calculate trajectory ("at this rate, 150 TODOs in 90 days")
3. We identify acceleration points ("debt adding faster since the auth refactor")

It's the same math you'd do manually, automated and tracked over time.

Code: `python examples/website_examples/02_tech_debt_trajectory.py`
```

**Q: Why Fair Source instead of MIT/Apache?**
```
Honest answer: sustainability.

MIT/Apache is great for adoption but makes commercial sustainability hard. Fair Source gives us:

- Free for students, educators, small teams (<5 employees)
- Affordable commercial license ($99/dev/year)
- Auto-converts to Apache 2.0 in 2029 (4 years)

You get everything MIT gives you for personal/small team use. Commercial users fund development. Everyone gets full open source in 2029.
```

### Enterprise Questions

**Q: Is this production-ready?**
```
Yes, with caveats:

Production-ready:
- Core memory system (battle-tested)
- Pattern storage/retrieval
- Security controls (PII scrubbing, secrets detection)
- Audit logging

Still maturing:
- Some advanced wizards
- IDE integrations
- CI/CD examples

We're at v2.2.4 with active development. Production users exist, but you should evaluate for your specific use case.
```

**Q: What about compliance (HIPAA/GDPR/SOC2)?**
```
Built-in:

- PII scrubbing (auto-detected and removed before storage)
- Secrets detection (API keys, passwords blocked)
- Audit logging (every memory operation logged)
- Healthcare patterns (SBAR, SOAP notes for HIPAA)
- Classification system (PUBLIC/INTERNAL/SENSITIVE)
- Encryption for sensitive patterns (AES-256-GCM)

We use this in healthcare contexts. The compliance patterns are tested.
```

**Q: Pricing for enterprise?**
```
Fair Source 0.9 license:

- Free: Students, educators, teams ≤5 employees
- Commercial: $99/developer/year
- Enterprise: Contact for volume pricing

No feature gates—everyone gets the same code. The license is the only difference.
```

---

## Hacker News Specific Tips

### What Works on HN

1. **Lead with the problem, not the solution**
2. **Be technical** - Show architecture, not just features
3. **Ask for feedback** - HN loves giving opinions
4. **Respond to every comment** - Shows engagement
5. **Don't be defensive** - Thank critics, learn from feedback

### What to Avoid

1. **Marketing speak** - "Revolutionary", "Game-changing", etc.
2. **Overpromising** - Be honest about limitations
3. **Astroturfing** - Don't have friends upvote/comment
4. **Ignoring criticism** - Engage respectfully

### Best Post Times

- Tuesday-Thursday, 9-10 AM PST
- Avoid weekends and holidays

---

## Product Hunt Specific Tips

### What Works on PH

1. **Strong visual assets** - Thumbnail, screenshots, video
2. **First comment immediately** - Tell your story
3. **Respond to every comment** - All day
4. **Share on social with PH link** - Cross-promotion
5. **Thank supporters** - Builds community

### Timing

- Post at 12:01 AM PST (PH reset time)
- Clear calendar for launch day
- Have response templates ready

---

## Action Items from Research

### Immediate (Today)

- [x] Document Redis DevRel contacts
- [x] Create expanded response templates
- [x] Research competitive landscape

### This Week

- [ ] Follow Redis DevRel on Twitter/LinkedIn
- [ ] Find 5 Reddit threads to engage with (search manually)
- [ ] Prepare Product Hunt visuals spec
- [ ] Draft HN Show HN for Day 8 soft launch

### Before Launch

- [ ] Test all response templates with team
- [ ] Prepare "thank you" messages
- [ ] Set up social monitoring
- [ ] Clear calendar for launch days

---

**Sources:**
- [Ricardo Ferreira - LinkedIn](https://linkedin.com/in/riferrei/)
- [Raphael De Lio - Redis DevRel Reflection](https://medium.com/redis-with-raphael-de-lio/reflection-on-my-first-year-as-a-developer-advocate-at-redis-8087ae4c2132)
- [Redis Insiders Program](https://redis.io/blog/redis-insiders-program/)
- [AI Memory Context Article](https://coderide.ai/blog/eliminate-ai-context-reset/)
- [LLM Orchestration Frameworks](https://www.zenml.io/blog/best-llm-orchestration-frameworks)
- [Multi-Agent AI Frameworks](https://getstream.io/blog/multiagent-ai-frameworks/)
