---
name: protocols
description: "Clinical protocol reference and listing. Triggers: 'protocol', 'screening criteria', 'interventions', 'qSOFA', 'escalation', 'list protocols', 'protocol details', 'clinical guidelines'."
---

# Clinical Protocols

Reference and details for available clinical monitoring protocols.

## What This Does

Lists available clinical protocols and provides details on screening criteria, interventions, monitoring frequency, and escalation criteria.

## How to Use

1. Call the `healthcare_list_protocols` MCP tool to see available protocols
2. Call the `healthcare_load_protocol` MCP tool with a protocol name for full details
3. Present protocol details in a structured format

## Protocol Reference

| Protocol | Screening Criteria | Threshold | Monitoring Frequency |
|----------|-------------------|-----------|---------------------|
| **sepsis** | qSOFA: SBP<=100, RR>=22, altered mental status | 2+ criteria | Every 15 minutes |
| **cardiac** | HR>120, SBP<90, O2_sat<90, RR>24 | 2+ criteria | Continuous |
| **respiratory** | RR>=28, O2_sat<=90, HR>=115 | 2+ criteria | Continuous |
| **post_operative** | Temp>=101F, HR>=110, SBP<=90, O2_sat<=92 | 2+ criteria | Every 4 hours |

## Protocol Details

### Sepsis Screening & Management (v2024.1)

- **Applies to**: Adult inpatient
- **Screening**: qSOFA score (3 criteria, threshold 2+)
- **Key interventions**: Blood cultures, broad-spectrum antibiotics within 1 hour, lactate level, IV fluid resuscitation
- **Reassessment**: 3-hour re-evaluation
- **Escalation**: Lactate >4, hypotension despite fluids, respiratory failure, worsening mental status

### Cardiac Monitoring (v2024.1)

- **Applies to**: Cardiac patients, post-MI, heart failure
- **Key interventions**: 12-lead ECG, supplemental oxygen, notify cardiologist, cardiac markers
- **Escalation**: Ventricular tachycardia, SBP<80, O2_sat<88, unrelieved chest pain

### Respiratory Monitoring (v2024.1)

- **Applies to**: Respiratory failure, COPD, asthma, pneumonia
- **Key interventions**: Supplemental oxygen, assess airway, ABG, notify respiratory therapy, consider NIV
- **Escalation**: O2_sat<88 despite oxygen, RR>30, altered mental status

### Post-Operative Monitoring (v2024.1)

- **Applies to**: Post-surgical patients
- **Key interventions**: Assess surgical site, check pain management, review I&O, notify surgeon
- **Escalation**: Temp>102F, O2_sat<90, SBP<85, altered mental status
