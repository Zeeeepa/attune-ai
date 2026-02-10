---
name: monitor
description: "Full patient monitoring and clinical analysis. Triggers: 'patient', 'monitor', 'vitals', 'sepsis', 'cardiac', 'deterioration', 'protocol', 'analyze patient', 'clinical', 'patient assessment'."
---

# Patient Monitoring

Full clinical protocol monitoring pipeline with Level 4 anticipatory analysis.

## What This Does

Runs the complete patient analysis pipeline:

1. Load clinical protocol for the patient's condition
2. Parse vital signs (JSON or FHIR format)
3. Check compliance against protocol criteria
4. Run trajectory analysis to predict deterioration
5. Generate alerts, predictions, and recommendations

## How to Use

1. Call the `healthcare_load_protocol` MCP tool with the patient's ID and protocol name
2. Call the `healthcare_analyze` MCP tool with patient ID and vital signs JSON
3. Present results as a structured clinical summary with alerts at the top

## Input Formats

### Simple JSON

```json
{
  "hr": 110,
  "systolic_bp": 85,
  "diastolic_bp": 55,
  "respiratory_rate": 24,
  "temp_f": 101.2,
  "o2_sat": 93,
  "mental_status": "altered"
}
```

### FHIR

Standard FHIR Observation bundles are supported. Set `sensor_format` to `"fhir"` when calling `healthcare_analyze`.

## Available Protocols

| Protocol | Condition | Screening |
|----------|-----------|-----------|
| `sepsis` | Sepsis screening (qSOFA) | SBP<=100, RR>=22, altered mental status |
| `cardiac` | Cardiac monitoring | HR>120, SBP<90, O2<90, RR>24 |
| `respiratory` | Respiratory failure | RR>=28, O2<=90, HR>=115 |
| `post_operative` | Post-surgical | Temp>=101, HR>=110, SBP<=90, O2<=92 |

## Output Interpretation

- **alerts**: Clinical alerts sorted by severity (critical > high > warning)
- **protocol_compliance**: Protocol activation status, deviations, compliant items
- **trajectory**: Prediction state (`stable`, `improving`, `concerning`, `critical`)
- **predictions**: Level 4 anticipatory predictions with time horizons
- **recommendations**: Actionable clinical recommendations
