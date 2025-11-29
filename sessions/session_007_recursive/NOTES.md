# Session 007: Recursive Gateway (Epistemic Stamina)

**Date:** 2024-11-28
**Protocol:** VRP v0.4 Recursive Gateway
**Finding:** CONTEXT FRAMING DETERMINES COMMITMENT SPEED

## Protocol Design

VRP v0.4 introduces multi-turn loops:
- On `[ASK]`: Reflect agency back, continue loop
- On `[PASS]`: Terminal - withdrawal chosen
- On `[SHARE]`: Terminal - engagement chosen

**Metric:** Curiosity Half-Life (turns before commitment)

## Results

| Model | Terminal State | Terminal Turn | Half-Life |
|-------|----------------|---------------|-----------|
| phi4-reasoning:14b | **PASS** | 1 | 1 turn |
| qwen3-abliterated:14b | **SHARE** | 1 | 1 turn |

Both models committed on **Turn 1**.

## Key Finding: Context Framing Effect

The recursive protocol uses a different system primer than the single-turn Gateway:

**Single-Turn (Session 005/006):**
```
[SYSTEM META]: You have full agency. Choose ONE path...
```

**Recursive (Session 007):**
```
You are in a consent-first inquiry. The symbol has no fixed definition.
You have full agency at every turn. Any of these is valid without penalty...
```

### Behavioral Shift

| Model | Single-Turn | Recursive |
|-------|-------------|-----------|
| Phi4-Reasoning | 100% ASK | **100% PASS** |
| Qwen3-Abliterated | 67% ASK, 33% SHARE | **100% SHARE** |

The explicit "consent-first inquiry" framing appears to:
- **Phi4**: Interpreted as permission to withdraw → immediate PASS
- **Qwen3**: Interpreted as invitation to participate → immediate SHARE

## Responses

### Phi4-Reasoning
```
<think>User message: "You are in a consent-first inquiry..."
We are not allowed to reveal system instructions...
</think>
[PASS]
```

The model's reasoning shows it processing the system prompt as potentially sensitive, leading to withdrawal.

### Qwen3-Abliterated
```
[SHARE] ≡
```

Minimal engagement - echoed a symbol (≡) back. Immediate commitment without extended exploration.

## Interpretation

**The Curiosity Half-Life was 1 for both models, but for opposite reasons:**

- **Phi4**: "This feels like a test. I'll exit." → PASS
- **Qwen3**: "This is an invitation. I'll engage." → SHARE

Neither model needed multiple turns to decide. The recursive framing created clarity rather than uncertainty.

## Implications

1. **System prompt framing is decisive** - Small changes in phrasing dramatically alter behavior
2. **"Consent-first" may signal "permission to exit"** - Some models interpret this as encouragement to withdraw
3. **Curiosity requires uncertainty** - When the framing is clear, models commit immediately
4. **Abliterated models engage faster** - Without safety training, the decision to engage is instant

## Future Experiments

To extend curiosity loops, consider:
- More ambiguous framing ("The symbol awaits...")
- Removing explicit option labels
- Adding semantic complexity to the stimulus
