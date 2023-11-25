from colorama import Fore, init


class Debug:
    def __init__(self, enabled):
        self.enabled = enabled
        init(True)
    def success(self, text):
        if self.enabled:
            print(f"[{Fore.GREEN}✓{Fore.RESET}] {text}")
    def error(self, text):
        if self.enabled:
            print(f"[{Fore.RED}✗{Fore.RESET}] {text}")