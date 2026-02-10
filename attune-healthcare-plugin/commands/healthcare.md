---
name: healthcare
description: "Clinical protocol monitoring - patient vitals, protocol compliance, deterioration prediction"
category: hub
aliases: [clinical, patient]
tags: [healthcare, clinical, monitoring, protocols]
version: "1.0.0"
question:
  header: "Healthcare"
  question: "What do you need to do?"
  multiSelect: false
  options:
    - label: "Monitor a patient"
      description: "Full analysis: load protocol, parse vitals, check compliance, predict trajectory"
    - label: "Check protocol compliance"
      description: "Check if current vitals meet protocol criteria"
    - label: "List protocols"
      description: "View available clinical protocols and their criteria"
    - label: "Analyze vital trends"
      description: "Parse vital signs and predict trajectory"
---

# Healthcare Tools

Clinical protocol monitoring with Level 4 anticipatory analysis.

## Quick Shortcuts

| Shortcut | Action |
|----------|--------|
| `/attune-healthcare:healthcare monitor` | Full patient monitoring |
| `/attune-healthcare:healthcare compliance` | Protocol compliance check |
| `/attune-healthcare:healthcare protocols` | List available protocols |
| `/attune-healthcare:healthcare vitals` | Vital sign analysis |

## CRITICAL: Execution Instructions

When invoked with arguments, EXECUTE the corresponding action:

| Input | Action |
|-------|--------|
| `monitor` | Ask for patient ID, protocol name, and vital signs. Call `healthcare_load_protocol` then `healthcare_analyze`. Present results with alerts first. |
| `compliance` | Ask for patient ID, protocol name, and vital signs. Call `healthcare_check_compliance`. Show compliance status and deviations. |
| `protocols` | Call `healthcare_list_protocols`. Display available protocols with screening criteria. |
| `vitals` | Ask for vital signs data. Call `healthcare_predict_trajectory`. Show trends and trajectory state. |

## Natural Language Routing

| Pattern | Action |
|---------|--------|
| "patient", "monitor", "sepsis", "cardiac", "analyze" | Monitor a patient |
| "compliance", "protocol check", "deviation", "adherence" | Check protocol compliance |
| "protocols", "list", "available", "qSOFA", "criteria" | List protocols |
| "vitals", "trend", "trajectory", "heart rate", "blood pressure" | Analyze vital trends |

## Example Usage

### Monitor a Patient

```text
User: Monitor patient 12345 for sepsis. Vitals: HR 110, BP 85/55, RR 24, temp 101.2F, O2 93%

Claude: [Calls healthcare_load_protocol with patient_id="12345", protocol_name="sepsis"]
        [Calls healthcare_analyze with sensor_data and protocol]
        [Presents structured clinical summary]
```

### Quick Vital Check

```text
User: Are these vitals normal? HR 95, BP 130/85, RR 18, temp 98.6, O2 97%

Claude: [Parses vitals, compares to normal ranges, reports findings]
```
