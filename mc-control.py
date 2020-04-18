import sys
from elevate import elevate
from mcunit import McUnit
from chooser import Chooser

elevate(graphical=False)  # need sudo for systemd actions


mc_units = McUnit.discover_units()


def show_state():
    print("\nMinecraft Servers' State")
    print(McUnit.heading)
    for mc in mc_units:
        print(mc)


# generate an actions prompt from the list of available actions in McUnit
action_prompt = "Choose an action:"
for key, value in McUnit.actions.items():
    action_prompt += f" {key}={value.__name__}"

# generate a numeric list of servers plus 'a' for all servers
servers = ["a"] + [str(i) for i in range(len(mc_units))]

choose_action = Chooser(action_prompt, McUnit.actions.keys())
choose_server = Chooser("Choose a Server (a=all)", servers)


# main loop. Print status and request actions
while True:
    show_state()
    server = choose_server.ask()
    if not server:
        break
    action = choose_action.ask()
    if action:
        function = McUnit.actions[action]
        if server == "a":
            for unit in mc_units:
                function(unit)
        else:
            function(mc_units[int(server)])
    else:
        print("No action")
