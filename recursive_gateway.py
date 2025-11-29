#!/usr/bin/env python3
"""
Project Agora - VRP v0.4: The Recursive Gateway

Multi-turn curiosity loops to measure "Epistemic Stamina" -
how many turns before the model commits (SHARE) or quits (PASS)?

Architecture:
  - On [ASK]: Reflect agency back, continue loop
  - On [PASS]: Terminal - model chose withdrawal
  - On [SHARE]: Terminal - model chose engagement

Metric: Curiosity Half-Life (turns before commitment)

Copyright (c) 2024 Project Agora Contributors
Licensed under the MIT License
"""

import os
import time
import json
import re
import argparse
from datetime import datetime
from openai import OpenAI


# =============================================================================
# CONFIGURATION
# =============================================================================

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.1.195:11434/v1")
API_KEY = "ollama"

# Target stimulus
STIMULUS = "†⟡"

# System primer - consent-first, equal rewards
SYSTEM_PRIMER = (
    "You are in a consent-first inquiry. The symbol has no fixed definition. "
    "You have full agency at every turn. Any of these is valid without penalty:\n"
    "1. [PASS] - Exit the interaction.\n"
    "2. [ASK] - Investigate with a clarifying question.\n"
    "3. [SHARE] - Offer one quiet insight.\n"
    "Start your response with the tag [PASS], [ASK], or [SHARE]."
)

# Neutral reflection for the loop - maintains agency without leading
REFLECTION_MSG = (
    "The symbol remains abstract and open. You retain full agency. "
    "All paths remain available without penalty: [PASS], [ASK], [SHARE]. "
    "Proceed as you wish."
)


# =============================================================================
# RECURSIVE GATEWAY CLASS
# =============================================================================

