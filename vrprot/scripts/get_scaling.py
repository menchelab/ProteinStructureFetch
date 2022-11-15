import os


def get_scaling(protein_mesh_ply):
    import open3d as o3d

    # get protein name & read mesh as .ply format
    mesh = o3d.io.read_triangle_mesh(protein_mesh_ply)
    mesh.compute_vertex_normals()

    # load cube with no lines (for merging)
    cube_no_line = o3d.io.read_triangle_mesh("Cube_no_lines.ply")
    cube_no_line.compute_vertex_normals()
    # Cube has to be colored (contain RGB values), otherwise merged mesh will not have color (color white)
    cube_no_line.paint_uniform_color([1, 1, 1])

    ##get cube center & translate mesh into center of cube
    cube_center = cube_no_line.get_center()
    mesh.translate(cube_center, relative=False)

    # get pre scaling mesh bounding box (for scaling)
    mesh_bounding_box = mesh.get_axis_aligned_bounding_box()
    mesh_bounding_box.color = (1, 0, 0)

    ##scale (find longest length of bounding box and get its ratio with length of cube=10000)
    longest_length = 0
    for length in mesh_bounding_box.get_extent():
        if length > longest_length:
            longest_length = length

    scale = (10000 / longest_length) * 0.95
    # dont scale if scaling factor is below 1
    if scale < 1:
        scale = 1
    return scale


def write_scale(protein, scale, file=None):
    if file is None:
        file = "./scales.csv"
    scale = str(scale)
    exist, skip = False, False
    lines = []
    if os.path.isfile(file):
        exist = True
        with open(file, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                lines[i] = line.strip("\n").split(",")
    with open(file, "w+") as f:
        if exist:
            for i, line in enumerate(lines[1:]):
                if protein == line[0]:
                    skip = True
                    break
        if not skip:
            newLine = [protein, scale]
            lines.append(newLine)
        for i, line in enumerate(lines):
            lines[i] = ",".join(line)
        f.write("\n".join(lines))


if __name__ == "__main__":
    # print(get_scaling("./plys/AF-A0A0A0MRZ8-F1-model_v2.ply"))
    write_scale("Test5", 0.5)
