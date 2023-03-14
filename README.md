# **ProteinStructureFetch**

This extension allows you to fetch protein structures from
[AlphaFold DB](https://alphafold.ebi.ac.uk/) to explore them on the VRNetzer
platform. This extension is built around the Python module
[vrprot](https://test.pypi.org/project/vrprot/0.0.6/). As
[vrprot](https://test.pypi.org/project/vrprot/0.0.6/) uses
[ChimeraX](https://www.cgl.ucsf.edu/chimerax/download.html) it is mandatory to
install it before using this extension.

## **Installation**

1. Download and install the latest version of
   [ChimeraX](https://www.cgl.ucsf.edu/chimerax/download.html).
2. Add the `ProteinStructureFetch` directory to your VRNetzer backend directory.
   The directory should be located at `"extensions/ProteinStructureFetch"`.
3. Before the line:
   ```
   python -m pip install -r requirements.txt
   ```
   add the following line to the VRNetzer backend's `build and run` script
   (Windows: `buildandRUN.ps`, Linux: `linux_buildandrun.sh`, Mac:
   `mac_buildandrun.sh`) :
   ```
   python -m pip install -r extensions/StringEx/requirements.txt
   ```
   It should now look something like this:
   ```
   python -m pip install -r extensions/StringEx/requirements.txt
   python -m pip install -r requirements.txt
   ```

## **Usage**

### **Automatically fetch structures**

---

If you are in the VR of the VRNetzer and the network you are exploring is a PPI,
you can select a node label. On the node panel, you'll see a second tab:
![Picture visualizing the protein structure tab on the node panel ](/pictures/nodepanel_example.png)
By selecting a protein structure in the dropdown menu, a fetching process is
started in the background. If the structure has not yet been processed
beforehand, the extension will fetch the structure from the AlphaFold DB and
process it. This process takes some seconds. After the process is finished, the
structure should be shown if you select the protein structure once more in the
dropdown menu.

---

### **Manually fetch structures**

---

To manually fetch a certain structure, you can navigate to:

http://localhost:5000/vrprot/fetch (Windows/Linux)

http://localhost:3000/vrprot/fetch (MacOS)

You define the protein structure you want to fetch by adding:

`?id=<UniProtID_ID>`to the URL.

For example, to fetch the structure with the UniProt ID `P68871`, you would
navigate to:

http://localhost:5000/vrprot/fetch?id=P68871

Furthermore, you can define the mode in which the structure will be preprocessed
in ChimarX by adding `&mode=<MODE>` to the URL.

To get a list of available modes you navigate to:

http://localhost:5000/vrprot/fetch?id=P68871&mode=help

---

### **Fetch all structures of a project**

---

To fetch all structures of a project, you can navigate to:

http://localhost:5000/vrprot/project (Windows/Linux)

http://localhost:3000/vrprot/project (MacOS).

You define the project you want to fetch by adding:

`?id=<PROJECT_NAME>`to the URL.

For example, to fetch the project with the project name `my_project`, you would
navigate to:

http://localhost:5000/vrprot/project?project=my_project

Here you can also define the mode as described
[above](#manually-fetch-structures.)

For this to work, each node has to have a `uniprot` attribute which is a list of
UniProt IDs. If a node has multiple UniProt IDs, all of them will be fetched and
processed

### Fetch a list of structures

---

To fetch a list of structures, you can navigate to:

http://localhost:5000/vrprot/list (Windows/Linux)

http://localhost:3000/vrprot/list (MacOS).

You define the list of structures by adding:

`?ids=<UniProtID_1>,<UniProtID_2>,...` to the URL.

For example, to fetch the structures with the UniProt IDs `P68871` and `P68872`,
you would navigate to:

http://localhost:5000/vrprot/list?ids=P68871,P68872

Here you can also define the mode as described
[above](#manually-fetch-structures).

## **Configuration**

The extension can be configured by editing the `config.ini` file in the
`ProteinStructureFetch` directory. For every value in this config file there is
a explanation provided. When this config file is not present, the extension will
create a default config file.
