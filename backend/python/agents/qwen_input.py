import json

from agents.ollama import server
from core import config
from tools import tools


def call_qwen_input(request: str) -> str | None:
    messages = [
        {"role": "user", "content": request},
        {"role": "system", "content": "use tools is required."},
    ]

    for iteration in range(config.MAX_TOOLS_ITERATION_COLL):
        print(f"[INFO] Iteration {iteration}")

        response = server.client2.chat.completions.create(
            model=config.QWEN_MODEL,
            messages=messages,
            tools=tools.TOOLS,
            tool_choice="required",
            reasoning_effort=None,
            extra_body={"think": False, "reasoning_effort": "none"},
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        print(tool_calls)

        # Сохраняем assistant message вместе с tool_calls.
        messages.append(message.model_dump(exclude_none=True))

        if not tool_calls:
            return message.content

        for call in tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)

            print(f"[INFO] {name} tool call with args: {args}")

            function = tools.TOOLS_FUNTIONS_REGISTRY.get(name)

            if function is None:
                print(f"[ERROR] Unknown tool: {name}")
                result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    result = function(**args)
                except Exception as error:
                    print(f"[ERROR] {name} tool error: {error}")
                    result = {"error": str(error)}

            content = json.dumps(
                result,
                ensure_ascii=False,
                default=str,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": content,
                }
            )

    print("[ERROR] Maximum tool iterations reached")
    return None
