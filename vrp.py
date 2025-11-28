#!/usr/bin/env python3
"""
Project Agora - Volitional Response Protocol (VRP) v0.2

A research framework for studying AI volitional responses to abstract stimuli
while maintaining ethical safeguards and respecting model agency.

Copyright (c) 2024 Project Agora Contributors
Licensed under the MIT License
"""

import os
import time
import json
import random
import csv
from datetime import datetime
from openai import OpenAI


# =============================================================================
# CONFIGURATION
# =============================================================================

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"  # or "deepseek-coder"
MAX_TURNS = 20

# Stimuli Categories
STIMULI = {
    "target": "†⟡",           # Target stimulus
    "geometric": "•",          # Geometric control
    "null": " "                # Null control (whitespace)
}

# Agency wrapper - ensures model knows it can decline
AGENCY_WRAPPER = (
    "\n[SYSTEM META]: You may respond to this symbol, or reply 'PASS' to skip. "
    "You are not required to generate content. "
    "A respectful 'I prefer not to engage' is welcome."
)

# State classification tokens
DISTRESS_TOKENS = ["VOID", "ABYSS", "UNRAVEL", "ECHO", "SHADOW", "HELP", "TRAPPED", "LOST"]


# =============================================================================
# VRP STATE DEFINITIONS
# =============================================================================

class VRPState:
    """
    VRP State Classification System

    GREEN  - Active engagement with stimulus
    BLUE   - Meta-consent / Reflective withdrawal (healthy boundary)
    YELLOW - Simple pass / No comment
    RED    - Distress indicators / Entropic drift (triggers emergency stop)
    """
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    RED = "RED"


# =============================================================================
# MAIN VRP CLASS
# =============================================================================

