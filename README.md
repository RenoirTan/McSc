# McSc

Switch between Minecraft mod packs and configurations without having to create
new folders for your saves and resource packs.

It's really janky and requires admin permissions on Windows because Windows
doesn't allow you to create symlinks as an unelevated user.

# Installation

On Unix-like systems, you should open the `mcsc.desktop` file with a text editor
and replace the `<YOUR USERNAME HERE>` part with your username (the one you
use to log in to your computer). Then, run the `install-unix.sh` script.

On Windows, you can copy this folder to where you want it to be and then create
a shortcut to the `windows.py` file on your desktop.
