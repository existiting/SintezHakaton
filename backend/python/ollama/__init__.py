from ollama import Client


class OllamaServer:
    def __init__(self):
        self.client = Client(Host="http://127.0.0.1:11434")


if __name__ == "__main__":
    server = OllamaServer()

    print(server.client.list())
