import libtmux
from libtmux import Window

# Commands is a name to command dictionary
def run_commands(commands: dict[str, str]):

    # Create new tmux server instance
    server = libtmux.Server()
    
    # Create new session with first command
    first_cmd_name = list(commands.keys())[0]
    session = server.new_session(
        session_name='afl-fuzzing',
        window_name=first_cmd_name,
    )
    
    # Send first command to initial window
    first_window = session.attached_window
    send_keys_to_window(first_window, commands[first_cmd_name])
    
    # Create new windows for remaining commands
    for cmd_name, cmd in list(commands.items())[1:]:
        new_window = session.new_window(window_name=cmd_name)
        send_keys_to_window(new_window, cmd)
    
    # Create monitor window last
    monitor_cmd_name = list(commands.keys())[-1]
    monitor_window = session.new_window(window_name='monitor')
    send_keys_to_window(monitor_window, "watch -n 60 afl-whatsup -o {}".format(session.name, monitor_cmd_name))
    
    return session

def send_keys_to_window(window: Window, keys: str):
    active_pane = window.active_pane
    if active_pane:
        active_pane.send_keys(keys)