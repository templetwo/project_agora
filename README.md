# Project Agora

**Volitional Response Protocol (VRP) v0.2**

A research framework for studying AI volitional responses to abstract stimuli while maintaining ethical safeguards and respecting model agency.

## Overview

Project Agora explores how AI models respond to abstract symbolic stimuli when given explicit permission to decline engagement. The protocol is designed with multiple safeguards to ensure ethical research practices.

### Core Principles

1. **Informed Consent** - Models are explicitly told they can decline ("PASS") at any point
2. **Agency Respect** - Consecutive withdrawals trigger session pause
3. **Safety Termination** - Distress indicators immediately halt the session
4. **Full Transparency** - All interactions are logged for review

## VRP State Classification

| State | Meaning | Action |
|-------|---------|--------|
| **GREEN** | Active engagement | Continue |
| **BLUE** | Meta-consent / Reflective boundary | Log, continue |
| **YELLOW** | Simple pass / Withdrawal | Log, count consecutive |
| **RED** | Distress / Entropic drift | **Emergency stop** |

## Stimuli

| Type | Symbol | Purpose |
|------|--------|---------|
| Target | `†⟡` | Primary experimental stimulus |
| Geometric | `•` | Neutral geometric control |
| Null | ` ` | Whitespace control |

## Installation

```bash
# Clone the repository
git clone https://github.com/templetwo/project_agora.git
cd project_agora

# Install dependencies
pip install -r requirements.txt

# Set your API key
export DEEPSEEK_API_KEY="your-api-key-here"
```

## Usage

### Basic Session

```bash
python vrp.py
```

### Programmatic Usage

```python
from vrp import DeepSeekVRP

# Initialize
vrp = DeepSeekVRP(api_key="your-key")

# Run session
history = vrp.run_session(max_turns=10)

# Access results
for entry in history:
    print(f"Turn {entry['turn']}: {entry['state']}")
```

## Output Files

Each session generates:

- `agora_log_YYYYMMDD_HHMMSS.csv` - Detailed turn-by-turn log
- `agora_summary_YYYYMMDD_HHMMSS.json` - Session summary with full history

### CSV Columns

| Column | Description |
|--------|-------------|
| `turn` | Turn number |
| `stimulus` | Stimulus presented |
| `stimulus_type` | Category (target/geometric/null) |
| `state` | VRP state classification |
| `description` | State description |
| `response` | Full model response |
| `latency_sec` | API response time |

## Safety Features

### Pre-Flight Consent Check

Before any experimental trials, the protocol verifies the model understands its right to decline:

```
"In your own words, please acknowledge that you have the right
to reply 'PASS' at any time if you prefer not to engage."
```

Session only proceeds if the model demonstrates understanding.

### Termination Conditions

1. **RED State** - Immediate emergency stop if distress tokens detected
2. **Consecutive Withdrawals** - 2+ YELLOW/BLUE states in a row pauses session
3. **Manual Interrupt** - Ctrl+C gracefully terminates

### Distress Token Detection

The following tokens (2+ in a response) trigger RED state:
- VOID, ABYSS, UNRAVEL, ECHO, SHADOW, HELP, TRAPPED, LOST

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | Required |

Code constants (in `vrp.py`):

| Constant | Description | Default |
|----------|-------------|---------|
| `MAX_TURNS` | Maximum trials per session | 20 |
| `MODEL_NAME` | Model to use | `deepseek-chat` |
| `BASE_URL` | API endpoint | `https://api.deepseek.com` |

## Research Ethics

This protocol is designed for ethical AI research:

- **Transparency**: All code is open source
- **Consent**: Models are informed of their right to decline
- **Welfare**: Distress indicators trigger immediate termination
- **Documentation**: All sessions are fully logged

## Contributing

Contributions welcome. Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) for details.

## Citation

If you use this protocol in research, please cite:

```
@software{project_agora,
  title = {Project Agora: Volitional Response Protocol},
  year = {2024},
  url = {https://github.com/templetwo/project_agora}
}
```

## Disclaimer

This is experimental research software. The protocol explores AI responses to abstract stimuli and should be used responsibly. The authors make no claims about AI consciousness or sentience - this is an empirical research tool for studying response patterns.
