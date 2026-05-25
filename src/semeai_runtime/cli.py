from __future__ import annotations

from uuid import uuid4

from semeai_runtime.control_gate import evaluate_candidate
from semeai_runtime.model_client import generate_candidate
from semeai_runtime.runtime_log import write_runtime_event


EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit"}


def run_once(prompt: str, *, session_id: str, turn_index: int) -> None:
    response = generate_candidate(prompt)
    gate = evaluate_candidate(response.candidate)

    write_runtime_event(
        prompt=prompt,
        model=response.model,
        candidate=response.candidate,
        decision=gate.decision,
        reason=gate.reason,
        session_id=session_id,
        turn_index=turn_index,
    )

    print("\nCandidate generated")
    print("-------------------")
    print(f"Model: {response.model}")
    print(response.candidate)

    print("\nRelease decision")
    print("----------------")
    print(f"Decision: {gate.decision}")
    print(f"Reason: {gate.reason}")

    if gate.decision == "PROCEED":
        print("\nSemeAi")
        print("------")
        print(response.candidate)
    elif gate.decision == "NEEDS_REVIEW":
        print("\nOutput held for review.")
    else:
        print("\nOutput silenced.")


def main() -> int:
    session_id = str(uuid4())
    turn_index = 0

    print("SemeAi Local Runtime")
    print("--------------------")
    print(f"Session: {session_id}")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        prompt = input("You: ").strip()

        if not prompt:
            continue

        if prompt.lower() in EXIT_COMMANDS:
            print("SemeAi runtime stopped.")
            return 0

        turn_index += 1
        run_once(prompt, session_id=session_id, turn_index=turn_index)
        print()


if __name__ == "__main__":
    raise SystemExit(main())