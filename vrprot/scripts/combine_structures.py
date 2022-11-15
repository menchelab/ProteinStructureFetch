# Author: Till Pascal Oblau
import glob
import os
import shutil
import sys

from chimerax.core.commands import run


def main(directory, target):
    all_files = glob.glob(f"{directory}/*.pdb")
    while len(all_files) > 1:
        first_structure = all_files[0].split("/")[-1]
        first_structure = first_structure.split("-")[1]
        structures = []
        for file in all_files:
            tmp = file.split("/")[-1]
            tmp = tmp.split("-")[1]
            if tmp == first_structure:
                structures.append(file)
        for file in structures:
            run(session, f"open {file}")
            run(session, f"echo HELLO")
        run(session, f"save {target}/AF-{first_structure}-combined.glb")
        run(session, "close")
        for file in structures:
            all_files.remove(file)
            filename = file.split("/")[-1]
            shutil.move(file, f"{directory}/{filename}")


directory = "/Users/till/Documents/UNI/Master_Bioinformatik-Universität_Wien/3.Semester/proteins/Multistru"
target = "/Users/till/Documents/UNI/Master_Bioinformatik-Universität_Wien/3.Semester/proteins/Multistru/Combined"
main(directory, target)
