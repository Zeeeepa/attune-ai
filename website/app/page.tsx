import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import GitHubStarsBadge from '@/components/GitHubStarsBadge';
import TestsBadge from '@/components/TestsBadge';

const features = [
  {
    icon: '⚡',
    title: '14 Integrated Workflows',
    description: 'Research, code review, debugging, refactoring, test generation, documentation, security scanning, performance optimization, and 4 new meta-workflows for release prep, test coverage boost, test maintenance, and documentation management.',
    link: '/workflows',
  },
  {
    icon: '🤖',
    title: '7 Agent Templates + 6 Composition Patterns',
    description: 'Pre-built agents for test coverage, security audits, code quality, documentation, performance, architecture, and refactoring. Requires Claude Code for agent creation and composition.',
    link: '/framework-docs/',
  },
  {
    icon: '🎛️',
    title: 'VSCode Dashboard',
    description: 'Real-time health scores, cost tracking, workflow monitoring, and quick actions. See your AI collaboration at a glance.',
    link: '/framework-docs/',
  },
  {
    icon: '🧠',
    title: 'Long-Term Memory',
    description: 'Your AI remembers patterns, decisions, and context across sessions. No more repeating yourself.',
    link: '/framework-docs/',
  },
  {
    icon: '🔌',
    title: 'Multi-Provider Support',
    description: 'Core workflows work with Anthropic, OpenAI, Gemini, and Ollama. Agent/team creation requires Claude Code.',
    link: '/framework-docs/',
  },
  {
    icon: '🔒',
    title: 'Enterprise Security',
    description: 'Built-in PII scrubbing, secrets detection, and audit logging. SOC2 and HIPAA-ready.',
    link: '/framework-docs/',
  },
  {
    icon: '🧙',
    title: '10 Smart Wizards',
    description: 'Security audit, code review, bug prediction, performance analysis, refactoring, test generation, documentation, dependency checks, release prep, and research.',
    link: '/wizards',
  },
];

const codeExample = `from empathy_os.orchestration import MetaOrchestrator

# Let the framework compose the right agent team automatically
orchestrator = MetaOrchestrator()
plan = orchestrator.analyze_and_compose(
    task="Boost test coverage to 90%",
    context={"current_coverage": 75, "focus": "auth module"}
)

print(f"Strategy: {plan.strategy.value}")      # sequential
print(f"Agents: {[a.role for a in plan.agents]}")  # [Analyzer, Generator, Validator]
print(f"Estimated cost: \${plan.estimated_cost:.2f}")

# Execute with progressive tier escalation (CHEAP → CAPABLE → PREMIUM)
result = await plan.execute()
print(f"Tests generated: {result.tests_created}")
print(f"Actual cost: \${result.actual_cost:.2f}")`;


export default function Home() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="relative overflow-hidden py-20 sm:py-28" aria-label="Hero">
          <div className="absolute inset-0" aria-hidden="true">
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary)] via-transparent to-[var(--secondary)] opacity-5" />
          </div>
          <div className="container relative">
            <div className="max-w-4xl mx-auto text-center animate-fade-in">
              {/* Credibility Badges */}
              <div className="flex flex-wrap gap-3 justify-center mb-8">
                <GitHubStarsBadge />
                <TestsBadge />
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[var(--border)] text-sm font-medium">
                  <span className="w-2 h-2 rounded-full bg-green-500"></span>
                  v4.4.0 Stable
                </span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
                Power Tools for{' '}
                <span className="text-gradient">Claude Code</span>
              </h1>
              <p className="text-xl text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto">
                Enhanced workflows, agent composition, and intelligent orchestration for VS Code power users.
                14 workflows, 10 smart wizards, and dynamic agent teams that compose themselves automatically.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link
                  href="/framework-docs/tutorials/quickstart/"
                  className="btn btn-primary text-lg px-8 py-4"
                  aria-label="Get started with the framework"
                >
                  pip install empathy-framework
                </Link>
                <Link
                  href="/workflows"
                  className="btn btn-outline text-lg px-8 py-4"
                  aria-label="Explore Workflows"
                >
                  Explore Workflows
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Code Example */}
        <section className="py-16 bg-[var(--border)] bg-opacity-30" aria-label="Code example">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold text-center mb-8">
                Get Started in 5 Lines of Code
              </h2>
              <div className="bg-[#1e1e1e] rounded-xl overflow-hidden shadow-2xl">
                <div className="flex items-center gap-2 px-4 py-3 bg-[#2d2d2d] border-b border-[#3d3d3d]">
                  <div className="w-3 h-3 rounded-full bg-[#ff5f56]"></div>
                  <div className="w-3 h-3 rounded-full bg-[#ffbd2e]"></div>
                  <div className="w-3 h-3 rounded-full bg-[#27ca40]"></div>
                  <span className="ml-2 text-sm text-gray-400">main.py</span>
                </div>
                <pre className="p-6 overflow-x-auto text-sm">
                  <code className="text-gray-300">{codeExample}</code>
                </pre>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className="py-20" aria-label="Features">
          <div className="container">
            <h2 className="text-3xl sm:text-4xl font-bold text-center mb-4">
              Power User Features
            </h2>
            <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
              Advanced capabilities for developers who want more from Claude Code.
            </p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
              {features.map((feature) => (
                <Link
                  key={feature.title}
                  href={feature.link}
                  className="group bg-[var(--background)] p-6 rounded-xl border-2 border-[var(--border)] hover:border-[var(--primary)] hover:shadow-lg transition-all"
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-bold mb-2 group-hover:text-[var(--primary)] transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-[var(--text-secondary)]">
                    {feature.description}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        </section>


        {/* Case Study Teaser */}
        <section className="py-20" aria-label="Case study">
          <div className="container">
            <div className="max-w-4xl mx-auto bg-gradient-to-r from-[var(--primary)] to-[var(--secondary)] rounded-2xl p-8 md:p-12 text-white">
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="flex-1">
                  <p className="text-sm font-medium opacity-80 mb-2">CASE STUDY</p>
                  <h3 className="text-2xl md:text-3xl font-bold mb-4">
                    Healthcare AI in Production
                  </h3>
                  <p className="opacity-90 mb-6">
                    See how we built 14+ HIPAA-compliant clinical AI tools using Empathy Framework,
                    including automated SBAR reports and diagnostic assistance.
                  </p>
                  <a
                    href="https://healthcare.smartaimemory.com/static/dashboard.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 bg-white text-[var(--primary)] px-6 py-3 rounded-lg font-medium hover:bg-opacity-90 transition-colors"
                  >
                    View Live Demo
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                  </a>
                </div>
                <div className="flex-shrink-0">
                  <div className="w-32 h-32 md:w-40 md:h-40 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center">
                    <span className="text-6xl md:text-7xl">🏥</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30" aria-label="Call to action">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Ready to Level Up?
              </h2>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                Join power users enhancing their Claude Code workflow.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/framework-docs/tutorials/quickstart/"
                  className="btn btn-primary text-lg px-8 py-4"
                >
                  Read the Docs
                </Link>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline text-lg px-8 py-4"
                >
                  Star on GitHub
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
