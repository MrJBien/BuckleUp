import openseespy.opensees as ops   # import OpenSeesPy
import opsvis as opsv               # import OpenSeesPy plotting commands
import numpy as np
import scipy.linalg as slin
import matplotlib.pyplot as plt
import tabulate
import sys

def main():
    buckling(*get_input(check_args(sys.argv)))

def check_args(argvs):
    if len(argvs) == 2:
        if argvs[1]=="-user":
            return "user"
        if argvs[1]=="-default":
            return "default"
        elif argvs[1]=="-help":
            sys.exit("Description:     This programm leverages OpenSees to perform a buckling analysis of rectangular plates.\n" +
                     "Optional Args:   -user allows the user to define all relevant parameters\n" +
                     "                 -default settings are used for demonstration otherwise")
        else:
            sys.exit("Valid arguments are: -user, -help, -default")
    elif len(argvs) > 2:
        sys.exit("Too many command-line arguments")
    return "default"

def get_input(arg = "default"):
    # Get input parameters in SI units (N,m,s,kg)
    # Set of default parameters with type, description and value range
    width =     {"value" : 1,           "ptype" : "float",  "description" : "width of plate [m]",               "pmin" : 0,     "pmax" : float("inf")}
    height =    {"value" : 1,           "ptype" : "float",  "description" : "height of plate [m]",              "pmin" : 0,     "pmax" : float("inf")}
    thickness = {"value" : 10,          "ptype" : "float",  "description" : "thickness of plate [mm]",          "pmin" : 0,     "pmax" : float("inf")}
    nelem =     {"value" : 10,          "ptype" : "int",    "description" : "min # of elements along boundary", "pmin" : 1,     "pmax" : float("inf")}
    sigma_x =   {"value" : -100 ,       "ptype" : "float",  "description" : "stress in x_direction [N/mm²]",    "pmin" : float("-inf"),  "pmax" : float("inf")}
    sigma_y =   {"value" : 0    ,       "ptype" : "float",  "description" : "stress in y_direction [N/mm²]",    "pmin" : float("-inf"),  "pmax" : float("inf")}
    nmodes =    {"value" : 4,           "ptype" : "int",    "description" : "number of modeshapes",             "pmin" : 0,     "pmax" : float("inf")}
    supports =  {"value" : 4,           "ptype" : "int",    "description" : "number of supports",               "pmin" : 1,     "pmax" : 5}
    material =  {"value" : "steel",     "ptype" : "str",    "description" : "material",                          "poptions" : ["steel", "aluminium"],    "poptions_E" : [210000, 70000],    "poptions_v" : [0.3, 0.35]}
    E =         {"value" : 210000,      "ptype" : "float",  "description" : "Young's modulus [N/mm²]",           "pmin" : 0,     "pmax" : float("inf")}
    v =         {"value" : 0.3,         "ptype" : "float",  "description" : "Poisson's ratio [-]",               "pmin" : 0,     "pmax" : 0.5}

    if arg == "user":
        print("###################################\n" +
              "## User-defined input parameters\n" +
              "###################################")
        for param in [width, height, thickness, nelem, sigma_x, sigma_y, nmodes, supports, material, E, v]:
            proceed=True
            while proceed==True:
                try:
                    if param["ptype"] == "float":
                        param["value"] = float(input(f"{param["description"]}: "))
                        if param["pmin"]<param["value"]<param["pmax"]:
                            proceed=False
                        else:
                            raise ValueError(f"Please enter a valid number between [{param["pmin"]}; {param["pmax"]}]")
                    elif param["ptype"] == "int":
                        param["value"] = int(input(f"{param["description"]}: "))
                        if param["pmin"]<param["value"]<param["pmax"]:
                            proceed=False
                        else:
                            raise ValueError(f"Please enter a valid integer between [{param["pmin"]}; {param["pmax"]}]")
                    elif param["ptype"] == "str":
                        param["value"] = input(f"{param["description"]}: ").lower()
                        if param["value"] in param["poptions"]:
                            E["value"] = param["poptions_E"][param["poptions"].index(param["value"])]
                            v["value"] = param["poptions_v"][param["poptions"].index(param["value"])]
                            print(f"{E["description"]}: {E["value"]}")
                            print(f"{v["description"]}: {v["value"]}")
                            break
                        else:
                            proceed=False
                            raise ValueError(f"Valid materials are: {param["poptions"]}. User-input required.")
                    if param==sigma_y and min(np.sign(sigma_x["value"]),np.sign(sigma_y["value"]))>=0:
                        proceed=True
                        raise ValueError(f"Please enter at least one negative stress component to perform a buckling analysis.")
                except ValueError as err:
                    print(err.args[0])
                    pass
                except EOFError:
                    print("")
                    return
            else:
                continue
            break
    elif arg == "default":
        print("###################################\n" +
              "## Default input parameters\n" +
              "###################################")

        for param in [width, height, thickness, nelem, sigma_x, sigma_y, nmodes, supports, material, E, v]:
            print(f"{param["description"]}: {param["value"]}")
        pass
    else:
        sys.exit("Invalid argument.")
    return width["value"], height["value"], thickness["value"]/1000, nelem["value"], sigma_x["value"]* 10**6, sigma_y["value"]* 10**6, nmodes["value"], supports["value"], E["value"]* 10**6, v["value"]

