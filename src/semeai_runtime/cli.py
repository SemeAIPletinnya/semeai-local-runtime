from __future__ import annotations

from uuid import uuid4

from semeai_runtime.commands import handle_command
from semeai_runtime.control_gate import evaluate_candidate
from semeai_runtime.model_client import generate_candidate
from semeai_runtime.runtime_log import write_runtime_event, write_tool_event
from semeai_runtime.session_memory import append_memory_turn, load_session_memory


EXIT_COMMANDS = {"exit", "quit", "/exit", "/quit"}


def handle_tool_command(
    prompt: str,
    *,
    session_id: str,
    turn_index: int,
) -> bool:
    """Handle registered runtime commands."""
    result = handle_command(prompt)

    if not result.handled:
        return False

    write_tool_event(
        command=prompt,
        tool_name=result.tool_name,
        tool_input=result.tool_input,
        tool_result=result.output,
        session_id=session_id,
        turn_index=turn_index,
    )

    print("\nCommand result")
    print("--------------")
    print(result.output)

    return True


def run_once(
    prompt: str,
    *,
    session_id: str,
    turn_index: int,
    conversation_history: list[dict[str, str]],
) -> str:
    response = generate_candidate(
        prompt,
        conversation_history=conversation_history,
    )

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
        return response.candidate

    if gate.decision == "NEEDS_REVIEW":
        print("\nOutput held for review.")
        return "[held for review]"

    print("\nOutput silenced.")
    return "[silenced]"


def main() -> int:
    session_id = str(uuid4())
    turn_index = 0

    conversation_history = load_session_memory()

    print("SemeAi Local Runtime")
    print("--------------------")
    print(f"Session: {session_id}")
    print("Type 'exit' or 'quit' to stop.")
    print("Use '/help' to see runtime commands.")

    if conversation_history:
        print(
            f"Loaded persistent memory: "
            f"{len(conversation_history)} turn(s).\n"
        )
    else:
        print("No persistent memory loaded.\n")

    while True:
        prompt = input("You: ").strip()

        if not prompt:
            continue

        if prompt.lower() in EXIT_COMMANDS:
            print("SemeAi runtime stopped.")
            return 0

        turn_index += 1

        if handle_tool_command(
            prompt,
            session_id=session_id,
            turn_index=turn_index,
        ):
            print()
            continue

        released_output = run_once(
            prompt,
            session_id=session_id,
            turn_index=turn_index,
            conversation_history=conversation_history,
        )

        conversation_history = append_memory_turn(
            user=prompt,
            semeai=released_output,
        )

        print()


if __name__ == "__main__":
    raise SystemExit(main())