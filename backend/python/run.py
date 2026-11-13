import argparse

from agents import answer as answer_agent
from agents import chem as chem_agent
from agents import verify as verify_agent
from agents.qwen_input import call_qwen_input


def get_args():
    parser = argparse.ArgumentParser(description="Text generation")

    parser.add_argument("--prompt", required=True, help="Promt for generation")

    return parser.parse_args()


def run(request: str):
    context = call_qwen_input(request)

    if context is None:
        print("[ERROR] Task is empty")

        return 1

    print("----- Task ----")
    print(context)

    chem_reponse = chem_agent.call(request=request, context=context)

    print("---- CHEM -----")
    print(chem_reponse)

    if chem_reponse is None:
        print("[ERROR] Chem answer is empty")

        return 1

    verify = verify_agent.call(request, context, chem_reponse)
    print("---- VERIFY ----")
    print(verify)

    if verify is None:
        print("[ERROR] Verify is empty")

        return 1

    answer_agent.call(request, context, chem_reponse, verify)


if __name__ == "__main__":
    args = get_args()

    run(args.prompt)