def get_esize(width, height, nelem):
    esize = min(width, height) / nelem                  # global edge length
    esize_w = width / round(width / esize / 2) / 2      # edge length along width
    esize_h = height / round(height / esize / 2) / 2    # edge length along width
    return esize, esize_w, esize_h

def build_model(width, height, thickness, nelem, supports, E, v):
    ###################################
    ## Model Setup
    ###################################
    ops.wipe()                                          # wipe model
    ops.model('basic', '-ndm', 3, '-ndf', 6)            # create model in 3D and 6 dof per node

    ###################################
    ## Define Material & Section
    ###################################
    ops.nDMaterial('ElasticIsotropic', 1, E, v, 0)   # nDMaterial(matType, matTag, *matArgs)
    ops.section('PlateFiber', 1, 1, thickness)          # section('PlateFiber', secTag, matTag, h)

    # ##################
    # NODES
    # ##################
    ops.node(1,+width/2,+height/2,0)                    # node(nodeTag, *crds, '-ndf', ndf, '-mass', *mass, '-disp', *disp, '-vel', *vel, '-accel', *accel)
    ops.node(2,+width/2,-height/2,0)
    ops.node(3,-width/2,-height/2,0)
    ops.node(4,-width/2,+height/2,0)

    esize, esize_w, esize_h = get_esize(width, height, nelem)

    ops.mesh('line',1,2,*[1,2],0,6,esize_h)             # mesh('line', tag, numnodes, *ndtags, id, ndf, meshsize, eleType='', *eleArgs=[])
    ops.mesh('line',2,2,*[2,3],0,6,esize_w)
    ops.mesh('line',3,2,*[3,4],0,6,esize_h)
    ops.mesh('line',4,2,*[4,1],0,6,esize_w)

    # ##################
    # Elements
    # ##################
    shelltype = 'ShellNLDKGQ'                               # Nonlinear Shellelement
    ops.mesh('quad',10,4,*[1,2,3,4],0,6,esize,shelltype,1)  # mesh('quad', tag, numlines, *ltags, id, ndf, meshsize, eleType='', *eleArgs=[])

    # ##################
    # Boundary Conditions
    # ##################
    # Fix all edge nodes in z
    ops.fixX(-width/2, 0,0,1,0,0,0)                      # fixX(x, *constrValues, '-tol', tol=1e-10)
    ops.fixX(+width/2, 0,0,1,0,0,0)
    if supports>2:
        ops.fixY(+height/2, 0,0,1,0,0,0)                 # fixY(y, *constrValues, '-tol', tol=1e-10)
    if supports>3:
        ops.fixY(-height/2, 0,0,1,0,0,0)

    # Fix nodes in symmetry lines in orthogonal direction
    ops.fixX(0, 1,0,0,0,0,0)
    ops.fixY(0, 0,1,0,0,0,0)

    opsv.plot_model(fig_wi_he=(50,20))                  # plot model and save (not possible in Codespace directly)
    plt.title(f'Model')
    plt.savefig(f'model.png')
    plt.close()

#    print("DOFs: " + str(max(ops.getNodeTags())*6))