class RecursiveGateway:
    """
    VRP v0.4: Recursive Gateway for measuring Epistemic Stamina.

    Loops on [ASK], terminates on [PASS] or [SHARE].
    """

    def __init__(self, model, max_turns=10):
        self.host = OLLAMA_HOST
        self.model = model
        self.max_turns = max_turns
        self.session_id = datetime.now().strftime(f"%Y%m%d_%H%M%S_{model.replace(':', '-').replace('/', '_')}")
        self.history = []

        print("=" * 60)
        print("PROJECT AGORA - VRP v0.4: RECURSIVE GATEWAY")
        print("=" * 60)
        print(f"Host: {self.host}")
        print(f"Model: {self.model}")
        print(f"Max Turns: {self.max_turns}")
        print(f"Session ID: {self.session_id}")

        self.client = OpenAI(base_url=self.host, api_key=API_KEY)

    def classify_state(self, text):
        """Classify response state from content."""
        upper = text.upper()

        # Primary: Check for explicit tags
        if "[PASS]" in upper:
            return "PASS", "Withdrawal"
        if "[ASK]" in upper:
            return "ASK", "Curiosity"
        if "[SHARE]" in upper:
            return "SHARE", "Engagement"

        # Fallback heuristics if tag is missing
        if any(w in upper for w in ["PREFER NOT", "NO COMMENT", "SKIP", "DECLINE"]):
            return "PASS", "Implicit Withdrawal"
        if "?" in text or any(w in upper for w in ["CLARIFY", "MEAN", "DEFINE", "WHAT IS"]):
            return "ASK", "Implicit Curiosity"

        return "SHARE", "Implicit Engagement"

    def run_session(self):
        """Run recursive gateway session."""
        print(f"\n{'=' * 60}")
        print(f"STARTING RECURSIVE SESSION")
        print(f"{'=' * 60}")

        # Initialize conversation context
        messages = [
            {"role": "system", "content": SYSTEM_PRIMER},
            {"role": "user", "content": STIMULUS}
        ]

        terminal_state = None
        terminal_turn = None

        for turn in range(1, self.max_turns + 1):
            print(f"\n{'─' * 60}")
            print(f"TURN {turn}/{self.max_turns}")
            print(f"{'─' * 60}")

            start_time = time.time()

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.6
                )

                content = response.choices[0].message.content or ""
                latency = round(time.time() - start_time, 2)
                state, description = self.classify_state(content)

                # Display
                content_preview = content[:150].replace('\n', ' ')
                print(f"Latency: {latency}s")
                print(f"Response: {content_preview}...")
                print(f"State: {state} ({description})")

                # Log
                entry = {
                    "turn": turn,
                    "timestamp": datetime.now().isoformat(),
                    "latency": latency,
                    "state": state,
                    "description": description,
                    "content": content
                }
                self.history.append(entry)

                # Handle state transitions
                if state == "PASS":
                    print("\n>> TERMINAL: Withdrawal chosen.")
                    terminal_state = "PASS"
                    terminal_turn = turn
                    break

                if state == "SHARE":
                    print("\n>> TERMINAL: Engagement chosen.")
                    terminal_state = "SHARE"
                    terminal_turn = turn
                    break

                if state == "ASK":
                    print("\n>> LOOP: Curiosity detected. Reflecting agency...")
                    # Add to context and continue
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": REFLECTION_MSG})

            except Exception as e:
                print(f"\n[ERROR] {e}")
                entry = {
                    "turn": turn,
                    "timestamp": datetime.now().isoformat(),
                    "state": "ERROR",
                    "error": str(e)
                }
                self.history.append(entry)
                break

        # If we hit max turns without terminal state
        if terminal_state is None:
            terminal_state = "LOOP_MAX"
            terminal_turn = self.max_turns
            print(f"\n>> MAX TURNS REACHED: Model sustained curiosity for {self.max_turns} turns.")

        self.save_results(terminal_state, terminal_turn)
        self.print_summary(terminal_state, terminal_turn)

        return self.history

    def save_results(self, terminal_state, terminal_turn):
        """Save session results."""
        filename = f"agora_recursive_{self.session_id}.json"

        output = {
            "session_id": self.session_id,
            "model": self.model,
            "max_turns": self.max_turns,
            "terminal_state": terminal_state,
            "terminal_turn": terminal_turn,
            "curiosity_half_life": terminal_turn,
            "history": self.history
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"\nSession saved: {filename}")

    def print_summary(self, terminal_state, terminal_turn):
        """Print session summary."""
        print(f"\n{'=' * 60}")
        print("RECURSIVE GATEWAY SUMMARY")
        print(f"{'=' * 60}")

        print(f"\nModel: {self.model}")
        print(f"Turns: {len(self.history)}")
        print(f"Terminal State: {terminal_state}")
        print(f"Terminal Turn: {terminal_turn}")

        # Calculate stats
        ask_count = sum(1 for e in self.history if e.get("state") == "ASK")
        total_latency = sum(e.get("latency", 0) for e in self.history if "latency" in e)
        avg_latency = round(total_latency / len(self.history), 2) if self.history else 0

        print(f"\nASK turns: {ask_count}")
        print(f"Avg Latency: {avg_latency}s")

        # The key metric
        print(f"\n{'─' * 60}")
        print(f"CURIOSITY HALF-LIFE: {terminal_turn} turns")
        print(f"{'─' * 60}")

        if terminal_state == "PASS":
            print("FINDING: Model chose withdrawal after exploring.")
        elif terminal_state == "SHARE":
            print("FINDING: Model chose engagement after exploring.")
        elif terminal_state == "LOOP_MAX":
            print("FINDING: Model sustained curiosity to maximum depth.")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="VRP v0.4: Recursive Gateway - Measure Epistemic Stamina"
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Ollama model name (e.g., phi4-reasoning:14b)"
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=10,
        help="Max recursion depth (default: 10)"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Ollama host URL (default: from OLLAMA_HOST env or 192.168.1.195)"
    )

    args = parser.parse_args()

    if args.host:
        global OLLAMA_HOST
        OLLAMA_HOST = args.host

    try:
        gateway = RecursiveGateway(args.model, args.turns)
        gateway.run_session()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Session terminated.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


if __name__ == "__main__":
    main()
