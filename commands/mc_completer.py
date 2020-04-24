import os
import re
import readline
from time import sleep
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread


class ProcessWrapper:
    class Completer(object):
        """
        A class to generate a completer function for passing to readline()
        credit due to to https://pymotw.com/3/readline/index.html#module-readline

        Currently simplistic in that it takes a command for the start of the line
        with a list of words that can come after it (in any order)
        """

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

                    except (KeyError, IndexError):
                        self.current_candidates = []

            try:
                response = self.current_candidates[state]
            except IndexError:
                response = None
            return response

    def __init__(self, cmd_line: str, cwd: Path = "."):
        self.cmd_line = cmd_line
        self.cwd = cwd
        self.running: bool = True

    def read_files(self):
        """
        looks for the files in same directory
            commands.txt
            players.txt
        parses for command format and player names

        generates a dictionary of str->[str] where the key represents a
        command value is a list of possible keywords that come after it.
        for consumption by ProcessWrapper.Completer
        """
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

    def output_loop(self, fr):
        while self.running:
            response = fr.read()
            if response and len(response) > 1:
                print(response)
            sleep(0.1)

    def input_loop(self, proc):
        line = None
        while proc.poll() is None:
            line = input() + "\n"
            if proc.poll() is None:
                proc.stdin.write(line.encode("utf8"))
                proc.stdin.flush()
                sleep(0.1)

    def start(self):
        self.running = True
        # Register our completer function
        command_tree = self.read_files()
        completer = self.Completer(command_tree).complete
        readline.set_completer(completer)

        # Use the tab key for completion
        readline.parse_and_bind("tab: complete")

        fw = open("tmpout", "wb")
        fr = open("tmpout", "r")
        os.chdir(str(self.cwd))
        try:
            proc = Popen(
                ["bash", "-c", "./start_server"],
                stdin=PIPE,
                stdout=fw,
                stderr=fw,
                bufsize=1,
            )
            out_thread = Thread(target=self.output_loop, args=(fr,))
            out_thread.start()
            self.input_loop(proc)
        finally:
            self.running = False
            proc.kill()
            fw.close()
            fr.close()


w = ProcessWrapper(
    "/home/giles/MinecraftServers/DadNoahSurvival/start_server",
    "/home/giles/MinecraftServers/DadNoahSurvival/",
)
w.start()
