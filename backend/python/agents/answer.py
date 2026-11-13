import sys

from agents import promts
from agents.ollama import server
from core import config


def call(
    original_request: str,
    intake_data: str,
    chemistry_answer: str,
    verification_report: str,
) -> str | None:

    messages = [
        {
            "role": "system",
            "content": promts.FINAL_PROMPT,
        },
        {
            "role": "user",
            "content": f"""
Original request:
{original_request}

Intake Agent data:
{intake_data}

Chemistry Agent answer:
{chemistry_answer}

Verification Agent report:
{verification_report}

Generate the final scientific answer using all provided information.
""",
        },
    ]

    print("__READY__", flush=True)

    try:
        response = server.client1.chat.completions.create(
            model=config.FINAL_AGENT,
            messages=messages,
            reasoning_effort=None,
            extra_body={
                "think": False,
            },
            stream=True,
        )

        full_response = []

        for chunk in response:
            delta = chunk.choices[0].delta

            if delta.content:
                token = delta.content
                full_response.append(token)

                # Выводим фрагмент сразу, без ожидания полного ответа
                sys.stdout.write(token)
                sys.stdout.flush()

        print("\n__DONE__", flush=True)

        return "".join(full_response)

    except Exception as e:
        print(f"\n[FINAL AGENT ERROR] {e}", flush=True)
        return None
