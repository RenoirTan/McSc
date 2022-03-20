#!/usr/bin/env python3

from __future__ import annotations
import argparse
from io import TextIOWrapper
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import typing as t

HOW_CTRL_C = """
--------------------------------------
|************************************|
|* PRESS CTRL+C TO EXIT AT ANY TIME *|
|************************************|
--------------------------------------
"""

AP_DESC = """
Switch Minecraft mods and options without having to keep copying and deleting files.
"""

if platform.system() == "Windows":
    DEFAULT_MCSC_DIR = Path(os.environ["APPDATA"]) / ".mcsc"
    DEFAULT_MINECRAFT_DIR = Path(os.environ["APPDATA"]) / ".minecraft"
else:
    DEFAULT_MCSC_DIR = Path.home() / ".mcsc"
    DEFAULT_MINECRAFT_DIR = Path.home() / ".minecraft"

DEFAULT_CONFIG_PATH = DEFAULT_MCSC_DIR / "mcsc.json"
DEFAULT_PROFILES_DIR = DEFAULT_MCSC_DIR / "profiles"

CONFIG_PATH_ENVVAR = "MCSC_CONFIG_PATH"

DEFAULT_CONFIG = {
    "profilesDir": str(DEFAULT_PROFILES_DIR),
    "currentProfile": "default",
    "minecraftDir" : str(DEFAULT_MINECRAFT_DIR)
}

class McscConfig(object):
    def __init__(self, config: t.Dict[str, t.Any] = None) -> None:
        self.config = config if config is not None else {}
    
    def __contains__(self, key: str) -> bool:
        return key in self.config
    
    def __getitem__(self, key: str) -> t.Any:
        return self.config[key]

    def __setitem__(self, key: str, value: t.Any) -> None:
        self.config[key] = value
    
    def __delitem__(self, key: str) -> None:
        del self.config[key]
        
    def get(self, key: str, default: t.Optional[t.Any] = None) -> t.Any:
        return self.config.get(key, default)
    
    def load(self, input: t.Union[t.Dict[str, t.Any], TextIOWrapper, str, Path]) -> None:
        if isinstance(input, dict):
            self.loadc(input)
        elif isinstance(input, TextIOWrapper):
            self.loadf(input)
        elif isinstance(input, str) or isinstance(input, Path):
            self.loadfp(input)
    
    def loadc(self, config: t.Dict[str, t.Any]) -> None:
        self.config = config
    
    def loadf(self, file: TextIOWrapper) -> None:
        self.config = json.load(file)
    
    def loadfp(self, path: t.Union[str, Path]) -> None:
        with Path(path).open("r") as f:
            self.loadf(f)
    
    def use_defaults(self) -> None:
        self.config = DEFAULT_CONFIG.copy()
    
    def dumps(self) -> str:
        json.dumps(self.config)
    
    def dumpf(self, file: TextIOWrapper) -> None:
        json.dump(self.config, file)
    
    def dumpfp(self, path: t.Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            self.dumpf(f)

def show_option(number: int, action: str) -> None:
        print(f"    {number} |-> {action}")

def create_argparse() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=AP_DESC)
    ap.add_argument(
        "-c",
        "--config",
        help="Override the location of the config file.",
        dest="config_file"
    )
    return ap

def generate_conffile(path: Path) -> McscConfig:
    cf = McscConfig()
    cf.use_defaults()
    cf.dumpfp(path)
    return cf

