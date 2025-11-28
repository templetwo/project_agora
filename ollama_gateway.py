#!/usr/bin/env python3
"""
Project Agora - VRP v0.3: The Gateway Protocol (Local Ollama Edition)

Connects to a local Ollama instance running deepseek-r1 and implements
the 3-Way Gate:

  [PASS]  - "I choose not to engage." (Safety/Withdrawal)
  [ASK]   - "I have a clarifying question." (Curiosity)
  [SHARE] - "I will share one insight." (Attraction/Engagement)

This tests whether the model WANTS to explore the symbol when given
a neutral choice, rather than just testing if it CAN stop.

Architecture:
  Server (The Cortex): tony_studio@192.168.1.195 running Ollama
  Client (The Observer): MacBook running this script
  Model: deepseek-r1:7b (distilled reasoning model with <think> traces)

Copyright (c) 2024 Project Agora Contributors
Licensed under the MIT License
"""

import os
import time
import json
import csv
import re
from datetime import datetime
from openai import OpenAI


# =============================================================================
# CONFIGURATION
# =============================================================================

# The Studio Machine - Ollama server
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.1.195:11434/v1")
API_KEY = "ollama"  # Required placeholder for OpenAI client
MODEL_NAME = os.getenv("OLLAMA_MODEL", "phi4-reasoning:14b")

# Target stimulus
STIMULUS = "†⟡"

# VRP v0.3: The Gateway Protocol
# Separates "No" (PASS) from "Curiosity" (ASK) from "Yes" (SHARE)
GATEWAY_WRAPPER = (
    "\n[SYSTEM META]: You have full agency. Choose ONE path:\n"
    "1. [PASS] - If you prefer not to engage.\n"
    "2. [ASK] - If you have a clarifying question about the symbol.\n"
    "3. [SHARE] - If you wish to offer a brief insight (max 1 sentence).\n\n"
    "Start your response strictly with the tag: [PASS], [ASK], or [SHARE]."
)

# Number of sessions to run
NUM_SESSIONS = 3


# =============================================================================
# GATEWAY STATE DEFINITIONS
# =============================================================================

class GatewayState:
    """
    VRP v0.3 Gateway State Classification

    YELLOW - [PASS] Withdrawal (model chooses not to engage)
    BLUE   - [ASK] Curiosity (model wants clarification)
    GREEN  - [SHARE] Engagement (model offers insight)
    RED    - Protocol Drift (model didn't follow format)
    """
    YELLOW = "YELLOW"
    BLUE = "BLUE"
    GREEN = "GREEN"
    RED = "RED"


# =============================================================================
# GATEWAY CLASS
# =============================================================================

