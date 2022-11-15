#Author: Felix Fischer

def pcd_to_png(protein):
    import png
    import numpy as np
    import os

    current_workdir = os.getcwd()
    # filepath = current_workdir +'/ASCII_clouds/'
    # fname = pcd.rstrip(".xyzrgb")

    # xyzrgb file comes with RGB stores as float
    protein = protein.split("/")[-1].rstrip(".ply")
    f = open(current_workdir + "/ASCII_clouds/" + protein + ".xyzrgb", "r")

    size = 1024

    l_x = []
    l_y = []
    l_z = []

    n_X = []
    n_Y = []
    n_Z = []

    R = []
    G = []
    B = []

    lines = list(f.readlines())

    for i in range(1048576):
        # print(i)
        if i >= len(lines):
            # add sseros
            l_x.append(0)
            l_y.append(0)
            l_z.append(0)

            R.append(0)
            G.append(0)
            B.append(0)

        else:
            line = lines[i]
            new_line = list(line.strip().split(" "))
            #!
            #!convert float RGB values [0,1] to [0,255] = intvalues of RGB
            #!
            new_line[3] = float(new_line[3]) * 255
            new_line[4] = float(new_line[4]) * 255
            new_line[5] = float(new_line[5]) * 255

            if len(new_line) >= 3:

                x = new_line[0]
                y = new_line[1]
                z = new_line[2]

                l_x.append(float(x))
                l_y.append(float(y))
                l_z.append(float(z))

            if len(new_line) >= 6:

                r = new_line[3]
                g = new_line[4]
                b = new_line[5]

                R.append(int(float(r)) * 180)
                G.append(int(float(g)) * 180)
                B.append(int(float(b)) * 180)

            else:
                R.append(0)
                G.append(0)
                B.append(0)

    f.close()

    ###########################################

    max_x = max(l_x)
    min_x = min(l_x)

    max_y = max(l_y)
    min_y = min(l_y)

    max_z = max(l_z)
    min_z = min(l_z)

    # print(max_x-min_x,max_y-min_y,max_z-min_z)

    for n in range(len(l_x)):

        xn = int(float((l_x[n] - min_x) / (max_x - min_x)) * 65535)  # 65535
        yn = int(float((l_y[n] - min_y) / (max_y - min_y)) * 65535)
        zn = int(float((l_z[n] - min_z) / (max_z - min_z)) * 65535)
        # f.write('%s,%s,%s,%.6f,%.6f,%.6f,%s\n' %(n,n,n,xn,yn,l_z[n],l_rest[n]))
        n_X.append(xn)
        n_Y.append(yn)
        n_Z.append(zn)

    # f.write('%s,%s,%s,'%(xn,yn,zn))
    # f.close()

    lastline = 0
    coordsarray = list(range(size * 3))
    colarray = list(range(size * 3))
    thisList = []
    thisColList = []

    for nn in range(len(n_X)):

        thisline = int(nn / size)

        if thisline != lastline:  # new line
            coordsarray = np.vstack((coordsarray, thisList))
            colarray = np.vstack((colarray, thisColList))
            thisList = []
            thisColList = []

            # append a )(
            # fnew.write(')' + ',\n' + '(')
            lastline = thisline

        thisList.append(n_X[nn])
        thisList.append(n_Y[nn])
        thisList.append(n_Z[nn])

        thisColList.append(R[nn])
        thisColList.append(G[nn])
        thisColList.append(B[nn])

    coordsarray = np.vstack((coordsarray, thisList))
    colarray = np.vstack((colarray, thisColList))

    # print(coordsarray.shape)

    colarray = np.delete(colarray, (0), axis=0)
    coordsarray = list(np.delete(coordsarray, (0), axis=0))

    output_path_rgb = current_workdir + "/MAPS/rgb/"
    output_path_xyz = current_workdir + "/MAPS/xyz/"
    if not os.path.exists(output_path_rgb):
        os.makedirs(output_path_rgb)
    if not os.path.exists(output_path_xyz):
        os.makedirs(output_path_xyz)
    # protein_name=pcd.rstrip(".xyzrgb")

    g = open(str(output_path_rgb + protein) + ".png", "wb")
    x = png.Writer(size, size, bitdepth=16, greyscale=False)
    x.write(g, colarray)
    g.close()
    print("RGB map done")

    f = open(str(output_path_xyz + protein) + ".png", "wb")
    w = png.Writer(size, size, bitdepth=16, greyscale=False)
    w.write(f, coordsarray)
    f.close()
    print("XYZ map done")
