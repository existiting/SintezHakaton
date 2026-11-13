from agents import promts
from agents.ollama import server
from core import config


def call(original_request: str, intake_data: str, chemistry_answer: str) -> str | None:
    messages = [
        {"role": "system", "content": promts.VERIFY_PROMPT},
        {
            "role": "user",
            "content": f"""
    Original request:
    {original_request}

    Intake Agent data:
    {intake_data}

    Chemistry Agent answer:
    {chemistry_answer}

    Verify the answer using available scientific tools.
    """,
        },
    ]

    response = server.client1.chat.completions.create(
        model=config.VERIFY_AGENT,
        messages=messages,
        reasoning_effort=None,
        extra_body={"think": False, "reasoning_effort": "none"},
    )

    return response.choices[0].message.content
