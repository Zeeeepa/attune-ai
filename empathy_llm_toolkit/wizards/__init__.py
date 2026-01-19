"""Empathy LLM Wizards - Canonical Examples

Core wizard base class and canonical domain examples demonstrating
the Empathy Framework's capabilities across different use cases.

Included Wizards (1 active example):
1. CustomerSupportWizard - Customer service and help desk

Deprecated Wizards (maintained for backward compatibility, will be removed in v5.0):
- HealthcareWizard - Use: pip install empathy-healthcare-wizards
- TechnologyWizard - Use empathy_software_plugin or pip install empathy-software-wizards

Additional Wizards Available:
For specialized domain wizards, install separate packages:
- Healthcare (23 wizards): pip install empathy-healthcare-wizards
- Tech & AI (20+ wizards): empathy_software_plugin (built-in) or pip install empathy-software-wizards
- Business (12+ wizards): pip install empathy-business-wizards

Or try the live dashboards:
- Healthcare: https://healthcare.smartaimemory.com/static/dashboard.html
- Tech & AI: https://wizards.smartaimemory.com/

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .base_wizard import BaseWizard, WizardConfig
from .customer_support_wizard import CustomerSupportWizard

# Deprecated - kept for backward compatibility
from .healthcare_wizard import HealthcareWizard  # Deprecated in v4.0, remove in v5.0
from .technology_wizard import TechnologyWizard  # Deprecated in v4.0, remove in v5.0

__all__ = [
    # Base classes
    "BaseWizard",
    "WizardConfig",
    # Active examples
    "CustomerSupportWizard",
    # Deprecated (backward compatibility only)
    "HealthcareWizard",  # DEPRECATED: Use empathy-healthcare-wizards
    "TechnologyWizard",  # DEPRECATED: Use empathy_software_plugin
]
