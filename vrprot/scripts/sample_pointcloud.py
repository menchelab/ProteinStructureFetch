# Author: Felix Fischer
import glob
import os

import open3d as o3d
from util import WD

CUBE_NO_LINES = os.path.join(WD, "static", "3d_objects", "Cube_no_line.ply")


def sample_pcd(
    ply_file,
    output,
    SAMPLE_POINTS=262144,
    cube_no_line=CUBE_NO_LINES,
):

    # get protein name & read mesh as .ply format
    mesh = o3d.io.read_triangle_mesh(ply_file)
    mesh.compute_vertex_normals()
    print(f"Processing structure:{ply_file}")

    # load cube with no lines (for merging)
    cube_no_line = o3d.io.read_triangle_mesh(cube_no_line)
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

    print(f"scaling factor: {scale}")

    mesh.scale(scale, center=mesh.get_center())

    ##Translate so that mesh does not exceed cube
    ##translate mesh to shifted cube center

    # get new bounding box post scaling to calculate shift
    ###center of mesh bounding box != mesh center###
    mesh_bounding_box_new = mesh.get_axis_aligned_bounding_box()
    shift = mesh.get_center() - mesh_bounding_box_new.get_center()
    mesh.translate(cube_center + shift, relative=False)

    ##sample point cloud
    mesh_combined = cube_no_line + mesh
    # sample points from merged mesh
    pcd = mesh_combined.sample_points_uniformly(number_of_points=SAMPLE_POINTS)

    # write point cloud as xyzrgb file (create new folder if ASCII_cloud does not exist)
    # containing xyz values and rgb values (as float [0,1]) for each point
    o3d.io.write_point_cloud(output, pcd)
    # # Debug to view structure with cube.
    # cube = o3d.io.read_triangle_mesh("Cube.ply")
    # cube.compute_vertex_normals()
    # o3d.visualization.draw_geometries([mesh, cube, mesh_bounding_box_new])
    # o3d.visualization.draw_geometries([pcd])
    return scale


def run_for_batch():
    from get_scaling import write_scale

    all_files = glob.glob(
        "/Users/till/Documents/UNI/Master_Bioinformatik-Universität_Wien/3.Semester/proteins/Multistru/Combined/*.ply"
    )
    for file in all_files:
        file_name = file.split("/")[-1]
        protein = file_name.split("-")[1]
        print(protein, file_name)
        file_name = file_name.replace("ply", "xyzrgb")
        print(file_name)
        output = f"/Users/till/Documents/UNI/Master_Bioinformatik-Universität_Wien/3.Semester/proteins/Multistru/Combined/ascii/{file_name}"
        if not os.path.isfile(output):
            scale = sample_pcd(file, output)
            write_scale(protein, scale)
            # os.remove(file)


if __name__ == "__main__":
    from sys import argv

    scale = sample_pcd(argv[1])
    # run_for_batch()
