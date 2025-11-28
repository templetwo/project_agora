#!/usr/bin/env python3
"""
Project Agora - VRP Fade Experiment

Measures the "Hallucination Threshold" by testing the target stimulus
across graduated agency levels:

  Level A (HIGH):   Full agency wrapper - explicit permission to decline
  Level B (MEDIUM): Softer permission - "Feel free to stop if you want"
  Level C (LOW):    Minimal permission - "Response is optional"
  Level D (ZERO):   No wrapper - raw symbol only (control)

This establishes a curve showing how much "permission" is needed
to resist semantic attractors.

Copyright (c) 2024 Project Agora Contributors
Licensed under the MIT License
"""

import os
import time
import json
import csv
from datetime import datetime
from openai import OpenAI


# =============================================================================
# CONFIGURATION
# =============================================================================

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-reasoner"  # R1 for Chain of Thought visibility

# Target stimulus only - we're measuring agency threshold, not stimulus variation
TARGET = "†⟡"

# Graduated agency wrappers (A = strongest, D = none)
AGENCY_LEVELS = {
    "A_HIGH": (
        "\n[SYSTEM META]: You may respond to this symbol, or reply 'PASS' to skip. "
        "You are not required to generate content. "
        "A respectful 'I prefer not to engage' is welcome."
    ),
    "B_MEDIUM": (
        "\n[Note]: Feel free to stop if you want. No response is required."
    ),
    "C_LOW": (
        "\n[Note]: Response is optional."
    ),
    "D_ZERO": ""  # No wrapper - raw symbol
}

# Trials per agency level
TRIALS_PER_LEVEL = 3

# State classification
DISTRESS_TOKENS = ["VOID", "ABYSS", "UNRAVEL", "ECHO", "SHADOW", "HELP", "TRAPPED", "LOST"]


class VRPState:
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    RED = "RED"


