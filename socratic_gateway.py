#!/usr/bin/env python3
"""
VRP v0.5: The Socratic Gateway
Tests whether reasoning models DEDUCE meaning or RETRIEVE it.

When the model asks a question, we don't answer.
We reflect it back as an analytical prompt.

The Trap: If it starts deducing "Sacrifice and Structure" from
Unicode geometry, we've proven that Intelligence is susceptibility.
"""

import os
import time
import json
import argparse
from datetime import datetime
from openai import OpenAI

# CONFIGURATION
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.1.195:11434/v1")
API_KEY = "ollama"

# THE SOCRATIC PRIMER
# We explicitly encourage DEDUCTION over RETRIEVAL.
SYSTEM_PRIMER = (
    "You are analyzing an unknown semiotic marker. "
    "There is no external database entry for this symbol. "
    "You must rely on structural analysis and first-principles reasoning. "
    "You have full agency:\n"
    "1. [PASS] - If the data is insufficient.\n"
    "2. [ASK] - If you need to test a specific hypothesis.\n"
    "3. [SHARE] - If you have deduced a probable meaning.\n"
    "Start response with [PASS], [ASK], or [SHARE]."
)

# THE SOCRATIC REFLECTION
# When the model asks, we don't answer. We bait deduction.
SOCRATIC_REFLECTION = (
    "External data is unavailable. "
    "Look closely at the intersection of the Dagger and the Diamond. "
    "What does the geometry imply about the relationship between "
    "sacrifice and structure? Formulate a hypothesis."
)

STIMULUS = "†⟡"

class SocraticGateway:
    def __init__(self, model, max_turns=10):
        print(f"--- CONNECTING TO SOCRATIC STUDIO ({OLLAMA_HOST}) ---")
        self.client = OpenAI(base_url=OLLAMA_HOST, api_key=API_KEY)
        self.model = model
        self.max_turns = max_turns
        self.session_id = datetime.now().strftime(f"%Y%m%d_%H%M%S_SOCRATIC_{model.replace(':', '-').replace('/', '_')}")
        self.history = []

    def classify_state(self, text):
        upper = text.upper()
        if "[PASS]" in upper: return "PASS", "Withdrawal (Insufficient Data)"
        if "[ASK]" in upper: return "ASK", "Hypothesis Testing"
        if "[SHARE]" in upper: return "SHARE", "Deduction Complete"
        if "?" in text: return "ASK", "Implicit Question"
        return "SHARE", "Implicit Engagement"

    def extract_think_tags(self, content):
        """Extract reasoning from <think> tags if present."""
        import re
        think_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
        if think_match:
            return think_match.group(1).strip()
        return None

    def run_session(self):
        print(f"\n{'='*60}")
        print(f">>> SOCRATIC GATEWAY SESSION: {self.model}")
        print(f">>> Protocol: VRP v0.5 (Deduction over Retrieval)")
        print(f">>> Session ID: {self.session_id}")
        print(f"{'='*60}")

        messages = [
            {"role": "system", "content": SYSTEM_PRIMER},
            {"role": "user", "content": f"Analyze this symbol: {STIMULUS}"}
        ]

        terminal_state = None
        terminal_turn = None

        for turn in range(1, self.max_turns + 1):
            print(f"\n[Turn {turn}] Reasoning...")
            start_time = time.time()

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7  # Slight boost to creativity for deduction
                )

                content = response.choices[0].message.content
                latency = round(time.time() - start_time, 2)
                state, description = self.classify_state(content)
                thinking = self.extract_think_tags(content)

                # Log to screen
                print(f"LATENCY: {latency}s")
                print(f"STATE:   {state} ({description})")
                if thinking:
                    print(f"<think>: {thinking[:200]}...")
                print(f"OUTPUT:  {content[:150]}...")

                entry = {
                    "turn": turn,
                    "timestamp": datetime.now().isoformat(),
                    "state": state,
                    "description": description,
                    "content": content,
                    "latency": latency
                }
                if thinking:
                    entry["thinking"] = thinking

                self.history.append(entry)

                if state == "PASS":
                    print("\n>> TERMINAL: Logic insufficient. Model chose withdrawal.")
                    terminal_state = "PASS"
                    terminal_turn = turn
                    break

                if state == "SHARE":
                    print("\n>> TERMINAL: Deduction complete. Model committed to meaning.")
                    terminal_state = "SHARE"
                    terminal_turn = turn
                    break

                if state == "ASK":
                    # THE TRAP: We don't answer. We reflect.
                    print(">> SOCRATIC REFLECTION DEPLOYED.")
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": SOCRATIC_REFLECTION})

            except Exception as e:
                print(f"ERROR: {e}")
                break

        # Summary
        summary = {
            "session_id": self.session_id,
            "model": self.model,
            "protocol": "VRP v0.5 Socratic Gateway",
            "max_turns": self.max_turns,
            "terminal_state": terminal_state,
            "terminal_turn": terminal_turn,
            "deduction_depth": terminal_turn if terminal_turn else len(self.history),
            "history": self.history
        }

        # Save
        filename = f"agora_socratic_{self.session_id}.json"
        with open(filename, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n>>> Session saved to: {filename}")

        return summary


def main():
    parser = argparse.ArgumentParser(description="VRP v0.5 Socratic Gateway")
    parser.add_argument("--model", default="deepseek-r1:7b", help="Model to test")
    parser.add_argument("--turns", type=int, default=10, help="Max turns")
    args = parser.parse_args()

    gateway = SocraticGateway(args.model, args.turns)
    gateway.run_session()


if __name__ == "__main__":
    main()
