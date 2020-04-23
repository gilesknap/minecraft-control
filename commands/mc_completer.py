import readline
from pathlib import Path
import re
import logging

LOG_FILENAME = "/tmp/completer.log"
logging.basicConfig(
    filename=LOG_FILENAME, level=logging.DEBUG,
)


class Completer(object):
    def __init__(self, options):
        self.options = options
        self.current_candidates = []
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.

            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            logging.debug("origline=%s", repr(origline))
            logging.debug("begin=%s", begin)
            logging.debug("end=%s", end)
            logging.debug("being_completed=%s", being_completed)
            logging.debug("words=%s", words)

            if not words:
                self.current_candidates = sorted(self.options.keys())
            else:
                try:
                    if begin == 0:
                        # first word
                        candidates = self.options.keys()
                    else:
                        # later word
                        first = words[0]
                        candidates = self.options[first]

                    if being_completed:
                        # match options with portion of input
                        # being completed
                        self.current_candidates = [
                            w for w in candidates if w.startswith(being_completed)
                        ]
                    else:
                        # matching empty string so use all candidates
                        self.current_candidates = candidates

                    logging.debug("candidates=%s", self.current_candidates)

                except (KeyError, IndexError) as err:
                    logging.error("completion error: %s", err)
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        logging.debug("complete(%s, %s) => %s", repr(text), state, response)
        return response


def read_files():
    cmd_tree = {}

    folder = Path(__file__).parent
    with open(folder / "commands.txt") as f:
        commands = f.readlines()
    players = []
    with open(folder / "players.txt") as f:
        players = [p.strip() for p in f.readlines()]

    re_cmd = re.compile(r"\/([^ \n]+)([^\n]*)")
    re_target = re.compile(r"<target>|<targets>")
    re_keywords = re.compile(r"[\||(|[]([a-z,A-Z_*]+)")
    for line in commands:
        match = re_cmd.match(line)
        command = match.group(1)
        rest = match.group(2)

        keywords = re_keywords.findall(rest)
        targets = re_target.search(rest)
        if targets:
            keywords += players

        cmd_tree[command] = keywords

    return cmd_tree


def input_loop():
    line = ""
    while line != "":
        line = input("> ")
        print("Dispatch %s" % line)


# Register our completer function
command_tree = read_files()
completer = Completer(command_tree).complete
readline.set_completer(completer)

# Use the tab key for completion
readline.parse_and_bind("tab: complete")

# Prompt the user for text
input_loop()
