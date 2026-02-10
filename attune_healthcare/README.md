# Attune Healthcare

Clinical protocol monitoring plugin for the [Attune AI](https://pypi.org/project/attune-ai/) framework.

## Installation

```bash
# Standalone (zero dependencies)
pip install attune-healthcare

# With Attune AI core (enables plugin auto-discovery)
pip install attune-ai attune-healthcare
```

## Quick Start

```python
from attune_healthcare import ClinicalProtocolMonitor

monitor = ClinicalProtocolMonitor()

# Load a clinical protocol
protocol = monitor.load_protocol(
    patient_id="12345",
    protocol_name="sepsis",
    patient_context={"age": 65, "post_op_day": 2},
)

# Analyze patient vitals
result = await monitor.analyze({
    "patient_id": "12345",
    "sensor_data": '{"heart_rate": 110, "systolic_bp": 85, "respiratory_rate": 24, "temperature": 38.5}',
})

print(result["alerts"])
print(result["predictions"])
print(result["recommendations"])
```

## Included Protocols

- **Sepsis** - qSOFA-based screening and Surviving Sepsis Campaign guidelines
- **Cardiac** - Cardiac pathway monitoring
- **Respiratory** - Respiratory pathway monitoring
- **Post-operative** - Post-operative care protocols

## Features

- **Level 4 Anticipatory Analysis** - Predicts patient deterioration before critical thresholds
- **Protocol Compliance Checking** - Validates interventions against evidence-based protocols
- **Trajectory Analysis** - Tracks vital sign trends and estimates time-to-critical
- **FHIR Support** - Parses FHIR Observation resources and LOINC codes
- **Zero Dependencies** - Uses only Python standard library

## License

Apache 2.0
