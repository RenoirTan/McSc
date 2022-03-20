#!/usr/bin/env sh

run_command() {
    echo "==> $@"
    "$@"
}

run_command mkdir -p $HOME/.local/bin
run_command cp ./mcsc $HOME/.local/bin/mcsc
run_command mkdir -p $HOME/.local/share/applications
run_command cp ./mcsc.desktop $HOME/.local/share/applications/mcsc.desktop
run_command mkdir -p $HOME/.local/lib
run_command cp ./mcsc.py $HOME/.local/lib/mcsc.py
