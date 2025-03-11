import os
import time


def run_sh_command(command: str) -> None:
    os.system(command)
    time.sleep(1)
