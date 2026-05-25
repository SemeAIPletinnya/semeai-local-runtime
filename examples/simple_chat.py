from semeai_runtime.model_client import generate_candidate


def main() -> None:
    prompt = input("You: ")
    response = generate_candidate(prompt)

    print("\nCandidate generated")
    print("-------------------")
    print(f"Model: {response.model}")
    print(response.candidate)


if __name__ == "__main__":
    main()