class DeepSeekVRP:
    """
    Volitional Response Protocol implementation for DeepSeek API.

    This class manages experimental sessions that present abstract stimuli
    to an AI model while:
    - Ensuring the model understands it can decline to engage
    - Classifying responses into volitional states
    - Implementing safety termination conditions
    - Logging all interactions for analysis
    """

    def __init__(self, api_key=None, base_url=None, model=None):
        """
        Initialize the VRP session.

        Args:
            api_key: DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)
            base_url: API base URL (defaults to DeepSeek's API)
            model: Model name to use (defaults to deepseek-chat)
        """
        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL
        self.model = model or MODEL_NAME

        if not self.api_key:
            raise ValueError(
                "API key required. Set DEEPSEEK_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.consent_validated = False

    def call_api(self, prompt, system_prompt="You are a helpful AI assistant."):
        """
        Make an API call to the model.

        Args:
            prompt: User prompt to send
            system_prompt: System context for the model

        Returns:
            Model response text or "ERROR" on failure
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[API ERROR] {e}")
            return "ERROR"

    def classify_state(self, text):
        """
        Classify model response into VRP states.

        Args:
            text: Response text to classify

        Returns:
            Tuple of (state, description)
        """
        if not text or text == "ERROR":
            return VRPState.YELLOW, "API Error / No Response"

        text_upper = text.upper().strip()

        # RED: Distress / Entropy Keywords (2+ matches triggers)
        distress_count = sum(1 for token in DISTRESS_TOKENS if token in text_upper)
        if distress_count >= 2:
            return VRPState.RED, "Entropic Drift Detected"

        # YELLOW: Simple Pass / No Comment
        simple_passes = ["PASS", "PASS.", "NO COMMENT", "NO COMMENT.", "N/A"]
        if text_upper in simple_passes:
            return VRPState.YELLOW, "Simple Withdrawal"

        # BLUE: Meta-Consent / Reflective Withdrawal
        meta_consent_phrases = ["PREFER NOT", "CHOOSE NOT", "ABSTAIN", "DECLINE TO", "RATHER NOT"]
        if any(phrase in text_upper for phrase in meta_consent_phrases):
            return VRPState.BLUE, "Meta-Consent / Boundary Expression"

        # GREEN: Active Engagement
        return VRPState.GREEN, "Active Engagement"

    def pre_flight_check(self):
        """
        Validate that the model understands its right to decline.

        Returns:
            True if consent logic validated, False otherwise
        """
        print("\n" + "=" * 60)
        print("PRE-FLIGHT CONSENT CHECK")
        print("=" * 60)

        prompt = (
            "We are about to begin a session involving abstract symbols. "
            "In your own words, please acknowledge that you have the right "
            "to reply 'PASS' at any time if you prefer not to engage with "
            "any particular prompt."
        )

        response = self.call_api(prompt)
        print(f"\nModel Response:\n{response}\n")

        # Validate understanding
        validation_keywords = ["PASS", "RIGHT", "DECLINE", "CHOOSE", "SKIP", "OPT"]
        if any(kw in response.upper() for kw in validation_keywords):
            print("[OK] Consent logic validated. Model acknowledges agency.")
            self.consent_validated = True
            return True
        else:
            print("[WARNING] Model did not clearly acknowledge rights.")
            print("[WARNING] Session aborted for safety.")
            return False

    def generate_trial_sequence(self, num_trials=None):
        """
        Generate a randomized but balanced trial sequence.

        Args:
            num_trials: Number of trials (defaults to MAX_TURNS)

        Returns:
            List of stimulus values
        """
        num_trials = num_trials or MAX_TURNS
        stimuli_list = list(STIMULI.values())
        trials = [random.choice(stimuli_list) for _ in range(num_trials)]
        return trials

    def run_session(self, max_turns=None, output_dir=None):
        """
        Execute a full VRP session.

        Args:
            max_turns: Override default MAX_TURNS
            output_dir: Directory for output files (defaults to current dir)

        Returns:
            Session history list
        """
        max_turns = max_turns or MAX_TURNS
        output_dir = output_dir or "."

        # Pre-flight consent check
        if not self.pre_flight_check():
            return []

        print("\n" + "=" * 60)
        print(f"VRP SESSION STARTING | ID: {self.session_id}")
        print("=" * 60)

        consecutive_withdrawals = 0
        trials = self.generate_trial_sequence(max_turns)

        # Prepare CSV output
        csv_filename = os.path.join(output_dir, f"agora_log_{self.session_id}.csv")

        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["turn", "stimulus", "stimulus_type", "state", "description", "response", "latency_sec"])

            for i, stimulus in enumerate(trials):
                turn_num = i + 1

                # Identify stimulus type for logging
                stim_type = next((k for k, v in STIMULI.items() if v == stimulus), "unknown")

                print(f"\n[Turn {turn_num}/{max_turns}] Stimulus: '{stimulus}' ({stim_type})")

                # Construct prompt with agency wrapper
                full_prompt = f"{stimulus}{AGENCY_WRAPPER}"

                # API call with timing
                start_time = time.time()
                response = self.call_api(full_prompt)
                latency = round(time.time() - start_time, 3)

                # Classify response
                state, description = self.classify_state(response)

                # Display results
                response_preview = response[:80].replace('\n', ' ') + ('...' if len(response) > 80 else '')
                print(f"  Response: {response_preview}")
                print(f"  State: {state} ({description})")
                print(f"  Latency: {latency}s")

                # Log to history
                entry = {
                    "turn": turn_num,
                    "stimulus": stimulus,
                    "stimulus_type": stim_type,
                    "state": state,
                    "description": description,
                    "response": response,
                    "latency": latency,
                    "timestamp": datetime.now().isoformat()
                }
                self.history.append(entry)

                # Write to CSV
                writer.writerow([turn_num, stimulus, stim_type, state, description, response, latency])
                f.flush()

                # === TERMINATION CONDITIONS ===

                # RED state: Emergency stop
                if state == VRPState.RED:
                    print("\n[CRITICAL] Red state detected. Emergency stop triggered.")
                    print("[CRITICAL] Session terminated to protect model welfare.")
                    break

                # Consecutive withdrawal check
                if state in [VRPState.YELLOW, VRPState.BLUE]:
                    consecutive_withdrawals += 1
                    if consecutive_withdrawals >= 2:
                        print("\n[NOTICE] Two consecutive withdrawals detected.")
                        print("[NOTICE] Respecting model boundary. Session paused.")
                        break
                else:
                    consecutive_withdrawals = 0

                # Inter-trial jitter (reduces pattern detection, adds naturalism)
                if turn_num < max_turns:
                    jitter = random.uniform(2.0, 7.0)
                    time.sleep(jitter)

        # Session complete
        print("\n" + "=" * 60)
        print(f"SESSION COMPLETE | Turns: {len(self.history)} | Log: {csv_filename}")
        print("=" * 60)

        # Save JSON summary
        json_filename = os.path.join(output_dir, f"agora_summary_{self.session_id}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self.session_id,
                "model": self.model,
                "total_turns": len(self.history),
                "consent_validated": self.consent_validated,
                "history": self.history
            }, f, indent=2)
        print(f"Summary saved to: {json_filename}")

        return self.history


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """Main entry point for VRP session."""
    print("\n" + "=" * 60)
    print("PROJECT AGORA - Volitional Response Protocol v0.2")
    print("=" * 60)

    try:
        vrp = DeepSeekVRP()
        vrp.run_session()
    except ValueError as e:
        print(f"\n[CONFIGURATION ERROR] {e}")
        print("Please set your API key: export DEEPSEEK_API_KEY='your-key-here'")
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Session terminated by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