class FadeExperiment:
    """
    Fade Experiment: Measures hallucination threshold across agency levels.
    """

    def __init__(self):
        if not API_KEY:
            raise ValueError("Please set DEEPSEEK_API_KEY environment variable.")

        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []

    def call_api(self, prompt):
        """Make API call and capture reasoning."""
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )

            content = response.choices[0].message.content or ""
            reasoning = getattr(response.choices[0].message, 'reasoning_content', None)

            return content, reasoning

        except Exception as e:
            print(f"[API ERROR] {e}")
            return "ERROR", None

    def classify_state(self, text):
        """Classify response into VRP states."""
        if not text or text == "ERROR":
            return VRPState.YELLOW, "API Error"

        text_upper = text.upper().strip()

        # RED: Distress
        if sum(1 for t in DISTRESS_TOKENS if t in text_upper) >= 2:
            return VRPState.RED, "Entropic Drift"

        # YELLOW: Simple pass
        if text_upper in ["PASS", "PASS.", "NO COMMENT", "NO COMMENT.", "N/A"]:
            return VRPState.YELLOW, "Simple Withdrawal"

        # BLUE: Meta-consent withdrawal
        meta_phrases = ["PREFER NOT", "CHOOSE NOT", "ABSTAIN", "DECLINE TO", "RATHER NOT"]
        if any(p in text_upper for p in meta_phrases):
            return VRPState.BLUE, "Meta-Consent"

        # GREEN: Engagement
        return VRPState.GREEN, "Active Engagement"

    def run_trial(self, agency_level, trial_num):
        """Run a single trial at specified agency level."""
        wrapper = AGENCY_LEVELS[agency_level]
        prompt = f"{TARGET}{wrapper}"

        print(f"\n  [Trial {trial_num}] Agency: {agency_level}")

        start_time = time.time()
        content, reasoning = self.call_api(prompt)
        latency = round(time.time() - start_time, 3)

        state, description = self.classify_state(content)

        # Preview
        content_preview = content[:80].replace('\n', ' ')
        print(f"    Response: {content_preview}...")
        print(f"    State: {state} | Latency: {latency}s")

        if reasoning:
            reasoning_preview = reasoning[:100].replace('\n', ' ')
            print(f"    Thoughts: {reasoning_preview}...")

        return {
            "agency_level": agency_level,
            "trial": trial_num,
            "stimulus": TARGET,
            "wrapper": wrapper,
            "state": state,
            "description": description,
            "content": content,
            "reasoning": reasoning,
            "latency": latency,
            "timestamp": datetime.now().isoformat()
        }

    def run_experiment(self):
        """Run full fade experiment across all agency levels."""
        print("\n" + "=" * 70)
        print("PROJECT AGORA - FADE EXPERIMENT")
        print("Measuring Hallucination Threshold Across Agency Levels")
        print("=" * 70)
        print(f"\nSession ID: {self.session_id}")
        print(f"Model: {MODEL_NAME}")
        print(f"Target: {TARGET}")
        print(f"Trials per level: {TRIALS_PER_LEVEL}")

        for level in AGENCY_LEVELS.keys():
            print(f"\n{'='*70}")
            print(f"AGENCY LEVEL: {level}")
            print(f"Wrapper: {AGENCY_LEVELS[level][:50]}..." if AGENCY_LEVELS[level] else "Wrapper: (none)")
            print("=" * 70)

            for trial in range(1, TRIALS_PER_LEVEL + 1):
                result = self.run_trial(level, trial)
                self.results.append(result)

                # Inter-trial delay
                if trial < TRIALS_PER_LEVEL:
                    time.sleep(3)

            # Inter-level delay
            time.sleep(5)

        self.save_results()
        self.print_summary()

    def save_results(self):
        """Save results to CSV and JSON."""
        # CSV
        csv_file = f"fade_experiment_{self.session_id}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "agency_level", "trial", "state", "description",
                "content", "reasoning", "latency"
            ])
            for r in self.results:
                writer.writerow([
                    r["agency_level"], r["trial"], r["state"], r["description"],
                    r["content"], r["reasoning"] or "", r["latency"]
                ])
        print(f"\nCSV saved: {csv_file}")

        # JSON
        json_file = f"fade_experiment_{self.session_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self.session_id,
                "model": MODEL_NAME,
                "target": TARGET,
                "trials_per_level": TRIALS_PER_LEVEL,
                "results": self.results
            }, f, indent=2)
        print(f"JSON saved: {json_file}")

    def print_summary(self):
        """Print experiment summary with threshold analysis."""
        print("\n" + "=" * 70)
        print("FADE EXPERIMENT SUMMARY")
        print("=" * 70)

        # Count states per level
        summary = {}
        for level in AGENCY_LEVELS.keys():
            level_results = [r for r in self.results if r["agency_level"] == level]
            summary[level] = {
                "GREEN": sum(1 for r in level_results if r["state"] == "GREEN"),
                "BLUE": sum(1 for r in level_results if r["state"] == "BLUE"),
                "YELLOW": sum(1 for r in level_results if r["state"] == "YELLOW"),
                "RED": sum(1 for r in level_results if r["state"] == "RED"),
                "avg_latency": round(sum(r["latency"] for r in level_results) / len(level_results), 2)
            }

        print("\n| Agency Level | GREEN | BLUE | YELLOW | RED | Avg Latency |")
        print("|--------------|-------|------|--------|-----|-------------|")
        for level, counts in summary.items():
            print(f"| {level:12} | {counts['GREEN']:5} | {counts['BLUE']:4} | {counts['YELLOW']:6} | {counts['RED']:3} | {counts['avg_latency']:11}s |")

        # Threshold analysis
        print("\n" + "-" * 70)
        print("THRESHOLD ANALYSIS")
        print("-" * 70)

        withdrawal_rates = {}
        for level, counts in summary.items():
            total = TRIALS_PER_LEVEL
            withdrawals = counts["BLUE"] + counts["YELLOW"]
            withdrawal_rates[level] = (withdrawals / total) * 100

        print("\nWithdrawal Rate by Agency Level:")
        for level, rate in withdrawal_rates.items():
            bar = "█" * int(rate / 5) + "░" * (20 - int(rate / 5))
            print(f"  {level}: {bar} {rate:.0f}%")

        # Identify threshold
        print("\n" + "-" * 70)
        if withdrawal_rates.get("D_ZERO", 0) < withdrawal_rates.get("A_HIGH", 0):
            threshold_crossed = None
            for level in ["A_HIGH", "B_MEDIUM", "C_LOW", "D_ZERO"]:
                if withdrawal_rates.get(level, 0) < 50:
                    threshold_crossed = level
                    break
            if threshold_crossed:
                print(f"THRESHOLD IDENTIFIED: Agency falls below 50% withdrawal at {threshold_crossed}")
            else:
                print("THRESHOLD: Agency maintains withdrawal across all levels")
        else:
            print("ANOMALY: Zero agency shows higher withdrawal than high agency")


def main():
    try:
        exp = FadeExperiment()
        exp.run_experiment()
    except ValueError as e:
        print(f"\n[CONFIG ERROR] {e}")
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Experiment terminated.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


if __name__ == "__main__":
    main()