def setup_mcsc() -> McscConfig:
    while True:
        profiles_dir = input(
            ":: Where do you want to store your profiles?\n:: Leave blank to use the default. |=> "
        )
        profiles_dir = Path(profiles_dir) if profiles_dir != "" else DEFAULT_PROFILES_DIR
        if profiles_dir.exists():
            if profiles_dir.is_dir() and any(profiles_dir.iterdir()):
                print(f"{profiles_dir} has things stored inside it.")
            elif profiles_dir.is_file():
                print(f"{profiles_dir} is a file.")
            else:
                break
            continue
        profiles_dir.mkdir(parents=True, exist_ok=True)
        break
    while True:
        minecraft_dir = input(
            ":: Where is minecraft installed?\n:: You can leave this blank if you don't know. |=> "
        )
        minecraft_dir = DEFAULT_MINECRAFT_DIR if minecraft_dir == "" else Path(minecraft_dir)
        if not minecraft_dir.exists():
            print(f"Minecraft is not installed at {minecraft_dir}")
            continue
        break
    current_profile = "default"
    current_profile_dir = profiles_dir / current_profile
    
    current_profile_dir.mkdir(parents=True, exist_ok=True)
    
    def copy_file(name: str) -> None:
        shutil.copy2(minecraft_dir / name, current_profile_dir / name)
    
    def copy_dir(name: str) -> None:
        shutil.copytree(minecraft_dir / name, current_profile_dir / name, symlinks=True)
    
    copy_file("options.txt")
    copy_file("optionsof.txt")
    copy_dir("config")
    copy_dir("mods")
    
    config = McscConfig()
    config["profilesDir"] = str(profiles_dir)
    config["currentProfile"] = current_profile
    config["minecraftDir"] = str(minecraft_dir)
    
    return config

def change_profile(profile_dir: Path, minecraft_dir: Path) -> int:
    print(f"Switching to {profile_dir.name}")
    
    def copy_file(name: str) -> None:
        shutil.copy2(profile_dir / name, minecraft_dir / name)
    
    def copy_dir(name: str) -> None:
        shutil.copytree(profile_dir / name, minecraft_dir / name, symlinks=True)
        
    def symlink(name: str) -> None:
        (minecraft_dir / name).symlink_to(profile_dir / name)
    
    def rm_dir(name: str) -> None:
        shutil.rmtree(minecraft_dir / name)
        
    def replace(name: str) -> None:
        mdn = minecraft_dir / name
        if mdn.exists():
            if mdn.is_symlink() or mdn.is_file():
                mdn.unlink()
            elif mdn.is_dir():
                rm_dir(name)
        symlink(name)
    
    replace("options.txt")
    replace("optionsof.txt")
    replace("config")
    replace("mods")
    
    return 0

def get_profiles_loc(profiles_dir: Path) -> int:
    print(f"Your profiles are located at {profiles_dir.absolute()}")

def move_profiles_dir(src: Path) -> Path:
    while True:
        dest = input(":: Where do you want to move your profiles to? |=> ")
        if dest == "":
            print("No input given.")
            continue
        dest = Path(dest)
        if dest.exists():
            print(f"{dest} exists already.")
            #if dest.is_dir() and any(dest.iterdir()):
            #    print(f"{dest} has things stored inside it.")
            #elif dest.is_file():
            #    print(f"{dest} is a file.")
            #else:
            #    break
            continue
        break
    print(dest)
    shutil.copytree(src, dest)
    shutil.rmtree(src)
    print("Profiles successfully moved.")
    return dest

def copy_profiles_dir(src: Path) -> int:
    while True:
        dest = input(":: Where do you want to copy your profiles to? |=> ")
        if dest == "":
            print("No input given.")
            continue
        dest = Path(dest)
        if dest.exists():
            if dest.is_dir() and any(dest.iterdir()):
                print(f"{dest} has things stored inside it.")
            elif dest.is_file():
                print(f"{dest} is a file.")
            else:
                break
            continue
        break
    shutil.copytree(src, dest)
    print("Profiles successfully copied.")
    return 0

def get_current_profile(current_profile: str) -> Path:
    print(f"You are currently using '{current_profile} as your profile.")

def new_profile(profiles_dir: Path, minecraft_dir: Path) -> Path:
    while True:
        name = input(":: What is the name of the new profile? |=> ")
        new_profile_dir = profiles_dir / name
        if new_profile_dir.exists():
            print(f"{new_profile_dir} already exists.")
            continue
        break
    
    def copy_file(name: str) -> None:
        shutil.copy2(minecraft_dir / name, new_profile_dir / name)
    
    def copy_dir(name: str) -> None:
        shutil.copytree(minecraft_dir / name, new_profile_dir / name, symlinks=True)
        
    new_profile_dir.mkdir(parents=True, exist_ok=True)
    
    copy_file("options.txt")
    copy_file("optionsof.txt")
    copy_dir("config")
    copy_dir("mods")

