import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import { generateMetadata, generateStructuredData } from '@/lib/metadata';

interface FAQItem {
  question: string;
  answer: string | ReactNode;
  answerText?: string; // Plain text version for structured data
}

interface FAQCategory {
  category: string;
  questions: FAQItem[];
}

const faqData: FAQCategory[] = [
  {
    category: 'General',
    questions: [
      {
        question: 'What is Empathy?',
        answer: 'Empathy is a production-ready 5-level maturity model for AI-human collaboration. It progresses from reactive responses (Level 1) to Level 4 Anticipatory Intelligence that predicts problems before they happen. It includes 10 smart wizards and 14 integrated workflows for software development.',
      },
      {
        question: 'What are the 5 levels of AI empathy?',
        answer: 'Level 1: Reactive - Responds only when asked. Level 2: Guided - Asks clarifying questions. Level 3: Proactive - Notices patterns and offers improvements. Level 4: Anticipatory - Predicts future problems before they happen. Level 5: Transformative - Reshapes workflows to prevent entire classes of problems.',
      },
      {
        question: 'What is Long-Term Memory?',
        answer: 'Long-Term Memory is the built-in pattern storage system in Empathy. It enables AI to remember context, decisions, and patterns across sessions, creating true continuity in your AI-human collaboration and enabling Level 5 Transformative Intelligence.',
      },
    ],
  },
  {
    category: 'Licensing & Pricing',
    questions: [
      {
        question: 'How much does Empathy cost?',
        answer: 'Empathy Framework is completely free and open source under the Apache License 2.0. Use it in personal projects, startups, or large enterprises at no cost. No license keys, no restrictions, no hidden fees.',
      },
      {
        question: 'What is the Apache 2.0 License?',
        answer: 'Apache 2.0 is a permissive open source license approved by the OSI. It allows you to use, modify, distribute, and sell products built with Empathy Framework. It includes patent protection and is approved by most enterprise legal teams.',
      },
      {
        question: 'Can I use Empathy for commercial projects?',
        answer: 'Yes! Apache 2.0 explicitly permits commercial use. Build and sell products using Empathy Framework without any licensing fees or restrictions.',
      },
    ],
  },
  {
    category: 'Technical',
    questions: [
      {
        question: 'Which LLM providers are supported?',
        answer: 'Core workflows support multiple LLM providers including Anthropic Claude, OpenAI GPT-4, Google Gemini, and local models via Ollama. Note: Agent and team creation features (Socratic agent builder, dynamic composition) require Anthropic Claude Code specifically.',
      },
      {
        question: 'What are wizards?',
        answer: 'Wizards are specialized AI agents in Empathy that anticipate needs and predict problems in specific domains. The framework includes 10 smart wizards: security audit, code review, bug prediction, performance analysis, refactoring, test generation, documentation, dependency checks, release prep, and research.',
      },
      {
        question: 'How is the framework tested?',
        answer: 'Empathy has 11,000+ comprehensive tests covering unit tests, integration tests, and cross-platform compatibility. Core modules are rigorously tested for security, memory systems, orchestration patterns, and meta-workflow functionality.',
      },
      {
        question: 'What platforms are supported?',
        answer: 'The framework is cross-platform and runs on macOS, Linux, and Windows. It requires Python 3.8+ and works with all major development environments including VS Code, JetBrains IDEs, and terminal-based workflows.',
      },
    ],
  },
  {
    category: 'Use Cases',
    questions: [
      {
        question: 'What can I build with Empathy?',
        answer: 'You can build anticipatory AI systems for software development (bug prediction, security scanning, test generation), healthcare (patient monitoring, clinical decision support), and any domain where predicting problems before they happen adds value.',
      },
      {
        question: 'What happened to the Fair Source License?',
        answer: 'As of January 28, 2026, we switched from Fair Source 0.9 to Apache 2.0. We realized the licensing restrictions were limiting adoption without generating revenue. Going fully open source lets us focus on building the best framework and growing a community.',
      },
      {
        question: 'Is the framework production-ready?',
        answer: 'Yes! The framework is v4.6.6 Production/Stable with 11,000+ comprehensive tests, extensive documentation, and is being used in production software development tools and AI workflows.',
      },
    ],
  },
  {
    category: 'Support & Community',
    questions: [
      {
        question: 'Where can I get help?',
        answer: 'Free users get community support via GitHub Discussions. Commercial users get email support and priority bug fixes. Enterprise users get dedicated support with SLA guarantees.',
      },
      {
        question: 'How do I report bugs?',
        answer: (
          <>
            Report bugs via{' '}
            <Link href="https://github.com/Smart-AI-Memory/empathy-framework/issues" className="text-[var(--primary)] hover:underline" target="_blank" rel="noopener noreferrer">
              GitHub Issues
            </Link>
            . Include your environment details, steps to reproduce, and expected vs actual behavior.
          </>
        ),
        answerText: 'Report bugs via GitHub Issues at https://github.com/Smart-AI-Memory/empathy-framework/issues. Include your environment details, steps to reproduce, and expected vs actual behavior.',
      },
      {
        question: 'Can I contribute to the project?',
        answer: 'Yes! We welcome contributions. Check out our GitHub repository for contribution guidelines. The framework is fully open source under Apache 2.0, making it easy to fork, modify, and contribute back.',
      },
    ],
  },
];

