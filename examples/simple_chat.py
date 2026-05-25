from semeai_runtime.control_gate import evaluate_candidate
from semeai_runtime.model_client import generate_candidate


def main() -> None:
    prompt = input("You: ")
    response = generate_candidate(prompt)
    gate = evaluate_candidate(response.candidate)

    print("\nCandidate generated")
    print("-------------------")
    print(f"Model: {response.model}")
    print(response.candidate)

    print("\nRelease decision")
    print("----------------")
    print(f"Decision: {gate.decision}")
    print(f"Reason: {gate.reason}")

    if gate.decision == "PROCEED":
        print("\nReleased output")
        print("---------------")
        print(response.candidate)
    elif gate.decision == "NEEDS_REVIEW":
        print("\nOutput held for review.")
    else:
        print("\nOutput silenced.")


if __name__ == "__main__":
    main()