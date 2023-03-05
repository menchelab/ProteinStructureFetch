class NodeTags:
    uniprot = "uniprot"


class ConfigCategories:
    parser = "AlphafoldDBParser"
    dirs = "Directories"

    class ParserKeys:
        alphafoldVersion = "alphafoldVersion"
        colorMode = "colorMode"
        keepPDB = "keep PDB files"
        keepGLB = "keep GLB files"
        keepPLY = "keep PLY files"
        keepASCII = "keep ASCII Clouds"
        imageSize = "imageSize"
        overwrite = "overwrite"
        thumbnails = "thumbnails"
        numCached = "num cached models"
        colors = "sec struc colors"
        logLevel = "log level"

    class DirKeys:
        WD = "WD"
        flaskTemplates = "flask templates"
        flaskStatic = "flask static"
        extensions = "extensions"
        vrnetzer = "vrnetzer"
        vrnetzerStatic = "vrnetzer static"
        vrnetzerProjects = "vrnetzer projects"
        maps = "maps"
        overviewFile = "overview file"
