from openai import OpenAI


class OllamaServer:
    def __init__(self, client: OpenAI, client2: OpenAI):
        self.client1: OpenAI = client
        self.client2: OpenAI = client2


server = OllamaServer(
    client=OpenAI(
        base_url="http://192.168.1.44:11434/v1",
        api_key="ollama",  # Ollama не требует настоящего ключа
    ),
    client2=OpenAI(
        base_url="http://192.168.1.44:11435/v1",
        api_key="ollama",  # Ollama не требует настоящего ключа
    ),
)