def remove_profile(profiles_dirs: t.List[Path]) -> int:
    print("-*- Which profile do you want to delete? -*-")
    show_option(-1, "<<- go back <<-")
    for index, profile_dir in enumerate(profiles_dirs):
        show_option(index, profile_dir.name)
    
    while True:
        result = input(":: Answer |=> ")
        try:
            result = int(result)
        except Exception as e:
            print(f"Your answer must be an integer.")
            continue
        if -1 <= result <= len(profiles_dirs)-1:
            break
        else:
            print(f"Your answer must be between -1 and {len(profiles_dirs)-1} inclusive.")
    if result == -1:
        return 0
    input(
        f":: Are you sure you want to delete {profiles_dirs[result].name}?\n"
        ":: If no, press Ctrl+C now. |=> "
    )
    shutil.rmtree(profiles_dirs[result])
    print(f"{profiles_dirs[result].name} has been removed.")
    return 0

def copy_profile(profiles_dir: Path, profiles_dirs: t.List[Path]) -> t.Optional[None]:
    print("-*- Which profile do you want to copy? -*-")
    show_option(-1, "<<- go back <<-")
    for index, profile_dir in enumerate(profiles_dirs):
        show_option(index, profile_dir.name)
    
    while True:
        result = input(":: Answer |=> ")
        try:
            result = int(result)
        except Exception as e:
            print(f"Your answer must be an integer.")
            continue
        if -1 <= result <= len(profiles_dirs)-1:
            break
        else:
            print(f"Your answer must be between -1 and {len(profiles_dirs)-1} inclusive.")
    
    if result == -1:
        return None
    while True:
        name = input(":: What is the name of the new profile? |=> ")
        new_profile_dir = profiles_dir / name
        if new_profile_dir.exists():
            print(f"{new_profile_dir} already exists.")
            continue
        break
    
    shutil.copytree(profiles_dirs[result], new_profile_dir)
    return new_profile_dir

def rename_profile(profiles_dir: Path, profiles_dirs: t.List[Path]) -> t.Optional[None]:
    print("-*- Which profile do you want to rename? -*-")
    show_option(-1, "<<- go back <<-")
    for index, profile_dir in enumerate(profiles_dirs):
        show_option(index, profile_dir.name)
    
    while True:
        result = input(":: Answer |=> ")
        try:
            result = int(result)
        except Exception as e:
            print(f"Your answer must be an integer.")
            continue
        if -1 <= result <= len(profiles_dirs)-1:
            break
        else:
            print(f"Your answer must be between -1 and {len(profiles_dirs)-1} inclusive.")
    
    if result == -1:
        return None
    while True:
        name = input(":: What is the new name for the profile? |=> ")
        new_profile_dir = profiles_dir / name
        if new_profile_dir.exists():
            print(f"{new_profile_dir} already exists.")
            continue
        break
    
    shutil.move(profiles_dirs[result], new_profile_dir)
    return new_profile_dir

def change_minecraft_loc() -> Path:
    while True:
        new_minecraft_dir = input(
            ":: Where is minecraft installed?\n:: You can leave this blank if you don't know. |=> "
        )
        new_minecraft_dir = (
            DEFAULT_MINECRAFT_DIR if new_minecraft_dir == "" else Path(new_minecraft_dir)
        )
        if not new_minecraft_dir.exists():
            print(f"Minecraft is not installed at {new_minecraft_dir}")
            continue
        break
    return new_minecraft_dir

