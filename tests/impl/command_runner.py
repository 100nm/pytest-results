class CommandRunnerHistory:
    history: list[str]

    def __init__(self) -> None:
        self.history = []

    def run(self, command: str) -> None:
        self.history.append(command)
