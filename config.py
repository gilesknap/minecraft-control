from pathlib import Path
from chooser import Chooser


class Config:
    # todo these should be read from a config file
    mc_root = Path("/opt/minecraft")
    unit_name_format = "minecraft@{}.service"
    screen_cmd_format = 'su - minecraft -c "/usr/bin/screen -Dr mc-{}"'
    non_worlds = ["logs", "debug", "plugins", "crash-reports"]

    def make_server_chooser(count):
        # generate a numeric list of servers plus 'a' for all servers
        servers = ["a"] + [str(i) for i in range(count)]

        return Chooser("Choose a Server (a=all)", servers)

    def make_action_chooser(actions):
        # generate an actions prompt from the list of available actions in McUnit
        action_prompt = "Choose an action:"
        for key, value in actions.items():
            action_prompt += f" {key}={value.__name__}"

        return Chooser(action_prompt, actions.keys())

    def make_world_chooser(worlds):
        prompt = "Choose a world:"
        for i, world in enumerate(worlds):
            prompt += f" {i}={world}"
        world_nums = [str(i) for i in range(len(worlds))]

        return Chooser(prompt, world_nums)
