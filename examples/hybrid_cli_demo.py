"""Hybrid CLI Demo - Slash Commands + Natural Language

Demonstrates the four levels of user interaction:
1. Discovery (slash commands)
2. Structured usage (slash commands)
3. Natural language (automatic routing)
4. AI assistant mode (fully automatic)

Usage:
    python examples/hybrid_cli_demo.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.cli_router import HybridRouter


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


async def demo_level_1_discovery():
    """Level 1: Discovery using slash commands."""
    print_section("LEVEL 1: Discovery (Slash Commands)")

    examples = [
        ("/help", "Show all available hubs"),
        ("/dev", "Show development tools"),
        ("/testing", "Show testing commands"),
        ("/workflows", "Show workflow commands"),
    ]

    router = HybridRouter()

    for command, description in examples:
        print(f"\n💡 {description}")
        print(f"   $ empathy {command}")

        result = await router.route(command)
        print(f"   → Type: {result['type']}")
        print(f"   → Hub: {result['hub']}")
        if result.get("command"):
            print(f"   → Command: {result['command']}")


async def demo_level_2_structured():
    """Level 2: Structured usage with slash commands."""
    print_section("LEVEL 2: Structured Usage (Slash Commands)")

    examples = [
        ("/dev commit", "Create a git commit"),
        ("/testing run", "Run test suite"),
        ("/workflows security-audit", "Run security audit"),
        ("/learning evaluate", "Evaluate session"),
    ]

    router = HybridRouter()

    for command, description in examples:
        print(f"\n🎯 {description}")
        print(f"   $ empathy {command}")

        result = await router.route(command)
        print(f"   → Hub: {result['hub']}")
        print(f"   → Command: {result['command']}")
        print(f"   → Confidence: {result['confidence']:.0%}")


async def demo_level_3_inference():
    """Level 3: Single word inference."""
    print_section("LEVEL 3: Command Inference (Single Words)")

    examples = [
        ("commit", "Infers /dev commit"),
        ("test", "Infers /testing run"),
        ("security", "Infers /workflows security-audit"),
        ("review", "Infers /dev review-pr"),
    ]

    router = HybridRouter()

    for keyword, description in examples:
        print(f"\n🔍 {description}")
        print(f"   $ empathy {keyword}")

        result = await router.route(keyword)
        print(f"   → Type: {result['type']}")
        print(f"   → Inferred: {result.get('slash_equivalent', 'N/A')}")
        print(f"   → Confidence: {result['confidence']:.0%}")
        print(f"   → Source: {result.get('source', 'N/A')}")


async def demo_level_4_natural_language():
    """Level 4: Natural language routing."""
    print_section("LEVEL 4: Natural Language (Automatic Routing)")

    examples = [
        ("I want to commit my changes", "Commit workflow"),
        ("Run security audit on auth.py", "Security analysis"),
        ("Generate tests for my new feature", "Test generation"),
        ("Something's slow in the API", "Performance audit"),
    ]

    router = HybridRouter()

    for text, description in examples:
        print(f"\n💬 User says: \"{text}\"")
        print(f"   Expected: {description}")

        result = await router.route(text)
        print(f"   → Type: {result['type']}")
        print(f"   → Workflow: {result.get('workflow', 'N/A')}")
        print(f"   → Slash equivalent: {result.get('slash_equivalent', 'N/A')}")
        print(f"   → Confidence: {result['confidence']:.0%}")
        if result.get("reasoning"):
            print(f"   → Reasoning: {result['reasoning']}")


async def demo_user_preference_learning():
    """Demo: User preference learning."""
    print_section("DEMO: User Preference Learning")

    router = HybridRouter()

    print("\n📚 Learning from user behavior:")

    # Scenario: User types "deploy" and chooses "/release prep"
    print("\n1. User types: deploy")
    print("   Framework suggests: /release prep")
    print("   User confirms: y")

    # Learn this preference
    router.learn_preference("deploy", "/release prep")
    print("   ✅ Learned: deploy → /release prep")

    # Next time user types "deploy"
    print("\n2. User types: deploy (again)")
    result = await router.route("deploy")

    if result["type"] == "inferred" and result.get("source") == "learned":
        print(f"   ✅ Auto-inferred: {result['slash_equivalent']}")
        print(f"   → Confidence: {result['confidence']:.0%}")
        print(f"   → Usage count: {router.preferences['deploy'].usage_count}")
    else:
        print("   ℹ️  No learned preference yet")


async def demo_real_world_flow():
    """Demo: Real-world user flow."""
    print_section("DEMO: Real-World User Flow")

    print("""
📖 Scenario: Developer's typical workflow

1. Morning: Check what to work on
   $ empathy /context status
   → Shows: memory, current tasks, recent activity

2. Start work: Make code changes
   [... editing files ...]

3. Run tests quickly:
   $ empathy test
   → Infers: /testing run
   → Runs test suite

4. Tests fail - debug:
   $ empathy "what's wrong with auth.py?"
   → Natural language routing
   → Suggests: /dev review + /workflows bug-predict

5. Fix bugs, run tests again:
   $ empathy test
   → Tests pass ✅

6. Commit changes:
   $ empathy commit
   → Infers: /dev commit
   → Creates commit with AI-generated message

7. Pre-commit hook triggers:
   $ empathy workflow run security-audit
   → Finds 5 issues
   → Chain triggers: bug-predict (auto)
   → Chain suggests: code-review (asks approval)

8. End of day: Evaluate session
   $ empathy /learning evaluate
   → Analyzes session, suggests improvements

💡 Multiple input styles in one workflow:
   - Slash commands for discovery (/context status)
   - Keywords for speed (test, commit)
   - Natural language for exploration ("what's wrong?")
   - All seamlessly integrated! ✨
    """)


async def demo_suggestions():
    """Demo: Command suggestions."""
    print_section("DEMO: Command Suggestions")

    router = HybridRouter()

    print("\n🔍 Autocomplete suggestions:")

    partial_inputs = ["com", "test", "sec", "rev"]

    for partial in partial_inputs:
        suggestions = router.get_suggestions(partial)
        print(f"\n   User types: '{partial}'")
        print("   Suggestions:")
        for suggestion in suggestions[:3]:
            print(f"     → {suggestion}")


async def main():
    """Run all demos."""
    print("=" * 70)
    print("HYBRID CLI DEMO")
    print("Empathy Framework - Slash Commands + Natural Language")
    print("=" * 70)

    try:
        await demo_level_1_discovery()
        await demo_level_2_structured()
        await demo_level_3_inference()
        await demo_level_4_natural_language()
        await demo_user_preference_learning()
        await demo_suggestions()
        await demo_real_world_flow()

        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE")
        print("=" * 70)

        print("""
🎯 Key Takeaways:

1. **Multiple Input Styles**
   - Slash commands for structure and discovery
   - Keywords for speed and muscle memory
   - Natural language for exploration

2. **Learning System**
   - Framework learns your preferences
   - Repeated usage increases confidence
   - Personalized experience over time

3. **Seamless Integration**
   - All styles work together
   - No learning curve required
   - Choose what feels natural

4. **Best of Both Worlds**
   - Slash commands: Predictable, structured
   - Natural language: Flexible, intuitive
   - Together: Powerful and accessible

📚 Next Steps:
1. Try: empathy /help (discovery)
2. Try: empathy commit (inference)
3. Try: empathy "run security check" (natural language)
        """)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
