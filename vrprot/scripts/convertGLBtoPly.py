from trimesh import load
from trimesh.exchange.ply import export_ply
from util import Logger

log = Logger("ConvertGLBtoPLY")

def ConvertGLBtoPLY(structure, output=None):
    log.debug(f"Structure:{structure}")
    mesh = load(structure, force="mesh")
    file = export_ply(mesh)
    if output is None:
        output = structure.replace(".glb", ".ply")
    f = open(output, "wb+")
    f.write(file)
    f.close()


def run_batch():
    for file in glob.glob(
        "GLB_files/*.glb"
    ):
        file_name = file.split("/")[-1]
        output_name = file_name.replace("X", "X")
        output = f"/GLB_files/plys/{output_name}"
        if not os.path.isfile(output):
            ConvertGLBtoPLY(file, output)


if __name__ == "__main__":
    import glob
    import os
    from sys import argv

    ConvertGLBtoPLY(argv[1])
