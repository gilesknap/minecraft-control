import sys


class Chooser:
    def __init__(self, prompt, actions):
        self.prompt = prompt
        self.actions = actions

    def ask(self):
        while True:
            print(f"\n{self.prompt}")
            response = sys.stdin.readline().strip("\n")
            if not response:
                return None
            elif response in self.actions:
                return response
            else:
                print("invalid entry")
