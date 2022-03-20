#!/usr/bin/env sh

run_command() {
    echo "==> $@"
    "$@"
}

run_command rm $HOME/.local/bin/mcsc
run_command rm $HOME/.local/share/applications/mcsc.desktop
run_command rm $HOME/.local/lib/mcsc.py
