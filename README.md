# BuckleUp

#### Video Demo: https://youtu.be/nVARNbwmjzQ

## Description:
Thin plates loaded in compression tend to fail in buckling. In many civil/mechanical engineering applications such failure mode needs to be adressed in the design of structural elements and must be verified. One common approach is to perform a linear bifurcation analysis (LBA) on a Finite Element model to calculate the critical buckling stress. The critical buckling stress represents the maximum load that a perfect plate (without any imperfections/flaws) can take until it fails. It is often used as an input parameter for verification checks prescribed by civil/mechanical engineering design standards such as EN 1993-1-5.

BuckleUp is a small program that calculates the critical load factor for rectangular plates by Finite-Element-Analysis. The following parameters can be altered:

- Plate dimensions width/height/thickness
- Min. number of elements along width/height
- Uniform axial stress in width (x) and height (y) direction
- Support conditions (2-/3- or 4-sided support)
- Material (Steel, Aluminium or User-defined)
- Number of critical load factors and modeshapes to be evaluated

The critical buckling stress is calculated as applied axial stress multiplied by the critical load factors. The critical load factors as well as the respective modeshapes of the plate are evaluated within an Eigenvalue Analysis.

## How to use the programm:
The programm can be called with the following arguments:
"-default": A set of default input parameters is used for demonstration purposes.
"-user":    The input parameters listed above can be specified by the user.
"-help":    A short description of the programm and it's usage is printed.

As an output, the programm prints a table of the calculated critical load factors and critical buckling stresses to the terminal window. Moreover, 3D plots are produced and stored as .png file in the root directory of the program.

## Behind the scenes:
The input parameters are used to build a 3D-Finite Element model using the open source FE environment of [OpenSeesPy](https://openseespydoc.readthedocs.io/en/latest/index.html). Unfortunately, [OpenSeesPy](https://openseespydoc.readthedocs.io/en/latest/index.html) does not have a built-in linear bifurcation analysis (LBA) to calculate the critical load factors. However, adopting the idea Michael H. Scott explained in this [blog post](https://portwooddigital.com/2021/05/29/right-under-your-nose/) worked out perfectly after some minor adjustments. To visualize the modeshapes, I set up aditional static analyses with imposed nodal deformations that correspond to the modeshapes and solve it. This way I can leverage the [Opsvis](https://opsvis.readthedocs.io/en/latest/#) library to plot the deformed shape of this static analysis and save it to a file using [Matplotlib](https://matplotlib.org/).

## Libraries used:
- [OpenSeesPy](https://openseespydoc.readthedocs.io/en/latest/index.html): OpenSees is a software framework for developing applications to simulate the performance of structural systems using the Finite-Element-Method. It was developed for scientific and educational purposes at UC Berkeley and ported to python by members of the Oregon State University.

- [Opsvis](https://opsvis.readthedocs.io/en/latest/#): Opsvis is an OpenSeesPy postprocessing and visualization module that offers a variety of predefined plots for pre- and postprocessing of OpenSeesPy models.

- [NumPy](https://numpy.org/devdocs/index.html): NumPy is the fundamental package for scientific computing in Python.

- [SciPy](https://scipy.org/): SciPy provides many advanced algorithms and extends the capabilities of NumPy. In BuckleUp the Eigenvalue solver of SciPy is used.

- [Matplotlib](https://matplotlib.org/): Matplotlib is a comprehensive library for creating visualizations in Python. It is used to save the Opsvis plots to an external file.

- [tabulate](https://github.com/astanin/python-tabulate): Tabulate allows easy and nice printing of tabular data in Python.
