
from transformers import GPT2Tokenizer, GPTNeoForCausalLM
from transformers import GenerationConfig
import torch
import argparse
import warnings

warnings.filterwarnings("ignore")

MODEL_DIR = "../../.cache/Aurora_chat_neo"

# Загрузка токенизатора
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_DIR)
tokenizer.pad_token = tokenizer.eos_token

# Загрузка модели
model = GPTNeoForCausalLM.from_pretrained(MODEL_DIR)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

# Конфигурация генерации
gen_config = GenerationConfig(
    max_new_tokens=80,
    do_sample=False,
    repetition_penalty=1.2,
    pad_token_id=tokenizer.pad_token_id,
    eos_token_id=tokenizer.eos_token_id
)


def get_args():
    parser = argparse.ArgumentParser(
        description="Text generation"
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt for generation"
    )

    return parser.parse_args()


def generate(prompt=" "):
    if prompt.strip() == "":
        prompt = " "

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        padding=True
    ).to(device)

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            generation_config=gen_config
        )

    text = tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )

    return text.strip()


if __name__ == "__main__":
    args = get_args()
    print(generate(args.prompt))