def buckling(width, height, thickness, nelem, sigma_x, sigma_y, nmodes, supports, E, v):
    print("###################################\n" +
    "## Building Model...")
    build_model(width, height, thickness, nelem, supports, E, v)

    # ##################
    # Buckling Analysis
    # ##################
    # OpenSees doesn't come with it's own implementation of a buckling analysis.
    # Implemented solution for the eigenvalue analysis is adopted from a blog post
    # written by Michael H. Scott: https://portwooddigital.com/2021/05/29/right-under-your-nose/

    # 1. Step: Get K0 in static Analysis without load
    ops.system('FullGeneral')
    ops.integrator('LoadControl',0)
    ops.algorithm('ModifiedNewton')
    ops.constraints('Plain')
    ops.numberer('RCM')
    ops.analysis('Static')
    print("## Extracting K0...")
    errflag = ops.analyze(1)
    if errflag!=0:
        sys.exit("## Error: Extraction of K0 failed, check if input values are reasonable.")

    N = ops.systemSize()                        # Extract K0
    Kmat = ops.printA('-ret')
    Kmat = np.array(Kmat)
    Kmat.shape = (N,N)

    # 2. Step: Get Kgeom in nonlinear static Analysis with load
    # ##################
    # Load Definition
    # ##################
    ops.timeSeries("Linear",1)                  # Create TimeSeries for load pattern with a tag of 1
    ops.pattern("Plain", 1, 1)                  # Create a plain load pattern associated with the TimeSeries (pattern, patternTag, timeseriesTag)

    _, esize_w, esize_h = get_esize(width, height, nelem)

    for node_tag in ops.getNodeTags():
        x_crd = ops.nodeCoord(node_tag)[0]
        y_crd = ops.nodeCoord(node_tag)[1]
        if x_crd == -width/2 or x_crd == +width/2:
            if y_crd == -height/2 or y_crd == +height/2:
                ops.load(node_tag, sigma_x*thickness*esize_h/2*np.sign(x_crd),0,0,0,0,0)
            else:
                ops.load(node_tag, sigma_x*thickness*esize_h/1*np.sign(x_crd),0,0,0,0,0)
        if y_crd == -height/2 or y_crd == +height/2:
            if x_crd == -width/2 or x_crd == +width/2:
                ops.load(node_tag, 0,sigma_y*thickness*esize_w/2*np.sign(y_crd),0,0,0,0)
            else:
                ops.load(node_tag, 0,sigma_y*thickness*esize_w/1*np.sign(y_crd),0,0,0,0)

    ops.system('FullGeneral')
    ops.integrator('LoadControl',1,100)
    ops.algorithm('ModifiedNewton')
    print("## Extracting Kgeo...")
    errflag = ops.analyze(1)
    if errflag!=0:
        sys.exit("## Error: Extraction of Kgeo failed, check if input values are reasonable.")

    opsv.plot_defo(unDefoFlag=1)                    # plot deformed shape of SA
    plt.title(f'Deformation plot')
    plt.savefig(f'static_defo.png')
    plt.close()

    Kgeo = ops.printA('-ret')                       # Extract Kgeo
    Kgeo = np.array(Kgeo)
    Kgeo.shape = (N,N)
    Kgeo = Kmat-Kgeo
    print("## Solving Eigenvalue problem...")
    if N>1800:
        print(f"## Warning: Number of unrestrained DOFs is {N}, solving the Eigenvalue may take a while or even time-out.")
    lam, x = slin.eig(Kmat,Kgeo)                    # Eigenvalue solution

    pos_idx = np.nonzero(lam > 0)[0]                # Indexes of positive Eigenvalues
    sort_idx = np.argsort(lam)                      # Indexes of sorted Eigenvalues
    idx = [value for value in sort_idx if value in pos_idx] #intersection of sort_idx and pos_idx
    if len(idx)==0:
        sys.exit("## Error: No positive Eigenvalues found, check if input values are reasonable.")
    elif len(idx)<nmodes:
        print(f"## Warning: Number of positive Eigenvalues is smaller than requested number of Modeshapes. Only {len(idx)} Modeshapes can be analysed.")
        nmodes=len(idx)

    table=[["Eigenmode", "Critical Load factor [-]", "Sxx,crit [N/mm²]", "Syy,crit [N/mm²]"]]
    for i in range (nmodes):
        table.append([i+1, np.real(lam[idx[i]]), np.real(lam[idx[i]])*(sigma_x*10**-6), np.real(lam[idx[i]])*(sigma_y*10**-6)])
    print(tabulate.tabulate(table,tablefmt="grid", headers="firstrow"))

    # ##################
    # Eigenmode visualisation
    # ##################
    node_tags = ops.getNodeTags()
    node_dofs = []
    for node_tag in node_tags:
        node_dofs.append(ops.nodeDOFs(node_tag))

    for i in range (nmodes):
        build_model(width, height, thickness, nelem, supports, E, v)

        ops.system('BandGen')
        ops.integrator('LoadControl',1,100)
        ops.constraints('Transformation')
        ops.algorithm('ModifiedNewton')
        ops.numberer('RCM')
        ops.analysis('Static')

        ops.timeSeries("Constant",1)
        ops.pattern("Plain", 1, 1)                             # Create a plain load pattern associated with the TimeSeries (pattern, patternTag, timeseriesTag)

        for node_tag in node_tags:                             # apply displacement BCs to resemble Eigenshape
            for j, _ in enumerate(node_dofs[node_tag-1]):
                if node_dofs[node_tag-1][j]!=-1 and 2<=j<=4:
                    ops.sp(node_tag, j+1, x[node_dofs[node_tag-1][j],idx[i]].item())

        ops.fixX(-width/2, 0,0,1,0,0,0)                        # fixX(x, *constrValues, '-tol', tol=1e-10)
        ops.fixX(+width/2, 0,0,1,0,0,0)
        ops.fixY(-height/2, 0,0,1,0,0,0)                       # fixY(y, *constrValues, '-tol', tol=1e-10)
        ops.fixY(+height/2, 0,0,1,0,0,0)
        ops.fixX(0, 1,0,0,0,0,0)
        ops.fixY(0, 0,1,0,0,0,0)
        print(f"## Plotting Modeshape {i+1}...")
        errflag = ops.analyze(1)
        if errflag!=0:
            print(f"## Warning: Static analysis for Modeshape {i+1} failed.")
            continue
        opsv.plot_defo(unDefoFlag=1)
        plt.title(f'Modeshape {i+1}, f = {np.real(lam[idx[i]]):.6}')
        plt.savefig(f'Mode_{i+1}.png')
        plt.close()

if __name__ == "__main__":
    main()
