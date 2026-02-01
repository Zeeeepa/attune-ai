#!/usr/bin/env python3
"""Test XML-enhanced wizard functionality."""

import sys

from attune_llm.wizards.healthcare_wizard import HealthcareWizard


def test_healthcare_wizard_xml():
    """Test HealthcareWizard XML prompt generation."""
    print("Testing HealthcareWizard XML-enhanced prompts...")

    # Create wizard instance with mock LLM
    class MockLLM:
        def __init__(self):
            self.model_name = "test-model"

    wizard = HealthcareWizard(llm=MockLLM())

    # Test 1: Check XML enabled method exists
    if hasattr(wizard, "_is_xml_enabled"):
        print("✅ _is_xml_enabled method exists")
    else:
        print("❌ _is_xml_enabled method missing")
        return False

    # Test 2: Check render_xml_prompt method exists
    if hasattr(wizard, "_render_xml_prompt"):
        print("✅ _render_xml_prompt method exists")
    else:
        print("❌ _render_xml_prompt method missing")
        return False

    # Test 3: Build system prompt
    try:
        prompt = wizard._build_system_prompt("Test patient query")
        if prompt and len(prompt) > 100:
            print(f"✅ System prompt generated ({len(prompt)} chars)")

            # Check if it contains HIPAA compliance mentions
            if "HIPAA" in prompt:
                print("✅ HIPAA compliance mentioned in prompt")
            else:
                print("⚠️  HIPAA not mentioned in prompt")
        else:
            print("❌ System prompt too short or empty")
            return False
    except Exception as e:
        print(f"❌ Error building system prompt: {e}")
        return False

    print("\n✅ All HealthcareWizard XML tests passed!")
    return True


if __name__ == "__main__":
    success = test_healthcare_wizard_xml()
    sys.exit(0 if success else 1)
