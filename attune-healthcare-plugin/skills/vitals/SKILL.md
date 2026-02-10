---
name: vitals
description: "Vital sign parsing and normal range checking. Triggers: 'parse vitals', 'FHIR', 'vital signs', 'heart rate', 'blood pressure', 'normal range', 'vital check', 'SpO2', 'temperature check'."
---

# Vital Sign Analysis

Parse raw vital sign data and check against normal ranges.

## What This Does

Accepts vital sign data in multiple formats, normalizes it, and checks values against clinical normal ranges. Can predict trajectory trends when historical data is available.

## How to Use

1. Accept vital data from the user (JSON, FHIR, or free text)
2. If free text, convert to simple JSON format using the key mappings below
3. Call `healthcare_check_compliance` to check against a specific protocol
4. Or call `healthcare_predict_trajectory` to analyze trends
5. Present findings with normal ranges highlighted

## Normal Ranges Reference

| Vital | Key | Normal Range | Unit |
|-------|-----|-------------|------|
| Heart Rate | `hr` | 60-100 | bpm |
| Systolic BP | `systolic_bp` | 90-140 | mmHg |
| Diastolic BP | `diastolic_bp` | 60-90 | mmHg |
| Respiratory Rate | `respiratory_rate` | 12-20 | breaths/min |
| Temperature | `temp_f` | 97.0-99.5 | F |
| O2 Saturation | `o2_sat` | 95-100 | % |

## Supported Input Formats

### Simple JSON

```json
{
  "hr": 80,
  "systolic_bp": 120,
  "diastolic_bp": 75,
  "respiratory_rate": 16,
  "temp_f": 98.6,
  "o2_sat": 98,
  "mental_status": "alert",
  "pain": 2
}
```

**Accepted key aliases**: `heart_rate` or `hr`, `rr` or `respiratory_rate`, `spo2` or `o2_sat`, `temp_c` or `temp_f`, `bp` (parsed as "systolic/diastolic")

### FHIR Observation Bundle

Standard HL7 FHIR Observation resources with LOINC codes. Set `sensor_format` to `"fhir"` when calling MCP tools.

## Trajectory States

When historical data is available, the trajectory analyzer reports:

- **stable**: Vitals within normal ranges, no concerning trends
- **improving**: Vitals trending toward normal
- **concerning**: One or more vitals trending away from normal
- **critical**: Imminent risk of critical threshold breach
