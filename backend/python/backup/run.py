#!/usr/bin/env python3
"""
AI Token Stream Emulator
Эмулирует загрузку ИИ и потоковую генерацию токенов.
"""

import random
import sys
import time

# --- Настройки ---
LOAD_TIME = 1.0  # Время "загрузки" ИИ (секунды)
TOKEN_DELAY_MIN = 0.50  # Минимальная задержка между токенами
TOKEN_DELAY_MAX = 1  # Максимальная задержка между токенами

SAMPLE_TEXT = (
    "Привет! Я языковая модель, работающая в потоковом режиме. "
    "Каждое слово появляется постепенно, имитируя реальную генерацию токенов. "
    "Такой подход позволяет пользователю видеть ответ в режиме реального времени, "
    "не дожидаясь полной обработки запроса."
)


def tokenize(text: str) -> list[str]:
    """Разбивает текст на псевдо-токены (слова + пробелы)."""
    tokens = []
    for word in text.split(" "):
        tokens.append(word)
        tokens.append(" ")
    return tokens[:-1]


def stream_tokens(tokens: list[str]) -> None:
    """Выводит токены с псевдослучайной задержкой."""
    for token in tokens:
        sys.stdout.write(token)
        sys.stdout.flush()
        sys.stdout.write("\n")
        time.sleep(random.uniform(TOKEN_DELAY_MIN, TOKEN_DELAY_MAX))


def main() -> None:
    print("__READY__", flush=True)
    time.sleep(0.1)

    tokens = tokenize(SAMPLE_TEXT)
    stream_tokens(tokens)
    print()

    print("__DONE__")


if __name__ == "__main__":
    main()