export const metadata: Metadata = generateMetadata({
  title: 'FAQ',
  description: 'Frequently asked questions about Empathy, open source licensing, and technical details.',
  url: 'https://smartaimemory.com/faq',
});

export default function FAQPage() {
  const structuredData = generateStructuredData('faq', {
    questions: faqData.flatMap(category =>
      category.questions.map(q => ({
        question: q.question,
        answer: q.answerText ?? (typeof q.answer === 'string' ? q.answer : ''),
      }))
    ),
  });

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(structuredData),
        }}
      />
      <Navigation />
      <main className="min-h-screen pt-16">
        {/* Hero Section */}
        <section className="py-20 gradient-primary text-white">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-5xl font-bold mb-6">
                Frequently Asked Questions
              </h1>
              <p className="text-2xl mb-8 opacity-90">
                Everything you need to know about Empathy
              </p>
            </div>
          </div>
        </section>

        {/* FAQ Sections */}
        <section className="py-20">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              {faqData.map((category, categoryIndex) => (
                <div
                  key={categoryIndex}
                  className="mb-12"
                >
                  <h2 className="text-3xl font-bold mb-6 text-[var(--primary)]">
                    {category.category}
                  </h2>
                  <div className="space-y-6">
                    {category.questions.map((item, questionIndex) => (
                      <details
                        key={questionIndex}
                        className="bg-[var(--background)] border-2 border-[var(--border)] rounded-lg p-6 hover:border-[var(--primary)] transition-all group"
                      >
                        <summary className="text-xl font-bold cursor-pointer list-none flex justify-between items-center">
                          <span>{item.question}</span>
                          <span className="text-[var(--primary)] ml-4 group-open:rotate-180 transition-transform">
                            ▼
                          </span>
                        </summary>
                        <p className="mt-4 text-[var(--text-secondary)] leading-relaxed">
                          {item.answer}
                        </p>
                      </details>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Still Have Questions CTA */}
        <section className="py-20 bg-[var(--border)] bg-opacity-30">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center">
              <h2 className="text-4xl font-bold mb-6">
                Still Have Questions?
              </h2>
              <p className="text-xl text-[var(--text-secondary)] mb-8">
                We&apos;re here to help. Reach out to our team or join the community.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <a
                  href="/contact"
                  className="btn btn-primary text-lg px-8 py-4"
                >
                  Contact Us
                </a>
                <a
                  href="https://github.com/Smart-AI-Memory/empathy-framework/discussions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-outline text-lg px-8 py-4"
                >
                  Join Community
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
