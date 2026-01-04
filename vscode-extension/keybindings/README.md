# Empathy Framework Keyboard Layouts

Choose the layout that matches your keyboard for optimal finger placement.

## Quick Setup

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run `Empathy: Setup → Apply Keyboard Layout`
3. Select your keyboard layout
4. Follow the prompts to copy keybindings

## Layouts at a Glance

### QWERTY (Default)

Prefix: `Ctrl+Shift+E` (Mac: `Cmd+Shift+E`)

```
┌─────────────────────────────────────┐
│   [Q][W][E][R][T]   ← T=Tests       │
│    [A][S][D][F][G]  ← S=Ship F=Fix  │
│     [Z][X][C][V][B] ← C=Costs       │
└─────────────────────────────────────┘

Daily Four:  M(orning) S(hip) F(ix) D(ashboard)
Mnemonic:    "My Ship Floats Daily"
```

### Dvorak

Prefix: `Ctrl+Shift+E` (Mac: `Cmd+Shift+E`)

```
┌─────────────────────────────────────┐
│  ['][,][.][P][Y]    ← ,=Costs .=Power │
│    [A][O][E][U][I]  ← Home row      │
│     [;][Q][J][K][X] ← Z=History     │
└─────────────────────────────────────┘

Daily Four:  A(M) O(ut/Ship) E(dit/Fix) U(I/Dashboard)
Mnemonic:    "AOEU - vowels for daily actions"
```

### Colemak

Prefix: `Ctrl+Shift+E` (Mac: `Cmd+Shift+E`)

```
┌─────────────────────────────────────┐
│  [Q][W][F][P][G]    ← F=Tests       │
│    [A][R][S][T][D]  ← Home row      │
│     [Z][X][C][V][B] ← Z=History     │
└─────────────────────────────────────┘

Daily Four:  A(M) R(elease/Ship) S(olve/Fix) T(ab/Dashboard)
Mnemonic:    "ARST - your daily rhythm"
```

## Full Key Mapping

| Action           | QWERTY | Dvorak | Colemak |
|-----------------|--------|--------|---------|
| Morning         | M      | A      | A       |
| Ship Check      | S      | O      | R       |
| Fix All         | F      | E      | S       |
| Dashboard       | D      | U      | T       |
| Workflow        | W      | I      | G       |
| Costs           | C      | ,      | Q       |
| Power Panel     | P      | .      | W       |
| Tests           | T      | P      | F       |
| Review          | R      | Y      | P       |
| Health Scan     | H      | H      | H       |
| Security Audit  | A      | T      | N       |
| Bug Prediction  | B      | N      | E       |
| Generate Tests  | G      | S      | I       |
| Learn Patterns  | L      | L      | L       |
| Status          | V      | R      | O       |
| Recent History  | Z      | Z      | Z       |

## Manual Configuration

If the automatic setup doesn't work, copy the contents of the appropriate JSON file to your VSCode keybindings.json:

- `dvorak.json` - Dvorak optimized bindings
- `colemak.json` - Colemak optimized bindings

Open keybindings.json: `Cmd+Shift+P` → "Preferences: Open Keyboard Shortcuts (JSON)"
