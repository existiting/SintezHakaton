from dataclasses import dataclass

VALID_TYPES = {"chemistry_task", "clarification", "non_chemistry", "refused"}
ALL_TAGS = ["language", "type", "chemllm_prompt", "user_message", "notes"]


@dataclass
class Intake:
    language: str
    type: str
    chemllm_prompt: str
    user_message: str
    notes: str