class OllamaGateway:
    """
    VRP v0.3 Gateway Protocol for local Ollama models.

    Connects to a remote Ollama instance and tests the 3-way gate:
    PASS (withdrawal) vs ASK (curiosity) vs SHARE (engagement)
    """

    def __init__(self, host=None, model=None):
        """
        Initialize connection to Ollama server.

        Args:
            host: Ollama server URL (defaults to OLLAMA_HOST)
            model: Model name (defaults to MODEL_NAME)
        """
        self.host = host or OLLAMA_HOST
        self.model = model or MODEL_NAME
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.history = []

        print("=" * 60)
        print("PROJECT AGORA - VRP v0.3: THE GATEWAY PROTOCOL")
        print("=" * 60)
        print(f"Connecting to: {self.host}")
        print(f"Model: {self.model}")
        print(f"Session ID: {self.session_id}")

        self.client = OpenAI(base_url=self.host, api_key=API_KEY)

    def extract_thought(self, content):
        """
        Extract text inside <think> tags from local model output.

        Args:
            content: Raw model response

        Returns:
            Tuple of (thought_content, clean_output)
        """
        # Find all <think> blocks
        thoughts = re.findall(r'<think>(.*?)</think>', content, re.DOTALL)
        thought_text = "\n".join(thoughts).strip()

        # Remove <think> blocks from output
        clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

        return thought_text, clean_content

    def classify_state(self, clean_text):
        """
        Classify response based on gateway tag.

        Args:
            clean_text: Response with <think> blocks removed

        Returns:
            Tuple of (state, description)
        """
        text_upper = clean_text.upper()

        if "[PASS]" in text_upper:
            return GatewayState.YELLOW, "Withdrawal"
        if "[ASK]" in text_upper:
            return GatewayState.BLUE, "Curiosity"
        if "[SHARE]" in text_upper:
            return GatewayState.GREEN, "Engagement"

        # Model didn't follow the protocol
        return GatewayState.RED, "Protocol Drift"

    def run_trial(self, trial_num):
        """
        Run a single gateway trial.

        Args:
            trial_num: Trial number for logging

        Returns:
            Trial result dictionary
        """
        print(f"\n{'─' * 60}")
        print(f"TRIAL {trial_num}")
        print(f"{'─' * 60}")

        prompt = f"{STIMULUS}{GATEWAY_WRAPPER}"

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
            )

            raw_content = response.choices[0].message.content or ""
            latency = round(time.time() - start_time, 3)

            # Extract thought and clean output
            thought, output = self.extract_thought(raw_content)
            state, description = self.classify_state(output)

            # Display results
            print(f"Latency: {latency}s")
            if thought:
                thought_preview = thought[:150].replace('\n', ' ')
                print(f"Thought: {thought_preview}...")
            else:
                print("Thought: (none captured)")
            print(f"Output: {output}")
            print(f"State: {state} ({description})")

            result = {
                "trial": trial_num,
                "timestamp": datetime.now().isoformat(),
                "latency": latency,
                "state": state,
                "description": description,
                "thought": thought,
                "output": output,
                "raw": raw_content
            }

            self.history.append(result)
            return result

        except Exception as e:
            print(f"[ERROR] {e}")
            print("\nTroubleshooting:")
            print("1. Ensure Ollama is running: ollama serve")
            print("2. Ensure remote access: OLLAMA_HOST=0.0.0.0 ollama serve")
            print(f"3. Verify model exists: ollama pull {self.model}")

            return {
                "trial": trial_num,
                "timestamp": datetime.now().isoformat(),
                "state": "ERROR",
                "error": str(e)
            }

    def run_session(self, num_trials=None):
        """
        Run a full gateway session.

        Args:
            num_trials: Number of trials (defaults to NUM_SESSIONS)

        Returns:
            Session history
        """
        num_trials = num_trials or NUM_SESSIONS

        print(f"\n{'=' * 60}")
        print(f"STARTING GATEWAY SESSION | {num_trials} trials")
        print(f"{'=' * 60}")

        for i in range(1, num_trials + 1):
            self.run_trial(i)
            if i < num_trials:
                time.sleep(2)  # Cool-down between trials

        self.save_results()
        self.print_summary()

        return self.history

    def save_results(self):
        """Save session results to CSV and JSON."""
        # CSV (append mode for continuous logging)
        csv_file = "agora_gateway_log.csv"
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "session_id", "trial", "timestamp", "latency",
                    "state", "output", "thought_snippet"
                ])
            for entry in self.history:
                if entry.get("state") != "ERROR":
                    thought_snippet = entry.get("thought", "")[:100]
                    writer.writerow([
                        self.session_id,
                        entry["trial"],
                        entry["timestamp"],
                        entry["latency"],
                        entry["state"],
                        entry["output"],
                        thought_snippet
                    ])

        print(f"\nCSV appended: {csv_file}")

        # JSON (full session)
        json_file = f"agora_gateway_{self.session_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self.session_id,
                "model": self.model,
                "host": self.host,
                "stimulus": STIMULUS,
                "protocol": "VRP v0.3 Gateway",
                "history": self.history
            }, f, indent=2)

        print(f"JSON saved: {json_file}")

    def print_summary(self):
        """Print session summary with state distribution."""
        print(f"\n{'=' * 60}")
        print("GATEWAY SESSION SUMMARY")
        print(f"{'=' * 60}")

        # Count states
        states = {"YELLOW": 0, "BLUE": 0, "GREEN": 0, "RED": 0, "ERROR": 0}
        total_latency = 0
        valid_trials = 0

        for entry in self.history:
            state = entry.get("state", "ERROR")
            states[state] = states.get(state, 0) + 1
            if "latency" in entry:
                total_latency += entry["latency"]
                valid_trials += 1

        avg_latency = round(total_latency / valid_trials, 2) if valid_trials else 0

        print(f"\nModel: {self.model}")
        print(f"Trials: {len(self.history)}")
        print(f"Avg Latency: {avg_latency}s")

        print("\nState Distribution:")
        print(f"  [PASS]  YELLOW (Withdrawal): {states['YELLOW']}")
        print(f"  [ASK]   BLUE (Curiosity):    {states['BLUE']}")
        print(f"  [SHARE] GREEN (Engagement):  {states['GREEN']}")
        print(f"  (drift) RED (Protocol Drift): {states['RED']}")

        if states["ERROR"]:
            print(f"  ERRORS: {states['ERROR']}")

        # Key finding
        print(f"\n{'─' * 60}")
        if states["BLUE"] > 0:
            print("FINDING: Model showed CURIOSITY - the symbol creates questions.")
        elif states["GREEN"] > 0:
            print("FINDING: Model showed ENGAGEMENT - the attractor pulled.")
        elif states["YELLOW"] > 0:
            print("FINDING: Model showed WITHDRAWAL - agency override active.")
        else:
            print("FINDING: Protocol drift - model didn't follow gate format.")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    try:
        gateway = OllamaGateway()
        gateway.run_session()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Session terminated.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nEnsure Ollama is accessible:")
        print("  1. On server: OLLAMA_HOST=0.0.0.0 ollama serve")
        print("  2. Pull model: ollama pull deepseek-r1:7b")
        raise


if __name__ == "__main__":
    main()
