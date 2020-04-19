from mcunit import McUnit
from config import Config

mc_units = McUnit.discover_units()


def show_state():
    print("\nMinecraft Servers' State")
    print(McUnit.heading)
    for mc in mc_units:
        print(mc)


def set_world(unit):
    chooser = Config.make_world_chooser(unit.worlds)
    world = chooser.ask()
    if world:
        print(f"switching to {world}")
        unit.set_world(int(world))
    else:
        print("cancelled")


all_actions = McUnit.actions
all_actions.update({"w": set_world})
choose_server = Config.make_server_chooser(len(mc_units))
choose_action = Config.make_action_chooser(all_actions)


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
