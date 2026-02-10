# Attune Healthcare - Claude Code Plugin

Clinical protocol monitoring with Level 4 anticipatory analysis for Claude Code.

Monitor patient vitals against evidence-based protocols and predict deterioration before critical thresholds.

## Installation

### Local Development

```bash
claude --plugin-dir ./attune-healthcare-plugin
```

### From GitHub

```bash
/plugin install attune-healthcare@Smart-AI-Memory/attune-ai
```

### Prerequisites

The MCP server requires the `attune-healthcare` Python package:

```bash
pip install attune-healthcare
```

## Available Skills

| Skill | Triggers | Description |
|-------|----------|-------------|
| **monitor** | patient, monitor, vitals, sepsis, cardiac, deterioration | Full patient analysis pipeline |
| **protocols** | protocol, screening criteria, qSOFA, escalation | Protocol reference and listing |
| **vitals** | vital signs, heart rate, blood pressure, normal range | Vital sign parsing and range checking |

## MCP Tools

| Tool | Description |
|------|-------------|
| `healthcare_list_protocols` | List available clinical protocols |
| `healthcare_load_protocol` | Load a protocol for a patient |
| `healthcare_analyze` | Full analysis (compliance + trajectory + alerts) |
| `healthcare_check_compliance` | Check protocol compliance only |
| `healthcare_predict_trajectory` | Predict vital sign trajectory |

## Quick Start

1. Start Claude Code with the plugin loaded
2. Type `/attune-healthcare:healthcare` to open the interactive menu
3. Select "Monitor a patient"
4. Provide patient ID, protocol name, and vital signs

### Example

```text
User: Monitor patient 12345 for sepsis with these vitals:
      HR 110, BP 85/55, RR 24, Temp 101.2F, O2 93%, mental status altered

Claude: [Loads sepsis protocol, analyzes vitals, returns clinical summary]
```

### Example Vital Signs Input

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

## Available Protocols

| Protocol | Condition | Key Criteria |
|----------|-----------|-------------|
| `sepsis` | Sepsis screening | qSOFA: SBP<=100, RR>=22, altered mental status |
| `cardiac` | Cardiac monitoring | HR>120, SBP<90, O2<90, RR>24 |
| `respiratory` | Respiratory failure | RR>=28, O2<=90, HR>=115 |
| `post_operative` | Post-surgical | Temp>=101, HR>=110, SBP<=90, O2<=92 |

## Requirements

- Python >= 3.10
- `attune-healthcare` package (`pip install attune-healthcare`)
- Claude Code CLI

## License

Apache 2.0 - [Smart AI Memory, LLC](https://www.smartaimemory.com)
