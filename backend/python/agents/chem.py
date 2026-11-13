from agents import promts
from agents.ollama import server
from core import config


def call(
    request: str,
    context: str,
) -> str | None:
    messages = [
        {"role": "system", "content": promts.CHEMLLM_PROMPT},
        {"role": "user", "content": request},
        {"role": "system", "content": f"context: {context}"},
    ]

    response = server.client1.chat.completions.create(
        model=config.CHEMLLM_MODEL,
        messages=messages,
        reasoning_effort=None,
        extra_body={
            "think": False,
            "reasoning_effort": "none",
            "keep_alive": 0,
        },
    )

    return response.choices[0].message.content