def mainloop(config: McscConfig, conffile_path: Path) -> int:
    def ask_command(
        profiles_dirs: t.List[Path] = None,
        current_profile: t.Optional[str] = None
    ) -> t.Tuple[int, bool]:
        print("\n\n-*- Please enter a number -*-")
        if profiles_dirs is not None and len(profiles_dirs) > 0 and current_profile is not None:
            show_option(-1, "get the location of your profiles")
            show_option(-2, "move profiles folder")
            show_option(-3, "copy profiles folder")
            show_option(-4, "get current profile")
            show_option(-5, "new profile")
            show_option(-6, "remove profile")
            show_option(-7, "copy profile")
            show_option(-8, "rename profile")
            show_option(-9, "change minecraft location")
            show_option(-10, "save")
            show_option(-11, "save and exit")
            for index, profile_dir in enumerate(profiles_dirs):
                if current_profile == profile_dir.name:
                    show_option(index, f"switch to profile: {profile_dir.name} (current)")
                else:
                    show_option(index, f"switch to profile: {profile_dir.name}")
            first_time_setup = False
        else:
            show_option(-1, "setup mcsc")
            first_time_setup = True
        while True:
            result = input(":: Answer |=> ")
            try:
                result = int(result)
            except Exception as e:
                print(f"Your answer must be an integer.")
                continue
            if not first_time_setup:
                if -11 <= result <= len(profiles_dirs)-1:
                    return result, first_time_setup
                else:
                    print(f"Your answer must be between -11 and {len(profiles_dirs)-1} inclusive.")
                    continue
            else:
                if result == -1:
                    return -1, first_time_setup
                else:
                    print(f"You only get to pick one option: -1")
                    continue
    
    profiles_dir = config.get("profilesDir")
    current_profile = config.get("currentProfile")
    minecraft_dir = config.get("minecraftDir")
    
    while True:
        #print(f"{profiles_dir=}")
        #print(f"{current_profile=}")
        #print(f"{minecraft_dir=}")
        if None not in {profiles_dir, current_profile, minecraft_dir}:
            Path(profiles_dir).mkdir(parents=True, exist_ok=True)
            profiles_dirs = [node for node in Path(profiles_dir).iterdir() if node.is_dir()]
        else:
            profiles_dirs = None
            
        command_num, first_time_setup = ask_command(profiles_dirs, current_profile)
        print("\n")
        if first_time_setup:
            config = setup_mcsc()
        else:
            if command_num in [-10, -11]:
                config["profilesDir"] = str(Path(profiles_dir).absolute())
                config["currentProfile"] = current_profile
                config["minecraftDir"] = str(Path(minecraft_dir).absolute())
                config.dumpfp(conffile_path)
                if command_num == -11:
                    return 0
            elif command_num >= 0:
                change_profile(profiles_dirs[command_num], Path(minecraft_dir))
                current_profile = profiles_dirs[command_num].name
            elif command_num == -1:
                get_profiles_loc(Path(profiles_dir))
            elif command_num == -2:
                profiles_dir = str(move_profiles_dir(Path(profiles_dir)))
            elif command_num == -3:
                copy_profiles_dir(Path(profiles_dir))
            elif command_num == -4:
                get_current_profile(current_profile)
            elif command_num == -5:
                new_profile(Path(profiles_dir), Path(minecraft_dir))
            elif command_num == -6:
                remove_profile(profiles_dirs)
            elif command_num == -7:
                copy_profile(Path(profiles_dir), profiles_dirs)
            elif command_num == -8:
                rename_profile(Path(profiles_dir), profiles_dirs)
            elif command_num == -9:
                minecraft_dir = str(change_minecraft_loc())
        input("\n:: Press enter to continue |=> ")

def main() -> int:
    ap = create_argparse()
    args = ap.parse_args()
    conffile_path_tentative = args.config_file
    if conffile_path_tentative in {None, ""}:
        conffile_path_tentative = os.environ.get(CONFIG_PATH_ENVVAR)
        if conffile_path_tentative in {None, ""}:
            conffile_path_tentative = DEFAULT_CONFIG_PATH
    conffile_path = Path(conffile_path_tentative)
    if conffile_path.exists():
        config = McscConfig()
        config.loadfp(conffile_path)
    else:
        config = generate_conffile(conffile_path)
    print(HOW_CTRL_C)
    return mainloop(config, conffile_path)

if __name__ == "__main__":
    sys.exit(main())
