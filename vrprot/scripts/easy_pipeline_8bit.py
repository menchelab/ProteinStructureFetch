# Author: Till Pascal Oblau & Felix Fischer
import sys
import time

from blender_converter import BlenderConverter
from pdb_parser import ChimeraXProcessing
from pointcloud2map_8bit import pcd_to_png
from sample_pointcloud import sample_pcd


class EasyPipeline:
    """An short class to run all the steps in the Process."""

    def __init__(self):
        """Initialization of the EasyPipeline class. Will check whether the user
        has give a list of proteins. Will use this list to generate the proteins dictionary.
        If the list of proteins is not given using the -p flag, the program will
        tell the user how to use the -p flag.
        User can define path to chimerax distribution by using the -ch_path=<path to chimerax> flag.
        User can define path to blender distribution by using the
        -bl_path=<path to blender> flag.
        """
        self.proteins = {}  # Dict containing all Proteins of interest.
        # Checks whether a list of proteins is given an startup.
        if "-p" in sys.argv:
            # extract all proteins from the list
            p = list(str(sys.argv[sys.argv.index("-p") + 1]).split(","))
            # Reorganize the list of proteins into the directory
            for protein in p:
                self.proteins[protein] = protein
        else:
            # Help the user if the -p flag and a list of protein is missing.
            print(
                'Please list proteins as list with the operator "-p" when starting the script. Here a little example:\neasy_pipeline.py -p Q9W3H5,Q99102'
            )
            exit()
        # Set path to chimerax and blender for linux as default.
        self.chimeraX = "chimerax"
        # Check wether user defined paths to chimerax or blender are given on execution.
        if "-ch_path=" in sys.argv:
            self.chimeraX = sys.argv[sys.argv.index("ch_path=*")].replace(
                "ch_path=", ""
            )
        # Create a new PDB Parser Object and Blender Converter Object
        self.parser = ChimeraXProcessing(
            self.proteins, keepFiles=True, chimeraX=self.chimeraX
        )
        if self.parser.executableSet == False:
            print(
                "Something is wrong with your chimeraX installation. Please check that our contact the developer of this pipeline."
            )
            exit()
        self.notFetched = []

    def pipeline(self):
        """
        A short function to run all steps of the process to generate XYZ and
        RGB values based on the given UniProtIDs. It will measure the total
        runtime of the process and tell the user to give a list of proteins,
        if it is forgotten. This will also measure the run time of each step
        and report it to the user."""
        # Begin with time measuring.
        start_time = time.time()
        # Run the pipeline for each protein in the directory.
        for i, protein in enumerate(self.proteins):
            ft_time = time.time()  # Start time for PDB Fetching
            if not self.parser.fetch_pdb(
                protein
            ):  # Fetch the pdb file from the database.
                # When the protein could not be fetched, it will be reported and added to the notFetched list.
                print("Could not be fetched from Alphafold DB or RCSB DB! Skipped!")
                self.notFetched.append(protein)
                continue
            # Report time needed to fetching the structure.
            print(
                "Fetching of the structure %s needed: %s seconds"
                % (protein, time.time() - ft_time)
            )
        # only proceed with fetched structures
        onlyFetched = {
            k: v for k, v in self.proteins.items() if k not in self.notFetched
        }
        ch_time = time.time()  # Start time for PDB Parsing.
        self.parser.apply_chimerax_processing(
            onlyFetched, processing="cartoons_ss_coloring"
        )  # Color the secondary structures.
        print(
            "Processing all available structures needed: %s seconds"
            % (time.time() - ch_time)
        )
        for i, protein in enumerate(onlyFetched):
            # Report time needed to parse PDB the structure.

            convert_time = time.time()  # Start time for Converting GLB to PLY.
            self.parser.convertGLBToPLY(protein)
            # Report time needed to convert GLB to PLY.
            print(
                "Converting the GLB of the structure %s needed: %s seconds"
                % (protein, time.time() - convert_time)
            )
            # point cloud
            pC_time = time.time()  # Start time for Point Cloud sampling.
            self.createPointCloud(protein)
            print(
                "Sampling Point Cloud for the structure %s needed: %s seconds"
                % (protein, time.time() - pC_time)
            )
            # point cloud
            png_time = time.time()
            self.createPNG(protein)
            print(
                "Generating output images for the structure %s needed: %s seconds"
                % (protein, time.time() - png_time)
            )

        # Print out the total runtime of the whole process
        print("Total Runtime: %s seconds" % (time.time() - start_time))

    def createPointCloud(self, protein):
        """
        Imports open3d, os
        Opens protein.ply and cube.ply, then translates center of protein to
        center of cube and scales protein (scaling factor is printed). Point
        cloud of protein mesh is sampled via Poisson sampling of 1048576 points,
        writes point cloud to file ASCII_clouds as .xyzrgb file
        """
        sample_pcd(self.parser.plys[protein])

    def createPNG(self, protein):
        """import png, numpy, os
        Opens .xyzrbg file of the point cloud and writes two separate .png files
        for the xyz coordinate and the RGB value for each point of the point cloud.
        Dimensions of both .png files: 1024x1024 (for 1048576 points)
        """
        pcd_to_png(self.parser.plys[protein])


if __name__ == "__main__":
    p = EasyPipeline()
    p.pipeline()
    print(f"Not fetched structures:\n{p.notFetched}")
